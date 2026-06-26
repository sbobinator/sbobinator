"""Registro lavori di trascrizione — nessun overwrite, storico persistente."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from sbobinator.config import project_root


@dataclass
class JobRecord:
    id: str
    stem: str
    source_name: str
    created_at: str
    output_dir: str
    has_summary: bool = False
    summary_requested: bool = False
    summary_error: str = ""
    transcript_chars: int = 0

    @property
    def label(self) -> str:
        ts = self.created_at.replace("T", " ")[:16]
        return f"{self.source_name} — {ts}"

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


def jobs_root() -> Path:
    return project_root() / "data" / "output" / "jobs"


def index_path() -> Path:
    return jobs_root() / "index.json"


def new_job_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_index() -> list[JobRecord]:
    path = index_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [JobRecord(**item) for item in data]


def save_index(jobs: list[JobRecord]) -> None:
    jobs_root().mkdir(parents=True, exist_ok=True)
    index_path().write_text(
        json.dumps([asdict(j) for j in jobs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def register_job(
    source_name: str,
    stem: str,
    *,
    summary_requested: bool = False,
) -> JobRecord:
    job_id = new_job_id()
    out = jobs_root() / job_id
    out.mkdir(parents=True, exist_ok=True)
    job = JobRecord(
        id=job_id,
        stem=stem,
        source_name=source_name,
        created_at=datetime.now().isoformat(timespec="seconds"),
        output_dir=str(out),
        summary_requested=summary_requested,
    )
    job.meta_path().write_text(json.dumps(asdict(job), ensure_ascii=False, indent=2), encoding="utf-8")
    jobs = load_index()
    jobs.insert(0, job)
    save_index(jobs)
    return job


def update_job(job: JobRecord) -> None:
    job.meta_path().write_text(json.dumps(asdict(job), ensure_ascii=False, indent=2), encoding="utf-8")
    jobs = load_index()
    jobs = [job if j.id == job.id else j for j in jobs]
    save_index(jobs)


def get_job(job_id: str) -> JobRecord | None:
    for job in load_index():
        if job.id == job_id:
            return job
    return None
