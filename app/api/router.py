from fastapi import APIRouter
from app.api import health, pipeline,dashboard

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(pipeline.router, tags=["pipeline"])
api_router.include_router(dashboard.router, tags=["dashboard"])
