import http
from typing import List
from uuid import UUID

from database.models import (
    CollectionModel,
    LinkCollectionAssociation,
    LinkModel
)

from fastapi import HTTPException

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.schemes.collection import CollectionDataScheme


class CollectionManager:
    async def get(
            self,
            collection_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> CollectionModel:
        query = select(CollectionModel).where(
            and_(
                CollectionModel.id == collection_id,
                CollectionModel.user_id == user_id
            )
        )
        result = await db_session.execute(query)
        db_collection = result.scalars().one_or_none()

        if not db_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail="Collection not found"
            )

        return db_collection

    async def create(
            self,
            collection_data: CollectionDataScheme,
            user_id: str,
            db_session: AsyncSession
    ) -> CollectionModel:
        query = select(CollectionModel).where(
            CollectionModel.title == collection_data.title
        )
        result = await db_session.execute(query)
        db_collection = result.scalars().one_or_none()

        if db_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Collection already exists"
            )

        new_collection = CollectionModel(
            title=collection_data.title,
            description=collection_data.description,
            user_id=user_id
        )

        db_session.add(new_collection)
        await db_session.commit()
        await db_session.refresh(new_collection)
        return new_collection

    async def update(
            self,
            collection_id: UUID,
            collection_data: CollectionDataScheme,
            user_id: str,
            db_session: AsyncSession
    ) -> CollectionModel | None:
        query = await db_session.execute(
            select(CollectionModel).where(
                and_(
                    CollectionModel.id == collection_id,
                    CollectionModel.user_id == user_id
                )
            )
        )

        original_collection = query.scalars().first()

        if not original_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Collection not found'
            )

        for key, value in collection_data.model_dump().items():
            if hasattr(original_collection, key):
                setattr(original_collection, key, value)

        await db_session.commit()

        await db_session.refresh(original_collection)

        return original_collection

    async def delete(
            self,
            collection_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        result = await db_session.execute(
            select(CollectionModel).where(
                and_(
                    CollectionModel.id == collection_id,
                    CollectionModel.user_id == user_id
                )
            )
        )

        db_collection = result.scalars().first()

        if not db_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Collection not found'
            )

        await db_session.delete(db_collection)
        await db_session.commit()

    async def add_link(
            self,
            link_id: UUID,
            collection_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        query = select(LinkCollectionAssociation).where(
            and_(
                LinkCollectionAssociation.link_id == link_id,
                LinkCollectionAssociation.collection_id == collection_id,
                LinkCollectionAssociation.user_id == user_id
            )
        )
        result = await db_session.execute(query)
        db_association = result.scalars().one_or_none()

        if db_association:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Association already exists"
            )

        query = select(LinkModel).where(
            and_(
                LinkModel.id == link_id,
                LinkModel.user_id == user_id
            )
        )
        result = await db_session.execute(query)
        db_link = result.scalars().one_or_none()

        if not db_link:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Link does not exists"
            )

        query = select(CollectionModel).where(
            and_(
                CollectionModel.id == collection_id,
                CollectionModel.user_id == user_id
            )
        )
        result = await db_session.execute(query)
        db_collection = result.scalars().one_or_none()

        if not db_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Collection does not exists"
            )

        association = LinkCollectionAssociation(
            link_id=link_id,
            collection_id=collection_id,
            user_id=UUID(user_id)
        )

        db_session.add(association)
        await db_session.commit()

    async def remove_link(
            self,
            link_id: UUID,
            collection_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        query = select(LinkCollectionAssociation).where(
            and_(
                LinkCollectionAssociation.link_id == link_id,
                LinkCollectionAssociation.collection_id == collection_id,
                LinkCollectionAssociation.user_id == user_id
            )
        )
        result = await db_session.execute(query)
        db_association = result.scalars().one_or_none()

        if db_association:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Association does not exists"
            )

        await db_session.delete(db_association)
        await db_session.commit()

    async def get_links(
            self,
            collection_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> List[LinkModel]:
        query = select(CollectionModel).where(
            and_(
                CollectionModel.id == collection_id,
                CollectionModel.user_id == user_id
            )
        ).options(selectinload(CollectionModel.links))
        result = await db_session.execute(query)
        db_collection = result.scalars().one_or_none()

        if not db_collection:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail="Collection not found"
            )

        return db_collection.links
