# from app.db.supabase_client import supabase

# """


# recent 10 articles tab 
# """
# def get_dashboard_data():
#     pass

from fastapi import APIRouter
from app.db.dashboard import get_dashboard_summary, get_source_label_bias, get_top_sources
# router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

router=APIRouter()
@router.get("/summary")
def dashboard_summary():
    return get_dashboard_summary()

@router.get("/top-sources")
def top_sources():
    return get_top_sources()

@router.get("/source-label-bias")
def source_label_bias():
    return get_source_label_bias()