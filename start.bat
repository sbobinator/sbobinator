@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente non trovato. Esegui prima: scripts\install-local.ps1
    pause
    exit /b 1
)

echo Avvio Sbobinator...
".venv\Scripts\sbobina.exe" ui
pause
