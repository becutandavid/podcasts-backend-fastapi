from fastapi import APIRouter, Depends

from ..models.models import PodcastTable
from ..schemas.users import UserOutputWithId
from ..services import favorite_podcasts as favorite_podcasts_service
from ..services.auth import get_current_user

router = APIRouter()


@router.post("/add_podcast_to_favorites/", response_model=list[PodcastTable])
async def add_podcast_to_favorites(
    podcast_id: int, user: UserOutputWithId = Depends(get_current_user)
) -> list[PodcastTable]:
    print(podcast_id, user)
    await favorite_podcasts_service.add_podcast_to_favorites(podcast_id, user)
    return await favorite_podcasts_service.list_favorite_podcasts_of_user(user)


@router.get("/favorite_podcasts/", response_model=list[PodcastTable])
async def list_favorite_pdocasts(
    user: UserOutputWithId = Depends(get_current_user),
) -> list[PodcastTable]:
    return await favorite_podcasts_service.list_favorite_podcasts_of_user(user)
