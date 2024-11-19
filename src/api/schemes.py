from typing import Any, Dict

from pydantic import (
    BaseModel, Field
)


class JWTScheme(BaseModel):
    auth_token: str = Field(
        examples=[
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2luZm8iOnsic2Vzc2l'
            'vbl9pZCI6ImY5ZGI5ODk0LTMyYmYtNGIxZC05NWMwLWMxMmVjMWU1ZTdjNCIsInV'
            'zZXJfaWQiOiJkYTQzYTRlYi0xMjFkLTRmNGItODBjNy0wZTBjMzA1YjlhZWMiLCJ'
            'lbWFpbCI6InVzZXJAYXV0aDAuY29tIiwicGhvbmUiOiI3MTIzNDU2Nzg5MCIsInJ'
            'vbGVfaWQiOiIzIn0sInNjb3BlIjoiYWRtaW4iLCJ0b2tlbl91dWlkIjoiZDIxMzh'
            'iYjctZTQ1NS00MzhhLWE0YWYtYjQ1ZTI3NTRiOTYwIn0.T-4pI39vwB8MFgEzjuV'
            '5u1k_Ghv3oZIzpr_yVA4Zo44'
        ]
    )
    refresh_token: str = Field(
        examples=[
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2luZm8iOnsic2Vzc2'
            'lvbl9pZCI6IjA4ZTViMTg3LWQ4MDUtNGI5Ni05NzIyLTA2Y2QzZTI1MzY5ZCIsI'
            'nVzZXJfaWQiOiJkYTQzYTRlYi0xMjFkLTRmNGItODBjNy0wZTBjMzA1YjlhZWMi'
            'LCJlbWFpbCI6InVzZXJAYXV0aDAuY29tIiwicGhvbmUiOiI3MTIzNDU2Nzg5MCI'
            'sInJvbGVfaWQiOiIzIn0sInNjb3BlIjoiYWRtaW4iLCJyZWZyZXNoX3V1aWQiOi'
            'JiM2JjNTM4Zi04ZDNmLTQ4OWYtOGQ4OS03YWM0YWM3OTc3YWEiLCJleHAiOjE3M'
            'TY3MTk4NjB9.7SyzVP3E2ZaWIJ44yi19xBcOY6H2WVDg5fah4Qb8MxU'
        ]
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


class DataResponseSchema(Response200Scheme):
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
