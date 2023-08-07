from pydantic import BaseModel

from podcasts_backend.models.models import EpisodeModel, Podcast


class EpisodeMetadata(BaseModel):
    podcast_id: int
    category: str | None
    language: str | None


# milvus queries
class Episode(BaseModel):
    id: int
    metadata: EpisodeMetadata
    text: str


class EpisodeVector(Episode):
    embedding: list[float]


class EpisodeVectorWithScore(EpisodeVector):
    score: float


class EpisodeModelWithScore(EpisodeModel):
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


class SemanticSearchByEpisodeDescriptionResult(BaseModel):
    podcast: Podcast
    relevant_episodes: list[EpisodeModelWithScore]


class SemanticSearchByEpisodeDescriptionResults(BaseModel):
    results: list[SemanticSearchByEpisodeDescriptionResult]
