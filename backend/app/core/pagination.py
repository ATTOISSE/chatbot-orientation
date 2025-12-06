"""
Pagination utilities for COMMIT 7
"""

from pydantic import BaseModel, Field
from typing import Tuple
from sqlalchemy.orm import Query
import math


class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationInfo(BaseModel):
    """Pagination information"""
    
    total_pages: int
    has_next: bool
    has_prev: bool


def apply_pagination(
    query: Query,
    params: PaginationParams
) -> Tuple[Query, PaginationInfo]:
    """
    Apply pagination to a SQLAlchemy query
    
    Returns:
        Tuple of (paginated_query, pagination_info)
    """
    
    total = query.count()
    total_pages = math.ceil(total / params.page_size) if params.page_size > 0 else 1
    
    offset = (params.page - 1) * params.page_size
    paginated_query = query.offset(offset).limit(params.page_size)
    
    pagination_info = PaginationInfo(
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1
    )
    
    return paginated_query, pagination_info
