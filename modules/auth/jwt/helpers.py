from datetime import UTC, datetime, timedelta

from settings import JWTConfig


def get_auth_expiration():
    return datetime.now(UTC) + timedelta(
        minutes=JWTConfig.auth_token_time_expiration_minutes
    )


def get_refresh_expiration():
    return datetime.now(UTC) + timedelta(
        minutes=JWTConfig.refresh_token_time_expiration_minutes
    )
