"""DEPRECATO — UI Streamlit sostituita da FastAPI (server.py). Non usare."""

"""Interfaccia web Streamlit per Sbobinator (deprecata)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

import streamlit as st

from sbobinator import __version__
from sbobinator.config import (
    DEFAULT_MODEL,
    SummaryLength,
    SummaryMode,
    TranscribeConfig,
    data_dir,
    local_summary_model_available,
    project_root,
)
from sbobinator.jobs import (
    ACTIVE_STATUSES,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_QUEUED,
    STATUS_RUNNING,
    JobRecord,
    cancel_job,
    count_active_jobs,
    enqueue_job,
    get_job,
    jobs_root,
    load_active_queue,
    load_index,
)
from sbobinator.worker import start_background_worker

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
    .files-box {
        background: #0f172a; border: 1px solid #22c55e; border-radius: 12px;
        padding: 1rem 1.25rem; margin: 1rem 0;
    }
    .files-box h4 { color: #86efac; margin: 0 0 0.75rem 0; font-size: 1rem; }
    .files-box code { color: #e2e8f0; font-size: 0.85rem; word-break: break-all; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _ensure_worker() -> None:
    start_background_worker()


def _init_session() -> None:
    if "selected_job_id" not in st.session_state:
        jobs = load_index()
        st.session_state["selected_job_id"] = jobs[0].id if jobs else ""
    if "uploader_nonce" not in st.session_state:
        st.session_state["uploader_nonce"] = 0


def _open_folder(path: Path) -> None:
    resolved = path.resolve()
    if sys.platform == "win32":
        os.startfile(resolved)  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(resolved)])  # noqa: S603
    else:
        subprocess.Popen(["xdg-open", str(resolved)])  # noqa: S603


def _render_files_box(job: JobRecord) -> None:
    """Box evidente con percorsi file su disco."""
    folder = job.path.resolve()
    lines: list[str] = [f"📁 Cartella lavoro: {folder}"]
    if job.txt_path().exists():
        lines.append(f"📝 Trascrizione: {job.txt_path().resolve()}")
    if job.srt_path().exists():
        lines.append(f"🎬 Sottotitoli:   {job.srt_path().resolve()}")
    if job.summary_path().exists():
        lines.append(f"📋 Riassunto:     {job.summary_path().resolve()}")

    st.markdown(
        f'<div class="files-box"><h4>💾 File salvati su disco</h4>'
        + "".join(f"<div><code>{line}</code></div>" for line in lines)
        + "</div>",
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📂 Apri cartella in Esplora file", key=f"open_{job.id}", use_container_width=True):
            _open_folder(folder)
    with col_b:
        st.caption(f"Base progetto: `{data_dir()}`")


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
        err = job.summary_error
        if "SSL" in err or "CERTIFICATE" in err:
            err = (
                "Modello IT5 non disponibile offline. "
                "Esegui: python scripts/download_summary_model.py"
            )
        st.warning("Riassunto richiesto ma non generato.")
        st.caption(err)
        return

    if job.status in ACTIVE_STATUSES:
        st.info("Riassunto in attesa — il lavoro è ancora in coda o in elaborazione.")
        return

    st.warning(
        "Riassunto richiesto ma file non trovato. "
        "Il testo della trascrizione è comunque salvato nella cartella del lavoro."
    )


def _render_job(job: JobRecord) -> None:
    st.markdown("---")

    if job.status == STATUS_FAILED:
        st.error(f"❌ Lavoro fallito — {job.source_name}")
        st.caption(job.error or job.progress_message)
        _render_files_box(job)
        return

    if job.status in ACTIVE_STATUSES:
        if job.status == STATUS_QUEUED:
            st.markdown(f"## ⏳ In coda — {job.source_name}")
        else:
            st.markdown(f"## ▶️ In elaborazione — {job.source_name}")
        st.progress(job.progress_pct / 100.0, text=job.progress_message or job.phase)
        st.caption(f"Cartella: `{job.path.name}` · Stato: **{job.status}**")
        if job.txt_path().exists():
            _render_files_box(job)
        else:
            st.info(f"I file verranno salvati in: `{job.path.resolve()}`")
        return

    if not job.txt_path().exists():
        st.warning(f"Lavoro {job.id} — trascrizione non ancora disponibile.")
        st.caption(f"Cartella prevista: `{job.path.resolve()}`")
        return

    text = job.txt_path().read_text(encoding="utf-8")
    st.markdown(f"## ✅ Risultati — {job.source_name}")
    st.caption(f"ID lavoro: `{job.id}`")

    _render_files_box(job)

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
        st.markdown("**Percorsi completi su disco:**")
        for label, p in [
            ("Trascrizione (TXT)", job.txt_path()),
            ("Sottotitoli (SRT)", job.srt_path()),
            ("Riassunto", job.summary_path()),
        ]:
            if p.exists():
                st.code(str(p.resolve()), language=None)

        st.divider()
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


def _dedupe_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    seen: set[str] = set()
    unique: list[JobRecord] = []
    for job in jobs:
        if job.id in seen:
            continue
        seen.add(job.id)
        unique.append(job)
    return unique


def _on_cancel_job(job_id: str) -> None:
    if cancel_job(job_id):
        st.session_state["_cancel_flash"] = f"Annullato: {job_id}"
    else:
        st.session_state["_cancel_flash"] = (
            "Impossibile annullare: il job e gia in elaborazione o terminato."
        )


def _on_cancel_all_queued() -> None:
    cancelled = 0
    for job in load_active_queue():
        if job.status == STATUS_QUEUED and cancel_job(job.id):
            cancelled += 1
    st.session_state["_cancel_flash"] = f"Annullati {cancelled} job in coda."


@st.fragment(run_every=timedelta(seconds=2))
def _render_queue_panel_live() -> None:
    """Coda live: aggiorna solo questo blocco (non rerun globale che mangia i click)."""
    flash = st.session_state.pop("_cancel_flash", None)
    if flash:
        st.toast(flash)

    active = _dedupe_jobs(load_active_queue())

    st.markdown("### 🔄 Coda elaborazione")
    if not active:
        st.caption("Nessun lavoro in coda o in elaborazione.")
        return

    queued = [j for j in active if j.status == STATUS_QUEUED]
    st.caption(
        f"{len(active)} lavoro/i attivi ({len(queued)} in attesa) · "
        f"cartella: `{jobs_root().resolve()}`"
    )
    if len(queued) > 1:
        st.button(
            "Annulla tutti in coda",
            key="cancel_all_queued",
            on_click=_on_cancel_all_queued,
        )

    with st.container(border=True):
        for job in active:
            cols = st.columns([4, 1])
            with cols[0]:
                icon = "▶️" if job.status == STATUS_RUNNING else "⏳"
                stato = "in elaborazione" if job.status == STATUS_RUNNING else "in coda"
                st.markdown(f"**{icon} {job.source_name}** — _{stato}_")
                st.progress(job.progress_pct / 100.0, text=job.progress_message or job.status)
                if job.summary_requested:
                    mode = "IT5" if job.summary_mode == "abstractive" else "sintesi"
                    st.caption(f"`{job.path.name}` · riassunto: {mode}")
                else:
                    st.caption(f"`{job.path.name}` · senza riassunto")
            with cols[1]:
                if job.status == STATUS_QUEUED:
                    st.button(
                        "Annulla",
                        key=f"cancel_{job.id}",
                        on_click=_on_cancel_job,
                        args=(job.id,),
                    )
                elif job.status == STATUS_RUNNING:
                    st.caption("_non annullabile_")


def _sidebar_jobs() -> JobRecord | None:
    jobs = load_index()
    active = load_active_queue()
    with st.sidebar:
        st.divider()
        if active:
            st.subheader("🔄 Coda")
            for job in active:
                icon = "▶️" if job.status == STATUS_RUNNING else "⏳"
                pct = int(job.progress_pct)
                st.caption(f"{icon} {job.source_name} ({pct}%)")
        st.subheader("📚 I tuoi lavori")
        st.caption(f"Tutti salvati in `{jobs_root().name}/` — nessun overwrite.")
        if not jobs:
            st.caption("Nessun lavoro ancora.")
            return None

        labels = {j.id: j.label for j in jobs}
        selected = st.selectbox(
            "Seleziona lavoro",
            options=list(labels.keys()),
            format_func=lambda jid: labels[jid],
            index=0,
        )
        st.session_state["selected_job_id"] = selected
        completed = sum(1 for j in jobs if j.status == STATUS_COMPLETED)
        st.caption(f"{len(jobs)} totali · {completed} completati")
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
        abstractive_ok = local_summary_model_available()
        mode_options = ["extractive", "abstractive"] if abstractive_ok else ["extractive"]
        summary_mode = st.selectbox(
            "Modalità",
            mode_options,
            format_func=lambda x: "Sintesi (estrativo)" if x == "extractive" else "Riassunto (IT5)",
            disabled=not summary_enabled,
        )
        if summary_enabled and not abstractive_ok:
            st.caption(
                "Riassunto (IT5): scarica prima il modello con "
                "`python scripts/download_summary_model.py` (~400 MB)."
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
        if summary_mode == "abstractive" and summary_enabled and abstractive_ok:
            st.caption("IT5 caricato da models/it5-small-news-summarization/ (offline).")

        st.divider()
        st.caption(f"Sbobinator v{__version__} · Python: `{sys.executable}`")
        st.caption("Modello ASR: ~2.5 GB al primo utilizzo")
        st.caption("ffmpeg deve essere installato e nel PATH")

    return TranscribeConfig(model_name=model, device=device_val), summary_enabled, summary_mode, summary_length


def main() -> None:
    _ensure_worker()
    _init_session()
    config, summary_enabled, summary_mode, summary_length = _sidebar_config()
    selected_job = _sidebar_jobs()

    st.markdown(
        """
        <div class="hero">
            <h1>🎙️ Sbobinator</h1>
            <p>Trascrizione in italiano · Coda job · File sempre salvati su disco</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active_count = count_active_jobs()
    col1, col2, col3, col4 = st.columns(4)
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
    with col4:
        st.markdown(
            f'<div class="stat-card"><div class="label">In coda</div>'
            f'<div class="value">{active_count}</div></div>',
            unsafe_allow_html=True,
        )

    _render_queue_panel_live()

    st.markdown("### 📂 Carica file")
    st.caption("Puoi caricare più file: verranno accodati e elaborati uno alla volta.")
    # L'uploader deve stare FUORI dal form: dentro st.form i file non sono visibili
    # a Python finché non si invia il form, quindi il bottone resterebbe sempre disabilitato.
    uploaded_files = st.file_uploader(
        "Trascina qui audio o video",
        type=["mp4", "mkv", "avi", "mov", "webm", "wav", "mp3", "flac", "m4a", "ogg"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state['uploader_nonce']}",
    )
    submitted = st.button(
        "▶️ Accoda sbobinatura",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files,
    )

    if submitted and uploaded_files:
        enqueued: list[str] = []
        skipped: list[str] = []
        work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_ui_"))
        try:
            for uploaded in uploaded_files:
                source_name = uploaded.name
                if any(j.source_name == source_name for j in load_active_queue()):
                    skipped.append(source_name)
                    continue
                stem = Path(source_name).stem
                tmp_path = work_dir / source_name
                tmp_path.write_bytes(uploaded.getvalue())
                job = enqueue_job(
                    tmp_path,
                    source_name,
                    stem,
                    summary_requested=summary_enabled,
                    model_name=config.model_name,
                    device=config.device,
                    summary_mode=summary_mode,
                    summary_length=summary_length,
                )
                enqueued.append(job.id)
            if enqueued:
                st.session_state["selected_job_id"] = enqueued[-1]
                st.session_state["uploader_nonce"] += 1
                n = len(enqueued)
                folder = jobs_root().resolve()
                st.success(
                    f"{'1 file accodato' if n == 1 else f'{n} file accodati'}! "
                    f"I risultati saranno salvati in sottocartelle di:\n`{folder}`"
                )
                for jid in enqueued:
                    j = get_job(jid)
                    if j:
                        st.caption(f"• `{jid}` → `{j.path.resolve()}`")
            if skipped:
                st.warning(
                    "Saltati (già in coda o in elaborazione): "
                    + ", ".join(f"`{n}`" for n in skipped)
                )
            if enqueued or skipped:
                st.rerun()
        finally:
            import shutil

            shutil.rmtree(work_dir, ignore_errors=True)

    job_id = st.session_state.get("selected_job_id", "")
    job = get_job(job_id) if job_id else selected_job
    if job:
        # Evita duplicare progress/coda: se attivo, basta il pannello coda sopra
        if job.status in (STATUS_COMPLETED, STATUS_FAILED):
            _render_job(job)
        elif job.status in ACTIVE_STATUSES:
            st.markdown("---")
            st.info(
                f"**{job.source_name}** è in coda o in elaborazione. "
                f"Segui lo stato nel riquadro **Coda elaborazione** sopra.  \n"
                f"Cartella output: `{job.path.name}`"
            )
        else:
            _render_job(job)


if __name__ == "__main__":
    main()
