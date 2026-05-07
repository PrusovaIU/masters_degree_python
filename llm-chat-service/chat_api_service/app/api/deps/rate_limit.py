from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from chat_api_service.app.core.config import settings
from chat_api_service.app.infra.redis import RedisClient


async def rate_limit_dependency(
        request: Request
) -> bool:
    """
    Dependency для проверки rate limiting через Redis.

    :param request: FastAPI request.
    :return: True если запрос разрешён.

    :raises HTTPException: Если лимит превышен.
    """
    user_id: str = request.client.host

    if not await RedisClient.check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Rate limit exceeded",
                "limit": settings.redis.rate_limit.llm_limit,
                "window_seconds": settings.redis.rate_limit.llm_window
            }
        )
    return True


RateLimitDep = Annotated[bool, Depends(rate_limit_dependency)]
