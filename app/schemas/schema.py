from pydantic import BaseModel
from typing import List, Optional


class ScrapeRequest(BaseModel):
    url: str


class article(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    url: str
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    source: Optional[str] = None
    pipeline_status: Optional[List[str]] = None


class coref_request(BaseModel):
    content: Optional[str] = None
    url: str


class item(BaseModel):
    sent: Optional[str] = None
    label: Optional[str] = None


class ItemScored(BaseModel):
    sent: Optional[str] = None
    label: Optional[str] = None
    score: Optional[float] = None


class Coref_Article(BaseModel):
    content: Optional[str] = None
    url: str
    chains: Optional[list] = None
    ner_list: Optional[List[item]] = None


class Inference_Response(BaseModel):
    aggregate_score: Optional[float] = None
    aggregate_label: Optional[str] = None
    scored_list: Optional[List[ItemScored]] = None
    median_score: Optional[float] = None
    mode_value: Optional[str] = None


class PipelineJobCreateResponse(BaseModel):
    job_id: str
    status: str


class PipelineJobStatusResponse(BaseModel):
    job_id: str
    status: str
    step: Optional[str] = None
    result: Optional[Inference_Response] = None
    error: Optional[str] = None