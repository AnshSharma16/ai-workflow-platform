from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import DuplicateEmailError


async def duplicate_email_handler(
    request: Request,
    exc: DuplicateEmailError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )