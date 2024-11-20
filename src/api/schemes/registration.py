import re

from pydantic import BaseModel, Field, model_validator

from src.api.schemes.response import Response200Scheme


email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class EmailRegisterScheme(BaseModel):
    email: str = Field(examples=['user@auth0.com'])
    password: str = Field(examples=['string'])
    repeat_password: str = Field(examples=['string'])

    @model_validator(mode='after')
    def check_passwords_match_and_email_validation(
            self
    ) -> 'EmailRegisterScheme':
        pw1 = self.password
        pw2 = self.repeat_password
        email = self.email
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords not equals')
        if not bool(re.match(
                email_pattern,
                email
        )):
            raise ValueError('Email must be in a valid format')
        return self


class EmailConfirmationScheme(BaseModel):
    email: str = Field(examples=['evgenii.dyatlov06@gmail.com'])
    email_verified: bool = Field(examples=[True, False])


class EmailConfirmationOutScheme(Response200Scheme):
    result: EmailConfirmationScheme


class EmailResendCodeScheme(BaseModel):
    email: str = Field(examples=['user@auth0.com'], pattern=email_pattern)
