import datetime
import enum
import uuid

from database import Base
from database.mixins import TimestampMixin

from settings import Database

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UUID,
    LargeBinary, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class LinkType(enum.Enum):
    website = 'website'
    book = 'book'
    article = 'article'
    music = 'music'
    video = 'video'


class UserModel(TimestampMixin, Base):
    __table_args__ = (
        {
            'extend_existing': True,
            'comment': 'Represents a user in the system'
        }
    )
    __tablename__ = f'{Database.prefix}users'
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the user"
    )
    password_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Hashed password of the user"
    )
    email: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        comment="Email address of the user"
    )
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        nullable=True,
        comment="Timestamp when the user was deleted"
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=False,
        comment="Indicates if the user's email is verified"
    )
    confirmation_codes: Mapped[list['ConfirmationCodeModel']] = relationship(
        back_populates='user',
    )

    @classmethod
    def get_criteria(cls, alias=None):
        if alias is None:
            alias = cls
        return alias.deleted_at.is_(None)


class ConfirmationCodeModel(TimestampMixin, Base):
    __tablename__ = f'{Database.prefix}confirmation_codes'
    __table_args__ = {
        'comment': 'Represents a confirmation code in the system'
    }

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the confirmation code"
    )
    code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Confirmation code"
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{Database.prefix}users.id', ondelete='CASCADE'),
        comment="Identifier of the user associated with the confirmation code"
    )
    expired_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        comment="Timestamp when the confirmation code expires"
    )
    used: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=False,
        comment="Indicates if the confirmation code has been used"
    )
    user: Mapped['UserModel'] = relationship(
        back_populates='confirmation_codes',
    )


class SessionModel(TimestampMixin, Base):
    __table_args__ = {
        'extend_existing': True,
        'comment': 'Represents a user session in the system'
    }
    __tablename__ = f'{Database.prefix}sessions'
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the session"
    )
    user_id: Mapped[str] = mapped_column(
        UUID(),
        ForeignKey(f'{Database.prefix}users.id'),
        nullable=False,
        comment="Identifier of the user associated with the session"
    )
    ip: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        comment="IP address of the session"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
        comment="Indicates if the session is active"
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=False,
        comment="Indicates if the session is closed"
    )
    auth_token_data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB()), nullable=True,
        comment="Data for the authentication token"
    )
    refresh_token_data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB()), nullable=True,
        comment="Data for the refresh token"
    )


class LinkCollectionAssociation(Base):
    __tablename__ = f'{Database.prefix}link_collection_associations'
    __table_args__ = (
        UniqueConstraint(
            "link_id",
            "collection_id",
            "user_id",
            name="uq_link_collection"
        ),
        {'extend_existing': True,
         'comment': ''}
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the collection"
    )
    link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f'{Database.prefix}links.id'),
        nullable=False,
        comment="Identifier of the user who owns the collection"
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f'{Database.prefix}collections.id'),
        nullable=False,
        comment="Identifier of the user who owns the collection"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f'{Database.prefix}users.id'),
        nullable=False,
        comment="Identifier of the user"
    )


class LinkModel(TimestampMixin, Base):
    __tablename__ = f'{Database.prefix}links'
    __table_args__ = (
        UniqueConstraint("user_id", "link", name="uq_user_link"),
        {'extend_existing': True, 'comment': 'Represents a user link in the system'}
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the link"
    )
    page_title: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Title of the page"
    )
    description: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
        comment="Description of the page"
    )
    link: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Link of the page"
    )
    image_url: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
        comment="Image URL of the page"
    )
    link_type: Mapped[LinkType] = mapped_column(
        Enum(LinkType),
        nullable=False,
        default=LinkType.website,
        comment='Type of the link'
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f'{Database.prefix}users.id'),
        nullable=False,
        comment="Identifier of the user associated with the link"
    )
    collections = relationship(
        "CollectionModel",
        secondary=f"{Database.prefix}link_collection_associations",
        back_populates="links"
    )


class CollectionModel(TimestampMixin, Base):
    __tablename__ = f'{Database.prefix}collections'
    __table_args__ = (
        {'extend_existing': True, 'comment': 'Represents a user collection in the system'}
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the collection"
    )
    title: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Title of the collection"
    )
    description: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
        comment="Description of the collection"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f'{Database.prefix}users.id'),
        nullable=False,
        comment="Identifier of the user who owns the collection"
    )
    links = relationship(
        "LinkModel",
        secondary=f"{Database.prefix}link_collection_associations",
        back_populates="collections"
    )
