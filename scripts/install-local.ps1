# Installazione locale Sbobinator (Windows, senza Docker)
# Uso: powershell -ExecutionPolicy Bypass -File scripts\install-local.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Sbobinator - installazione locale ===" -ForegroundColor Cyan

# ffmpeg
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "ATTENZIONE: ffmpeg non trovato nel PATH." -ForegroundColor Yellow
    Write-Host "Installalo con: winget install Gyan.FFmpeg" -ForegroundColor Yellow
    Write-Host "oppure: choco install ffmpeg" -ForegroundColor Yellow
    Write-Host ""
}

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERRORE: Python 3.12+ non trovato." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creazione virtualenv..."
    python -m venv .venv
}

Write-Host "Attivazione virtualenv..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Aggiornamento pip..."
python -m pip install --upgrade pip

Write-Host "Installazione PyTorch (CPU)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

Write-Host "Installazione Sbobinator con tutte le dipendenze..."
pip install -e ".[local]"

Write-Host ""
Write-Host "=== Installazione completata ===" -ForegroundColor Green
Write-Host ""
Write-Host "Avvia l'interfaccia web con:" -ForegroundColor Cyan
Write-Host "  start.bat" -ForegroundColor White
Write-Host "  oppure: sbobina ui" -ForegroundColor White
Write-Host ""
Write-Host "Primo avvio: download modelli (~2.5 GB ASR + ~300 MB riassunto)" -ForegroundColor Yellow
