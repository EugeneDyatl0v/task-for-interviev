from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from database.models import LinkType
from src.api.schemes.response import DataResponseScheme


class PageDataScheme(BaseModel):
    page_title: str
    description: Optional[str]
    image_url: Optional[str]
    link_type: LinkType


class LinkOutScheme(BaseModel):
    id: UUID
    page_title: str
    description: Optional[str]
    image_url: Optional[str]
    link_type: LinkType


class LinkResponseScheme(DataResponseScheme):
    data: LinkOutScheme
