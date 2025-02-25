from pydantic import BaseModel
from typing import Optional


class ProcessRequest(BaseModel):
    """
    A model representing a request for processing a file.
    """
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_rest: Optional[int] = 0
