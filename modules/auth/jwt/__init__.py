from database.models import SessionModel, UserModel

from modules.auth.jwt.abstract import JWT
from modules.auth.jwt.classes import (
    JWTArgsConstField, JWTModelConstField, JWTModelEditableField
)

from settings import JWTConfig


JWT_PAYLOAD_USER = {
    "session_id": JWTArgsConstField("id", "id"),
    "user_id": JWTModelConstField(
        UserModel, "user_id", "id", "id"
    ),
    "email": JWTModelEditableField(
        UserModel, "user_id", "id", "email"
    )
}


class JWTUser(JWT):
    scope: str = JWTConfig.scope_user
    jwt_payload_structure: dict = JWT_PAYLOAD_USER
    SessionModel = SessionModel
