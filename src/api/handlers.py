import traceback

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.schemes.response import (
    Response400Scheme,
    Response401Scheme,
    Response403Scheme,
    Response404Scheme,
    Response422Scheme,
    Response500Scheme
)

from starlette.exceptions import HTTPException as StarletteHTTPException


async def internal_exception_handler(
    request: Request,
    exc: Exception
):
    try:
        raise exc
    except Exception:
        tb = traceback.format_exc()
        tb_lines = tb.split('\n')
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder({
            "code": 500,
            "msg": "Internal Server Error.",
            "traceback": tb_lines
        })
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors_data = exc.errors()
    response_result = {}
    for error in errors_data:
        message = error.get("msg")
        if len(error["loc"]) == 2:
            response_error = {
                "field": error["loc"][1],
                "message": message
            }
            response_result[error["loc"][1]] = response_error
        else:
            break
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "code": 422,
            "detail": response_result
        })
    )


async def sc_response_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    schemes_status_code_dict = {
        status.HTTP_400_BAD_REQUEST: Response400Scheme,
        status.HTTP_401_UNAUTHORIZED: Response401Scheme,
        status.HTTP_403_FORBIDDEN: Response403Scheme,
        status.HTTP_404_NOT_FOUND: Response404Scheme,
        status.HTTP_422_UNPROCESSABLE_ENTITY: Response422Scheme,
        status.HTTP_500_INTERNAL_SERVER_ERROR: Response500Scheme,
    }

    status_code = exc.status_code
    scheme = schemes_status_code_dict.get(
        status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    return JSONResponse(
        status_code=status_code,
        content=scheme(message=exc.detail).model_dump()
    )
