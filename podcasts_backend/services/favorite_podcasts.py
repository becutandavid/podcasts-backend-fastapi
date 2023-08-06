from fastapi import HTTPException

from ..models.models import PodcastTable
from ..repository.db.postgres import favorite_podcasts_repository
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
