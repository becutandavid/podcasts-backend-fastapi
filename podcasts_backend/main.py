import fastapi

from podcasts_backend.repository.repository import Repository

from .repository.db.postgres import engine, init_db
from .repository.mock_data_upload import upload_data
from .repository.vector_database.providers.milvus import MilvusDataStore
from .schemas.schemas import Query, ResponseQueryResult

app = fastapi.FastAPI()
milvus_db = MilvusDataStore()

repository = Repository(db_session=engine, vector_db_session=milvus_db)
# app.include_router(podcasts.router)


@app.on_event("startup")
async def startup_event() -> None:
    print("starting up...")
    print("initialize postgres")
    init_db()
    print("uploading data to postgres")
    print(await upload_data(repository))


@app.post("/query/", response_model=ResponseQueryResult)
async def query_milvus(query: Query) -> ResponseQueryResult:
    results = await milvus_db.query([query])
    return ResponseQueryResult(results=results)
