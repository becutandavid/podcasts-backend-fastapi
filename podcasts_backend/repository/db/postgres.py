import os

from sqlmodel import SQLModel, create_engine

from ..podcast_repository import Repository
from ..vector_database.providers.milvus import MilvusDataStore

DATABASE_URL = os.getenv("DATABASE_URL") or ""
assert DATABASE_URL != "", "DATABASE_URL environment variable must be set"

engine = create_engine(DATABASE_URL, echo=True)


milvus_db = MilvusDataStore()
repository = Repository(db_session=engine, vector_db_session=milvus_db)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
