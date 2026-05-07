from fastapi import status
from fastapi.responses import RedirectResponse

LOGIN_REDIRECT = RedirectResponse(
    url="/auth/login",
    status_code=status.HTTP_302_FOUND
)
