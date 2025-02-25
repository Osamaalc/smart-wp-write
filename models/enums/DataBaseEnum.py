from enum import Enum


class DataBaseEnum(Enum):
    """
    Enum representing database collection names.
    """
    COLLECTION_PROJECT_NAME = "projects"
    COLLECTION_CHUNK_NAME = "chunks"
    COLLECTION_ASSETS_NAME = "assets"
