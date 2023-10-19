from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel


class Podcast(SQLModel):
    podcast_id: int
    url: str
    title: str
    lastUpdate: int
    link: str
    lastHttpStatus: int
    dead: int
    contentType: str
    itunesId: int
    originalUrl: str
    itunesAuthor: str
    itunesOwnerName: str
    explicit: int
    imageUrl: str
    itunesType: str
    generator: str
    newestItemPubdate: int
    language: str
    oldestItemPubdate: int
    episodeCount: int
    popularityScore: int
    priority: int
    createdOn: int
    updateFrequency: int
    chash: str
    host: str
    newestEnclosureUrl: str
    podcastGuid: str
    description: str
    category1: str
    category2: str
    category3: str
    category4: str
    category5: str
    category6: str
    category7: str
    category8: str
    category9: str
    category10: str
    newestEnclosureDuration: int


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
    title: str
    link: str
    description: str
    guid: str
    datePublished: int
    datePublishedPretty: str
    dateCrawled: int
    enclosureUrl: str
    enclosureType: str
    enclosureLength: int
    duration: int
    explicit: int
    episode: str
    episodeType: str
    season: int
    image: str
    feedItunesId: int
    feedImage: str
    feedId: int
    feedLanguage: str
    feedDead: int
    feedDuplicateOf: str
    chaptersUrl: str
    transcriptUrl: str


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
