import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.schema import (
    ScrapeRequest,
    PipelineJobCreateResponse,
    PipelineJobStatusResponse,
)
from app.services.job_store import create_job, get_job, update_job
from app.services.pipeline_runner import run_pipeline_job
from app.utils.http_client import build_url
from app.db.lookup import get_cached_article


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
        raise HTTPException(status_code=5005, detail=str(e))
    
    cached_status, cached = get_cached_article(str(data.url))
    job_id = str(uuid.uuid4())
    
    # Fully cached → return completed immediately
    if cached_status and isinstance(cached, dict):
        cached_data={
        "aggregate_score": cached.get('bias_score'),
        "aggregate_label": cached.get('label'),
        "median_score": cached.get('median_score'),
        "mode_value": cached.get('mode_score')
    }
        create_job(
            job_id,
            status="completed",
            step="done",
            result=cached_data,
            error=None
        )
        return PipelineJobCreateResponse(
            job_id=job_id,
            status="completed"
        )

    # Partially cached or not cached → queue pipeline
    create_job(job_id)

    # Pass article_id if partial cached, else None
    background_tasks.add_task(
        run_pipeline_job,
        job_id,
        data,
        article_id = cached.get('article_id') if (not cached_status and cached) else None
        
        )

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