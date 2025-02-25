import logging
from typing import List
from qdrant_client import models, QdrantClient
from ..VectorDBEnums import DistanceMethodEnum
from models.db_schemes import RetrieveDocument
from ..VectorDBInterfase import VectorDBInterfase
import json


class QdrantDBProvider(VectorDBInterfase):
    """
    Class to interact with Qdrant database, providing functionality to manage collections and insert,
    delete, and search documents using vectors.
    """

    def __init__(self, db_path: str, distance_method: str):
        """
        Initialize the QdrantDBProvider with the given database path and distance method.

        :param db_path: Path to the Qdrant database.
        :param distance_method: Distance method to use for vector comparisons.
        """
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.DOT_PRODUCT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        """
        Establish a connection to the Qdrant client using the provided database path.
        """
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        """
        Disconnect the Qdrant client.
        """
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the database.

        :param collection_name: The name of the collection to check.
        :return: True if the collection exists, False otherwise.
        """
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        """
        List all collections in the Qdrant database.

        :return: List of collection names.
        """
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        """
        Get information about a specific collection.

        :param collection_name: The name of the collection to retrieve info for.
        :return: A dictionary with collection information.
        """
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        """
        Delete a collection from the database if it exists.

        :param collection_name: The name of the collection to delete.
        """
        if self.is_collection_existed(collection_name=collection_name):
            self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        """
        Create a new collection or reset an existing collection with the specified parameters.

        :param collection_name: The name of the collection to create.
        :param embedding_size: The size of the vectors stored in the collection.
        :param do_reset: Whether to reset the collection if it already exists.
        :return: True if the collection was successfully created, False otherwise.
        """
        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method  # Properly passing the distance
                )
            )
            return True
        return False

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        """
        Insert a single record into the Qdrant collection.

        :param collection_name: The name of the collection to insert the record into.
        :param text: The text associated with the vector.
        :param vector: The vector to insert.
        :param metadata: Optional metadata to include with the record.
        :param record_id: Optional ID for the record.
        :return: True if the record was inserted successfully, False otherwise.
        """
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

    def insert_many(self, collection_name: str, texts: list, vectors: list,
                    metadata: list = None, record_ids: list = None,
                    embedding_size: int = 1536, batch_size: int = 50):
        """
        Insert multiple records into the Qdrant collection in batches.

        :param collection_name: The name of the collection to insert the records into.
        :param texts: The list of text associated with each vector.
        :param vectors: The list of vectors to insert.
        :param metadata: Optional metadata associated with each record.
        :param record_ids: Optional list of record IDs.
        :param embedding_size: The expected size of the vectors.
        :param batch_size: The size of each batch to insert.
        :return: True if the records were inserted successfully, False otherwise.
        """
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

            valid_batch = []
            for idx, vector in enumerate(batch_vectors):
                if len(vector) != embedding_size:
                    self.logger.warning(
                        f"Skipping vector with invalid size at index {i + idx}: {len(vector)} (expected {embedding_size})"
                    )
                    continue
                valid_batch.append(models.PointStruct(
                    id=batch_record_ids[idx],
                    vector=vector,
                    payload={"text": batch_texts[idx], "metadata": batch_metadata[idx]}
                ))

            if valid_batch:
                try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=valid_batch
                    )
                    self.logger.info(f"Successfully inserted batch from index {i} to {batch_end}")
                except Exception as e:
                    self.logger.error(f"Error while inserting batch: {e}")
                    return False
            else:
                self.logger.warning(f"No valid vectors to insert for batch from index {i} to {batch_end}")

        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        """
        Search for documents in a collection based on the provided vector.

        :param collection_name: The name of the collection to search.
        :param vector: The query vector.
        :param limit: The maximum number of results to return.
        :return: A list of retrieved documents, or None if no results were found.
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
        )
        if not results or len(results) == 0:
            return None
        return [
            RetrieveDocument(**{
                "score": result.score,
                "text": result.payload["text"],
            })
            for result in results
        ]
