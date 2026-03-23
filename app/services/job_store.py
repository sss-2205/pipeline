from typing import Any, Dict

jobs: Dict[str, Dict[str, Any]] = {}


def create_job(job_id: str) -> None:
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "step": "waiting",
        "result": None,
        "error": None,
    }


def update_job(job_id: str, **kwargs) -> None:
    if job_id in jobs:
        jobs[job_id].update(kwargs)


def get_job(job_id: str):
    return jobs.get(job_id)