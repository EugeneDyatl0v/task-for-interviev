from database.models import SessionModel

from jose import JWTError, jwt

from passlib.context import CryptContext

from services.session import SessionService

from settings import AppConfig, JWTConfig

from sqlalchemy.ext.asyncio import AsyncSession


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def get_password_hash(password: str) -> str:
    password = f'{password}{AppConfig.secret_key}'
    return pwd_context.hash(password)


async def get_data_from_token(token: str) -> dict[str, str]:
    try:
        decoded_payload = jwt.decode(
            token, JWTConfig.secret_key, algorithms=[JWTConfig.algorithm]
        )
        return decoded_payload
    except JWTError:
        raise JWTError


async def get_session_by_id(
        session_id: str,
        db_session: AsyncSession
) -> SessionModel | None:
    return await SessionService.get_by_id(
        session_id=session_id,
        db_session=db_session
    )
