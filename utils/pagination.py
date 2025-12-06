"""
Pagination Utilities for MiPastel Application

Provides helper functions and classes for implementing pagination
in database queries and API responses.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from math import ceil
from pydantic import BaseModel


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = 1
    page_size: int = 50
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size
    
    def validate(self):
        """Validate pagination parameters."""
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 50
        if self.page_size > 100:
            self.page_size = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> 'PaginatedResponse[T]':
        """
        Create a paginated response.
        
        Args:
            items: List of items for current page
            total: Total number of items across all pages
            page: Current page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            PaginatedResponse: Paginated response object
        """
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


def paginate_list(
    items: List[T],
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: Full list of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        dict: Paginated response with items and metadata
    """
    params = PaginationParams(page=page, page_size=page_size)
    params.validate()
    
    total = len(items)
    start = params.offset
    end = start + params.page_size
    
    page_items = items[start:end]
    
    response = PaginatedResponse.create(
        items=page_items,
        total=total,
        page=params.page,
        page_size=params.page_size
    )
    
    return response.dict()


def get_pagination_metadata(
    total: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Get pagination metadata without items.
    
    Args:
        total: Total number of items
        page: Current page number
        page_size: Items per page
        
    Returns:
        dict: Pagination metadata
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }


def calculate_offset_limit(page: int, page_size: int) -> tuple[int, int]:
    """
    Calculate offset and limit for database queries.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        tuple: (offset, limit) for database query
    """
    params = PaginationParams(page=page, page_size=page_size)
    params.validate()
    
    return params.offset, params.limit


# Example usage in FastAPI endpoint:
"""
from fastapi import Query
from utils.pagination import PaginationParams, PaginatedResponse

@app.get("/api/items")
async def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    params = PaginationParams(page=page, page_size=page_size)
    params.validate()
    
    # Get total count from database
    total = db.count_items()
    
    # Get items for current page
    items = db.get_items(offset=params.offset, limit=params.limit)
    
    # Create paginated response
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size
    )
"""
