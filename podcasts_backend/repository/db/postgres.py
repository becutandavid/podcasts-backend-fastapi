from sqlmodel import SQLModel, create_engine

DATABASE_URL = "postgresql://postgres:password@postgres:5432/postgres"
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
