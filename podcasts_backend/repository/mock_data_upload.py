import numpy as np
import pandas as pd

from podcasts_backend.repository.repository import Repository

from ..models.models import EpisodeModel, Podcast


async def upload_data(repository: Repository) -> bool:
    podcasts = pd.read_pickle("/podcasts_data/transfer/podcasts_short.pkl")
    episodes = pd.read_pickle("/podcasts_data/transfer/episodes_short.pkl")

    podcasts["lastBuildDate"].replace({pd.NaT: None}, inplace=True)
    episodes["pubDate"].replace({pd.NaT: None}, inplace=True)
    episodes.replace({np.nan: None, "": None}, inplace=True)

    podcasts = podcasts.apply(
        lambda x: Podcast(
            podcast_id=x.name,
            title=x["title"],
            author=x["author"],
            categories=",".join(x["categories"]),
            description=x["description"],
            explicit=x["explicit"],
            generator=str(x.get("generator", "")),
            imageURL=x["imageURL"],
            language=x["language"],
            lastBuildDate=x["lastBuildDate"],
            link=x["link"],
            summary=x["summary"],
            owner_email=x["owner_email"],
            owner_name=x["owner_name"],
        ),
        axis=1,
    ).to_list()

    episodes_list = []
    for _, row in episodes.iterrows():
        episode = EpisodeModel(
            description=row.description,
            duration=row.duration,
            enclosure=str(row.enclosure),
            guid=row.guid,
            keywords=row.keywords,
            link=row.link,
            ner=row.ner,
            podcast_id=row.podcastId,
            pubDate=row.pubDate,
            summary=row.summary,
            title=row.title,
        )
        episodes_list.append(episode)

    await repository.add_many_podcasts(podcasts)
    # for episode in episodes_list:
    #     await repository.add_episode(episode)
    await repository.add_many_episodes(episodes_list)

    return True
