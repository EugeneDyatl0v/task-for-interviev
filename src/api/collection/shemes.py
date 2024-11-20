from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from src.api.link.schemes import LinkOutScheme
from src.api.schemes.response import DataResponseScheme


class CollectionDataScheme(BaseModel):
    title: str
    description: Optional[str]


class CollectionOutScheme(BaseModel):
    id: UUID
    title: str
    description: Optional[str]


class CollectionResponseScheme(DataResponseScheme):
    data: CollectionOutScheme


class LinkListResponseScheme(DataResponseScheme):
    data: List[LinkOutScheme]
