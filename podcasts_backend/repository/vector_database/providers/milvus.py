import os
from uuid import uuid4

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusException,
    connections,
    utility,
)

from podcasts_backend.schemas.schemas import (
    EpisodeMetadata,
    EpisodeMetadataFilter,
    EpisodeVector,
    EpisodeVectorWithScore,
    QueryResult,
    QueryWithEmbedding,
)

from ..datastore import DataStore

MILVUS_COLLECTION = os.environ.get("MILVUS_COLLECTION") or "c" + uuid4().hex
MILVUS_HOST = os.environ.get("MILVUS_HOST") or "localhost"
MILVUS_PORT = os.environ.get("MILVUS_PORT") or 19530
MILVUS_USER = os.environ.get("MILVUS_USER")
MILVUS_PASSWORD = os.environ.get("MILVUS_PASSWORD")
MILVUS_USE_SECURITY = False if MILVUS_PASSWORD is None else True

UPSERT_BATCH_SIZE = 100
OUTPUT_DIM = 768
TOP_K = 20

SCHEMA = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, max_length=1000),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=OUTPUT_DIM),
    FieldSchema(name="podcast_id", dtype=DataType.INT64),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=100),
]


class MilvusDataStore(DataStore):
    def __init__(
        self,
        override: bool = False,
        index_params: dict | None = None,  # type: ignore
        search_params: dict | None = None,  # type: ignore
    ) -> None:
        # Set the index_params to passed in or the default
        self.index_params = index_params

        # The default search params
        self.default_search_params = {
            "IVF_FLAT": {"metric_type": "L2", "params": {"nprobe": 10}},
            "IVF_SQ8": {"metric_type": "L2", "params": {"nprobe": 10}},
            "IVF_PQ": {"metric_type": "L2", "params": {"nprobe": 10}},
            "HNSW": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_FLAT": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_SQ": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_PQ": {"metric_type": "L2", "params": {"ef": 10}},
            "IVF_HNSW": {"metric_type": "L2", "params": {"nprobe": 10, "ef": 10}},
            "ANNOY": {"metric_type": "L2", "params": {"search_k": 10}},
            "AUTOINDEX": {"metric_type": "L2", "params": {}},
        }

        try:
            i = [
                connections.get_connection_addr(x[0])
                for x in connections.list_connections()
            ].index({"host": MILVUS_HOST, "port": MILVUS_PORT})
            self.alias = connections.list_connections()[i][0]
        except ValueError:
            self.alias = uuid4().hex
            connections.connect(
                self.alias,
                user=MILVUS_USER,
                password=MILVUS_PASSWORD,
                host=MILVUS_HOST,
                port=MILVUS_PORT,
                secure=MILVUS_USE_SECURITY,
            )

        self._create_collection(override)

        index_params = self.index_params or {}

        # Use in the passed in search params or the default for the specified index
        self.search_params = (
            search_params or self.default_search_params[index_params["index_type"]]
        )

    def _create_collection(self, create_new: bool) -> None:
        """Create a collection based on environment and passed in variables.
        Args:
            create_new (bool): Whether to overwrite if collection already exists.
        """

        # If the collection exists and create_new is True, drop the existing collection
        if utility.has_collection(MILVUS_COLLECTION, using=self.alias) and create_new:
            utility.drop_collection(MILVUS_COLLECTION, using=self.alias)

        # Check if the collection doesn't exist
        if utility.has_collection(MILVUS_COLLECTION, using=self.alias) is False:
            # If it doesn't exist use the field params from init to create a new schema
            schema = CollectionSchema(SCHEMA)
            # Use the schema to create a new collection
            self.col = Collection(
                MILVUS_COLLECTION,
                schema=schema,
                consistency_level="Strong",
                using=self.alias,
            )
        else:
            # If the collection exists, point to it
            self.col = Collection(
                MILVUS_COLLECTION, consistency_level="Strong", using=self.alias
            )

        # If no index on the collection, create one
        if len(self.col.indexes) == 0:
            if self.index_params is not None:
                # Create an index on the 'embedding' field with the index params found
                # in init
                self.col.create_index("embedding", index_params=self.index_params)
            else:
                # If no index param supplied, to first create an HNSW index for Milvus
                try:
                    print("Attempting creation of Milvus default index")
                    i_p = {
                        "metric_type": "L2",
                        "index_type": "HNSW",
                        "params": {"M": 8, "efConstruction": 64},
                    }

                    self.col.create_index("embedding", index_params=i_p)
                    self.index_params = i_p
                    print("Creation of Milvus default index successful")
                # If create fails, most likely due to being Zilliz Cloud instance,
                # try to create an AutoIndex
                except MilvusException:
                    print("Attempting creation of Zilliz Cloud default index")
                    i_p = {"metric_type": "L2", "index_type": "AUTOINDEX", "params": {}}
                    self.col.create_index("embedding", index_params=i_p)
                    self.index_params = i_p
                    print("Creation of Zilliz Cloud default index successful")
        # If an index already exists, grab its params
        else:
            self.index_params = self.col.indexes[0].to_dict()["index_param"]

        self.col.load()

    def _get_values_insert(
        self, episode: EpisodeVector
    ) -> list[str | int | None | list[float]]:
        """Get the values to insert into the collection.
        Args:
            episode (EpisodeVector): The episode to insert.
        Returns:
            list: The values to insert.
        """
        return [
            episode.id,
            episode.text,
            episode.embedding,
            episode.metadata.podcast_id,
            episode.metadata.category,
            episode.metadata.language,
        ]

    async def _upsert(self, episodes: list[EpisodeVector]) -> list[int]:
        """Upsert a batch of data into the collection.
        Args:
            data (list[dict]): The data to upsert.
        """

        episode_ids = []
        insert_data = [[] for i in range(len(SCHEMA))]  # type: ignore

        for episode in episodes:
            episode_ids.append(episode.id)
            insert_row = self._get_values_insert(episode)
            for i in range(len(insert_row)):
                insert_data[i].append(insert_row[i])

        # Slice up our insert data into batches
        batches = [
            insert_data[i : i + UPSERT_BATCH_SIZE]
            for i in range(0, len(insert_data), UPSERT_BATCH_SIZE)
        ]
        # Attempt to insert each batch into our collection
        for batch in batches:
            if len(batch[0]) != 0:
                try:
                    print(f"Upserting batch of size {len(batch[0])}")
                    self.col.insert(batch)
                    print("Upserted batch successfully")
                except Exception as e:
                    print(f"Error upserting batch: {e}")
                    raise e

        # This setting performs flushes after insert. Small insert == bad to use
        # self.col.flush()

        return episode_ids

    async def _single_query(
        self, query: QueryWithEmbedding
    ) -> list[EpisodeVectorWithScore]:
        """Query the QueryWithEmbedding in Milvus.
        Search the embedding and its filter in the collection.

        Args:
            query (QueryWithEmbedding): The query to query for.

        Returns:
            list[QueryResult]: A list of the results of the query.
        """
        filter = None
        if query.filter is not None:
            filter = self._get_filter(query.filter)

        top_k = TOP_K
        if query.top_k is not None:
            top_k = query.top_k

        results = self.col.search(
            [query.embedding],
            "embedding",
            self.search_params,
            top_k,
            filter,
            output_fields=["text", "podcast_id", "category", "language"],
        )

        query_results: list[EpisodeVectorWithScore] = []
        for result in results[0]:
            score = result.score
            episode_with_score = EpisodeVectorWithScore(
                metadata=EpisodeMetadata(
                    podcast_id=result.entity.get("podcast_id"),
                    category=result.entity.get("category"),
                    language=result.entity.get("language"),
                ),
                text=result.entity.get("text"),
                score=score,
                embedding=query.embedding,
                id=result.id,
            )

            query_results.append(episode_with_score)

        return query_results

    async def _query(self, queries: list[QueryWithEmbedding]) -> list[QueryResult]:
        """Query the list of QueryWithEmbeddings in Milvus.

        Args:
            queries (list[QueryWithEmbedding]): list of queries.

        Returns:
            list[QueryResult]: A list of the results of the queries.
        """
        results: list[QueryResult] = [
            QueryResult(query=query.query, results=await self._single_query(query))
            for query in queries
        ]

        return results

    async def delete(
        self,
        ids: list[str] | None = None,
        delete_all: bool | None = None,
    ) -> bool:
        """
        Removes vectors by ids, or everything in the datastore.
        Returns whether the operation was successful.
        """
        if delete_all:
            # Release the collection from memory
            self.col.release()
            # Drop the collection
            self.col.drop()
            # Recreate the new collection
            self._create_collection(True)
            return True

        delete_count = 0
        chunk_size = 100
        # Check if empty ids
        if ids is not None:
            while len(ids) > 0:
                ids_chunk = ids[:chunk_size]
                ids = ids[chunk_size:]
                # Add quotation marks around the string format id
                ids_chunk = [f"{str(id)}" for id in ids_chunk]
                # delete the ids
                res = self.col.delete(f"pk in [{','.join(ids_chunk)}]")
                delete_count += int(res.delete_count)

        return True

    def _get_filter(self, filter: EpisodeMetadataFilter) -> str:
        """Get the filter string for the query.
        Args:
            filter (QueryFilter): The filter to use.
        Returns:
            str: The filter string.
        """
        filter_string = []
        if filter.podcast_id is not None:
            filter_string.append(f'(podcast_id == "{filter.podcast_id}")')
        if filter.category is not None:
            filter_string.append(f'(category == "{filter.category}")')
        if filter.language is not None:
            filter_string.append(f'(language == "{filter.language}")')
        return " and ".join(filter_string)
