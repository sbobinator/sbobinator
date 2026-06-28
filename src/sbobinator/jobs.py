"""Registro lavori con coda SQLite — storico persistente, nessun overwrite."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Iterator

from sbobinator.config import DEFAULT_MODEL, data_dir

# Stati job
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"

ACTIVE_STATUSES = {STATUS_QUEUED, STATUS_RUNNING}


@dataclass
class JobRecord:
    id: str
    stem: str
    source_name: str
    created_at: str
    output_dir: str
    input_path: str = ""
    status: str = STATUS_QUEUED
    phase: str = "idle"
    progress_pct: float = 0.0
    progress_message: str = ""
    queued_at: str = ""
    started_at: str | None = None
    finished_at: str | None = None
    error: str = ""
    has_summary: bool = False
    summary_requested: bool = False
    summary_error: str = ""
    transcript_chars: int = 0
    model_name: str = DEFAULT_MODEL
    device: str | None = None
    summary_mode: str = "extractive"
    summary_length: str = "auto"

    @property
    def label(self) -> str:
        badge = _status_icon(self.status)
        return f"{badge} {self.source_name} ({self.id})"

    @property
    def path(self) -> Path:
        return Path(self.output_dir)

    def txt_path(self) -> Path:
        return self.path / "trascrizione.txt"

    def srt_path(self) -> Path:
        return self.path / "sottotitoli.srt"

    def summary_path(self) -> Path:
        return self.path / "riassunto.txt"

    def meta_path(self) -> Path:
        return self.path / "job.json"

    def source_copy_path(self) -> Path:
        if self.input_path:
            return Path(self.input_path)
        return self.path / f"source{Path(self.source_name).suffix}"


def _status_icon(status: str) -> str:
    return {
        STATUS_QUEUED: "⏳",
        STATUS_RUNNING: "▶️",
        STATUS_COMPLETED: "✅",
        STATUS_FAILED: "❌",
        STATUS_CANCELLED: "🚫",
    }.get(status, "•")


def jobs_root() -> Path:
    return data_dir() / "output" / "jobs"


def db_path() -> Path:
    return jobs_root() / "queue.db"


def index_path() -> Path:
    return jobs_root() / "index.json"


def _safe_dir_part(name: str, max_len: int = 60) -> str:
    """Nome cartella sicuro da stem file (senza estensione)."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name.strip())
    s = re.sub(r"_+", "_", s).strip("_.")
    return s[:max_len] or "file"


