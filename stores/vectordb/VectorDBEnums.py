from enum import Enum
class VectorDBType(Enum):
    QDRANT = "QDRANT"
    FAISS = "FAISS"
    ANNOY = "ANNOY"
    HNSWLIB = "HNSWLIB"
    VESPA = "VESPA"
    PINECONE = "PINECONE"
    VECTORDB = "VECTORDB"
    WEAVIATE = "WEAVIATE"  # تم إضافة WEAVIATE لتحديد مزود Weaviate

class DistanceMethodEnum(Enum):
    EUCLIDEAN = "EUCLIDEAN"
    COSINE = "COSINE"
    DOT_PRODUCT = "DOT_PRODUCT"