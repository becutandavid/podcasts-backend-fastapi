from datetime import datetime

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel


class Podcast(SQLModel):
    podcast_id: int
    title: str
    author: str | None
    categories: str | None
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


class FavoritePodcastLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="usertable.id", primary_key=True)
    podcast_id: int = Field(foreign_key="podcasttable.podcast_id", primary_key=True)


class PodcastTable(Podcast, table=True):
    podcast_id: int = Field(primary_key=True)
    episodes: list["EpisodeTable"] = Relationship(back_populates="podcast")
    user_favorites: list["UserTable"] = Relationship(
        back_populates="favorite_podcasts", link_model=FavoritePodcastLink
    )


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


class UserTable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column("username", VARCHAR, unique=True, index=True)
    )
    email: str
    password_hash: str = ""

    favorite_podcasts: list[PodcastTable] = Relationship(
        back_populates="user_favorites",
        link_model=FavoritePodcastLink,
    )
