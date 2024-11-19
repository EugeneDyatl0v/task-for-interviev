from database.models import SessionModel, UserModel

from modules.auth.jwt.abstract import JWT
from modules.auth.jwt.classes import (
    JWTArgsConstField, JWTModelConstField, JWTModelEditableField
)

from settings import JWTConfig


JWT_PAYLOAD_ADMIN = {
    "session_id": JWTArgsConstField("id", "id"),
    "user_id": JWTModelConstField(
        UserModel, "user_id", "id", "id"
    ),
    "email": JWTModelEditableField(
        UserModel, "user_id", "id", "email"
    )
}

JWT_PAYLOAD_CLIENT = {**JWT_PAYLOAD_ADMIN}


class JWTAdmin(JWT):
    scope: str = JWTConfig.scope_admin
    jwt_payload_structure: dict = JWT_PAYLOAD_ADMIN
    SessionModel = SessionModel
