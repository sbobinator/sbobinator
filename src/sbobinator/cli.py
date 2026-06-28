import logging
import shutil
import tempfile
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from sbobinator import __version__
from sbobinator.config import DEFAULT_MODEL, SummaryLength, SummaryMode, TranscribeConfig
from sbobinator.export import export_all, export_summary_text
from sbobinator.jobs import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    enqueue_job,
    get_job,
    jobs_root,
    load_index,
    requeue_failed,
)
from sbobinator.pipeline import run_pipeline
from sbobinator.summarize import summarize
from sbobinator.transcribe import transcribe as run_transcribe
from sbobinator.transcribe import unload_model
from sbobinator.ui.launch import launch_ui
from sbobinator.worker import run_worker_forever

app = typer.Typer(
    name="sbobina",
    help="Sbobina audio e video in testo (italiano) con NVIDIA NeMo Parakeet.",
)
console = Console()
jobs_app = typer.Typer(help="Gestione lavori e coda.")
app.add_typer(jobs_app, name="jobs")


class OutputFormat(str, Enum):
    txt = "txt"
    srt = "srt"


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Senza sottocomando avvia l'interfaccia web."""
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]Avvio interfaccia web...[/bold cyan]")
        console.print("Apri il browser su [link=http://localhost:8501]http://localhost:8501[/link]")
        launch_ui()


@app.command()
def ui(
    port: int = typer.Option(8501, "--port", "-p", help="Porta del server web"),
) -> None:
    """Avvia l'interfaccia web (FastAPI)."""
    console.print(f"[bold cyan]Interfaccia web su http://localhost:{port}[/bold cyan]")
    launch_ui(port=port)


@app.command()
def worker(
    poll_interval: float = typer.Option(1.0, "--interval", help="Secondi tra un poll e l'altro"),
) -> None:
    """Avvia il worker che elabora la coda job (per Docker o server headless)."""
    _setup_logging(verbose=False)
    console.print("[bold cyan]Worker coda avviato[/bold cyan]")
    console.print(f"Cartella lavori: [cyan]{jobs_root()}[/cyan]")
    console.print("Ctrl+C per fermare.\n")
    run_worker_forever(poll_interval=poll_interval)


