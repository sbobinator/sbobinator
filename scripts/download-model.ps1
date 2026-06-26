# Scarica il modello Parakeet evitando il bug SSL di Python su Windows
# Uso: powershell -ExecutionPolicy Bypass -File scripts\download-model.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$modelsDir = Join-Path (Get-Location) "models"
$outFile = Join-Path $modelsDir "parakeet-tdt-0.6b-v3.nemo"
$url = "https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/resolve/main/parakeet-tdt-0.6b-v3.nemo"

New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null

$MIN_COMPLETE_MB = 2200

if (Test-Path $outFile) {
    $size = (Get-Item $outFile).Length / 1MB
    if ($size -gt $MIN_COMPLETE_MB) {
        Write-Host "Modello già presente: $outFile ($([math]::Round($size)) MB)" -ForegroundColor Green
        exit 0
    }
    if ($size -gt 50) {
        Write-Host "Ripresa download da $([math]::Round($size)) MB..." -ForegroundColor Yellow
    } else {
        Remove-Item $outFile -Force
    }
}

Write-Host "Download modello Parakeet (~2.5 GB)..." -ForegroundColor Cyan
Write-Host "Destinazione: $outFile"
Write-Host "Può richiedere 10-30 minuti in base alla connessione."
Write-Host ""

# curl.exe usa i certificati Windows; -C - riprende download interrotti
curl.exe --ssl-no-revoke -L -C - --progress-bar -o $outFile $url

if (-not (Test-Path $outFile)) {
    Write-Host "ERRORE: download fallito." -ForegroundColor Red
    exit 1
}

$finalSize = (Get-Item $outFile).Length / 1MB
if ($finalSize -lt $MIN_COMPLETE_MB) {
    Write-Host "ERRORE: file incompleto ($([math]::Round($finalSize)) MB). Rilancia lo script." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Download completato: $([math]::Round($finalSize)) MB" -ForegroundColor Green
Write-Host "Ora riavvia Sbobinator e clicca Sbobina."
