import http

from fastapi import HTTPException

from jose import JWTError, jwt

from settings import JWTConfig


def validate_token(refresh_token: str) -> dict[str, str]:
    try:
        return jwt.decode(refresh_token, JWTConfig.secret_key)
    except JWTError:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Invalid token'
        )
