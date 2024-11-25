from datetime import datetime, timedelta, UTC
import random
from typing import List
import uuid

from database.models import (
    CollectionModel,
    LinkCollectionAssociation,
    LinkModel,
    LinkType,
    UserModel
)

from logger import logger

from settings import Database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SYNC_DATABASE_URL = Database.url.replace('+asyncpg', '')

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def create_test_data():
    try:
        session.query(LinkCollectionAssociation).delete()
        session.query(LinkModel).delete()
        session.query(CollectionModel).delete()
        session.query(UserModel).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception(f"Error during cleanup: {e}")


    users: List[UserModel] = []
    for i in range(1, 21):
        user = UserModel(
            id=uuid.uuid4(),
            email=f"user{i}@example.com",
            password_hash=f"hash{i}",
            email_verified=True,
            created_at=(
                    datetime.now(UTC).replace(tzinfo=None) - timedelta(days=i)
            ),
            updated_at=datetime.now(UTC).replace(tzinfo=None)
        )
        users.append(user)

    session.add_all(users)
    session.flush()

    all_links = []
    for user in users:
        num_links = random.randint(1, 50)
        for j in range(num_links):
            link = LinkModel(
                id=uuid.uuid4(),
                page_title=f"Test Page {j + 1} for {user.email}",
                description=f"Description for test page {j + 1}",
                link=f"https://example.com/user{user.id}/page{j + 1}",
                image_url=f"https://example.com/images/{j + 1}.jpg",
                link_type=random.choice(list(LinkType)),
                user_id=user.id,
                created_at=datetime.now(UTC).replace(tzinfo=None),
                updated_at=datetime.now(UTC).replace(tzinfo=None)
            )
            all_links.append(link)

    session.add_all(all_links)
    session.flush()

    all_collections = []
    for user in users:
        for k in range(10):
            collection = CollectionModel(
                id=uuid.uuid4(),
                title=f"Collection {k + 1} for {user.email}",
                description=f"Test collection {k + 1} description",
                user_id=user.id,
                created_at=datetime.now(UTC).replace(tzinfo=None),
                updated_at=datetime.now(UTC).replace(tzinfo=None)
            )
            all_collections.append(collection)

    session.add_all(all_collections)
    session.flush()

    associations = []
    for link in all_links:
        user_collections = [c for c in all_collections if
                            c.user_id == link.user_id]
        for collection in user_collections:
            if random.random() < 0.3:
                association = LinkCollectionAssociation(
                    id=uuid.uuid4(),
                    link_id=link.id,
                    collection_id=collection.id,
                    user_id=link.user_id
                )
                associations.append(association)

    session.add_all(associations)

    try:
        session.commit()
        logger.info("Test data successfully created!")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error creating test data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    create_test_data()
