import http

from fastapi import HTTPException

from modules.auth.classes import EmailPasswordAuthHandler
from modules.auth.schemes import EmailLoginScheme


def get_login_handler(
        login_info: EmailLoginScheme
):
    if isinstance(login_info, EmailLoginScheme):
        return EmailPasswordAuthHandler
    else:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Invalid request scheme'
        )
