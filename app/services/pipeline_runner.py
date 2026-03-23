from starlette.concurrency import run_in_threadpool

from app.schemas.schema import (
    ScrapeRequest,
    article,
    coref_request,
    Coref_Article,
    Inference_Response,
)
from app.services.job_store import update_job
from app.utils.http_client import build_url, post_json


SCRAPE_API = build_url("SCRAPE_API", "api/v1/scrape")
PREPROCESS_API = build_url("PREPROCESS_API", "api/v1/preprocess")
COREF_API = build_url("COREF_API", "api/v1/coref")
BIAS_API = build_url("BIAS_API", "api/v1/bias/inference")


async def run_pipeline_job(job_id: str, data: ScrapeRequest) -> None:
    try:
        update_job(job_id, status="running", step="scraping")

        scraped_json = await run_in_threadpool(
            post_json,
            SCRAPE_API,
            {"url": str(data.url)}
        )
        scraped_article = article(**scraped_json)
        scraped_article.pipeline_status = ["scraped"]

        update_job(job_id, status="running", step="preprocessing")

        preprocessed_json = await run_in_threadpool(
            post_json,
            PREPROCESS_API,
            scraped_article.model_dump()
        )
        preprocessed = article(**preprocessed_json)
        preprocessed.pipeline_status = scraped_article.pipeline_status + ["preprocessed"]

        update_job(job_id, status="running", step="coreference")

        coref_payload = coref_request(
            content=preprocessed.content,
            url=str(preprocessed.url)
        )

        coref_json = await run_in_threadpool(
            post_json,
            COREF_API,
            coref_payload.model_dump()
        )
        coref_result = Coref_Article(**coref_json)

        preprocessed.content = coref_result.content
        if preprocessed.pipeline_status is None:
            preprocessed.pipeline_status = []
        preprocessed.pipeline_status.append("coref_resolved")

        update_job(job_id, status="running", step="bias_inference")

        bias_payload = {
            "ner_list": [i.model_dump() for i in (coref_result.ner_list or [])]
        }

        bias_json = await run_in_threadpool(
            post_json,
            BIAS_API,
            bias_payload
        )
        bias_score_result = Inference_Response(**bias_json)

        update_job(
            job_id,
            status="completed",
            step="done",
            result=bias_score_result.model_dump(),
            error=None,
        )

    except Exception as e:
        update_job(
            job_id,
            status="failed",
            step="error",
            error=str(e),
        )
