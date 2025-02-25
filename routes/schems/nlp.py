from pydantic import BaseModel
from typing import Optional


class PushRequest(BaseModel):
    """
    A model representing a request to push data.
    """
    do_rest: Optional[bool] = False  # Default should be False instead of 0


class SearchRequest(BaseModel):
    """
    A model representing a request to search for text.
    """
    text: str
    limit: Optional[int] = 10
