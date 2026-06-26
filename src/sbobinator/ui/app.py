"""Interfaccia web Streamlit per Sbobinator."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import streamlit as st

from sbobinator.config import DEFAULT_MODEL, SummaryLength, SummaryMode, TranscribeConfig, project_root
from sbobinator.export import TranscriptResult, export_srt, export_summary_text, export_txt
from sbobinator.jobs import JobRecord, get_job, load_index, register_job, update_job
from sbobinator.summarize import summarize
from sbobinator.transcribe import transcribe, unload_model

st.set_page_config(
    page_title="Sbobinator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main .block-container { padding-top: 2rem; max-width: 1100px; }
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 50%, #1e2433 100%);
        border: 1px solid #3d4f6f; border-radius: 16px;
        padding: 2rem 2.5rem; margin-bottom: 2rem;
    }
    .hero h1 { color: #f0f4ff; font-size: 2.2rem; font-weight: 700; margin: 0 0 0.5rem 0; }
    .hero p { color: #94a3b8; font-size: 1.05rem; margin: 0; }
    .stat-card {
        background: #1e2433; border: 1px solid #334155; border-radius: 12px;
        padding: 1rem 1.25rem; text-align: center;
    }
    .stat-card .label { color: #64748b; font-size: 0.8rem; text-transform: uppercase; }
    .stat-card .value { color: #38bdf8; font-size: 1.4rem; font-weight: 600; margin-top: 0.25rem; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _init_session() -> None:
    if "selected_job_id" not in st.session_state:
        jobs = load_index()
        st.session_state["selected_job_id"] = jobs[0].id if jobs else ""


def _export_job_files(result: TranscriptResult, job: JobRecord) -> None:
    job.path.mkdir(parents=True, exist_ok=True)
    export_txt(result, job.txt_path())
    export_srt(result, job.srt_path())
    job.transcript_chars = len(result.text)


def _summary_tab_message(job: JobRecord, summary_text: str) -> None:
    if summary_text:
        st.markdown(summary_text)
        if job.has_summary:
            st.caption("Riassunto generato con successo.")
        return

    if not job.summary_requested:
        st.info("Riassunto disattivato per questo lavoro. Attivalo nella sidebar prima di sbobinare.")
        return

    if job.summary_error:
        st.warning("Riassunto richiesto ma non generato.")
        st.caption(job.summary_error)
        return

    st.warning(
        "Riassunto richiesto ma file non trovato. "
        "Il testo della trascrizione è comunque salvato nella cartella del lavoro."
    )


def _render_job(job: JobRecord) -> None:
    if not job.txt_path().exists():
        st.error(f"File del lavoro {job.id} non trovato su disco.")
        return

    text = job.txt_path().read_text(encoding="utf-8")
    st.markdown("---")
    st.markdown(f"## ✅ Risultati — {job.source_name}")
    st.caption(f"ID lavoro: `{job.id}` · cartella: `{job.path}`")

    tab1, tab2, tab3 = st.tabs(["📝 Trascrizione", "📋 Riassunto", "💾 Download"])

    with tab1:
        st.text_area("Testo completo", value=text, height=320, label_visibility="collapsed")
        st.caption(f"{len(text):,} caratteri · {len(text.split()):,} parole")

    with tab2:
        summary_text = ""
        if job.summary_path().exists():
            summary_text = job.summary_path().read_text(encoding="utf-8")
        _summary_tab_message(job, summary_text)

    with tab3:
        if job.txt_path().exists():
            st.download_button(
                "⬇️ Scarica TXT",
                job.txt_path().read_text(encoding="utf-8"),
                file_name=f"{job.stem}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        if job.srt_path().exists():
            st.download_button(
                "⬇️ Scarica SRT",
                job.srt_path().read_text(encoding="utf-8"),
                file_name=f"{job.stem}.srt",
                mime="text/plain",
                use_container_width=True,
            )
        if job.summary_path().exists():
            st.download_button(
                "⬇️ Scarica riassunto",
                job.summary_path().read_text(encoding="utf-8"),
                file_name=f"{job.stem}_riassunto.txt",
                mime="text/plain",
                use_container_width=True,
            )


def _sidebar_jobs() -> JobRecord | None:
    jobs = load_index()
    with st.sidebar:
        st.divider()
        st.subheader("📚 Storico lavori")
        if not jobs:
            st.caption("Nessun lavoro ancora. Ogni sbobinata viene salvata qui.")
            return None

        labels = {j.id: j.label for j in jobs}
        selected = st.selectbox(
            "Seleziona lavoro",
            options=list(labels.keys()),
            format_func=lambda jid: labels[jid],
            index=0,
        )
        st.session_state["selected_job_id"] = selected
        st.caption(f"{len(jobs)} lavori salvati — nessuno viene sovrascritto.")
        return get_job(selected)


def _sidebar_config() -> tuple[TranscribeConfig, bool, str, str]:
    with st.sidebar:
        st.header("⚙️ Impostazioni")
        device = st.selectbox("Dispositivo", ["auto", "cpu", "cuda"], index=0)
        device_val = None if device == "auto" else device
        model = st.text_input("Modello ASR", value=DEFAULT_MODEL)

        st.divider()
        st.subheader("Riassunto")
        summary_enabled = st.toggle("Genera riassunto", value=True)
        summary_mode = st.selectbox(
            "Modalità",
            ["extractive", "abstractive"],
            format_func=lambda x: "Veloce (estrativo)" if x == "extractive" else "Qualità (mT5)",
            disabled=not summary_enabled,
        )
        summary_length = st.selectbox(
            "Lunghezza riassunto",
            ["auto", "short", "normal", "detailed"],
            format_func=lambda x: {
                "auto": "Automatica (in base al testo)",
                "short": "Breve",
                "normal": "Normale",
                "detailed": "Dettagliato",
            }[x],
            disabled=not summary_enabled,
        )
        if summary_mode == "abstractive" and summary_enabled:
            st.caption("mT5: su Windows può fallire per SSL. Preferisci estrattivo.")

        st.divider()
        st.caption("Modello ASR: ~2.5 GB al primo utilizzo")
        st.caption("ffmpeg deve essere installato e nel PATH")

    return TranscribeConfig(model_name=model, device=device_val), summary_enabled, summary_mode, summary_length


def main() -> None:
    _init_session()
    config, summary_enabled, summary_mode, summary_length = _sidebar_config()
    selected_job = _sidebar_jobs()

    st.markdown(
        """
        <div class="hero">
            <h1>🎙️ Sbobinator</h1>
            <p>Trascrizione audio e video in italiano · Riassunto · Storico lavori persistente</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="stat-card"><div class="label">Device</div>'
            f'<div class="value">{config.resolve_device().upper()}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="stat-card"><div class="label">Lingua</div>'
            '<div class="value">IT</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        jobs_count = len(load_index())
        st.markdown(
            f'<div class="stat-card"><div class="label">Lavori salvati</div>'
            f'<div class="value">{jobs_count}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 📂 Carica file")
    uploaded = st.file_uploader(
        "Trascina qui audio o video",
        type=["mp4", "mkv", "avi", "mov", "webm", "wav", "mp3", "flac", "m4a", "ogg"],
    )
    run = st.button("▶️ Sbobina", type="primary", use_container_width=True, disabled=uploaded is None)

    if run and uploaded:
        work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_ui_"))
        source_name = uploaded.name
        stem = Path(source_name).stem
        job = register_job(source_name, stem, summary_requested=summary_enabled)

        try:
            input_path = work_dir / source_name
            input_path.write_bytes(uploaded.getvalue())

            progress = st.progress(0, text="Preparazione audio...")
            progress.progress(15, text="Caricamento modello NeMo (1–2 min al primo avvio)...")

            with st.spinner("Trascrizione in corso..."):
                result = transcribe(input_path, config=config, work_dir=work_dir)
            progress.progress(55, text="Salvataggio trascrizione...")

            _export_job_files(result, job)
            update_job(job)

            if summary_enabled and result.text.strip():
                progress.progress(70, text="Riassunto in corso...")
                unload_model()
                try:
                    with st.spinner("Generazione riassunto..."):
                        summary = summarize(
                            result.text,
                            mode=SummaryMode(summary_mode),
                            length=SummaryLength(summary_length),
                        )
                    export_summary_text(summary.text, job.summary_path())
                    job.has_summary = True
                except Exception as exc:
                    job.summary_error = str(exc)
                    job.has_summary = False
                update_job(job)

            progress.progress(100, text="Fatto!")
            st.session_state["selected_job_id"] = job.id
            st.success(f"Completato! Lavoro salvato: {job.id}")
            st.rerun()

        except Exception as exc:
            st.error(f"Errore: {exc}")
            st.exception(exc)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    job_id = st.session_state.get("selected_job_id", "")
    job = get_job(job_id) if job_id else selected_job
    if job:
        _render_job(job)


if __name__ == "__main__":
    main()
