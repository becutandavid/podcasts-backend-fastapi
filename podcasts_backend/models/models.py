from pydantic import BaseModel

# class Podcast(SQLModel):
#     author: str
#     categories: list[str]
#     description: str
#     explicit: bool
#     generator: str
#     imageURL: str
#     language: str
#     lastBuildDate: str
#     link: str


# class PodcastTable(Podcast, table=True):
#     id: int = Field(primary_key=True)


class EpisodeMetadata(BaseModel):
    podcast_id: int
    category: str | None
    language: str | None


class Episode(BaseModel):
    id: str
    metadata: EpisodeMetadata
    text: str


class EpisodeVector(Episode):
    embedding: list[float]


class EpisodeVectorWithScore(EpisodeVector):
    score: float


class EpisodeMetadataFilter(BaseModel):
    podcast_id: int | None
    category: str | None
    language: str | None


class Query(BaseModel):
    query: str
    filter: EpisodeMetadataFilter | None = None
    top_k: int = 20


class QueryWithEmbedding(Query):
    embedding: list[float]


class QueryResult(BaseModel):
    query: str
    results: list[EpisodeVectorWithScore]


class ResponseQueryResult(BaseModel):
    results: list[QueryResult]
