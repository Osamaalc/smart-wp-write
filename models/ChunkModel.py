from typing import List
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .db_schemes import Project, DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        """
        Initialize the ChunkModel with the provided database client.

        :param db_client: The database client used for interactions with the database.
        """
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create an instance of ChunkModel and initialize its collection.

        :param db_client: The database client used for interactions with the database.
        :return: An instance of ChunkModel.
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        """
        Initialize the collection for chunks. Creates the collection and its indexes if not already present.

        :return: None
        """
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index['key'], name=index['name'], unique=index['unique'])

    async def create_chunk(self, chunk: DataChunk):
        """
        Insert a new chunk into the collection.

        :param chunk: The chunk to be created.
        :return: The created chunk with an assigned ID.
        """
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        """
        Retrieve a specific chunk by its ID.

        :param chunk_id: The ID of the chunk to retrieve.
        :return: The chunk if found, or None if not found.
        """
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})

        if result is None:
            return None
        return DataChunk(**result)

    async def insert_many_chunks(self, chunks: list, batch_size: int = 400):
        """
        Insert multiple chunks into the collection in batches.

        :param chunks: A list of chunks to insert.
        :param batch_size: The size of each batch to insert. Default is 400.
        :return: The total number of chunks inserted.
        """
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operation = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operation)

        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: ObjectId):
        """
        Delete all chunks associated with a specific project ID.

        :param project_id: The project ID to delete chunks for.
        :return: The number of deleted chunks.
        """
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """
        Delete chunks by project ID (alias for delete_chunk_by_project_id).

        :param project_id: The project ID to delete chunks for.
        :return: The number of deleted chunks.
        """
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

    async def get_project_chunk(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
        """
        Retrieve chunks associated with a specific project ID, with pagination.

        :param project_id: The project ID to get chunks for.
        :param page_no: The page number to retrieve (default is 1).
        :param page_size: The number of chunks per page (default is 50).
        :return: A list of DataChunk objects.
        """
        result = await self.collection.find(
            {"chunk_project_id": project_id}
        ).skip((page_no - 1) * page_size).limit(page_size).to_list(length=None)

        return [
            DataChunk(**record)
            for record in result
        ]
