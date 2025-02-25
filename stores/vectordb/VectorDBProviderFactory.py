from .providers.QdrantDBProvider import QdrantDBProvider
from .providers.WeaviateDBProvider import WeaviateDBProvider
from .VectorDBEnums import VectorDBType
from controllers.BaseController import BaseController


class VectorDBProviderFactory:
    """
    Factory class to create instances of different Vector Database providers (e.g., Qdrant, Weaviate).

    This class takes in a configuration and uses it to initialize the corresponding database provider.
    """

    def __init__(self, config):
        """
        Initialize the VectorDBProviderFactory with the given configuration.

        :param config: The configuration containing the necessary settings (e.g., database paths, distance methods).
        """
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        """
        Create and return an instance of the specified VectorDB provider.

        :param provider: The name of the vector database provider (e.g., 'QDRANT', 'WEAVIATE').
        :return: An instance of the corresponding provider, or None if the provider is not supported.
        """
        if provider == VectorDBType.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )

        if provider == VectorDBType.WEAVIATE.value:
            return WeaviateDBProvider(
                db_url=self.config.VECTOR_DB_PATH,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                api_key=getattr(self.config, "WEAVIATE_API_KEY", None)  # Avoid error if the key is not defined
            )

        return None
