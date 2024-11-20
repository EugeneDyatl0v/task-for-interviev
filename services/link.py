import http
from uuid import UUID

from bs4 import BeautifulSoup

from database.models import LinkModel, LinkType

from fastapi import HTTPException

import httpx

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemes.link import PageDataScheme


class LinkManager:
    async def fetch_page_data(self, url: str) -> PageDataScheme:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch the URL"
            )

        soup = BeautifulSoup(response.text, "html.parser")

        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        og_type = soup.find("meta", property="og:type")

        title = soup.title.string if soup.title else None
        meta_description = soup.find(
            "meta", attrs={"name": "description"}
        )

        return PageDataScheme(
            page_title=og_title["content"] if og_title else title,
            description=(
                og_description["content"]
                if og_description
                else (
                    meta_description["content"]
                    if meta_description
                    else None
                )
            ),
            image_url=og_image["content"] if og_image else None,
            link_type=(
                LinkType[og_type["content"]] if og_type else LinkType.website
            )
        )

    async def get(
            self,
            link_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> LinkModel:
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
                status_code=http.HTTPStatus.NOT_FOUND,
                detail="Link not found"
            )

        return db_link

    async def create(
            self,
            link: str,
            user_id: str,
            db_session: AsyncSession
    ) -> LinkModel:
        query = select(LinkModel).where(LinkModel.link == link)
        result = await db_session.execute(query)
        db_link = result.scalars().one_or_none()

        if db_link:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Link already exists'
            )

        page_data = await self.fetch_page_data(link)

        new_link = LinkModel(
            page_title=page_data.page_title,
            description=page_data.description,
            image_url=page_data.image_url,
            link_type=page_data.link_type,
            link=link,
            user_id=UUID(user_id)
        )

        db_session.add(new_link)
        await db_session.commit()
        await db_session.refresh(new_link)
        return new_link

    async def update(
            self,
            link_id: UUID,
            link_data: PageDataScheme,
            user_id: str,
            db_session: AsyncSession
    ) -> LinkModel | None:
        query = await db_session.execute(
            select(LinkModel).where(
                and_(
                    LinkModel.id == link_id,
                    LinkModel.user_id == user_id
                )
            )
        )

        original_link = query.scalars().first()

        if not original_link:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Link not found'
            )

        for key, value in link_data.model_dump().items():
            if hasattr(original_link, key):
                setattr(original_link, key, value)

        await db_session.commit()

        await db_session.refresh(original_link)

        return original_link

    async def delete(
            self,
            link_id: UUID,
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        result = await db_session.execute(
            select(LinkModel).where(
                and_(
                    LinkModel.id == link_id,
                    LinkModel.user_id == user_id
                )
            )
        )

        db_link = result.scalars().first()

        if not db_link:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Link not found'
            )

        await db_session.delete(db_link)
        await db_session.commit()
