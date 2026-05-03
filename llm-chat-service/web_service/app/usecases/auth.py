from libs.schemas.user import UserPublic
from web_service.app.services.auth_client import AuthClient
from fastapi import Request


class AuthUsecase:
    @staticmethod
    async def auth_page(request: Request) -> UserPublic | None:
        if not getattr(request.state, "is_authenticated", False):
            return None
        access_token = request.state.access_token
        try:
            resp: UserPublic = await AuthClient.get_me(access_token)
        except Exception:
            return None
        return resp
