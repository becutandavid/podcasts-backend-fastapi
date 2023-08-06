import os

from sqlmodel import SQLModel, create_engine

from ..favorite_podcasts import FavoritePodcastsRepository
from ..podcast_repository import Repository
from ..vector_database.providers.milvus import MilvusDataStore

DATABASE_URL = os.getenv("DATABASE_URL") or ""
assert DATABASE_URL != "", "DATABASE_URL environment variable must be set"

engine = create_engine(DATABASE_URL, echo=True)


milvus_db = MilvusDataStore()
podcast_repository = Repository(db_session=engine, vector_db_session=milvus_db)
favorite_podcasts_repository = FavoritePodcastsRepository(db_session=engine)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
