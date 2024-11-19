from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from modules.auth.classes import JWTBearer
from modules.auth.schemes import UserInfo
from services.link import LinkManager
from src.api.link.schemes import LinkResponseSchema, LinkOutSchema, \
    PageDataScheme
from src.api.schemes import jwt_bearer_responses, ExceptionScheme, \
    Response200Scheme

router = APIRouter(
    prefix='/link',
    tags=['Link'],
)


@router.get(
    '/',
    responses={
        200: {
            'model': LinkResponseSchema,
            'description': 'Retrieves link',
        },
        **jwt_bearer_responses,
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Retrieves link'
)
async def get_link(
        link_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> LinkResponseSchema:
    link = await LinkManager().get(
        link_id=link_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return LinkResponseSchema(
        data=LinkOutSchema(
            id=link.id,
            page_title=link.page_title,
            description=link.description,
            image_url=link.image_url,
            link_type=link.link_type
        )
    )


@router.post(
    '/',
    responses={
        200: {
            'model': LinkResponseSchema,
            'description': 'Link successfully created',
        },
        **jwt_bearer_responses,
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Link creation'
)
async def create_link(
        link: str = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> LinkResponseSchema:
    link = await LinkManager().create(
        link=link,
        user_id=user_info.user_id,
        db_session=db_session
    )
    return LinkResponseSchema(
        data=LinkOutSchema(
            id=link.id,
            page_title=link.page_title,
            description=link.description,
            image_url=link.image_url,
            link_type=link.link_type
        )
    )


@router.patch(
    '/',
    responses={
        200: {
            'model': LinkResponseSchema,
            'description': 'Link successfully updated',
        },
        **jwt_bearer_responses,
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Link updating'
)
async def update_link(
        link_data: PageDataScheme,
        link_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> LinkResponseSchema:
    link = await LinkManager().update(
        link_id=link_id,
        link_data=link_data,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return LinkResponseSchema(
        data=LinkOutSchema(
            id=link.id,
            page_title=link.page_title,
            description=link.description,
            image_url=link.image_url,
            link_type=link.link_type
        )
    )


@router.delete(
    '/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Link successfully deleted',
        },
        **jwt_bearer_responses,
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Link deleting'
)
async def delete_link(
        link_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> Response200Scheme:
    await LinkManager().delete(
        link_id=link_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return Response200Scheme(
        message='Link successfully deleted',
    )
