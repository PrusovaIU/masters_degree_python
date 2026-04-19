from fastapi import APIRouter

from chat_api_service.app.core.config import settings
from chat_api_service.app.schemas.health_check import HealthCheck

router_health = APIRouter(tags=["health"])


@router_health.get(
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
