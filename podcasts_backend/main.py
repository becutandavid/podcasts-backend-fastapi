from fastapi import FastAPI

from .repository.db.postgres import init_db

# from .repository.db.postgres import init_db, podcast_repository
# from .repository.mock_data_upload import upload_data
from .routers import auth, favorite_podcasts, podcasts

app = FastAPI()

# repository = Repository(db_session=engine, vector_db_session=milvus_db)

app.include_router(podcasts.router)
app.include_router(auth.router)
app.include_router(favorite_podcasts.router)


@app.on_event("startup")
async def startup_event() -> None:
    init_db()
