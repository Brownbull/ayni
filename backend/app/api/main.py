from fastapi import APIRouter

from app.api.routes import health, items, login, private, users, utils
from app.api.v1.endpoints import monitoring, tasks
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(tasks.router, prefix="/tasks")
api_router.include_router(monitoring.router, prefix="/monitoring")


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
