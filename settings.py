import dataclasses
import os


APP_NAME = "link_vault"


@dataclasses.dataclass
class Database:
    prefix = 'link_vault_'
    url = os.environ.get('DATABASE_URL')
    pool_size = int(
        os.environ.get(
            'DB_ENGINE_OPTION_POOL_SIZE', default=5
        )
    )
    max_overflow = int(
        os.environ.get(
            'DB_ENGINE_OPTION_MAX_OVERFLOW', default=50
        )
    )
    pool_recycle = int(
        os.environ.get(
            'DB_ENGINE_OPTION_POOL_RECYCLE', default=600
        )
    )
    pool_pre_ping = os.environ.get(
        'DB_ENGINE_OPTION_POOL_PRE_PING', default=False
    )


@dataclasses.dataclass
class AppConfig:
    secret_key = os.environ.get('APP_SECRET_KEY', default='secret')
    debug = os.environ.get('APP_DEBUG', default=False)


@dataclasses.dataclass
class JWTConfig:
    secret_key = os.environ.get(
        'JWT_SECRET_KEY',
        default=(
            '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
        )
    )
    algorithm = 'HS256'
    auth_token_time_expiration_minutes = 60
    refresh_token_time_expiration_minutes = 60 * 24 * 7
    user_property = 'user_info'
    scope_user = 'user'


@dataclasses.dataclass
class TemplatesConfig:
    reset_password = '/email/reset_password.html'
    subject_reset_password = 'Password recovery'
    verification = '/email/verify_email.html'
    subject_verification = 'Email verification'


@dataclasses.dataclass
class UnisenderConfig:
    api_key = os.environ.get(
        'UNISENDER_API_KEY'
    )
    sender_name = os.environ.get(
        'UNISENDER_SENDER_NAME'
    )
    sender_email = os.environ.get(
        'UNISENDER_SENDER_EMAIL'
    )
    default_list_id = os.environ.get(
        'UNISENDER_DEFAULT_LIST_ID'
    )
    registration_template_id = os.environ.get(
        'UNISENDER_REGISTER_CODE_TEMPLATE_ID'
    )
    password_reset_template_id = os.environ.get(
        'UNISENDER_PASSWORD_RESET_TEMPLATE_ID'
    )
    sending_timeout = os.environ.get(
        'UNISENDER_SENDING_TIMEOUT'
    )
