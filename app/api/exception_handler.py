from fastapi import Request
from fastapi.responses import JSONResponse


async def generic_exception_handler(
        request: Request,
        exception: Exception,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exception),
            "request_id": request_id,
            "code": 500
        }
    )
