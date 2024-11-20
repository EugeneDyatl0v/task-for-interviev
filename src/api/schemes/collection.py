from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.api.schemes.link import LinkOutScheme
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
