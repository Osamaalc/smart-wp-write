import logging
import uuid

import weaviate
from typing import List
from weaviate.classes.config import Configure, Property, DataType
from weaviate.collections.classes.config import VectorDistances

from ..VectorDBEnums import DistanceMethodEnum
from models.db_schemes import RetrieveDocument
from ..VectorDBInterfase import VectorDBInterfase


class WeaviateDBProvider(VectorDBInterfase):
    def __init__(self, db_url: str, distance_method: str, api_key: str = None):
        self.client = None
        self.db_url = db_url
        self.api_key = api_key
        self.distance_method = None

        # تعيين طريقة حساب المسافة
        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = "cosine"
        elif distance_method == DistanceMethodEnum.DOT_PRODUCT.value:
            self.distance_method = "dot"
        elif distance_method == DistanceMethodEnum.EUCLIDEAN.value:
            self.distance_method = "l2"

        self.logger = logging.getLogger(__name__)

    def connect(self):
        """الاتصال بقاعدة بيانات Weaviate باستخدام الإصدار 4.11.0"""
        try:
            # إنشاء اتصال مع Weaviate بالإصدار الجديد
            self.client = client = weaviate.connect_to_local()

            # اختبار الاتصال
            if self.client.is_ready():
                self.logger.info("✅ Connected to Weaviate!")
                return True
            else:
                self.logger.error("❌ Connection to Weaviate failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error connecting to Weaviate: {str(e)}")
            return False

    def disconnect(self):
        """فصل الاتصال بقاعدة بيانات Weaviate."""
        self.client = None
        self.logger.info("✅ Disconnected from Weaviate.")

    def is_collection_existed(self, collection_name: str) -> bool:
        """التحقق من وجود مجموعة معينة."""
        return self.client.collections.exists(collection_name)

    def list_all_collections(self) -> List:
        """عرض جميع المجموعات."""
        collections = self.client.collections.list_all()
        return [collection.name for collection in collections]

    def get_collection_info(self, collection_name: str) -> dict:
        """الحصول على معلومات مجموعة معينة."""
        return self.client.collections.get(collection_name)

    def delete_collection(self, collection_name: str):
        """حذف مجموعة معينة."""
        if self.is_collection_existed(collection_name):
            self.client.collections.delete(collection_name)

    from weaviate.classes.config import Configure, Property, DataType
    from weaviate.collections.classes.config import VectorDistances

    from weaviate.classes.config import Configure, Property, DataType, ReferenceProperty

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        """إنشاء مجموعة جديدة باستخدام OpenAI embeddings للتخزين."""
        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):
            self.client.collections.create(
                name=collection_name,
                description="Collection for storing OpenAI embeddings",
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE
                ),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(
                        name="metadata",
                        data_type=DataType.OBJECT,
                        nested_properties=[  # ✅ أضف خصائص فرعية هنا
                            Property(name="author", data_type=DataType.TEXT),
                            Property(name="timestamp", data_type=DataType.DATE),
                            Property(name="source", data_type=DataType.TEXT)
                        ]
                    )
                ]
            )
            return True
        return False

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        """إدخال مستند واحد."""
        try:
            data_object = {
                "text": text,
                "metadata": metadata
            }
            self.client.data.insert_object(
                collection=collection_name,
                properties=data_object,
                vector=vector,
                uuid=record_id
            )
            return True
        except Exception as e:
            self.logger.error(f"❌ Error inserting record: {e}")
            return False

    # def insert_many(self, collection_name: str, texts: list, vectors: list,
    #                 metadata: list = None, record_ids: list = None, batch_size: int = 50):
    #     """إدخال مجموعة من المستندات دفعة واحدة."""
    #     if metadata is None:
    #         metadata = [None] * len(texts)
    #     if record_ids is None:
    #         record_ids = [str(i) for i in range(len(texts))]
    #
    #     with self.client.batch.fixed_size(batch_size=batch_size) as batch:
    #         for text, vector, meta, record_id in zip(texts, vectors, metadata, record_ids):
    #             try:
    #                 batch.add_object(
    #                     collection=collection_name,
    #                     properties={
    #                         "text": text,
    #                         "metadata": meta
    #                     },
    #                     vector=vector,
    #                     uuid=record_id
    #                 )
    #             except Exception as e:
    #                 self.logger.error(f"❌ Error inserting record: {e}")
    #                 return False
    #     return True
    import uuid
    from typing import List, Optional

    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                    metadata: Optional[List[dict]] = None, record_ids: Optional[List[str]] = None,
                    batch_size: int = 50) -> bool:
        """إدخال مجموعة من المستندات دفعة واحدة إلى مجموعة Weaviate."""
        # تحقق من أن جميع القوائم لها نفس الطول
        if not (len(texts) == len(vectors) == (len(metadata) if metadata else len(texts)) == (
        len(record_ids) if record_ids else len(texts))):
            raise ValueError("All input lists (texts, vectors, metadata, record_ids) must have the same length.")

        # إعداد القيم الافتراضية
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]  # استخدام UUID لضمان الفريدة

        # بدء الإدخال على دفعات
        try:
            with self.client.batch.fixed_size(batch_size=batch_size) as batch:
                for text, vector, meta, record_id in zip(texts, vectors, metadata, record_ids):
                    batch.add_object(
                        collection=collection_name,
                        properties={
                            "text": text,
                            "metadata": meta
                        },
                        vector=vector,
                        uuid=record_id
                    )
        except Exception as e:
            self.logger.error(f"❌ Error inserting batch: {e}")
            return False

        return True

    import uuid
    from typing import List, Optional

    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                    metadata: Optional[List[dict]] = None, record_ids: Optional[List[str]] = None,
                    batch_size: int = 50) -> bool:
        """إدخال مجموعة من المستندات دفعة واحدة إلى مجموعة Weaviate."""

        # تحقق من أن جميع القوائم لها نفس الطول
        if not (len(texts) == len(vectors) == (len(metadata) if metadata else len(texts)) == (
        len(record_ids) if record_ids else len(texts))):
            raise ValueError("All input lists (texts, vectors, metadata, record_ids) must have the same length.")

        # إعداد القيم الافتراضية
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]  # ✅ استخدام UUID كنصوص
        else:
            record_ids = [str(record_id) for record_id in record_ids]  # ✅ تحويل أي معرف إلى نص

        # بدء الإدخال على دفعات
        try:
            with self.client.batch.fixed_size(batch_size=batch_size) as batch:
                for text, vector, meta, record_id in zip(texts, vectors, metadata, record_ids):
                    batch.add_object(
                        collection=collection_name,
                        properties={
                            "text": text,
                            "metadata": meta
                        },
                        vector=vector,
                        uuid=record_id  # ✅ الآن سيكون دائمًا من نوع str أو uuid.UUID
                    )
        except Exception as e:
            self.logger.error(f"❌ Error inserting batch: {e}")
            return False

        return True

    import uuid
    from typing import List, Optional

    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                    metadata: Optional[List[dict]] = None, record_ids: Optional[List[str]] = None,
                    batch_size: int = 50) -> bool:
        """إدخال مجموعة من المستندات دفعة واحدة إلى مجموعة Weaviate."""

        # تحقق من أن جميع القوائم لها نفس الطول
        if not (len(texts) == len(vectors) == (len(metadata) if metadata else len(texts)) == (
        len(record_ids) if record_ids else len(texts))):
            raise ValueError("All input lists (texts, vectors, metadata, record_ids) must have the same length.")

        # إعداد القيم الافتراضية
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            # ✅ استخدام UUID صالح
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        else:
            # ✅ ضمان أن جميع المعرفات هي UUID صالح
            try:
                record_ids = [str(uuid.UUID(str(record_id))) for record_id in record_ids]
            except ValueError as e:
                self.logger.error(f"❌ Invalid UUID provided: {e}")
                return False

        # بدء الإدخال على دفعات
        try:
            with self.client.batch.fixed_size(batch_size=batch_size) as batch:
                for text, vector, meta, record_id in zip(texts, vectors, metadata, record_ids):
                    batch.add_object(
                        collection=collection_name,
                        properties={
                            "text": text,
                            "metadata": meta
                        },
                        vector=vector,
                        uuid=record_id
                    )
        except Exception as e:
            self.logger.error(f"❌ Error inserting batch: {e}")
            return False

        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> List[RetrieveDocument]:
        """البحث باستخدام المتجهات."""
        try:
            # بناء وتنفيذ استعلام البحث باستخدام المتجه
            result = (
                self.client.query.get(
                    collection_name,
                    ["text", "metadata"]
                )
                .with_near_vector({
                    "vector": vector,
                    "distance": self.distance_method  # أو يمكنك استخدام "certainty" حسب الإعدادات المطلوبة
                })
                .with_limit(limit)
                .do()
            )
            # الوصول إلى النتائج من الرد ضمن: data -> Get -> collection_name
            items = result.get("data", {}).get("Get", {}).get(collection_name, [])
            return [
                RetrieveDocument(
                    score=item["_additional"]["certainty"],
                    text=item["text"]
                ) for item in items
            ]
        except Exception as e:
            self.logger.error(f"❌ Error during vector search: {e}")
            return []

