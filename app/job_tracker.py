"""Async job tracking for long-running operations like ingestion."""
import time
import uuid
from enum import Enum
from typing import Dict, Optional
from threading import Lock

from .logging_utils import get_logger, log_event

logger = get_logger("job_tracker")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    def __init__(self, job_id: str, operation: str):
        self.job_id = job_id
        self.operation = operation
        self.status = JobStatus.PENDING
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.chunks_ingested: Optional[int] = None
        self.error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "chunks_ingested": self.chunks_ingested,
            "error": self.error,
        }


class JobTracker:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = Lock()

    def create_job(self, operation: str) -> Job:
        job_id = str(uuid.uuid4())
        with self._lock:
            job = Job(job_id, operation)
            self._jobs[job_id] = job
        log_event(logger, "job created", job_id=job_id, operation=operation)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                log_event(logger, "job updated", job_id=job_id, **kwargs)

    def mark_running(self, job_id: str) -> None:
        self.update_job(
            job_id,
            status=JobStatus.RUNNING,
            started_at=time.time()
        )

    def mark_completed(self, job_id: str, chunks_ingested: int) -> None:
        self.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            completed_at=time.time(),
            chunks_ingested=chunks_ingested
        )

    def mark_failed(self, job_id: str, error: str) -> None:
        self.update_job(
            job_id,
            status=JobStatus.FAILED,
            completed_at=time.time(),
            error=error
        )


# Global job tracker instance
job_tracker = JobTracker()