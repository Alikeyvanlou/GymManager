from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error": [{"message": exc.detail, "path": request.url.path}]
        },
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": err["loc"][-1], "message": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"success": False, "status_code": 422, "error": errors},
    )