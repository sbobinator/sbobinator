import logging
import shutil
import tempfile
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

from sbobinator import __version__
from sbobinator.config import DEFAULT_MODEL, SummaryLength, SummaryMode, TranscribeConfig
from sbobinator.export import export_all, export_summary_text
from sbobinator.summarize import summarize
from sbobinator.transcribe import transcribe as run_transcribe
from sbobinator.transcribe import unload_model
from sbobinator.ui.launch import launch_ui

app = typer.Typer(
    name="sbobina",
    help="Sbobina audio e video in testo (italiano) con NVIDIA NeMo Parakeet.",
)
console = Console()


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
    """Avvia l'interfaccia web Streamlit."""
    console.print(f"[bold cyan]Interfaccia web su http://localhost:{port}[/bold cyan]")
    launch_ui(port=port)


@app.command()
def transcribe(
    input_path: Path = typer.Argument(..., help="File audio o video da trascrivere", exists=True),
    output_dir: Path = typer.Option(
        Path("data/output"),
        "--output",
        "-o",
        help="Cartella di output",
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
        help="Formati di export (ripetibile)",
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
        help="extractive=veloce, abstractive=mT5",
    ),
    summary_length: SummaryLength = typer.Option(
        SummaryLength.auto,
        "--summary-length",
        help="auto, short, normal, detailed",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Trascrive un file audio o video in testo."""
    _setup_logging(verbose)

    config = TranscribeConfig(model_name=model, device=device)
    fmt_names = [f.value for f in formats]

    console.print(f"[bold]Input:[/bold]  {input_path}")
    console.print(f"[bold]Modello:[/bold] {model}")
    console.print(f"[bold]Device:[/bold]  {config.resolve_device()}")
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

        preview = result.text[:300] + ("..." if len(result.text) > 300 else "")
        console.print(f"\n[dim]Anteprima:[/dim]\n{preview}")

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@app.command()
def info() -> None:
    """Mostra modello predefinito e requisiti."""
    config = TranscribeConfig()
    console.print(f"[bold]Sbobinator[/bold] v{__version__}\n")
    console.print(f"Modello predefinito: [cyan]{DEFAULT_MODEL}[/cyan]")
    console.print("Lingua: italiano (auto-rilevamento, incluso nel modello)")
    console.print(f"Device rilevato:    [cyan]{config.resolve_device()}[/cyan]")
    console.print("\nIl modello è [bold]pre-addestrato[/bold]: nessun training necessario.")
    console.print("Primo avvio: download ~2.5 GB del checkpoint NeMo.\n")
    console.print("Uso:")
    console.print("  sbobina              # avvia interfaccia web")
    console.print("  sbobina ui           # idem")
    console.print("  sbobina transcribe video.mp4 -o data/output -s")


if __name__ == "__main__":
    app()
