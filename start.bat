@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\sbobina.exe" (
    echo Avvio Sbobinator ^(virtualenv^)...
    ".venv\Scripts\python.exe" scripts\restart_ui.py
) else if exist "C:\Python313\python.exe" (
    echo Avvio Sbobinator ^(Python313^)...
    "C:\Python313\python.exe" scripts\restart_ui.py
) else (
    echo Ambiente non trovato. Esegui prima:
    echo   python scripts\install_local.py
    pause
    exit /b 1
)
pause
