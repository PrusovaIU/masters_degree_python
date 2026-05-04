from fastapi.responses import RedirectResponse
from fastapi import status

LOGIN_REDIRECT = RedirectResponse(
    url="/auth/login",
    status_code=status.HTTP_302_FOUND
)