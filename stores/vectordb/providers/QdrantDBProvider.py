import logging
from typing import List
from qdrant_client import models, QdrantClient
from ..VectorDBEnums import DistanceMethodEnum
from models.db_schemes import RetrieveDocument
from ..VectorDBInterfase import VectorDBInterfase
import json
class QdrantDBProvider(VectorDBInterfase):
    def __init__(self, db_path: str, distance_method: str):
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE

        elif distance_method == DistanceMethodEnum.DOT_PRODUCT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            self.delete_collection(collection_name=collection_name)
        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method  # ✅ تمرير distance بشكل صحيح هنا
                )
            )

            return True
        return False

    # def insert_one(self, collection_name: str, text: str, vector: list,
    #                metadata: dict = None,
    #                record_id: str = None):
    #     if not self.is_collection_existed(collection_name=collection_name):
    #         self.logger.error(f"can not insert new record to non-existed collection{collection_name}")
    #         return False
    #     try:
    #         self.client.uploaded_records(collection_name=collection_name, records=[
    #             models.Record(
    #                 id=[record_id],
    #                 vector=vector,
    #                 payload={"text": text, "metadata": metadata}
    #             )
    #         ])
    #     except Exception as e:
    #         self.logger.error(f"Error while inserting record :{e}")
    #         return False
    #     return True

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Cannot insert new record to non-existent collection: {collection_name}")
            return False
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata}
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False
        return True

    # def insert_many(self, collection_name: str, texts: list, vectors: list,
    #                 metadata: list = None,
    #                 record_ids: list = None, batch_size: int = 50):
    #
    #     if metadata is None:
    #         metadata = [None] * len(texts)
    #     if record_ids is None:
    #         record_ids = list(range(0,len(texts)))
    #     for i in range(0, len(texts), batch_size):
    #         batch_end = i + batch_size
    #         batch_texts = texts[i:batch_end]
    #         batch_vectors = vectors[i:batch_end]
    #         batch_metadata = metadata[i:batch_end]
    #         batch_record_ids = record_ids[i:batch_end]
    #         batch_records = [
    #             models.Record(
    #                 id=batch_record_ids[x],
    #                 vector=batch_vectors[x],
    #                 payload={
    #                     "text": batch_texts[x], "metadata": batch_metadata[x]
    #                 }
    #             )
    #             for x in range(len(batch_texts))
    #         ]
    #         try:
    #             _ = self.client.uploaded_records(collection_name=collection_name, records=batch_records)
    #         except Exception as e:
    #             self.logger.error(f"Error while inserting batch :{e}")
    #             return False
    #     return True

    def insert_many(self, collection_name: str, texts: list, vectors: list,
                    metadata: list = None, record_ids: list = None,
                    embedding_size: int = 1536, batch_size: int = 50):  # ✅ تمرير embedding_size

        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = list(range(len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            # ✅ التحقق من صحة المتجهات
            valid_batch = []

            for idx, vector in enumerate(batch_vectors):
                if len(vector) != embedding_size:
                    self.logger.warning(
                        f"⚠️ Skipping vector with invalid size at index {i + idx}: {len(vector)} (expected {embedding_size})"
                    )
                    continue
                valid_batch.append(models.PointStruct(
                    id=batch_record_ids[idx],
                    vector=vector,
                    payload={"text": batch_texts[idx], "metadata": batch_metadata[idx]}
                ))

            # ✅ إدراج الدفعة إذا كانت صالحة
            if valid_batch:
                try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=valid_batch
                    )
                    self.logger.info(f"✅ Successfully inserted batch from index {i} to {batch_end}")
                except Exception as e:
                    self.logger.error(f"❌ Error while inserting batch: {e}")
                    return False
            else:
                self.logger.warning(f"⚠️ No valid vectors to insert for batch from index {i} to {batch_end}")

        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        results= self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
        )
        if not results or len(results)==0:
            return None
        return [
            RetrieveDocument(**{
                "score":result.score,
                "text":result.payload["text"],
            })
            for result in results
        ]