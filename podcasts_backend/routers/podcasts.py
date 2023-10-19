from fastapi import APIRouter

from ..models.models import EpisodeModel, EpisodeTable, Podcast, PodcastTable
from ..services import podcast_episode_service

router = APIRouter()


@router.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/podcasts", response_model=list[PodcastTable])
async def get_podcasts() -> list[PodcastTable]:
    return podcast_episode_service.list_podcasts()


@router.get("/episodes/{podcast_id}", response_model=list[EpisodeTable])
async def get_episodes(podcast_id: int) -> list[EpisodeTable]:
    return podcast_episode_service.list_episodes_from_podcast(podcast_id)


@router.post("/podcasts/add_episodes", response_model=list[EpisodeTable])
async def add_episodes(episodes: list[EpisodeModel]) -> list[EpisodeTable]:
    return podcast_episode_service.add_episodes(episodes)


@router.post("/podcasts/add_podcast", response_model=PodcastTable)
async def add_podcast(podcast: Podcast) -> PodcastTable:
    return await podcast_episode_service.add_podcast(podcast)


@router.post("/podcasts/add_podcasts", response_model=list[PodcastTable])
async def add_podcasts(podcasts: list[Podcast]) -> list[PodcastTable]:
    return podcast_episode_service.add_podcasts(podcasts)
