# Uso locale su Windows

Guida per sviluppo e uso quotidiano **senza Docker**.

## Setup completo

```cmd
git clone https://github.com/sbobinator/sbobinator.git
cd sbobinator
python scripts\install_local.py
python scripts\download_model.py
python scripts\download_summary_model.py
```

## Avvio

```cmd
start.bat
```

`start.bat` usa:

1. `.venv\Scripts\python.exe` se esiste
2. Altrimenti `C:\Python313\python.exe`
3. Esegue `scripts\restart_ui.py` (una sola istanza Streamlit)

## Percorsi

| Cosa | Path |
|------|------|
| Input | `data\input\` |
| Output job | `data\output\jobs\` |
| Modelli | `models\` |
| Virtualenv | `.venv\` |

## Python globale vs venv

Consigliato: **venv** creato da `install_local.py`.  
Se usi Python globale, assicurati `pip install -e ".[local]"` sullo stesso interprete di `sbobina`.

## WSL

Sbobinator funziona anche in WSL2 Ubuntu con gli stessi comandi Linux. L'SSL HuggingFace in Linux è generalmente più affidabile, ma l'approccio **resta offline** con script curl/python di download.

## Manutenzione

| Operazione | Comando |
|------------|---------|
| Svuota output | `python scripts\clean_output.py` |
| Riavvio UI pulito | `python scripts\restart_ui.py` |
| Ritenta job falliti | `sbobina jobs retry` |
| Benchmark | `python scripts\benchmark_monitor.py` |

## Antivirus

Non usare script PowerShell `.ps1` — possono essere bloccati. Solo Python e `start.bat`.

Vedi [SSL Windows](../troubleshooting/ssl-windows.md) se i download falliscono.
