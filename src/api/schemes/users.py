import datetime
from typing import Optional
from uuid import UUID

from fastapi_pagination import Page

from pydantic import BaseModel, Field


user_email_optional_pattern = (
    r'^(deleted_[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|'
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
)
user_email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class BasicUser(BaseModel):
    email: str | None = Field(
        None,
        pattern=user_email_optional_pattern,
        examples=['client@email.com']
    )
    email_verified: bool = Field(
        False,
        description='User\'s email verification status'
    )
    phone_verified: bool = Field(
        False,
        description='User\'s phone verification status'
    )


class UserWithMixins(BasicUser, BaseModel):
    deleted_at: Optional[datetime.datetime] = Field(
        None,
        description='User\'s deleted status: delete or not'
    )
    created_at: Optional[datetime.datetime] = Field(
        None,
        description='User\'s created status: delete or not'
    )
    updated_at: Optional[datetime.datetime] = Field(
        None,
        description='User\'s updated status: delete or not'
    )


class UserScheme(UserWithMixins):
    id: Optional[UUID] = Field(
        description='User\'s ID',
        examples=['311c056c-217e-4421-a124-47de2549ebdc']
    )

    class Config:
        from_attributes = True


class CreateUserScheme(UserWithMixins):

    password: Optional[str] = Field(
        'super_secret_password',
        description='User\'s password'
    )

    class Config:
        json_scheme_extra = {
            'example': {
                'phone': '78888888888',
                'email': 'ilya@google.com',
                'password': 'super_secret_password',
                'email_verified': False,
                'phone_verified': False,
                'deleted_at': None,
                'created_at': None,
                'updated_at': None,
            }
        }


class EditUserScheme(BasicUser):
    pass


class ClientEditUserScheme(BaseModel):
    pass


class UserFilterScheme(BaseModel):
    email: Optional[str] = Field(
        None,
        description='Filter by email address'
    )
    email_verified: Optional[bool] = Field(
        None,
        description='Filter by email verification status'
    )
    created_at: Optional[datetime.datetime] = Field(
        None,
        description='Filter by user\'s created status'
    )
    updated_at: Optional[datetime.datetime] = Field(
        None,
        description='Filter by user\'s updated status'
    )


class UserListResponse(BaseModel):
    success: bool = True
    result: Page[UserScheme]
    filters: Optional[UserFilterScheme] = None


class UserResponse(BaseModel):
    success: bool = True
    result: UserScheme

    class Config:
        from_attributes = True


class ClientInfoResponse(BaseModel):
    success: bool = True
    result: BasicUser

    class Config:
        from_attributes = True
