from fastapi import HTTPException

from ..models.models import (
    EpisodeModel,
    EpisodeTable,
    Podcast,
    PodcastTable,
)
from ..repository.db.postgres import podcast_repository


async def add_podcast(
    podcast: Podcast,
) -> PodcastTable:
    return await podcast_repository.add_podcast(podcast)


async def add_podcasts(
    podcasts: list[Podcast],
) -> list[PodcastTable]:
    return await podcast_repository.add_many_podcasts(podcasts)


async def add_episode(
    episode: EpisodeModel,
) -> EpisodeTable:
    return await podcast_repository.add_episode(episode)


async def add_episodes(
    episodes: list[EpisodeModel],
) -> list[EpisodeTable]:
    return await podcast_repository.add_many_episodes(episodes)


def list_podcasts(limit: int, offset: int) -> list[PodcastTable]:
    try:
        podcasts = podcast_repository.list_podcasts(limit, offset)
        return podcasts
    except ValueError:
        return []


def list_podcast_ids(limit: int, offset: int) -> list[int]:
    try:
        podcast_ids = podcast_repository.list_podcast_ids(limit, offset)
        return podcast_ids
    except ValueError:
        return []


def get_podcasts_count() -> int:
    try:
        return podcast_repository.get_podcasts_count()
    except ValueError:
        return 0


def get_podcast(podcast_id: int) -> PodcastTable | None:
    try:
        return podcast_repository.get_podcast(podcast_id)
    except ValueError:
        return None


def list_episodes_from_podcast(podcast_id: int) -> list[EpisodeTable]:
    try:
        return podcast_repository.list_episodes_from_podcast(podcast_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Podcast not found")


def get_latest_update_date() -> int:
    """get latest update date, in unix time. Returns -1 if no podcasts or episodes in
    database

    Returns:
        int: latest update date, in unix time
    """
    try:
        latest_podcast = podcast_repository.get_latest_updated_podcast()
        latest_podcast_date = (
            latest_podcast.lastUpdate if latest_podcast.lastUpdate else -1
        )
    except ValueError:
        latest_podcast_date = -1
    try:
        latest_episode = podcast_repository.get_latest_episode()
        latest_episode_date = (
            latest_episode.dateCrawled if latest_episode.dateCrawled else -1
        )
    except ValueError:
        latest_episode_date = -1

    return max(latest_podcast_date, latest_episode_date)


def get_latest_podcast_id() -> int:
    """return the largest podcast id in the database

    Returns:
        int: largest podcast id in the database. Returns -1 if no podcasts in database.
    """
    try:
        return podcast_repository.get_latest_podcast().podcast_id
    except ValueError:
        return -1
