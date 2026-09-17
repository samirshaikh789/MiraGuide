"""Sessions API endpoints"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_settings
from app.db.base import get_db
from app.models.session import Session
from app.schemas.ai import SessionCreateRequest, SessionResponse
from app.schemas.base import ResponseEnvelope, REQUEST_ID_HEADER
from app.services import ai_service

router = APIRouter(prefix="/sessions", tags=["sessions"])
settings = get_settings()


@router.post(
    "",
    response_model=ResponseEnvelope[SessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
    description="Create a new session for maintaining context across interactions",
)
async def create_session(
    request: Request,
    session_data: SessionCreateRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[SessionResponse]:
    """Create a new session."""
    session = await ai_service._get_or_create_session(
        db, user_id=session_data.user_id
    )
    await db.commit()
    await db.refresh(session)

    return ResponseEnvelope(
        success=True,
        data=SessionResponse.model_validate(session),
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )


@router.get(
    "/{session_id}",
    response_model=ResponseEnvelope[SessionResponse],
    summary="Get session",
    description="Get session details including context",
)
async def get_session(
    session_id: UUID,
    request: Request,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[SessionResponse]:
    """Get session by ID."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    return ResponseEnvelope(
        success=True,
        data=SessionResponse.model_validate(session),
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )


@router.delete(
    "/{session_id}",
    response_model=ResponseEnvelope[dict],
    summary="Delete session",
    description="Delete a session and all its interactions",
)
async def delete_session(
    session_id: UUID,
    request: Request,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Delete a session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    await db.delete(session)
    await db.commit()

    return ResponseEnvelope(
        success=True,
        data={"message": "Session deleted"},
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )