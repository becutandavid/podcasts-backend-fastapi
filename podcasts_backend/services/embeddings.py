# mypy: allow-untyped-defs
from sentence_transformers import SentenceTransformer

# TODO: implement Ray serve
# TODO: cache folder from config
print("loading model...")
model = SentenceTransformer("all-mpnet-base-v2", cache_folder="/podcasts_data")


def get_embeddings(descriptions: list[str]) -> list[list[float]]:
    """get embeddings for a list od episode descriptions

    Args:
        descriptions (list[str]): list of episode descriptions

    Returns:
        list[float]: list of descriptions
    """
    embeddings = model.encode(descriptions, convert_to_numpy=True)
    return embeddings.tolist()  # type: ignore
