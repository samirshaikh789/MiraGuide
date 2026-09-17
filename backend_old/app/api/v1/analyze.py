"""Analyze API endpoints - Core workflows"""

import uuid
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_settings
from app.db.base import get_db
from app.schemas.ai import (
    AnalyzeImageRequest,
    AnalyzeDocumentRequest,
    AnalyzeFormRequest,
    AskQuestionRequest,
    SimplifyTextRequest,
    SummarizeTextRequest,
    ChatRequest,
)
from app.schemas.base import ResponseEnvelope, REQUEST_ID_HEADER
from app.services import ai_service
from app.services.providers import provider_registry

router = APIRouter(prefix="/analyze", tags=["analyze"])
settings = get_settings()

# Allowed MIME types
ALLOWED_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/pdf",
]
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )


@router.post(
    "/image",
    response_model=ResponseEnvelope[dict],
    summary="Analyze image - See & Understand / Visual Q&A",
    description="""
    Analyze an uploaded image for accessibility.
    
    **Workflows:**
    - **See & Understand**: Upload image without question -> describes scene
    - **Visual Q&A**: Upload image WITH question -> answers question about image
    
    Returns structured AI response with intent, summary, details, entities, confidence, etc.
    """,
)
async def analyze_image(
    request: Request,
    image: UploadFile = File(..., description="Image file (JPG, PNG, WebP, GIF)"),
    session_id: str = Form(None, description="Optional session ID for context"),
    question: str = Form(None, description="Optional question about the image (Visual Q&A)"),
    detail_level: str = Form("standard", description="Detail level: brief, standard, detailed"),
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Analyze an image - See & Understand or Visual Q&A."""
    validate_file(image)

    image_data = await image.read()
    session_uuid = UUID(session_id) if session_id else None

    try:
        ai_response, decision, session, interaction = await ai_service.analyze_image(
            image_data=image_data,
            mime_type=image.content_type,
            session_id=session_uuid,
            question=question,
            detail_level=detail_level,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/document",
    response_model=ResponseEnvelope[dict],
    summary="Analyze document - Read & Explain",
    description="""
    Analyze a document image for text extraction and explanation.
    
    **Workflow:**
    - **Read & Explain**: Upload document -> OCR extracts text -> AI explains/simplifies
    
    Returns structured AI response with extracted text, summary, simplification.
    """,
)
async def analyze_document(
    request: Request,
    image: UploadFile = File(..., description="Document image file"),
    session_id: str = Form(None, description="Optional session ID"),
    simplify_level: str = Form("simple", description="Simplification level: simple, very-simple, child"),
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Analyze a document - Read & Explain."""
    validate_file(image)

    image_data = await image.read()
    session_uuid = UUID(session_id) if session_id else None

    try:
        ai_response, decision, session, interaction = await ai_service.analyze_document(
            image_data=image_data,
            mime_type=image.content_type,
            session_id=session_uuid,
            simplify_level=simplify_level,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/form",
    response_model=ResponseEnvelope[dict],
    summary="Analyze form - Form Assist",
    description="""
    Analyze a form image to identify fields, labels, and structure.
    
    **Workflow:**
    - **Form Assist**: Upload form -> AI identifies fields, explains each one
    
    Returns structured AI response with field list, explanations, and guidance.
    """,
)
async def analyze_form(
    request: Request,
    image: UploadFile = File(..., description="Form image file"),
    session_id: str = Form(None, description="Optional session ID"),
    explain_fields: str = Form("true", description="Whether to explain each field"),
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Analyze a form - Form Assist."""
    validate_file(image)

    image_data = await image.read()
    session_uuid = UUID(session_id) if session_id else None
    explain = explain_fields.lower() == "true"

    try:
        ai_response, decision, session, interaction = await ai_service.analyze_form(
            image_data=image_data,
            mime_type=image.content_type,
            session_id=session_uuid,
            explain_fields=explain,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Form analysis failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/ask",
    response_model=ResponseEnvelope[dict],
    summary="Ask about what you see - Visual Q&A follow-up",
    description="""
    Ask a follow-up question about a previously analyzed image/document.
    
    **Workflow:**
    - **Ask About What You See**: Provide session_id + question -> AI uses context
    
    Requires a session_id from a previous image/document analysis.
    """,
)
async def ask_question(
    request: Request,
    question_data: AskQuestionRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Ask a question about previous visual context."""
    try:
        ai_response, decision, session, interaction = await ai_service.ask_question(
            question=question_data.question,
            session_id=question_data.session_id,
            include_context=question_data.include_context,
            request_id=request_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question processing failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/simplify",
    response_model=ResponseEnvelope[dict],
    summary="Simplify text",
    description="Simplify text to a more accessible reading level.",
)
async def simplify_text(
    request: Request,
    simplify_data: SimplifyTextRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Simplify text."""
    try:
        ai_response, decision, session, interaction = await ai_service.simplify_text(
            text=simplify_data.text,
            level=simplify_data.level,
            session_id=simplify_data.session_id,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simplification failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/summarize",
    response_model=ResponseEnvelope[dict],
    summary="Summarize text",
    description="Summarize text with key points.",
)
async def summarize_text(
    request: Request,
    summarize_data: SummarizeTextRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Summarize text."""
    try:
        ai_response, decision, session, interaction = await ai_service.summarize_text(
            text=summarize_data.text,
            session_id=summarize_data.session_id,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.post(
    "/chat",
    response_model=ResponseEnvelope[dict],
    summary="Chat with assistant",
    description="General chat with the accessibility assistant.",
)
async def chat(
    request: Request,
    chat_data: ChatRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Chat with assistant."""
    try:
        ai_response, decision, session, interaction = await ai_service.chat(
            message=chat_data.message,
            session_id=chat_data.session_id,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )


@router.get(
    "/providers",
    response_model=ResponseEnvelope[dict],
    summary="List available AI providers",
    description="Get list of available AI providers for each capability.",
)
async def list_providers(
    request: Request,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
) -> ResponseEnvelope[dict]:
    """List available AI providers."""
    return ResponseEnvelope(
        success=True,
        data={
            "vision": provider_registry.available_vision,
            "text": provider_registry.available_text,
            "ocr": provider_registry.available_ocr,
            "stt": provider_registry.available_stt,
            "tts": provider_registry.available_tts,
        },
        request_id=request_id,
        demo_mode=settings.DEMO_MODE,
    )