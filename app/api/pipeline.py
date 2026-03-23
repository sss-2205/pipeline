import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.schema import (
    ScrapeRequest,
    PipelineJobCreateResponse,
    PipelineJobStatusResponse,
)
from app.services.job_store import create_job, get_job
from app.services.pipeline_runner import run_pipeline_job
from app.utils.http_client import build_url


router = APIRouter()


@router.post("/pipeline", response_model=PipelineJobCreateResponse)
async def create_pipeline_job(
    data: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    # Validate that required env vars exist
    try:
        build_url("SCRAPE_API", "api/v1/scrape")
        build_url("PREPROCESS_API", "api/v1/preprocess")
        build_url("COREF_API", "api/v1/coref")
        build_url("BIAS_API", "api/v1/bias/inference")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    job_id = str(uuid.uuid4())
    create_job(job_id)

    background_tasks.add_task(run_pipeline_job, job_id, data)

    return PipelineJobCreateResponse(
        job_id=job_id,
        status="queued"
    )


@router.get("/pipeline/{job_id}", response_model=PipelineJobStatusResponse)
async def get_pipeline_status(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return PipelineJobStatusResponse(**job)