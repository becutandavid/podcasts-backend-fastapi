import fastapi

from .models.models import Query, ResponseQueryResult
from .repository.database import upload_to_milvus
from .repository.providers.milvus import MilvusDataStore

app = fastapi.FastAPI()
milvus = MilvusDataStore()
# app.include_router(podcasts.router)


@app.on_event("startup")
def startup_event() -> None:
    print("starting up...")
    print(upload_to_milvus(milvus))


@app.post("/query/", response_model=ResponseQueryResult)
async def query_milvus(query: Query) -> ResponseQueryResult:
    results = await milvus.query([query])
    return ResponseQueryResult(results=results)
