from sqlmodel import SQLModel, create_engine

from ..repository import Repository
from ..vector_database.providers.milvus import MilvusDataStore

DATABASE_URL = "postgresql://postgres:password@postgres:5432/postgres"
engine = create_engine(DATABASE_URL, echo=True)


milvus_db = MilvusDataStore()
repository = Repository(db_session=engine, vector_db_session=milvus_db)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
