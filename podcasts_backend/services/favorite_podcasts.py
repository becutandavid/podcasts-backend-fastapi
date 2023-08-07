import math

from fastapi import HTTPException

from ..models.models import Podcast, PodcastTable
from ..repository.db.postgres import (
    favorite_podcasts_repository,
    milvus_db,
    podcast_repository,
)
from ..schemas.schemas import (
    EpisodeModelWithScore,
    Query,
    SemanticSearchByEpisodeDescriptionResult,
    SemanticSearchByEpisodeDescriptionResults,
)
from ..schemas.users import UserOutputWithId


async def add_podcast_to_favorites(podcast_id: int, user: UserOutputWithId) -> bool:
    """add podcast to favorites, returns True if podcast added, False if podcast already
    in favorites.

    Args:
        podcast_id (int): id of podcast
        user (UserOutputWithId): user object

    Raises:
        HTTPException: user or podcast not found in databse

    Returns:
        bool: True if podcast added, false if podcast already in favorites
    """
    try:
        return favorite_podcasts_repository.add_podcast_to_favorites(
            user.id, podcast_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="User or podcast not found")


async def list_favorite_podcasts_of_user(user: UserOutputWithId) -> list[PodcastTable]:
    try:
        return favorite_podcasts_repository.list_favorite_podcasts_of_user(user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


async def delete_podcast_from_favorites(
    podcast_id: int, user: UserOutputWithId
) -> bool:
    """delete podcast from favorites, returns True if podcast deleted, False if podcast
    not in favorites.

    Args:
        podcast_id (int): podcast id
        user (UserOutputWithId): user object

    Returns:
        bool: True if podcast deleted, False if podcast not in favorites
    """
    try:
        return favorite_podcasts_repository.remove_podcast_from_favorites(
            user.id, podcast_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="User or podcast not found")


async def semantic_search_by_episode_description(
    query: Query,
) -> SemanticSearchByEpisodeDescriptionResults:
    """semantic search by episode description, returns a list of podcasts with their
    relevant episodes. Sorted by best score.

    Args:
        query (Query): search query, with optional filters

    Raises:
        HTTPException: http 500, if query failed.

    Returns:
        SemanticSearchByEpisodeDescriptionResults: list of podcasts with relevant
        episodes, sorted by best scores.
    """
    try:
        query_result = (await milvus_db.query([query]))[0]

        podcast_results: dict[int, list[EpisodeModelWithScore]] = {}
        best_scores_by_podcast: dict[int, float] = {}
        podcast_model_by_id: dict[int, Podcast] = {}
        for episode in query_result.results:
            # get podcast and episode from db
            podcast_table = podcast_repository.get_podcast_from_episode_id(episode.id)
            episode_table = podcast_repository.get_episode(episode.id)
            # convert tables to models for output
            podcast_model = Podcast(**podcast_table.__dict__)
            episode_model = EpisodeModelWithScore(
                **episode_table.dict(), score=episode.score
            )
            # result dictionaries operations
            if podcast_table.podcast_id not in podcast_results:
                podcast_results[podcast_table.podcast_id] = []
                best_scores_by_podcast[podcast_table.podcast_id] = math.inf
                podcast_model_by_id[podcast_model.podcast_id] = podcast_model

            podcast_results[podcast_table.podcast_id].append(episode_model)
            best_scores_by_podcast[podcast_table.podcast_id] = min(
                best_scores_by_podcast[podcast_table.podcast_id], episode.score
            )

        # sort groups by best score
        podcast_results_tuples = sorted(
            podcast_results.items(),
            key=lambda x: best_scores_by_podcast[x[0]],
        )
        # sort episodes by score
        formatted_podcast_result_tuples = [
            (podcast_model_by_id[podcast_id], sorted(episodes, key=lambda x: x.score))
            for (podcast_id, episodes) in podcast_results_tuples
        ]

        # format output
        output = []
        for podcast, episodes in formatted_podcast_result_tuples:
            output_element = SemanticSearchByEpisodeDescriptionResult(
                podcast=podcast,
                relevant_episodes=episodes,
            )

            output.append(output_element)

        return SemanticSearchByEpisodeDescriptionResults(results=output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
