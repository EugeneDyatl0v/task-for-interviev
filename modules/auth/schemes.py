from pydantic import BaseModel, EmailStr, Field


class EmailLoginScheme(BaseModel):
    email: EmailStr = Field(examples=['evgenii.dyatlov06@gmail.com'])
    password: str


class UserInfo(BaseModel):
    session_id: str = Field(examples=['7bbb46e4-5c1e-4f7c-8e95-31ce323779b6'])
    user_id: str = Field(examples=['951b2a00-523a-4a7c-a85f-395ee1910064'])
    email: str | None = Field(examples=['user@auth0.com'])


class UserJwtPayload(BaseModel):
    user_info: UserInfo = Field()
    scope: str = Field(examples=['admin', 'client'])
    token_uuid: str = Field(examples=['92a3098a-b402-495c-8069-697abe4c3f3f'])
