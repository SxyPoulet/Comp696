"""
Main API v1 router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import companies, discovery, profiles, intelligence, content, tasks

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["companies"]
)

api_router.include_router(
    discovery.router,
    prefix="/discover",
    tags=["discovery"]
)

api_router.include_router(
    profiles.router,
    prefix="/profiles",
    tags=["profiles"]
)

api_router.include_router(
    intelligence.router,
    prefix="/intelligence",
    tags=["intelligence"]
)

api_router.include_router(
    content.router,
    prefix="/content",
    tags=["content"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)
