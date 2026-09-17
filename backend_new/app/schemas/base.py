"""Base schemas and common types"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


T = TypeVar("T")


class ResponseEnvelope(BaseSchema, Generic[T]):
    """Standard API response envelope."""

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    request_id: Optional[str] = None
    demo_mode: bool = False


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseSchema):
    """Error response."""

    success: bool = False
    error: str
    error_code: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str = "healthy"
    version: str
    demo_mode: bool
    database: str = "connected"
    ai_providers: Dict[str, bool] = Field(default_factory=dict)


# Request ID header
REQUEST_ID_HEADER = "X-Request-ID"
DEMO_MODE_HEADER = "X-Demo-Mode"