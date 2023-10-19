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


def list_podcasts() -> list[PodcastTable]:
    try:
        podcasts = podcast_repository.list_podcasts()
        return podcasts
    except ValueError:
        raise HTTPException(status_code=404, detail="No podcasts in database")


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
    """get latest update date, in unix time

    Returns:
        int: latest update date, in unix time
    """
    latest_podcast = podcast_repository.get_latest_podcast()
    latest_episode = podcast_repository.get_latest_episode()

    if latest_podcast > latest_episode:
        return latest_podcast
    return latest_episode
