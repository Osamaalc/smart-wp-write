from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict = Field(default={})
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        """
        Returns the indexes for the DataChunk model.

        :return: A list of index definitions for the DataChunk model.
        """
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]


class RetrieveDocument(BaseModel):
    text: str
    score: float
