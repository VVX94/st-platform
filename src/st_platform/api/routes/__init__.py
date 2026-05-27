"""API route registration."""

from fastapi import APIRouter

from .algorithms import router as algorithms_router
from .datasets import router as datasets_router
from .experiments import router as experiments_router
from .health import router as health_router
from .runs import router as runs_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(algorithms_router)
api_router.include_router(datasets_router)
api_router.include_router(experiments_router)
api_router.include_router(runs_router)
