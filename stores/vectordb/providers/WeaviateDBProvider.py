import hashlib
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict

import tenacity
import weaviate
import numpy as np

from weaviate.classes.config import Configure, Property, DataType
from weaviate.collections.classes.config import VectorDistances
from weaviate.collections.classes.grpc import MetadataQuery

from routes.data import logger
from ..VectorDBEnums import DistanceMethodEnum
from models.db_schemes import RetrieveDocument
from ..VectorDBInterfase import VectorDBInterfase


class WeaviateDBProvider(VectorDBInterfase):
    def __init__(self, db_url: str, distance_method: str, api_key: str = None):
        self.client = None
        self.db_url = db_url
        self.api_key = api_key
        self.distance_method = None

        # Assign distance method
        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = "cosine"
        elif distance_method == DistanceMethodEnum.DOT_PRODUCT.value:
            self.distance_method = "dot"
        elif distance_method == DistanceMethodEnum.EUCLIDEAN.value:
            self.distance_method = "l2"

        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Connect to Weaviate database (version 4.11.0)"""
        try:
            # Establish connection with Weaviate
            self.client = weaviate.connect_to_local()

            # Test the connection
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
        """Disconnect from Weaviate database"""
        self.client = None
        self.logger.info("✅ Disconnected from Weaviate.")

    def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        return self.client.collections.exists(collection_name)

    def list_all_collections(self) -> List:
        """List all collections"""
        collections = self.client.collections.list_all()
        return [collection.name for collection in collections]

    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a specific collection"""
        return self.client.collections.get(collection_name)

    def delete_collection(self, collection_name: str):
        """Delete a specific collection"""
        if self.is_collection_existed(collection_name):
            self.client.collections.delete(collection_name)

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        """Create a new collection using OpenAI embeddings for storage"""
        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):
            self.client.collections.create(
                name=collection_name,
                description="Collection for storing OpenAI embeddings",
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE,  # Use Cosine as it's best for text
                    ef_construction=128  # Improve input accuracy
                ),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(
                        name="metadata",
                        data_type=DataType.OBJECT,
                        nested_properties=[
                            Property(name="author", data_type=DataType.TEXT),
                            Property(name="timestamp", data_type=DataType.DATE),
                            Property(name="source", data_type=DataType.TEXT)
                        ]
                    )
                ]
            )
            self.logger.info(f"✅ Collection '{collection_name}' created successfully.")
            return True

        self.logger.info(f"ℹ️ Collection '{collection_name}' already exists.")
        return False

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        """Insert a single document"""
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

    def insert_many(
            self,
            collection_name: str,
            texts: List[str],
            vectors: List[list],
            metadata: Optional[List[dict]] = None,
            record_ids: Optional[List[str]] = None,
            batch_size: int = 50
    ) -> bool:
        """
        Insert a batch of documents into a Weaviate collection.

        :param collection_name: The name of the collection in Weaviate.
        :param texts: A list of texts to insert.
        :param vectors: A list of vectors corresponding to each text.
        :param metadata: A list of metadata (optional).
        :param record_ids: A list of unique identifiers (UUID) for each text.
        :param batch_size: The batch size for insertion.
        :return: True if the insertion was successful, otherwise False.
        """
        if not (len(texts) == len(vectors) == (len(metadata) if metadata else len(texts)) == (
                len(record_ids) if record_ids else len(texts))):
            raise ValueError("All input lists (texts, vectors, metadata, record_ids) must have the same length.")

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        else:
            try:
                record_ids = [str(uuid.UUID(str(record_id))) for record_id in record_ids]
            except ValueError as e:
                self.logger.error(f"❌ Invalid UUID provided: {e}")
                return False

        for text, vector in zip(texts, vectors):
            if len(vector) != 1536:
                raise ValueError(f"❌ Vector length must be 1536, but got {len(vector)}")
            text = text.strip()

        success_count = 0
        failure_count = 0
        try:
            with self.client.batch.fixed_size(batch_size=batch_size) as batch:
                for text, vector, meta, record_id in zip(texts, vectors, metadata, record_ids):
                    try:
                        batch.add_object(
                            collection=collection_name,
                            properties={"text": text, "metadata": meta},
                            vector=vector,
                            uuid=record_id
                        )
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"❌ Error inserting record {record_id}: {e}")
                        failure_count += 1

        except Exception as e:
            self.logger.error(f"❌ Error inserting batch: {e}")
            return False

        self.logger.info(f"✅ Inserted {success_count} records successfully.")
        if failure_count > 0:
            self.logger.warning(f"⚠️ Failed to insert {failure_count} records.")

        return success_count > 0

    def search_by_vector(
            self,
            collection_name: str,
            vector: List[float],
            query_text: Optional[str] = None,
            limit: int = 5,
            min_score: float = None,
            use_hybrid: bool = True,
            enable_fallback: bool = True
    ) -> Optional[List[Dict]]:
        """
        Advanced search function with features:
        - Hybrid search (text + vector)
        - Multi-criteria ranking
        - Smart error recovery
        - Handling duplicate results
        - Fallback results if no exact match is found

        Args:
            collection_name (str): The name of the collection to search in.
            vector (List[float]): The vector used for the search.
            query_text (Optional[str]): The query text for hybrid search (if used).
            limit (int): The maximum number of results.
            min_score (float): The minimum accepted similarity score.
            use_hybrid (bool): Use hybrid search (text + vector).
            enable_fallback (bool): Enable fallback search when no exact match is found.

        Returns:
            Optional[List[Dict]]: A list of results or None if no matches are found.
        """
        def preprocess_text(text: str) -> str:
            processed = text.lower().strip()
            processed = "".join([c for c in processed if not c.isdigit()])
            return hashlib.md5(processed.encode()).hexdigest()

        @tenacity.retry(
            stop=tenacity.stop_after_attempt(3),
            wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
            retry=tenacity.retry_if_exception_type((TimeoutError, ConnectionError)),
            before_sleep=lambda *_: self.logger.warning("Retrying search due to error...")
        )
        def execute_query():
            """Execute query with automatic retries"""
            nonlocal collection, response

            if use_hybrid and query_text:
                response = collection.query.hybrid(
                    query=query_text,
                    vector=vector,
                    limit=limit * 5,
                    return_metadata=MetadataQuery(certainty=True, score=True)
                )
            else:
                response = collection.query.near_vector(
                    near_vector=vector,
                    limit=limit * 5,
                    return_metadata=MetadataQuery(certainty=True, score=True)
                )

        try:
            collection = self.client.collections.get(collection_name)
            response = None

            execute_query()

            objects = response.objects
            if not objects:
                return None

            scores = [obj.metadata.certainty or obj.metadata.score or 0.0 for obj in objects]
            effective_min_score = min_score or (max(scores) * 0.85 if scores else 0.8)

            unique_results = []
            seen_hashes = set()

            for obj in objects:
                raw_text = obj.properties.get("text", "")
                text_hash = preprocess_text(raw_text)
                score = obj.metadata.certainty or obj.metadata.score or 0.0

                if score >= effective_min_score and text_hash not in seen_hashes:
                    unique_results.append({
                        "obj": obj,
                        "score": score,
                        "hash": text_hash,
                        "popularity": obj.properties.get("popularity", 0),
                        "date": obj.properties.get("date", "1970-01-01")
                    })
                    seen_hashes.add(text_hash)

            sorted_results = sorted(
                unique_results,
                key=lambda x: (-x['score'], -x['popularity'], x['date'])
            )[:limit]

            final_results = [
                RetrieveDocument(
                    score=item['score'],
                    text=item['obj'].properties.get("text", ""),
                    metadata={
                        'source': item['obj'].properties.get("source"),
                        'page': item['obj'].properties.get("page")
                    }
                ) for item in sorted_results
            ]

            if not final_results and enable_fallback:
                self.logger.warning("No high-quality results, returning fallback matches")
                fallback = [obj for obj in objects[:limit]]
                return [
                    {
                        "score": obj.metadata.certainty or 0.0,
                        "text": obj.properties.get("text", ""),
                        "metadata": {
                            'source': obj.properties.get("source"),
                            'page': obj.properties.get("page")
                        }
                    } for obj in fallback
                ]

            return final_results

        except Exception as e:
            self.logger.error(f"Critical search error: {str(e)}", exc_info=True)
            return None
