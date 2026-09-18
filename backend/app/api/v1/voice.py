"""Voice API endpoints"""

import uuid
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_settings
from app.db.base import get_db
from app.schemas.ai import TranscribeRequest, SynthesizeRequest
from app.schemas.base import ResponseEnvelope, REQUEST_ID_HEADER
from app.services import ai_service

router = APIRouter(prefix="/voice", tags=["voice"])
settings = get_settings()

# Allowed audio MIME types
ALLOWED_AUDIO_MIME_TYPES = [
    "audio/wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
]
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB


def validate_audio(file: UploadFile) -> None:
    """Validate uploaded audio file."""
    if file.size and file.size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file too large. Maximum size is {MAX_AUDIO_SIZE // (1024*1024)}MB",
        )

    if file.content_type not in ALLOWED_AUDIO_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio type. Allowed: {', '.join(ALLOWED_AUDIO_MIME_TYPES)}",
        )


@router.post(
    "/transcribe",
    response_model=ResponseEnvelope[dict],
    summary="Transcribe audio to text",
    description="Convert speech audio to text using STT provider.",
)
async def transcribe_audio(
    request: Request,
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, WebM, OGG)"),
    session_id: str = Form(None, description="Optional session ID"),
    language: str = Form("en", description="Language code (e.g., en, es, fr)"),
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Transcribe audio to text."""
    validate_audio(audio)

    audio_data = await audio.read()
    session_uuid = UUID(session_id) if session_id else None

    try:
        ai_response, decision, session, interaction = await ai_service.transcribe(
            audio_data=audio_data,
            mime_type=audio.content_type,
            session_id=session_uuid,
            language=language,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
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
    "/synthesize",
    response_model=ResponseEnvelope[dict],
    summary="Synthesize text to speech",
    description="Convert text to speech audio using TTS provider.",
)
async def synthesize_speech(
    request: Request,
    synthesize_data: SynthesizeRequest,
    request_id: str = Header(None, alias=REQUEST_ID_HEADER),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Synthesize text to speech."""
    try:
        ai_response, decision, session, interaction, audio_data = await ai_service.synthesize(
            text=synthesize_data.text,
            voice=synthesize_data.voice,
            speed=synthesize_data.speed,
            session_id=synthesize_data.session_id,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis failed: {str(e)}",
        )

    import base64
    audio_base64 = base64.b64encode(audio_data).decode("utf-8") if audio_data else ""

    return ResponseEnvelope(
        success=True,
        data={
            "session_id": str(session.id),
            "interaction_id": str(interaction.id),
            "ai_response": ai_response.model_dump(),
            "decision": decision.model_dump(),
            "audio_base64": audio_base64,
            "audio_mime_type": "audio/mpeg",
        },
        request_id=request_id,
        demo_mode=ai_response.demo_mode,
    )