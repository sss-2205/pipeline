from pydantic import BaseModel, HttpUrl

class ScrapeRequest(BaseModel):
    url: str

class article(BaseModel):

    title: str | None = None
    content: str | None = None
    url: str
    error_code: int | None = None
    error_message: str | None = None
    source: str | None = None
    pipeline_status: str | None = None

class coref_request(BaseModel): # the schema for the input request for coreference api. change this according to orchestration method

    content: str | None = None
    url: str
    

class Coref_Article(BaseModel): # the schema for the input request for preprocessing api. change this according to orchestration method

    content: str | None = None
    url: str
    chains: list | None = None 