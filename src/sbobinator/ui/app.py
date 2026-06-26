"""Interfaccia web Streamlit per Sbobinator."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import streamlit as st

from sbobinator.config import DEFAULT_MODEL, SummaryLength, SummaryMode, TranscribeConfig, project_root
from sbobinator.export import export_all, export_summary_text
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

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 50%, #1e2433 100%);
        border: 1px solid #3d4f6f;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }

    .hero h1 {
        color: #f0f4ff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }

    .hero p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }

    .stat-card {
        background: #1e2433;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }

    .stat-card .label {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-card .value {
        color: #38bdf8;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    div[data-testid="stFileUploader"] {
        background: #1a1f2e;
        border: 2px dashed #475569;
        border-radius: 12px;
        padding: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _init_session() -> None:
    defaults = {
        "transcript_text": "",
        "summary_text": "",
        "filename": "",
        "summary_meta": "",
        "job_done": False,
        "output_dir": project_root() / "data" / "output",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _render_results(output_dir: Path, stem: str) -> None:
    text = st.session_state.get("transcript_text", "")
    if not text:
        txt_path = output_dir / f"{stem}.txt"
        if txt_path.exists():
            text = txt_path.read_text(encoding="utf-8")
            st.session_state["transcript_text"] = text

    if not text:
        return

    st.markdown("---")
    st.markdown("## ✅ Risultati")
    tab1, tab2, tab3 = st.tabs(["📝 Trascrizione", "📋 Riassunto", "💾 Download"])

    with tab1:
        st.text_area("Testo completo", value=text, height=320, label_visibility="collapsed")
        st.caption(f"{len(text):,} caratteri · {len(text.split()):,} parole")

    with tab2:
        summary_text = st.session_state.get("summary_text", "")
        if not summary_text:
            sum_path = output_dir / f"{stem}_riassunto.txt"
            if sum_path.exists():
                summary_text = sum_path.read_text(encoding="utf-8")
        if summary_text:
            st.markdown(summary_text)
            if st.session_state.get("summary_meta"):
                st.caption(st.session_state["summary_meta"])
        else:
            st.info("Riassunto non generato. Attivalo nella sidebar e riesegui.")

    with tab3:
        txt_path = output_dir / f"{stem}.txt"
        srt_path = output_dir / f"{stem}.srt"
        sum_path = output_dir / f"{stem}_riassunto.txt"

        if txt_path.exists():
            st.download_button(
                "⬇️ Scarica TXT",
                txt_path.read_text(encoding="utf-8"),
                file_name=f"{stem}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        if srt_path.exists():
            st.download_button(
                "⬇️ Scarica SRT",
                srt_path.read_text(encoding="utf-8"),
                file_name=f"{stem}.srt",
                mime="text/plain",
                use_container_width=True,
            )
        if sum_path.exists():
            st.download_button(
                "⬇️ Scarica riassunto",
                sum_path.read_text(encoding="utf-8"),
                file_name=f"{stem}_riassunto.txt",
                mime="text/plain",
                use_container_width=True,
            )


def _hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🎙️ Sbobinator</h1>
            <p>Trascrizione audio e video in italiano · Riassunto intelligente · Tutto in locale</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sidebar() -> TranscribeConfig:
    with st.sidebar:
        st.header("⚙️ Impostazioni")

        device = st.selectbox(
            "Dispositivo",
            options=["auto", "cpu", "cuda"],
            index=0,
            help="auto = GPU NVIDIA se disponibile, altrimenti CPU",
        )
        device_val = None if device == "auto" else device

        model = st.text_input("Modello ASR", value=DEFAULT_MODEL)

        st.divider()
        st.subheader("Riassunto")
        summary_enabled = st.toggle("Genera riassunto", value=True)
        summary_mode = st.selectbox(
            "Modalità",
            options=["extractive", "abstractive"],
            format_func=lambda x: "Veloce (estrativo)" if x == "extractive" else "Qualità (mT5)",
            disabled=not summary_enabled,
        )
        if summary_mode == "extractive":
            summary_length = st.selectbox(
                "Lunghezza riassunto",
                options=["auto", "short", "normal", "detailed"],
                format_func=lambda x: {
                    "auto": "Automatica (in base al testo)",
                    "short": "Breve",
                    "normal": "Normale",
                    "detailed": "Dettagliato",
                }[x],
                disabled=not summary_enabled,
                help="Il numero di frasi si adatta alla lunghezza della trascrizione",
            )
        else:
            summary_length = st.selectbox(
                "Lunghezza riassunto",
                options=["auto", "short", "normal", "detailed"],
                format_func=lambda x: {
                    "auto": "Automatica (in base al testo)",
                    "short": "Breve",
                    "normal": "Normale",
                    "detailed": "Dettagliato",
                }[x],
                disabled=not summary_enabled,
            )
            st.caption("mT5-small: primo avvio scarica ~300 MB")

        st.divider()
        st.caption("Modello ASR: ~2.5 GB al primo utilizzo")
        st.caption("ffmpeg deve essere installato e nel PATH")

    st.session_state["summary_enabled"] = summary_enabled
    st.session_state["summary_mode"] = summary_mode
    st.session_state["summary_length"] = summary_length

    return TranscribeConfig(model_name=model, device=device_val)


def main() -> None:
    _init_session()
    config = _sidebar()
    _hero()

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
        st.markdown(
            '<div class="stat-card"><div class="label">Output</div>'
            '<div class="value">TXT · SRT</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 📂 Carica file")
    uploaded = st.file_uploader(
        "Trascina qui audio o video",
        type=["mp4", "mkv", "avi", "mov", "webm", "wav", "mp3", "flac", "m4a", "ogg"],
        help="Supportati: MP4, MKV, WAV, MP3, FLAC e altri",
    )

    run = st.button("▶️ Sbobina", type="primary", use_container_width=True, disabled=uploaded is None)

    if run and uploaded:
        work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_ui_"))
        stem = Path(uploaded.name).stem
        output_dir = project_root() / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            input_path = work_dir / uploaded.name
            input_path.write_bytes(uploaded.getvalue())

            progress = st.progress(0, text="Preparazione audio...")
            progress.progress(15, text="Caricamento modello NeMo (1–2 min al primo avvio)...")

            with st.spinner("Trascrizione in corso..."):
                result = transcribe(input_path, config=config, work_dir=work_dir)
            progress.progress(60, text="Trascrizione completata")

            export_all(result, output_dir, stem, ["txt", "srt"])
            st.session_state["transcript_text"] = result.text
            st.session_state["filename"] = stem
            st.session_state["summary_text"] = ""
            st.session_state["summary_meta"] = ""

            if st.session_state.get("summary_enabled") and result.text.strip():
                progress.progress(75, text="Riassunto in corso...")
                unload_model()
                mode = SummaryMode(st.session_state["summary_mode"])
                length = SummaryLength(st.session_state["summary_length"])
                with st.spinner("Generazione riassunto..."):
                    summary = summarize(result.text, mode=mode, length=length)
                export_summary_text(summary.text, output_dir / f"{stem}_riassunto.txt")
                st.session_state["summary_text"] = summary.text
                mode_label = "estrativa" if summary.mode == SummaryMode.extractive else "astrattiva (mT5)"
                st.session_state["summary_meta"] = (
                    f"Modalità: {mode_label} · "
                    f"{summary.summary_sentences} frasi su {summary.source_sentences} originali"
                )

            progress.progress(100, text="Fatto!")
            st.session_state["job_done"] = True
            st.success("Completato!")
            st.rerun()

        except Exception as exc:
            st.error(f"Errore: {exc}")
            st.exception(exc)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    stem = st.session_state.get("filename", "")
    output_dir = project_root() / "data" / "output"
    if not stem:
        txts = sorted(output_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        txts = [p for p in txts if not p.name.endswith("_riassunto.txt")]
        if txts:
            stem = txts[0].stem
            st.session_state["filename"] = stem
    if stem:
        _render_results(output_dir, stem)


if __name__ == "__main__":
    main()
