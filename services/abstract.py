import http
from abc import ABC, abstractmethod

from database.models import ConfirmationCodeModel, UserModel

from fastapi import HTTPException

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRegistration(ABC):
    """
    Abstract class for registration.

    Subclasses must implement the _register method to provide specific
    registration logic

    Attributes:
        is_password_recovery: bool, shows whether it is possible to recover
            the password using this registration method
    """

    is_password_recovery: bool

    @abstractmethod
    async def _user_exists(
            self,
            registration_data: BaseModel,
            db_session: AsyncSession
    ) -> bool:
        """
        Abstract method for checking user existence.

            This method must be implemented by subclasses to provide
            the specific logic for checking user existence.

            Args:
                registration_data: BaseModel, user data.
                db_session: AsyncSession, database session.
        """

    @abstractmethod
    async def _register(
            self,
            request: BaseModel,
            db_session: AsyncSession
    ) -> 'UserModel':
        """
        Abstract method to registration.

        This method must be implemented by subclasses to provide
        the specific logic for registration.

        Args:
            request: BaseModel, user data.
            db_session: AsyncSession, database session.
        """

    @abstractmethod
    async def _create_confirmation_code(
            self,
            user: UserModel,
            db_session: AsyncSession
    ) -> str:
        """
        Abstract method for confirmation code creating.
        Returns created confirmation code

        This method must be implemented by subclasses to provide
        the specific logic for confirmation code creating.
        """

    @abstractmethod
    async def _send_confirmation_code(
            self,
            request: BaseModel,
            confirmation_code: str
    ):
        """
        Abstract method to send confirmation code.

        This method must be implemented by subclasses to provide
        the specific logic for sending of confirmation code.
        """

    async def register(
            self,
            request: BaseModel,
            db_session: AsyncSession
    ) -> 'UserModel':
        """
        Registers a new user in the system.

        Args:
            request (BaseModel): The request object containing the user's
                registration details.
            db_session (AsyncSession): The database session used for
                interacting with the database.

        Returns:
            user: The newly created user object.

        Raises:
            HTTPException: If a user with the provided details already exists,
                an exception is raised with a 400 status code and a relevant
                error message.
        """
        if await self._user_exists(request, db_session):
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='User already exists'
            )

        user = await self._register(request, db_session)

        confirmation_code = await self._create_confirmation_code(
            user, db_session
        )

        await self._send_confirmation_code(request, confirmation_code)

        await db_session.commit()

        return user


class AbstractPasswordRecovery(ABC):
    """
    Abstract class for password recovery.

    Subclasses must implement the _register method to provide specific
    registration logic
    """

    @abstractmethod
    async def _get_user(
            self,
            credentials: BaseModel,
            db_session: AsyncSession
    ) -> UserModel:
        """
        Abstract method for checking user existence.

        This method must be implemented by subclasses to provide
        the specific logic for checking user existence.

        Arguments:
            credentials (BaseModel): user data.
            db_session (AsyncSession): database session.
        """

    @abstractmethod
    async def _create_confirmation_code(
            self,
            user: UserModel,
            db_session: AsyncSession
    ) -> ConfirmationCodeModel:
        """
        Abstract method for confirmation code creating.
        Returns created confirmation code

        This method must be implemented by subclasses to provide
        the specific logic for confirmation code creating.
        """

    @abstractmethod
    async def _send_confirmation_code(
            self,
            credentials: BaseModel,
            confirmation_code: str
    ):
        """
        Abstract method to send confirmation code.

        This method must be implemented by subclasses to provide
        the specific logic for sending of confirmation code.
        """

    async def password_recovery_request(
            self,
            credentials: BaseModel,
            db_session: AsyncSession
    ) -> ConfirmationCodeModel:
        """
        User password recovery by email.

        This method check existence of user using
        `_checking_user_existence` method,
        send code for email confirmation using
        `_send_confirmation_code` method and
        create confirmation code in database using
        `_create_confirmation_code` method.
        """
        user = await self._get_user(credentials, db_session)
        if not user:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Wrong credentials'
            )

        confirmation_code = await self._create_confirmation_code(
            user,
            db_session
        )

        await self._send_confirmation_code(credentials, confirmation_code.code)

        await db_session.commit()

        return confirmation_code
