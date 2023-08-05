from podcasts_backend.models.models import (
    EpisodeModel,
    EpisodeTable,
    Podcast,
    PodcastTable,
)

from ..repository.db.postgres import repository


async def add_podcast(
    podcast: Podcast,
) -> PodcastTable:
    return await repository.add_podcast(podcast)


async def add_podcasts(
    podcasts: list[Podcast],
) -> list[PodcastTable]:
    return await repository.add_many_podcasts(podcasts)


async def add_episode(
    episode: EpisodeModel,
) -> EpisodeTable:
    return await repository.add_episode(episode)


async def add_episodes(
    episodes: list[EpisodeModel],
) -> list[EpisodeTable]:
    return await repository.add_many_episodes(episodes)


def list_podcasts() -> list[PodcastTable]:
    return repository.list_podcasts()


def get_podcast(podcast_id: int) -> PodcastTable | None:
    try:
        return repository.get_podcast(podcast_id)
    except ValueError:
        return None


def list_episodes_from_podcast(podcast_id: int) -> list[EpisodeTable]:
    return repository.list_episodes_from_podcast(podcast_id)
