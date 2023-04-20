from abc import ABC, abstractmethod

from ..models.models import (
    Episode,
    EpisodeVector,
    Query,
    QueryResult,
    QueryWithEmbedding,
)
from ..services.embeddings import get_embeddings


class DataStore(ABC):
    async def upsert(
        self, episodes: list[Episode], delete_all: bool = False
    ) -> list[str]:
        """
        Takes in a list of episodes and inserts them into the database.
        First deletes all the existing vectors with the episode id (if necessary,
        depends on the vector db), then inserts the new ones.
        Return a list of episode ids.
        """
        # Delete any existing vectors for documents with the input document ids
        await self.delete(
            ids=[episode.id for episode in episodes if episode.id],
            delete_all=delete_all,
        )

        # calculate embeddings for the episodes
        episodes_embeddings = [
            EpisodeVector(**episode.dict(), embedding=get_embeddings([episode.text])[0])
            for episode in episodes
        ]

        return await self._upsert(episodes_embeddings)

    @abstractmethod
    async def _upsert(self, episodes: list[EpisodeVector]) -> list[str]:
        """
        Takes in a list of episodes and inserts them into the database.
        Return a list of episode ids.
        """

        raise NotImplementedError

    async def query(self, queries: list[Query]) -> list[QueryResult]:
        """
        Takes in a list of queries and filters and returns a list of query results with
        matching episodes and scores.
        """
        # get a list of of just the queries from the Query list
        query_texts = [query.query for query in queries]
        query_embeddings = get_embeddings(query_texts)
        # hydrate the queries with embeddings
        queries_with_embeddings = [
            QueryWithEmbedding(**query.dict(), embedding=embedding)
            for query, embedding in zip(queries, query_embeddings)
        ]
        return await self._query(queries_with_embeddings)

    @abstractmethod
    async def _query(self, queries: list[QueryWithEmbedding]) -> list[QueryResult]:
        """
        Takes in a list of queries with embeddings and filters and returns a list of
        query results with matching episodes and scores.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        ids: list[str] | None = None,
        delete_all: bool | None = None,
    ) -> bool:
        """
        Removes vectors by ids, or everything in the datastore.
        Multiple parameters can be used at once.
        Returns whether the operation was successful.
        """
        raise NotImplementedError
