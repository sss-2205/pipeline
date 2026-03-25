from typing import Any, Dict

jobs: Dict[str, Dict[str, Any]] = {}


def create_job(job_id: str, status: str | None = None, **kwargs) -> None:
    jobs[job_id] = {
        "job_id": job_id,
        "status": status or "queued",
        "step": "waiting",
        "result": None,
        "error": None,
    }

    # ✅ override defaults if provided
    jobs[job_id].update(kwargs)


def update_job(job_id: str, **kwargs) -> None:
    if job_id in jobs:
        jobs[job_id].update(kwargs)


def get_job(job_id: str):
    return jobs.get(job_id)