from sqlalchemy import func
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select

from podcasts_backend.models.models import (
    EpisodeModel,
    EpisodeTable,
    Podcast,
    PodcastTable,
)
from podcasts_backend.repository.vector_database.datastore import DataStore
from podcasts_backend.schemas.schemas import Episode, EpisodeMetadata


class Repository:
    def __init__(self, db_session: Engine, vector_db_session: DataStore) -> None:
        self.db_session = db_session
        self.vector_db_session = vector_db_session

    async def add_podcast(self, obj: Podcast) -> PodcastTable:
        with Session(self.db_session) as session:
            podcast = PodcastTable.from_orm(obj, update={"episodes": []})
            session.add(podcast)
            session.commit()
            session.refresh(podcast)

            return podcast

    async def add_many_podcasts(self, objs: list[Podcast]) -> list[PodcastTable]:
        with Session(self.db_session) as session:
            already_in_db = session.exec(select(PodcastTable.podcast_id)).all()
            podcasts = [
                PodcastTable.from_orm(
                    obj, update={"episodes": [], "user_favorites": []}
                )
                for obj in objs
                if obj.podcast_id not in already_in_db
            ]
            session.add_all(podcasts)
            session.commit()
            for podcast in podcasts:
                session.refresh(podcast)
            return podcasts

    async def add_episode(self, obj: EpisodeModel) -> EpisodeTable:
        """adds episode to database and vector database, Episode ValueError if podcast
        not in database

        Args:
            obj (EpisodeModel): EpisodeModel to add

        Raises:
            ValueError: if podcast not in database

        Returns:
            EpisodeTable: Added episode.
        """
        with Session(self.db_session) as session:
            podcast = session.get(PodcastTable, obj.podcast_id)
            if not podcast:
                raise ValueError("Podcast not found")
            episode = EpisodeTable.from_orm(obj, update={"podcast": podcast})
            session.add(episode)
            session.commit()
            session.refresh(episode)

            if episode.title is None and episode.description is None:
                embedding_text = f"{podcast.title} {podcast.description}"
            embedding_text = f"{episode.title} {episode.description}"
            episode_vector = Episode(
                id=episode.episode_id,  # type: ignore
                metadata=EpisodeMetadata(
                    podcast_id=episode.podcast_id,
                    category=podcast.category1,
                    language=podcast.language,
                ),
                text=embedding_text,
            )
            await self.vector_db_session.upsert([episode_vector])
            return episode

    async def add_many_episodes(self, objs: list[EpisodeModel]) -> list[EpisodeTable]:
        """add many episodes to database and vector database, raise ValueError if
        not all episodes are added.

        Args:
            objs (list[EpisodeModel]): lists of episodes to add

        Raises:
            ValueError: if podcast not in database
            ValueError: if failed to add all episodes

        Returns:
            list[EpisodeTable]: list of added episodes
        """
        with Session(self.db_session) as session:
            episodes = []
            for obj in objs:
                podcast = session.exec(
                    select(PodcastTable).where(
                        col(PodcastTable.podcast_id) == obj.podcast_id
                    )
                ).first()
                if not podcast:
                    raise ValueError("Podcast not found")
                episode = EpisodeTable.from_orm(
                    obj,
                    update={"podcast": podcast, "podcast_id": podcast.podcast_id},
                )
                episodes.append(episode)

            session.add_all(episodes)
            session.commit()

            episode_vectors = []
            for episode in episodes:
                session.refresh(episode)
                podcast = session.get(PodcastTable, episode.podcast_id)
                episode_vector = Episode(
                    id=episode.episode_id,  # type: ignore
                    metadata=EpisodeMetadata(
                        podcast_id=episode.podcast_id,
                        category=podcast.category1,  # type: ignore
                        language=podcast.language,  # type: ignore
                    ),
                    text=episode.title,
                )
                episode_vectors.append(episode_vector)

            upserts = await self.vector_db_session.upsert(episode_vectors)
            if len(upserts) != len(episode_vectors) and len(episode_vectors) != len(
                episodes
            ):
                raise ValueError("Failed to add all episodes")
        return episodes

    def list_podcasts(self, limit: int, offset: int) -> list[PodcastTable]:
        with Session(self.db_session) as session:
            podcasts = session.exec(
                select(PodcastTable).offset(offset).limit(limit)
            ).all()
            return podcasts

    def list_podcast_ids(self, limit: int, offset: int) -> list[int]:
        with Session(self.db_session) as session:
            podcast_ids = session.exec(
                select(PodcastTable.podcast_id).offset(offset).limit(limit)
            ).all()
            return podcast_ids

    def get_podcasts_count(self) -> int:
        with Session(self.db_session) as session:
            count = session.exec(select(func.count(PodcastTable.podcast_id))).one()  # type: ignore
            return count

    def list_episodes_from_podcast(self, podcast_id: int) -> list[EpisodeTable]:
        with Session(self.db_session) as session:
            podcast = session.get(PodcastTable, podcast_id)
            if podcast is not None:
                return podcast.episodes
            else:
                raise ValueError("Podcast not found")

    def get_podcast(self, podcast_id: int) -> PodcastTable:
        with Session(self.db_session) as session:
            podcast = session.get(PodcastTable, podcast_id)
            if podcast is None:
                raise ValueError("Podcast not found")
            return podcast

    def get_episode(self, episode_id: int) -> EpisodeTable:
        with Session(self.db_session) as session:
            episode = session.get(EpisodeTable, episode_id)
            if episode is None:
                raise ValueError("Episode not found")
            return episode

    def get_podcast_from_episode_id(self, episode_id: int) -> PodcastTable:
        with Session(self.db_session) as session:
            episode = session.get(EpisodeTable, episode_id)
            if episode is None:
                raise ValueError("Episode not found")
            return episode.podcast

    def get_latest_updated_podcast(self) -> PodcastTable:
        with Session(self.db_session) as session:
            latest_podcast = session.exec(
                select(PodcastTable).order_by(PodcastTable.lastUpdate)
            ).first()
            if latest_podcast is None:
                raise ValueError("No podcasts in database")
            return latest_podcast

    def get_latest_episode(self) -> EpisodeTable:
        with Session(self.db_session) as session:
            latest_episode = session.exec(
                select(EpisodeTable).order_by(EpisodeTable.dateCrawled)
            ).first()

            if latest_episode is None:
                raise ValueError("No episodes in database")
            return latest_episode

    def get_latest_podcast(self) -> PodcastTable:
        with Session(self.db_session) as session:
            latest_podcast = session.exec(
                select(PodcastTable).order_by(col(PodcastTable.podcast_id).desc())
            ).first()
            if latest_podcast is None:
                raise ValueError("No podcasts in database")
            return latest_podcast
