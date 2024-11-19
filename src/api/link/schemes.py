from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from database.models import LinkType
from src.api.schemes import DataResponseSchema


class PageDataScheme(BaseModel):
    page_title: str
    description: Optional[str]
    image_url: Optional[str]
    link_type: LinkType


class LinkOutSchema(BaseModel):
    id: UUID
    page_title: str
    description: Optional[str]
    image_url: Optional[str]
    link_type: LinkType


class LinkResponseSchema(DataResponseSchema):
    data: LinkOutSchema
