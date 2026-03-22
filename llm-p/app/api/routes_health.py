from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health_check import HealthCheck

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get(
    "/",
    summary="Health check",
    description="Проверка работоспособности сервера",
    response_model=HealthCheck
)
async def health_check():
    """
    Проверка работоспособности сервера.
    """
    return HealthCheck(
        status="OK",
        environment=settings.env
    )
