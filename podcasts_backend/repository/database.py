import asyncio

import pandas as pd

from ..models.models import Episode, EpisodeMetadata
from ..repository.providers.milvus import MilvusDataStore


def upload_to_milvus(milvus_db: MilvusDataStore):
    """Temporary function that uploads the first 50 episodes to milvus
    TODO: change this to a proper function that uploads all episodes periodically

    Args:
        milvus_db (MilvusDataStore): milvus database connection

    Returns:
        _type_: _description_
    """
    print("uploading to milvus...")
    milvus = milvus_db
    df = pd.read_pickle("/podcasts_data/xaa_episodes_short.pkl")
    podcasts = pd.read_pickle("/podcasts_data/xaa_podcasts.pkl")
    df = df.iloc[:50]

    df = pd.merge(
        df,
        podcasts.loc[:, ["categories", "language", "id"]],
        left_on="podcastId",
        right_on="id",
        how="inner",
    )

    df = df[~df["description"].isna()]
    episodes = df.apply(
        lambda x: Episode(
            id=f'{x["podcastId"]}_{x.name}',
            metadata=EpisodeMetadata(
                podcast_id=x["podcastId"],
                category=x["categories"][0] if len(x["categories"]) > 0 else "",
                language=x["language"],
            ),
            text=x["description"],
        ),
        axis=1,
    ).to_list()
    print("upload done...")
    # return True
    return asyncio.gather(milvus.upsert(episodes, delete_all=True))
