from sqlalchemy.engine import Engine
from sqlmodel import Session

from ..models.models import PodcastTable, UserTable


class FavoritePodcastsRepository:
    def __init__(self, db_session: Engine) -> None:
        self.db_session = db_session

    def add_podcast_to_favorites(self, user_id: int, podcast_id: int) -> bool:
        """add podcast to favorites, returns True if podcast added, False if podcast
        already in favorites.

        Args:
            user_id (int): id of user
            podcast_id (int): id of podcast

        Raises:
            ValueError: user not found
            ValueError: podcast not found

        Returns:
            bool: True if podcast added, False if podcast already in favorites.
        """
        with Session(self.db_session) as session:
            user = session.get(UserTable, user_id)
            podcast = session.get(PodcastTable, podcast_id)
            if user is None:
                raise ValueError("User not found")
            elif podcast is None:
                raise ValueError("Podcast not found")

            if podcast in user.favorite_podcasts:
                return False
            user.favorite_podcasts.append(podcast)
            session.add(user)
            session.commit()
            return True

    def remove_podcast_from_favorites(self, user_id: int, podcast_id: int) -> bool:
        """remove podcast from favorites, returns True if podcast removed, False if
        podcast not in favorites.

        Args:
            user_id (int): id of user
            podcast_id (int): id of podcast

        Raises:
            ValueError: user not found
            ValueError: podcast not found

        Returns:
            bool: True if podcast removed, False if podcast not in favorites.
        """
        with Session(self.db_session) as session:
            user = session.get(UserTable, user_id)
            podcast = session.get(PodcastTable, podcast_id)
            if user is None:
                raise ValueError("User not found")
            elif podcast is None:
                raise ValueError("Podcast not found")

            if podcast not in user.favorite_podcasts:
                return False
            user.favorite_podcasts.remove(podcast)
            session.add(user)
            session.commit()
            return True

    def list_favorite_podcasts_of_user(self, user_id: int) -> list[PodcastTable]:
        with Session(self.db_session) as session:
            user = session.get(UserTable, user_id)
            if user is None:
                raise ValueError("User not found")
            return user.favorite_podcasts
