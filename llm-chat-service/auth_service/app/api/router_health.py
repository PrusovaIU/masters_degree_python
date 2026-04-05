from fastapi import APIRouter

from auth_service.app.core.config import settings
from auth_service.app.schemas.health_check import HealthCheck

health_router = APIRouter(tags=["health"])


@health_router.get(
    "/health",
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
