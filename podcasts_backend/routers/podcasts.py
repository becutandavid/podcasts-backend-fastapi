from fastapi import APIRouter


from ..models.models import EpisodeTable, PodcastTable
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
