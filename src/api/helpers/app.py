from src.api.handlers import (
    internal_exception_handler,
    sc_response_exception_handler,
    validation_exception_handler
)

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

from settings import AppConfig

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


def init_exc_handlers(app) -> None:
    app.exception_handler(HTTPException)(sc_response_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)

    if AppConfig.debug:
        app.exception_handler(500)(internal_exception_handler)


allow_origins = [
    'http://localhost',
    'https://localhost'
]


def init_middleware(app) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SessionMiddleware, secret_key=AppConfig.secret_key)
