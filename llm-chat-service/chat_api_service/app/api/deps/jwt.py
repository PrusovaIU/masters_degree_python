from typing import Annotated

from fastapi import Depends
from chat_api_service.app.core.config import settings
from libs.jwt_token.token_data import TokenUserData


UserDataDep = Annotated[TokenUserData, Depends(settings.jwt.bearer)]
