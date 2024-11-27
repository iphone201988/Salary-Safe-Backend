from fastapi import APIRouter

from app.api.routes import (
    candidates, clients, jobs, utils
)

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
