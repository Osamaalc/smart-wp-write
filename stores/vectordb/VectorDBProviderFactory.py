from .providers.QdrantDBProvider import QdrantDBProvider
from .providers.WeaviateDBProvider import WeaviateDBProvider
from .VectorDBEnums import VectorDBType
from controllers.BaseController import BaseController


class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        """إنشاء موفر قاعدة البيانات حسب نوعها."""
        if provider == VectorDBType.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(db_path=db_path, distance_method=self.config.VECTOR_DB_DISTANCE_METHOD)

        if provider == VectorDBType.WEAVIATE.value:
            return WeaviateDBProvider(
                db_url=self.config.VECTOR_DB_PATH,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                api_key=getattr(self.config, "WEAVIATE_API_KEY", None)  # تجنب الخطأ إذا كان المفتاح غير معرف
            )

        return None
