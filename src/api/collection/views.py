from uuid import UUID

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from modules.auth.classes import JWTBearer
from modules.auth.schemes import UserInfo
from services.collection import CollectionManager
from src.api.collection.shemes import (
    CollectionResponseScheme,
    CollectionOutScheme,
    CollectionDataScheme,
    LinkListResponseScheme
)
from src.api.link.schemes import LinkOutScheme
from src.api.schemes.response import jwt_bearer_responses, ExceptionScheme, \
    Response200Scheme


router = APIRouter(
    prefix='/collection',
    tags=['Collection'],
)


@router.get(
    '/',
    responses={
        200: {
            'model': CollectionResponseScheme,
            'description': 'Retrieves collection',
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
    summary='Retrieves a collection by its ID.'
)
async def get_collection(
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> CollectionResponseScheme:
    collection = await CollectionManager().get(
        collection_id=collection_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return CollectionResponseScheme(
        data=CollectionOutScheme(
            id=collection.id,
            title=collection.title,
            description=collection.description
        )
    )


@router.post(
    '/',
    responses={
        200: {
            'model': CollectionResponseScheme,
            'description': 'Collection successfully created',
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
    summary='Creates a new collection.'
)
async def create_collection(
        collection_data: CollectionDataScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> CollectionResponseScheme:
    collection = await CollectionManager().create(
        collection_data=collection_data,
        user_id=user_info.user_id,
        db_session=db_session
    )
    return CollectionResponseScheme(
        data=CollectionOutScheme(
            id=collection.id,
            title=collection.title,
            description=collection.description
        )
    )


@router.patch(
    '/',
    responses={
        200: {
            'model': CollectionResponseScheme,
            'description': 'Collection successfully updated',
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
    summary='Updates an existing collection.'
)
async def update_collection(
        collection_data: CollectionDataScheme,
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> CollectionResponseScheme:
    collection = await CollectionManager().update(
        collection_id=collection_id,
        collection_data=collection_data,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return CollectionResponseScheme(
        data=CollectionOutScheme(
            id=collection.id,
            title=collection.title,
            description=collection.description
        )
    )


@router.delete(
    '/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Collection successfully deleted',
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
    summary='Deletes a collection by its ID.'
)
async def delete_collection(
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> Response200Scheme:
    await CollectionManager().delete(
        collection_id=collection_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return Response200Scheme(
        message='Collection successfully deleted',
    )


@router.get(
    '/links/',
    responses={
        200: {
            'model': LinkListResponseScheme,
            'description': 'Retrieves links in collection',
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
    summary='Retrieves all links within a specified collection.'
)
async def get_links_in_collection(
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> LinkListResponseScheme:
    links = await CollectionManager().get_links(
        collection_id=collection_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return LinkListResponseScheme(
        data=[
            LinkOutScheme(
                id=link.id,
                page_title=link.page_title,
                description=link.description,
                image_url=link.image_url,
                link_type=link.link_type
            ) for link in links
        ]
    )


@router.post(
    '/link/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Link successfully added to collection',
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
    summary='Adds a link to a specified collection.'
)
async def add_link_to_collection(
        link_id: UUID = Query(...),
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> Response200Scheme:
    await CollectionManager().add_link(
        link_id=link_id,
        collection_id=collection_id,
        user_id=user_info.user_id,
        db_session=db_session
    )
    return Response200Scheme(
        message=(
            f'Link with id {link_id} successfully added '
            f'to collection with id {collection_id}'
        )
    )


@router.delete(
    '/link/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Link successfully deleted from collection',
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
    summary='Deletes a link from a specified collection.'
)
async def delete_link_to_collection(
        link_id: UUID = Query(...),
        collection_id: UUID = Query(...),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
) -> Response200Scheme:
    await CollectionManager().remove_link(
        link_id=link_id,
        collection_id=collection_id,
        user_id=user_info.user_id,
        db_session=db_session
    )

    return Response200Scheme(
        message=(
            f'Link with id {link_id} successfully deleted '
            f'from collection with id {collection_id}'
        )
    )
