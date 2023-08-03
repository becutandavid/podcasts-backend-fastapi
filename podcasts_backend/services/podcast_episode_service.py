from podcasts_backend.models.models import (
    EpisodeModel,
    EpisodeTable,
    Podcast,
    PodcastTable,
)

from ..repository.repository import Repository


class PodcastEpisodeService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    async def add_podcast(
        self,
        podcast: Podcast,
    ) -> PodcastTable:
        return await self.repository.add_podcast(podcast)

    async def add_podcasts(
        self,
        podcasts: list[Podcast],
    ) -> list[PodcastTable]:
        return await self.repository.add_many_podcasts(podcasts)

    async def add_episode(
        self,
        episode: EpisodeModel,
    ) -> EpisodeTable:
        return await self.repository.add_episode(episode)

    async def add_episodes(
        self,
        episodes: list[EpisodeModel],
    ) -> list[EpisodeTable]:
        return await self.repository.add_many_episodes(episodes)

    def list_podcasts(self) -> list[PodcastTable]:
        return self.repository.list_podcasts()

    def get_podcast(self, podcast_id: int) -> PodcastTable | None:
        try:
            return self.repository.get_podcast(podcast_id)
        except ValueError:
            return None

    def list_episodes_from_podcast(self, podcast_id: int) -> list[EpisodeTable]:
        return self.repository.list_episodes_from_podcast(podcast_id)
