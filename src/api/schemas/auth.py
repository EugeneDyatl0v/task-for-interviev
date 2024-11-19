from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel, Field
)


class LoginResponse(BaseModel):
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
        ])


class SessionSchema(BaseModel):
    id: UUID = Field(examples=[UUID('3cb2a142-a2f4-4ecc-ba02-3cb2a1ef2dfb')])
    user_id: UUID = Field(examples=[
        UUID('b55b5c42-a2f4-4ecc-ba02-3cb2a1ef2dfb')
    ])
    ip: str = Field(examples=['127.0.0.1', '192.168.0.1'])
    is_active: bool = Field(examples=[True, False], default=True)


class SessionsListSchema(BaseModel):
    sessions: List[SessionSchema]
