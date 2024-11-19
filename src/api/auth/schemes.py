import http

from fastapi import HTTPException

from pydantic import BaseModel, field_validator, Field


class ChangePasswordScheme(BaseModel):
    old_password: str = Field(...)
    new_password: str = Field(...)
    repeat_password: str = Field(...)

    @field_validator('repeat_password')
    def check_passwords_match(cls, repeat_password, values):
        new_password = values.data.get('new_password')
        if new_password and repeat_password != new_password:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Passwords do not match'
            )
        return repeat_password