from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
import requests
import os

from app.schemas.schema import (
    ScrapeRequest,
    article,
    coref_request,
    Coref_Article
)


router = APIRouter()

import os

def build_url(env_key: str, path: str) -> str:
    base = os.environ.get(env_key)
    if not base:
        raise RuntimeError(f"Missing environment variable: {env_key}")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"

SCRAPE_API = build_url("SCRAPE_API", "api/v1/scrape")
PREPROCESS_API = build_url("PREPROCESS_API", "api/v1/preprocess")
COREF_API = build_url("COREF_API", "api/v1/coref")


# SCRAPE_API= 'http://localhost:8020/api/v1/scrape'
# PREPROCESS_API = 'http://localhost:8000/api/v1/preprocess'
# COREF_API = 'http://localhost:8010/api/v1/coref'


def post_json(url: str, payload: dict):
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


@router.post("/pipeline", response_model=article)
async def pipeline(data: ScrapeRequest):

    if not all([SCRAPE_API, PREPROCESS_API, COREF_API]):
        raise HTTPException(status_code=500, detail="API endpoints not configured")

    # 1️⃣ Scrape
    scraped_json = await run_in_threadpool(
        post_json,
        SCRAPE_API,
        {"url": str(data.url)}
    )
    scraped_article = article(**scraped_json)
    scraped_article.pipeline_status = ["scraped"]

    # 2️⃣ Preprocess
    preprocessed_json = await run_in_threadpool(
        post_json,
        PREPROCESS_API,
        scraped_article.model_dump()
    )
    preprocessed = article(**preprocessed_json)
    preprocessed.pipeline_status = scraped_article.pipeline_status + ["preprocessed"]

    # 3️⃣ Coreference
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


    # Replace content with coref output
    preprocessed.content = coref_result.content
    preprocessed.pipeline_status.append("coref_resolved")   
    preprocessed.ner_list = coref_result.ner_list

    return preprocessed
