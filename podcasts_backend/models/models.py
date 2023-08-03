from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Podcast(SQLModel):
    podcast_id: int
    title: str
    author: str | None
    categories: list[str] = []
    description: str | None
    explicit: bool | None
    generator: str | None
    imageURL: str | None
    language: str | None
    lastBuildDate: datetime | None
    link: str | None
    summary: str | None
    owner_name: str | None
    owner_email: str | None

    # @property
    # def num_episodes(self) -> int:
    #     return len(Podcast.episodes)


class PodcastTable(Podcast, table=True):
    podcast_id: int = Field(primary_key=True)
    episodes: list["EpisodeTable"] = Relationship(back_populates="podcast")


class EpisodeModel(SQLModel):
    description: str | None
    duration: int | None
    enclosure: str
    guid: str | None
    keywords: str | None
    link: str | None
    ner: list[str] | None
    podcast_id: int
    pubDate: datetime | None
    summary: str | None
    title: str


class EpisodeTable(EpisodeModel, table=True):
    episode_id: int | None = Field(primary_key=True, default=None)
    podcast_id: int = Field(foreign_key="podcasttable.podcast_id")
    podcast: PodcastTable = Relationship(back_populates="episodes")
