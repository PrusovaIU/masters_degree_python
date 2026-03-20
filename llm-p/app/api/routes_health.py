from app.core.config import settings
from fastapi import APIRouter


health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
async def health_check():
    """
    Проверка работоспособности сервера.
    """
    return {
        "status": "healthy",
        "environment": settings.environment
    }
