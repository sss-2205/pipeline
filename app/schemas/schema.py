from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

class item(BaseModel):
    sent: str | None = None
    label: str | None = None

class article(BaseModel):

    title: str | None = None
    content: str | None = None
    url: str
    error_code: int | None = None
    error_message: str | None = None
    source: str | None = None
    pipeline_status: str | None = None
    ner_list: list[item] | None = None # this will hold the ner list in string format. change this according to orchestration method

class coref_request(BaseModel): # the schema for the input request for coreference api. change this according to orchestration method

    content: str | None = None
    url: str
    

class Coref_Article(BaseModel): # the schema for the input request for preprocessing api. change this according to orchestration method

    content: str | None = None
    url: str
    chains: list | None = None 
    ner_list: list[item] | None = None # this will hold the ner list in string format. change this according to orchestration method