def new_job_id(stem: str) -> str:
    """ID leggibile: YYYYMMDD_HHMMSS_nome-file (con suffisso se collisione)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = _safe_dir_part(stem)
    base = f"{ts}_{safe}"
    if not (jobs_root() / base).exists():
        return base
    for n in range(2, 100):
        candidate = f"{ts}_{safe}_{n}"
        if not (jobs_root() / candidate).exists():
            return candidate
    return f"{ts}_{safe}_{datetime.now().strftime('%f')}"


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    jobs_root().mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            stem TEXT NOT NULL,
            source_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            output_dir TEXT NOT NULL,
            input_path TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'queued',
            phase TEXT DEFAULT 'idle',
            progress_pct REAL DEFAULT 0,
            progress_message TEXT DEFAULT '',
            queued_at TEXT DEFAULT '',
            started_at TEXT,
            finished_at TEXT,
            error TEXT DEFAULT '',
            has_summary INTEGER DEFAULT 0,
            summary_requested INTEGER DEFAULT 0,
            summary_error TEXT DEFAULT '',
            transcript_chars INTEGER DEFAULT 0,
            model_name TEXT DEFAULT '',
            device TEXT,
            summary_mode TEXT DEFAULT 'extractive',
            summary_length TEXT DEFAULT 'auto'
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC)")


def _row_to_job(row: sqlite3.Row) -> JobRecord:
    data = dict(row)
    data["has_summary"] = bool(data.get("has_summary"))
    data["summary_requested"] = bool(data.get("summary_requested"))
    if not data.get("model_name"):
        data["model_name"] = DEFAULT_MODEL
    return JobRecord(**data)


def _sync_job_json(job: JobRecord) -> None:
    job.path.mkdir(parents=True, exist_ok=True)
    job.meta_path().write_text(json.dumps(asdict(job), ensure_ascii=False, indent=2), encoding="utf-8")


def _upsert_job(conn: sqlite3.Connection, job: JobRecord) -> None:
    d = asdict(job)
    d["has_summary"] = int(job.has_summary)
    d["summary_requested"] = int(job.summary_requested)
    cols = list(d.keys())
    placeholders = ", ".join("?" * len(cols))
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != "id")
    conn.execute(
        f"INSERT INTO jobs ({', '.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT(id) DO UPDATE SET {updates}",
        [d[c] for c in cols],
    )
    _sync_job_json(job)


def _migrate_index_json(conn: sqlite3.Connection) -> None:
    path = index_path()
    if not path.exists():
        return
    try:
        items = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    known = {f.name for f in fields(JobRecord)}
    for item in items:
        job_id = item.get("id")
        if not job_id:
            continue
        existing = conn.execute("SELECT id FROM jobs WHERE id=?", (job_id,)).fetchone()
        if existing:
            continue
        item.setdefault("status", STATUS_COMPLETED)
        item.setdefault("queued_at", item.get("created_at", ""))
        item.setdefault("input_path", "")
        item.setdefault("model_name", DEFAULT_MODEL)
        item.setdefault("summary_mode", "extractive")
        item.setdefault("summary_length", "auto")
        filtered = {k: v for k, v in item.items() if k in known}
        job = JobRecord(**filtered)
        _upsert_job(conn, job)
    backup = path.with_suffix(".json.bak")
    if not backup.exists():
        shutil.copy2(path, backup)


_db_ready = False


def ensure_db() -> None:
    """Inizializza schema SQLite (idempotente). Ripara DB ricreato a vuoto."""
    global _db_ready
    with _connect() as conn:
        _init_schema(conn)
        if not _db_ready:
            _migrate_index_json(conn)
            _db_ready = True


def load_index(
    *,
    status: str | None = None,
    statuses: set[str] | None = None,
    limit: int | None = None,
) -> list[JobRecord]:
    ensure_db()
    query = "SELECT * FROM jobs"
    params: list = []
    clauses: list[str] = []
    if status:
        clauses.append("status=?")
        params.append(status)
    if statuses:
        placeholders = ", ".join("?" * len(statuses))
        clauses.append(f"status IN ({placeholders})")
        params.extend(sorted(statuses))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_job(r) for r in rows]


def get_job(job_id: str) -> JobRecord | None:
    ensure_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return _row_to_job(row) if row else None


def update_job(job: JobRecord) -> None:
    ensure_db()
    with _connect() as conn:
        _upsert_job(conn, job)


def update_job_progress(
    job_id: str,
    *,
    phase: str | None = None,
    progress_pct: float | None = None,
    progress_message: str | None = None,
    status: str | None = None,
) -> None:
    job = get_job(job_id)
    if not job:
        return
    if phase is not None:
        job.phase = phase
    if progress_pct is not None:
        job.progress_pct = progress_pct
    if progress_message is not None:
        job.progress_message = progress_message
    if status is not None:
        job.status = status
    update_job(job)


def enqueue_job(
    source_path: Path,
    source_name: str,
    stem: str,
    *,
    summary_requested: bool = False,
    model_name: str = DEFAULT_MODEL,
    device: str | None = None,
    summary_mode: str = "extractive",
    summary_length: str = "auto",
) -> JobRecord:
    """Accoda un lavoro: copia il file sorgente nella cartella job."""
    ensure_db()
    now = datetime.now().isoformat(timespec="seconds")
    job_id = new_job_id(stem)
    out = jobs_root() / job_id
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"source{Path(source_name).suffix}"
    shutil.copy2(source_path, dest)

    job = JobRecord(
        id=job_id,
        stem=stem,
        source_name=source_name,
        created_at=now,
        output_dir=str(out.resolve()),
        input_path=str(dest.resolve()),
        status=STATUS_QUEUED,
        phase="queued",
        progress_pct=0.0,
        progress_message="In coda, in attesa di elaborazione...",
        queued_at=now,
        summary_requested=summary_requested,
        model_name=model_name,
        device=device,
        summary_mode=summary_mode,
        summary_length=summary_length,
    )
    with _connect() as conn:
        _upsert_job(conn, job)
    return job


def claim_next_job() -> JobRecord | None:
    """Prende il prossimo job in coda (atomico) e lo marca running."""
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM jobs WHERE status=? ORDER BY queued_at ASC LIMIT 1",
            (STATUS_QUEUED,),
        ).fetchone()
        if not row:
            return None
        job_id = row["id"]
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """
            UPDATE jobs SET status=?, phase=?, started_at=?, progress_pct=?, progress_message=?
            WHERE id=? AND status=?
            """,
            (STATUS_RUNNING, "starting", now, 1.0, "Avvio elaborazione...", job_id, STATUS_QUEUED),
        )
        if conn.total_changes == 0:
            return None
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    job = _row_to_job(row)
    _sync_job_json(job)
    return job


def requeue_job(job_id: str) -> bool:
    """Rimette in coda un job fallito o annullato (stessi file già su disco)."""
    ensure_db()
    job = get_job(job_id)
    if not job or job.status not in (STATUS_FAILED, STATUS_CANCELLED):
        return False
    job.status = STATUS_QUEUED
    job.phase = "queued"
    job.progress_pct = 0.0
    job.progress_message = "In coda, in attesa di elaborazione..."
    job.started_at = None
    job.finished_at = None
    job.error = ""
    update_job(job)
    return True


def requeue_failed() -> list[str]:
    """Rimette in coda tutti i job falliti o annullati."""
    requeued: list[str] = []
    for job in load_index(statuses={STATUS_FAILED, STATUS_CANCELLED}):
        if requeue_job(job.id):
            requeued.append(job.id)
    return requeued


def recover_orphaned_running_jobs() -> list[str]:
    """Rimette in coda job lasciati in 'running' senza worker (crash o riavvio)."""
    ensure_db()
    recovered: list[str] = []
    for job in load_index(status=STATUS_RUNNING):
        job.status = STATUS_QUEUED
        job.phase = "queued"
        job.progress_pct = 0.0
        job.progress_message = "In coda, in attesa di elaborazione..."
        job.started_at = None
        job.finished_at = None
        job.error = ""
        update_job(job)
        recovered.append(job.id)
    return recovered


def cancel_job(job_id: str) -> bool:
    """Annulla un job solo se ancora in coda."""
    ensure_db()
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status=?, phase=?, progress_message=?, finished_at=? "
            "WHERE id=? AND status=?",
            (
                STATUS_CANCELLED,
                "cancelled",
                "Annullato dall'utente",
                datetime.now().isoformat(timespec="seconds"),
                job_id,
                STATUS_QUEUED,
            ),
        )
        ok = conn.total_changes > 0
    if ok:
        job = get_job(job_id)
        if job:
            _sync_job_json(job)
    return ok


def count_active_jobs() -> int:
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM jobs WHERE status IN (?, ?)",
            (STATUS_QUEUED, STATUS_RUNNING),
        ).fetchone()
    return int(row["n"]) if row else 0


def load_active_queue() -> list[JobRecord]:
    """Job in coda o in elaborazione, ordinati: running prima, poi FIFO per queued_at."""
    ensure_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM jobs
            WHERE status IN (?, ?)
            ORDER BY
              CASE status WHEN ? THEN 0 ELSE 1 END,
              queued_at ASC
            """,
            (STATUS_QUEUED, STATUS_RUNNING, STATUS_RUNNING),
        ).fetchall()
    return [_row_to_job(r) for r in rows]


def is_source_in_active_queue(source_name: str) -> bool:
    """True se un file con lo stesso nome è già in coda o in elaborazione."""
    return any(j.source_name == source_name for j in load_active_queue())
