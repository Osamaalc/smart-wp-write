from enum import Enum


class VectorDBType(Enum):
    """
    Enum representing different types of Vector Databases.
    """
    QDRANT = "QDRANT"
    FAISS = "FAISS"
    ANNOY = "ANNOY"
    HNSWLIB = "HNSWLIB"
    VESPA = "VESPA"
    PINECONE = "PINECONE"
    VECTORDB = "VECTORDB"
    WEAVIATE = "WEAVIATE"  # Added WEAVIATE to specify Weaviate provider


class DistanceMethodEnum(Enum):
    """
    Enum representing different distance methods for vector comparisons.
    """
    EUCLIDEAN = "EUCLIDEAN"
    COSINE = "COSINE"
    DOT_PRODUCT = "DOT_PRODUCT"
