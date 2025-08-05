from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationResponse(BaseModel, Generic[T]):
    """Response schema cho pagination"""
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: int | None
    prev_page: int | None 