@app.command()
def transcribe(
    input_path: Path = typer.Argument(..., help="File audio o video da trascrivere", exists=True),
    output_dir: Path = typer.Option(
        Path("data/output"),
        "--output",
        "-o",
        help="Cartella di output (solo con --legacy-output)",
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        "-m",
        help="Modello NeMo pre-addestrato",
    ),
    device: str | None = typer.Option(
        None,
        "--device",
        "-d",
        help="cpu o cuda (default: auto)",
    ),
    formats: list[OutputFormat] = typer.Option(
        [OutputFormat.txt, OutputFormat.srt],
        "--format",
        "-f",
        help="Formati di export (solo con --legacy-output)",
    ),
    summarize_result: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Genera anche un riassunto del testo",
    ),
    summary_mode: SummaryMode = typer.Option(
        SummaryMode.extractive,
        "--summary-mode",
        help="extractive=sintesi veloce, abstractive=riassunto IT5",
    ),
    summary_length: SummaryLength = typer.Option(
        SummaryLength.auto,
        "--summary-length",
        help="auto, short, normal, detailed",
    ),
    legacy_output: bool = typer.Option(
        False,
        "--legacy-output",
        help="Salva in data/output/{nome}.txt senza registro jobs/",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Trascrive un file audio o video in testo."""
    _setup_logging(verbose)
    config = TranscribeConfig(model_name=model, device=device)

    if legacy_output:
        fmt_names = [f.value for f in formats]
        console.print(f"[bold]Input:[/bold]  {input_path}")
        console.print(f"[bold]Output:[/bold]  {output_dir} ({', '.join(fmt_names)})")
        work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_"))
        try:
            with console.status("[bold green]Trascrizione in corso..."):
                result = run_transcribe(input_path, config=config, work_dir=work_dir)
            written = export_all(result, output_dir, input_path.stem, fmt_names)
            if summarize_result:
                unload_model()
                with console.status("[bold green]Riassunto in corso..."):
                    summary = summarize(result.text, mode=summary_mode, length=summary_length)
                path = export_summary_text(
                    summary.text, output_dir / f"{input_path.stem}_riassunto.txt"
                )
                written.append(path)
            console.print("\n[bold green]Completato![/bold green]")
            for path in written:
                console.print(f"  → {path}")
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
        return

    console.print(f"[bold]Input:[/bold]  {input_path}")
    console.print(f"[bold]Modello:[/bold] {model}")
    console.print(f"[bold]Device:[/bold]  {config.resolve_device()}")

    job = enqueue_job(
        input_path,
        input_path.name,
        input_path.stem,
        summary_requested=summarize_result,
        model_name=model,
        device=device,
        summary_mode=summary_mode.value,
        summary_length=summary_length.value,
    )
    console.print(f"[bold]Job ID:[/bold]  {job.id}")
    console.print(f"[bold]Cartella:[/bold] {job.path}")

    with console.status("[bold green]Elaborazione in corso..."):
        run_pipeline(job.id)

    job = get_job(job.id)
    if job and job.status == STATUS_COMPLETED:
        console.print("\n[bold green]Completato![/bold green]")
        console.print(f"  → {job.txt_path()}")
        console.print(f"  → {job.srt_path()}")
        if job.summary_path().exists():
            console.print(f"  → {job.summary_path()}")
    elif job and job.status == STATUS_FAILED:
        console.print(f"\n[bold red]Fallito:[/bold red] {job.error}")
        raise typer.Exit(code=1)


@jobs_app.command("list")
def jobs_list(
    status: str | None = typer.Option(None, "--status", help="Filtra per stato"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Elenca i lavori salvati."""
    jobs = load_index(status=status, limit=limit) if status else load_index(limit=limit)
    if not jobs:
        console.print("Nessun lavoro.")
        return
    table = Table(title="Lavori Sbobinator")
    table.add_column("ID")
    table.add_column("File")
    table.add_column("Stato")
    table.add_column("Cartella")
    for job in jobs:
        table.add_row(job.id, job.source_name, job.status, str(job.path))
    console.print(table)


@jobs_app.command("show")
def jobs_show(job_id: str) -> None:
    """Mostra dettaglio di un lavoro."""
    job = get_job(job_id)
    if not job:
        console.print(f"[red]Job {job_id} non trovato[/red]")
        raise typer.Exit(code=1)
    console.print(f"[bold]ID:[/bold]      {job.id}")
    console.print(f"[bold]File:[/bold]    {job.source_name}")
    console.print(f"[bold]Stato:[/bold]   {job.status}")
    console.print(f"[bold]Cartella:[/bold] {job.path}")
    if job.txt_path().exists():
        console.print(f"[bold]TXT:[/bold]     {job.txt_path()}")
    if job.srt_path().exists():
        console.print(f"[bold]SRT:[/bold]     {job.srt_path()}")
    if job.summary_path().exists():
        console.print(f"[bold]Riassunto:[/bold] {job.summary_path()}")
    if job.error:
        console.print(f"[bold red]Errore:[/bold red] {job.error}")


@jobs_app.command("retry")
def jobs_retry(
    job_id: str | None = typer.Argument(None, help="ID job (se omesso, ritenta tutti i falliti)"),
) -> None:
    """Rimette in coda job falliti per rielaborarli."""
    if job_id:
        from sbobinator.jobs import requeue_job

        if requeue_job(job_id):
            console.print(f"[green]Job {job_id} rimesso in coda.[/green]")
        else:
            console.print(f"[red]Impossibile rimettere in coda {job_id}[/red]")
            raise typer.Exit(code=1)
        return

    requeued = requeue_failed()
    if not requeued:
        console.print("Nessun job fallito da ritentare.")
        return
    console.print(f"[green]{len(requeued)} job rimessi in coda:[/green]")
    for jid in requeued:
        console.print(f"  • {jid}")


@app.command()
def info() -> None:
    """Mostra modello predefinito e requisiti."""
    config = TranscribeConfig()
    console.print(f"[bold]Sbobinator[/bold] v{__version__}\n")
    console.print(f"Modello predefinito: [cyan]{DEFAULT_MODEL}[/cyan]")
    console.print("Lingua: italiano (auto-rilevamento, incluso nel modello)")
    console.print(f"Device rilevato:    [cyan]{config.resolve_device()}[/cyan]")
    console.print(f"Cartella lavori:    [cyan]{jobs_root()}[/cyan]")
    console.print("\nIl modello è [bold]pre-addestrato[/bold]: nessun training necessario.")
    console.print("Primo avvio: download ~2.5 GB del checkpoint NeMo.\n")
    console.print("Uso:")
    console.print("  sbobina              # avvia interfaccia web (coda automatica)")
    console.print("  sbobina worker       # worker headless per Docker")
    console.print("  sbobina transcribe video.mp4 -s")
    console.print("  sbobina jobs list")


if __name__ == "__main__":
    app()
