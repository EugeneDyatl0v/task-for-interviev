import http
import uuid
from abc import ABC

from database import Session

from fastapi import HTTPException

from jose import jwt

from modules.auth.jwt.classes import (
    JWTArgsEditableField,
    JWTArgsField,
    JWTModelEditableField,
    JWTModelField,
)

from settings import JWTConfig

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError


JWT_PAYLOAD = {}


class JWT(ABC):
    """Handles operations with JsonWebTokens

    Attributes:
        session (Session): the current session object
        payload (dict): payload from the previous token, if the data has not
            changed
    """

    jwt_payload_structure: dict = JWT_PAYLOAD
    scope: str = None
    SessionModel = None
    payload: dict[str, str] | None = None

    def __init__(self, auth_session, **kwargs):
        self.session = auth_session
        self.payload = kwargs.get('old_payload')

    async def generate_payload(self) -> None:
        """Generate the filled JWT payload.

        Returns:
            dict, ready-made payload.
        """
        user_property = JWTConfig.user_property
        if self.payload:
            payload = self.payload
        else:
            payload = dict()
            payload[user_property] = {}
            attrs = self.jwt_payload_structure.items()
            for attr, val in attrs:
                if isinstance(val, (JWTModelField, JWTArgsField)):
                    await val.set_value(self.session)
                payload[user_property][attr] = str(val.value)
        await self.revive_session(payload[user_property].get('session_id'))
        payload['scope'] = self.scope
        self.payload = payload

    async def revive_session(self, payload_session_id) -> None:
        """Set expired session in not expired state.

        Args:
            payload_session_id (str): id of the session to revive.

        Returns:
            None:
        """
        try:
            async with Session() as session:
                user_session = await session.execute(
                    select(self.SessionModel).where(
                        self.SessionModel.id == payload_session_id
                    )
                )
                user_session = user_session.scalars().first()
                user_session.is_expired = False
                session.add(user_session)
                await session.commit()
                await session.refresh(user_session)

        except DatabaseError:
            session.rollback()
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='The session has expired and cannot be revived'
            )

    async def generate_auth_token(self) -> tuple[str, dict[str, str]]:
        """Generate an auth token.

        Returns:
            str: an auth token.
        """
        to_encode = self.payload.copy()
        to_encode.update({'token_uuid': str(uuid.uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, JWTConfig.secret_key, algorithm=JWTConfig.algorithm
        )
        return encoded_jwt, to_encode

    async def generate_refresh_token(self) -> tuple[str, dict[str, str]]:
        """Generate a refresh token.

        Returns:
            str: a refresh token.
        """
        to_encode = self.payload.copy()
        to_encode.update({'refresh_uuid': str(uuid.uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, JWTConfig.secret_key, algorithm=JWTConfig.algorithm
        )
        return encoded_jwt, to_encode

    @classmethod
    def get_jwt_editable_models(cls) -> dict[object, list[list[str]]]:
        """
        Get the models of the editable fields of the JWT payload
        and their tracked fields, as well as the field related
        with the auth Session object.

        Returns:
            dict: editable fields of the JWT payload data.
        """

        main_model_field_data = list()
        model_field_data = dict()

        for k, v in cls.jwt_payload_structure.items():
            if isinstance(v, (JWTModelEditableField, JWTArgsEditableField)):
                main_model_field_data.append(
                    v.get_editable_fields(cls.SessionModel)
                )

        for edit_field in main_model_field_data:
            if edit_field.model in main_model_field_data:
                model_field_data[edit_field.model][0].append(
                    edit_field.field_out)
            else:
                model_field_data[edit_field.model] = [
                    [edit_field.field_out, ], ]
                model_field_data[edit_field.model].append(
                    edit_field.session_field_name
                )
                model_field_data[edit_field.model].append(
                    edit_field.field_in
                )

        return model_field_data
