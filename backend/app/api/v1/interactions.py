"""Interactions API endpoints"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_settings
from app.db.base import get_db
from app.models.session import Session, Interaction
from app.schemas.ai import InteractionResponse
from app.schemas.base import ResponseEnvelope, PaginatedResponse, REQUEST_ID_HEADER

router = APIRouter(prefix="/interactions", tags=["interactions"])
settings = get_settings()


@router.get(
    "/session/{session_id}",
    response_model=ResponseEnvelope[PaginatedResponse[InteractionResponse]],
    summary="Get interactions for a session",
    description="Get paginated interaction history for a session.",
)
async def get_session_interactions(
    session_id: UUID,
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PaginatedResponse[InteractionResponse]]:
    """Get interactions for a session."""
    # Verify session exists
    session_result = await db.execute(select(Session).where(Session.id == session_id))
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get total count
    count_result = await db.execute(
        select(Interaction).where(Interaction.session_id == session_id)
    )
    total = len(count_result.scalars().all())

    # Get paginated results
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Interaction)
        .where(Interaction.session_id == session_id)
        .order_by(desc(Interaction.created_at))
        .offset(offset)
        .limit(page_size)
    )
    interactions = result.scalars().all()

    items = [InteractionResponse.model_validate(i) for i in interactions]

    return ResponseEnvelope(
        success=True,
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        ),
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )


@router.get(
    "/{interaction_id}",
    response_model=ResponseEnvelope[InteractionResponse],
    summary="Get interaction by ID",
    description="Get a specific interaction with full details.",
)
async def get_interaction(
    interaction_id: UUID,
    request: Request,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[InteractionResponse]:
    """Get interaction by ID."""
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction {interaction_id} not found",
        )

    return ResponseEnvelope(
        success=True,
        data=InteractionResponse.model_validate(interaction),
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )