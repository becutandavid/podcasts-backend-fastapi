from fastapi import APIRouter

from ..models.models import Episodes, EpisodeTable, Podcast, Podcasts, PodcastTable
from ..services import podcast_episode_service

router = APIRouter()


@router.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/podcasts", response_model=list[PodcastTable])
async def get_podcasts(limit: int = 200, offset: int = 0) -> list[PodcastTable]:
    return podcast_episode_service.list_podcasts(limit, offset)


@router.get("/podcasts/ids", response_model=list[int])
async def get_podcast_ids(limit: int = 200, offset: int = 0) -> list[int]:
    return podcast_episode_service.list_podcast_ids(limit, offset)


@router.get("/podcasts/count", response_model=int)
async def get_podcasts_count() -> int:
    return podcast_episode_service.get_podcasts_count()


@router.get("/episodes/{podcast_id}", response_model=list[EpisodeTable])
async def get_episodes(podcast_id: int) -> list[EpisodeTable]:
    return podcast_episode_service.list_episodes_from_podcast(podcast_id)


@router.post("/podcasts/add_episodes", response_model=list[EpisodeTable])
async def add_episodes(episodes: Episodes) -> list[EpisodeTable]:
    return await podcast_episode_service.add_episodes(episodes.episodes)


@router.post("/podcasts/add_podcast", response_model=PodcastTable)
async def add_podcast(podcast: Podcast) -> PodcastTable:
    return await podcast_episode_service.add_podcast(podcast)


@router.post("/podcasts/add_podcasts", response_model=list[PodcastTable])
async def add_podcasts(podcasts: Podcasts) -> list[PodcastTable]:
    return await podcast_episode_service.add_podcasts(podcasts.podcasts)


@router.get("/podcasts/latest_update_time", response_model=int)
async def get_latest_update_date() -> int:
    """
    get latest update date, in unix time. Returns -1 if no podcasts or episodes in
    database
    """
    return podcast_episode_service.get_latest_update_date()


@router.get("/podcasts/latest_podcast_id", response_model=int)
async def get_latest_podcast_id() -> int:
    """
    get latest podcast id. Returns -1 if no podcasts or episodes in
    database
    """
    return podcast_episode_service.get_latest_podcast_id()
