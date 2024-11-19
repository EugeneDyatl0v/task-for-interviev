from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from src.api.link.schemes import LinkOutSchema
from src.api.schemes import DataResponseSchema


class CollectionDataScheme(BaseModel):
    title: str
    description: Optional[str]


class CollectionOutSchema(BaseModel):
    id: UUID
    title: str
    description: Optional[str]


class CollectionResponseSchema(DataResponseSchema):
    data: CollectionOutSchema


class LinkListResponseSchema(DataResponseSchema):
    data: List[LinkOutSchema]
