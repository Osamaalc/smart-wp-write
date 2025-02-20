# import logging
# from typing import List
# from pymilvus import connections,Collection,CollectionSchema,FieldSchema,DataType,utility
# from models.db_schemes import RetrieveDocument
# from ..VectorDBInterfase import VectorDBInterfase
#
# class MilvusDBProvider(VectorDBInterfase):
#     def __init__(self, host: str, port: str, collection_prefix: str = "milvus_"):
#         """
#         :param host: عنوان الخادم الخاص بـ Milvus (مثلاً "127.0.0.1")
#         :param port: رقم المنفذ (مثلاً "19530")
#         :param collection_prefix: بادئة تُضاف إلى اسم المجموعة لتفادي التعارض (اختياري)
#         """
#         self.host = host
#         self.port = port
#         self.collection_prefix = collection_prefix
#         self.logger = logging.getLogger(__name__)
#         self.connected = False
#
#     def _get_full_collection_name(self, collection_name: str) -> str:
#         return f"{self.collection_prefix}{collection_name}"
#
#     def connect(self):
#         try:
#             connections.connect(alias="default", host=self.host, port=self.port)
#             self.connected = True
#             self.logger.info("Successfully connected to Milvus.")
#         except Exception as e:
#             self.logger.error(f"Error connecting to Milvus: {e}")
#             self.connected = False
#
#     def disconnect(self):
#         try:
#             connections.disconnect("default")
#             self.connected = False
#             self.logger.info("Disconnected from Milvus.")
#         except Exception as e:
#             self.logger.error(f"Error disconnecting from Milvus: {e}")
#
#     def is_collection_existed(self, collection_name: str) -> bool:
#         full_name = self._get_full_collection_name(collection_name)
#         return utility.has_collection(full_name)
#
#     def list_all_collections(self) -> List:
#         return utility.list_collections()
#
#     def get_collection_info(self, collection_name: str) -> dict:
#         full_name = self._get_full_collection_name(collection_name)
#         if not self.is_collection_existed(collection_name):
#             self.logger.error(f"Collection {full_name} does not exist.")
#             return {}
#         collection = Collection(name=full_name)
#         return collection.describe()
#
#     def delete_collection(self, collection_name: str):
#         full_name = self._get_full_collection_name(collection_name)
#         if self.is_collection_existed(collection_name):
#             utility.drop_collection(full_name)
#             self.logger.info(f"Collection {full_name} deleted.")
#         else:
#             self.logger.warning(f"Collection {full_name} does not exist.")
#
#     def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
#         full_name = self._get_full_collection_name(collection_name)
#         if do_reset and self.is_collection_existed(collection_name):
#             self.delete_collection(collection_name)
#         if not self.is_collection_existed(collection_name):
#             # تعريف الحقول: معرف، نص، بيانات وصفية، ومتجه التضمين
#             fields = [
#                 FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
#                 FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, description="Text field"),
#                 FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535, description="Metadata as JSON string"),
#                 FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_size)
#             ]
#             schema = CollectionSchema(fields, description="Milvus collection schema")
#             Collection(name=full_name, schema=schema)
#             self.logger.info(f"Collection {full_name} created successfully.")
#             return True
#         else:
#             self.logger.warning(f"Collection {full_name} already exists.")
#             return False
#
#     def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
#         full_name = self._get_full_collection_name(collection_name)
#         if not self.is_collection_existed(collection_name):
#             self.logger.error(f"Cannot insert record; collection {full_name} does not exist.")
#             return False
#         try:
#             collection = Collection(name=full_name)
#             # تحويل metadata إلى سلسلة JSON إذا كانت موجودة
#             metadata_str = json.dumps(metadata) if metadata else ""
#             data = [
#                 [text],              # حقل النص
#                 [metadata_str],      # حقل البيانات الوصفية
#                 [vector]             # حقل المتجه
#             ]
#             # ملاحظة: حقل "id" يُنشأ تلقائيًا بسبب auto_id=True
#             collection.insert(data)
#             collection.flush()
#             self.logger.info("Record inserted successfully.")
#             return True
#         except Exception as e:
#             self.logger.error(f"Error while inserting record: {e}")
#             return False
#
#     def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: List[dict] = None,
#                     record_ids: List[str] = None, batch_size: int = 50):
#         full_name = self._get_full_collection_name(collection_name)
#         if not self.is_collection_existed(collection_name):
#             self.logger.error(f"Cannot insert records; collection {full_name} does not exist.")
#             return False
#         if metadata is None:
#             metadata = [None] * len(texts)
#         try:
#             collection = Collection(name=full_name)
#             total = len(texts)
#             for i in range(0, total, batch_size):
#                 batch_texts = texts[i:i+batch_size]
#                 batch_vectors = vectors[i:i+batch_size]
#                 batch_metadata = metadata[i:i+batch_size]
#                 # تحويل metadata إلى JSON strings
#                 batch_metadata_str = [json.dumps(md) if md else "" for md in batch_metadata]
#                 data = [
#                     batch_texts,          # حقل النص
#                     batch_metadata_str,   # حقل البيانات الوصفية
#                     batch_vectors         # حقل المتجهات
#                 ]
#                 collection.insert(data)
#                 self.logger.info(f"Inserted batch from index {i} to {i+batch_size}")
#             collection.flush()
#             return True
#         except Exception as e:
#             self.logger.error(f"Error while inserting records: {e}")
#             return False
#
#     def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> List[RetrieveDocument]:
#         full_name = self._get_full_collection_name(collection_name)
#         if not self.is_collection_existed(collection_name):
#             self.logger.error(f"Collection {full_name} does not exist.")
#             return []
#         try:
#             collection = Collection(name=full_name)
#             # إعداد معلمات البحث (يمكنك تعديلها حسب الحاجة)
#             search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
#             # إجراء البحث في حقل المتجه
#             results = collection.search(
#                 data=[vector],
#                 anns_field="embedding",
#                 param=search_params,
#                 limit=limit,
#                 expr=None
#             )
#             documents = []
#             for result in results[0]:
#                 # استرجاع النص والبيانات الوصفية؛ يمكن تحويل metadata إلى dict إذا لزم الأمر
#                 text = result.entity.get("text", "")
#                 metadata_str = result.entity.get("metadata", "")
#                 try:
#                     metadata = json.loads(metadata_str) if metadata_str else {}
#                 except Exception:
#                     metadata = {}
#                 documents.append(RetrieveDocument(score=result.distance, text=text, metadata=metadata))
#             return documents
#         except Exception as e:
#             self.logger.error(f"Error during search: {e}")
#             return []
