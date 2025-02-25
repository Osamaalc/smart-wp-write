from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator


class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        """
        Validates that the project ID is alphanumeric.

        :param value: The project ID to validate.
        :return: The validated project ID if it is alphanumeric.
        :raises ValueError: If the project ID is not alphanumeric.
        """
        if not value.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        return value

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        """
        Returns the indexes for the Project model.

        :return: A list of index definitions for the Project model.
        """
        return [
            {
                "key": [("project_id", 1)],
                "name": "project_id_index",
                "unique": True
            }
        ]
