from pydantic import BaseModel, Field
from typing import List, Dict, Optional


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
    target: Optional[str] = None
    label: Optional[str] = None
    score: Optional[float] = None

class AlternativeSource(BaseModel):
    source: str
    title: str
    url: str
    why_suggested: str

class Coref_Article(BaseModel):
    content: Optional[str] = None
    url: str
    chains: Optional[list] = None
    ner_list: Optional[List[item]] = None


class Inference_Response(BaseModel):
    bjp_axis: Optional[float] = None
    congress_axis: Optional[float] = None
    scored_list: Optional[List[ItemScored]] = None
    median_score: Optional[float] = None
    mode_value: Optional[str] = None

class ExplainRequest(BaseModel):
    bjp_axis: float
    congress_axis: float
    scored_list: List[ItemScored]
    # article_summary: Optional[str] = None


class ExplainResponse(BaseModel):
    bias_explanation: str
    overall_interpretation: str
    axis_analysis: Dict[str, str]
    evidence: List[str]
    confidence_note: str
    alternative_sources: Optional[List[AlternativeSource]] = Field(default_factory=list)

class PipelineJobCreateResponse(BaseModel):
    job_id: str
    status: str

class FinalResult(BaseModel):
    bias: Inference_Response
    explainability: ExplainResponse

class PipelineJobStatusResponse(BaseModel):
    job_id: str
    status: str
    step: Optional[str] = None
    result: Optional[FinalResult] = None
    error: Optional[str] = None