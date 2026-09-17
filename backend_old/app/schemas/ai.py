"""AI-related schemas for structured input/output"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import BaseSchema


class IntentType(str, Enum):
    """Intent types for the accessibility decision engine."""

    SEE_UNDERSTAND = "see_understand"
    READ_EXPLAIN = "read_explain"
    FORM_ASSIST = "form_assist"
    VISUAL_QA = "visual_qa"
    SIMPLIFY = "simplify"
    SUMMARIZE = "summarize"
    COMMUNICATE = "communicate"
    CHAT = "chat"
    UNKNOWN = "unknown"


class ResponseMode(str, Enum):
    """Response output mode."""

    TEXT = "text"
    VOICE = "voice"
    TEXT_AND_VOICE = "text_and_voice"
    VISUAL = "visual"


# --- Core AI Output Schemas ---

class Entity(BaseSchema):
    """Extracted entity from AI analysis."""

    type: str = Field(..., description="Entity type (e.g., 'field', 'button', 'text_block', 'sign')")
    label: str = Field(..., description="Human-readable label")
    value: Optional[str] = Field(None, description="Extracted value if applicable")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    bounding_box: Optional[Dict[str, float]] = Field(
        None, description="Relative coordinates {x, y, width, height}"
    )


class ImportantInformation(BaseSchema):
    """Important information item from analysis."""

    label: str = Field(..., description="What this information is")
    value: str = Field(..., description="The information itself")
    priority: int = Field(default=1, ge=1, le=5, description="Priority 1-5")
    source: Optional[str] = Field(None, description="Where this came from (ocr, vision, context)")


class StructuredAIResponse(BaseSchema):
    """Standardized structured AI response - ALL AI outputs must conform to this."""

    intent: IntentType = Field(..., description="Detected or requested intent")
    summary: str = Field(..., description="Human-readable summary")
    details: List[str] = Field(default_factory=list, description="Detailed points")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    important_information: List[ImportantInformation] = Field(
        default_factory=list, description="Key information for user"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    needs_clarification: bool = Field(False, description="Whether clarification is needed")
    clarification_question: Optional[str] = Field(
        None, description="Question to ask user if clarification needed"
    )
    safety_note: Optional[str] = Field(None, description="Safety warning if applicable")
    response_mode: ResponseMode = Field(
        default=ResponseMode.TEXT, description="Recommended response mode"
    )
    follow_up_suggestions: List[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )

    # Provider metadata
    provider: str = Field(..., description="AI provider used")
    model: str = Field(..., description="Model used")
    processing_time_ms: int = Field(..., description="Processing time")
    demo_mode: bool = Field(False, description="Whether this is a demo response")


class DecisionEngineResult(BaseSchema):
    """Result from the Accessibility Decision Engine."""

    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_clarification: bool
    clarification_question: Optional[str] = None
    response_mode: ResponseMode
    safety_concerns: List[str] = Field(default_factory=list)
    recommended_workflow: str
    context_used: bool = False


# --- API Request/Response Schemas ---

class AnalyzeImageRequest(BaseSchema):
    """Request for image analysis."""

    session_id: Optional[UUID] = None
    question: Optional[str] = Field(
        None, description="Optional question about the image (for Visual Q&A)"
    )
    detail_level: str = Field(
        default="standard", description="Detail level: brief, standard, detailed"
    )


class AnalyzeDocumentRequest(BaseSchema):
    """Request for document analysis."""

    session_id: Optional[UUID] = None
    simplify_level: str = Field(
        default="simple", description="Simplification level: simple, very-simple, child"
    )


class AnalyzeFormRequest(BaseSchema):
    """Request for form analysis."""

    session_id: Optional[UUID] = None
    explain_fields: bool = Field(
        default=True, description="Whether to explain each field"
    )


class AskQuestionRequest(BaseSchema):
    """Request for visual question answering."""

    session_id: UUID
    question: str = Field(..., min_length=1, max_length=2000)
    include_context: bool = Field(
        default=True, description="Whether to include previous visual context"
    )


class SimplifyTextRequest(BaseSchema):
    """Request for text simplification."""

    text: str = Field(..., min_length=1, max_length=10000)
    level: str = Field(default="simple", description="simple, very-simple, child")
    session_id: Optional[UUID] = None


class SummarizeTextRequest(BaseSchema):
    """Request for text summarization."""

    text: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[UUID] = None


class ChatRequest(BaseSchema):
    """Chat request."""

    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[UUID] = None


class SessionCreateRequest(BaseSchema):
    """Create session request."""

    user_id: Optional[UUID] = None


class SessionResponse(BaseSchema):
    """Session response."""

    id: UUID
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    context_data: Optional[str] = None


class InteractionResponse(BaseSchema):
    """Interaction response."""

    id: UUID
    session_id: UUID
    input_type: str
    intent: str
    question: Optional[str]
    response: Optional[str]
    structured_response: Optional[str]
    confidence: float
    needs_clarification: bool
    clarification_question: Optional[str]
    safety_note: Optional[str]
    created_at: datetime


# --- Voice Schemas ---

class TranscribeRequest(BaseSchema):
    """Transcribe audio request."""

    session_id: Optional[UUID] = None
    language: str = Field(default="en", description="Language code")


class SynthesizeRequest(BaseSchema):
    """Text-to-speech request."""

    text: str = Field(..., min_length=1, max_length=5000)
    voice: Optional[str] = Field(None, description="Voice identifier")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    session_id: Optional[UUID] = None


# --- Demo Mode Schemas ---

class DemoResponse(BaseSchema):
    """Demo mode response indicator."""

    demo_mode: bool = True
    notice: str = "This is a simulated result for the MiraGuide demo; please verify important details independently."