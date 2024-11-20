from typing import Any, Dict

from pydantic import (
    BaseModel, Field
)


# Responses
class Response200Scheme(BaseModel):
    success: bool = True
    message: str = 'Success'


class Response400Scheme(BaseModel):
    success: bool = False
    message: str = 'Bad request'


class Response401Scheme(BaseModel):
    success: bool = False
    message: str = 'Not authenticated'


class Response403Scheme(BaseModel):
    success: bool = False
    message: str = 'Unauthorized'


class Response404Scheme(BaseModel):
    success: bool = False
    message: str = 'Not found'


class Response422Scheme(BaseModel):
    success: bool = False
    message: str = 'Unprocessable entity'


class Response500Scheme(BaseModel):
    success: bool = False
    message: str = 'Internal server error'


class ExceptionScheme(BaseModel):
    detail: Any = Field(examples=['Some error occurred.'])


class DataResponseScheme(Response200Scheme):
    data: Dict[str, Any]


jwt_bearer_responses = {
    400: {
        'model': ExceptionScheme,
        'description': 'Invalid credentials'
    },
    403: {
        'model': ExceptionScheme,
        'description': 'Insufficient privileges'
    },
}
