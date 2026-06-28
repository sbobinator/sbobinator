"""Garantisce una sola istanza UI/worker e verifica che il pacchetto sia aggiornato."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from sbobinator.config import project_root

UI_APP_MARKERS = (
    "sbobinator.ui.server",
    "sbobinator\\ui\\server.py",
    "sbobinator/ui/server.py",
)
WORKER_MARKERS = (
    "sbobinator.cli worker",
    "-m sbobinator.cli worker",
)


def pids_on_port(port: int) -> set[int]:
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(["netstat", "-ano"], text=True, errors="replace")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return set()
        pids: set[int] = set()
        for line in out.splitlines():
            if f":{port}" not in line or "LISTENING" not in line:
                continue
            parts = line.split()
            if parts and parts[-1].isdigit():
                pids.add(int(parts[-1]))
        return pids

    try:
        out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    return {int(x) for x in out.split() if x.strip().isdigit()}


def _python_processes() -> list[tuple[int, str]]:
    if sys.platform != "win32":
        try:
            out = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        rows: list[tuple[int, str]] = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit():
                rows.append((int(parts[0]), parts[1]))
        return rows

    try:
        out = subprocess.check_output(
            [
                "wmic",
                "process",
                "where",
                "name='python.exe' or name='pythonw.exe'",
                "get",
                "ProcessId,CommandLine",
                "/format:csv",
            ],
            text=True,
            errors="replace",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    rows: list[tuple[int, str]] = []
    for line in out.splitlines():
        if not line.strip() or line.startswith("Node,"):
            continue
        parts = line.split(",", 2)
        if len(parts) < 3:
            continue
        pid_s = parts[1].strip()
        cmd = parts[2].strip()
        if pid_s.isdigit():
            rows.append((int(pid_s), cmd))
    return rows


def _matches_markers(cmd: str, markers: tuple[str, ...]) -> bool:
    norm = cmd.lower().replace("/", "\\")
    return any(marker.lower() in norm for marker in markers)


def find_ui_pids(port: int = 8501) -> set[int]:
    pids = pids_on_port(port)
    for pid, cmd in _python_processes():
        if _matches_markers(cmd, UI_APP_MARKERS) or (
            "uvicorn" in cmd.lower() and "sbobinator.ui.server" in cmd.lower()
        ):
            pids.add(pid)
    return pids


def find_worker_pids() -> set[int]:
    pids: set[int] = set()
    for pid, cmd in _python_processes():
        if _matches_markers(cmd, WORKER_MARKERS):
            pids.add(pid)
    return pids


def kill_pids(pids: set[int]) -> int:
    killed = 0
    for pid in sorted(pids):
        if pid == 0:
            continue
        if sys.platform == "win32":
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                killed += 1
        else:
            try:
                import os
                import signal

                os.kill(pid, signal.SIGTERM)
                killed += 1
            except OSError:
                pass
    return killed


def clear_package_cache() -> None:
    root = project_root() / "src" / "sbobinator"
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def clear_worker_pid_file() -> None:
    from sbobinator.jobs import jobs_root

    worker_pid = jobs_root() / "worker.pid"
    worker_pid.unlink(missing_ok=True)


def ensure_clean_ui_environment(port: int = 8501, *, wait_sec: float = 2.0) -> int:
    """Termina UI/worker Sbobinator già attivi. Ritorna quanti processi sono stati killati."""
    pids = find_ui_pids(port) | find_worker_pids()
    if not pids:
        return 0
    killed = kill_pids(pids)
    clear_worker_pid_file()
    if wait_sec > 0:
        time.sleep(wait_sec)
    return killed


def verify_runtime() -> None:
    """Verifica che l'installazione editable esponga le API attuali."""
    import sbobinator.config as config_mod

    config_file = Path(config_mod.__file__).resolve()
    expected = (project_root() / "src" / "sbobinator" / "config.py").resolve()
    if config_file != expected:
        raise RuntimeError(
            f"Pacchetto sbobinator non aggiornato.\n"
            f"  Caricato da: {config_file}\n"
            f"  Atteso:       {expected}\n"
            f"Esegui: {sys.executable} -m pip install -e \".[local]\""
        )

    missing = [name for name in ("data_dir", "project_root", "models_dir") if not hasattr(config_mod, name)]
    if missing:
        raise RuntimeError(
            f"Modulo config incompleto (mancano: {', '.join(missing)}). "
            f"Riavvia con: python scripts\\restart_ui.py"
        )

    from sbobinator.config import data_dir  # noqa: F401
