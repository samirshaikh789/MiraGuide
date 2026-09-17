"""Health check endpoint"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_db
from app.schemas.base import HealthResponse, REQUEST_ID_HEADER
from app.services import provider_registry

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Check service health and AI provider availability",
)
async def health_check(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """Health check endpoint."""
    request_id = request.headers.get(REQUEST_ID_HEADER)

    # Check database
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Check AI providers
    ai_providers = {
        "vision": list(provider_registry.available_vision),
        "text": list(provider_registry.available_text),
        "ocr": list(provider_registry.available_ocr),
        "stt": list(provider_registry.available_stt),
        "tts": list(provider_registry.available_tts),
    }

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.APP_VERSION,
        demo_mode=settings.DEMO_MODE,
        database=db_status,
        ai_providers={k: len(v) > 0 for k, v in ai_providers.items()},
    )