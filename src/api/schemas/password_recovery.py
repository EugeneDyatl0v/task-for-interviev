import datetime
import re

from src.api.schemes import Response200Scheme

from pydantic import BaseModel, Field, model_validator


class PasswordSchema(BaseModel):
    password: str
    repeat_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'PasswordSchema':
        pw1 = self.password
        pw2 = self.repeat_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return self


class EmailRecoverySchema(BaseModel):
    email: str = Field(examples=['evgenii.dyatlov06@gmail.com'])

    @model_validator(mode='after')
    def check_email(self) -> 'EmailRecoverySchema':
        email = self.email
        if not bool(re.match(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                email
        )):
            raise ValueError('Email must be in a valid format')
        return self


class ResetCodeSchemaOut(BaseModel):
    expired_at: datetime.datetime = Field()


class ConfirmationCodeResponseScheme(Response200Scheme):
    result: ResetCodeSchemaOut
