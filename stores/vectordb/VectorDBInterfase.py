from abc import ABC, abstractmethod
from typing import List
from models.db_schemes import RetrieveDocument


class VectorDBInterfase(ABC):
    """
    Abstract base class for interacting with vector databases.

    This class defines the essential methods that any vector database provider
    (e.g., Qdrant, FAISS, Weaviate) must implement for managing collections and performing
    CRUD operations with vectors.
    """

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the vector database.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the vector database.
        """
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the vector database.

        :param collection_name: The name of the collection to check.
        :return: True if the collection exists, False otherwise.
        """
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        """
        List all collections in the vector database.

        :return: A list of collection names.
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        """
        Get information about a specific collection.

        :param collection_name: The name of the collection to get information for.
        :return: A dictionary containing collection information.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        """
        Delete a collection from the vector database.

        :param collection_name: The name of the collection to delete.
        """
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        """
        Create a new collection in the vector database.

        :param collection_name: The name of the collection to create.
        :param embedding_size: The size of the vectors to store in the collection.
        :param do_reset: Whether to reset the collection if it already exists (default: False).
        """
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, text: str, vector: list,
                   metadata: dict = None, record_id: str = None):
        """
        Insert a single document into a collection.

        :param collection_name: The name of the collection.
        :param text: The text associated with the vector.
        :param vector: The vector to insert.
        :param metadata: Optional metadata to associate with the document.
        :param record_id: Optional ID for the document.
        :return: True if insertion was successful, False otherwise.
        """
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, texts: list, vectors: list,
                    metadata: List[dict] = None, record_ids: List[str] = None, batch_size: int = 50):
        """
        Insert multiple documents into a collection.

        :param collection_name: The name of the collection.
        :param texts: A list of texts to associate with the vectors.
        :param vectors: A list of vectors to insert.
        :param metadata: Optional list of metadata to associate with the documents.
        :param record_ids: Optional list of IDs for the documents.
        :param batch_size: The size of the batches for insertion (default: 50).
        :return: True if all documents were inserted successfully, False otherwise.
        """
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int) -> List[RetrieveDocument]:
        """
        Search for documents in a collection by vector.

        :param collection_name: The name of the collection to search in.
        :param vector: The query vector.
        :param limit: The maximum number of results to return.
        :return: A list of retrieved documents or an empty list if no results are found.
        """
        pass
