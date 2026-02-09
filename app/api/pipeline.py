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

SCRAPE_API= os.getenv("SCRAPE_API")
PREPROCESS_API = os.getenv("PREPROCESS_API")
COREF_API = os.getenv("COREF_API")

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

    # 2️⃣ Preprocess
    preprocessed_json = await run_in_threadpool(
        post_json,
        PREPROCESS_API,
        scraped_article.model_dump()
    )
    preprocessed = article(**preprocessed_json)

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

    return preprocessed