from sqlalchemy import BigInteger
from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel


class Podcast(SQLModel):
    podcast_id: int
    url: str | None = None
    title: str | None = None
    lastUpdate: int | None = None
    link: str | None = None
    lastHttpStatus: int | None = None
    dead: int | None = None
    contentType: str | None = None
    itunesId: int | None = None
    originalUrl: str | None = None
    itunesAuthor: str | None = None
    itunesOwnerName: str | None = None
    explicit: int | None = None
    imageUrl: str | None = None
    itunesType: str | None = None
    generator: str | None = None
    newestItemPubDate: int | None = None
    language: str | None = None
    oldestItemPubDate: int | None = None
    episodeCount: int | None = None
    popularityScore: int | None = None
    priority: int | None = None
    createdOn: int | None = None
    updateFrequency: int | None = None
    chash: str | None = None
    host: str | None = None
    newestEnclosureUrl: str | None = None
    podcastGuid: str | None = None
    description: str | None = None
    category1: str | None = None
    category2: str | None = None
    category3: str | None = None
    category4: str | None = None
    category5: str | None = None
    category6: str | None = None
    category7: str | None = None
    category8: str | None = None
    category9: str | None = None
    category10: str | None = None
    newestEnclosureDuration: int | None = None


class Podcasts(SQLModel):
    podcasts: list[Podcast]


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
    episode_id: int
    podcast_id: int
    title: str | None = None
    link: str | None = None
    description: str | None = None
    guid: str | None = None
    datePublished: int | None = None
    datePublishedPretty: str | None = None
    dateCrawled: int | None = None
    enclosureUrl: str | None = None
    enclosureType: str | None = None
    enclosureLength: int | None = None
    duration: int | None = None
    explicit: int | None = None
    episode: int | None = None
    episodeType: str | None = None
    season: int | None = None
    image: str | None = None
    feedItunesId: int | None = None
    feedImage: str | None = None
    feedId: int | None = None
    feedLanguage: str | None = None
    feedDead: int | None = None
    feedDuplicateOf: str | None = None
    chaptersUrl: str | None = None
    transcriptUrl: str | None = None


class Episodes(SQLModel):
    episodes: list[EpisodeModel]


class EpisodeTable(EpisodeModel, table=True):
    episode_id: int = Field(sa_column=Column(BigInteger(), primary_key=True))
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
