"""Session and Interaction Models"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InputType(PyEnum):
    """Type of input for an interaction."""

    IMAGE = "image"
    DOCUMENT = "document"
    FORM = "form"
    TEXT = "text"
    VOICE = "voice"
    QUESTION = "question"


class IntentType(PyEnum):
    """Detected intent type."""

    SEE_UNDERSTAND = "see_understand"
    READ_EXPLAIN = "read_explain"
    FORM_ASSIST = "form_assist"
    VISUAL_QA = "visual_qa"
    SIMPLIFY = "simplify"
    SUMMARIZE = "summarize"
    COMMUNICATE = "communicate"
    CHAT = "chat"
    UNKNOWN = "unknown"


class ProcessingStatus(PyEnum):
    """Processing status for input metadata."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(Base):
    """User session for maintaining context."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Session context (stored as JSON)
    context_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    interactions: Mapped[list["Interaction"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Interaction.created_at"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id})>"


class Interaction(Base):
    """Single interaction within a session."""

    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Input
    input_type: Mapped[InputType] = mapped_column(Enum(InputType), nullable=False)
    intent: Mapped[IntentType] = mapped_column(Enum(IntentType), default=IntentType.UNKNOWN)
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI Response
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Confidence & Safety
    confidence: Mapped[float] = mapped_column(default=0.0)
    needs_clarification: Mapped[bool] = mapped_column(default=False)
    clarification_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    safety_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    processing_time_ms: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="interactions")
    input_metadata: Mapped[list["InputMetadata"]] = relationship(
        back_populates="interaction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, intent={self.intent.value})>"


class InputMetadata(Base):
    """Metadata about uploaded/processed input files."""

    __tablename__ = "input_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False
    )

    input_type: Mapped[str] = mapped_column(String(32), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(default=0)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File reference (temporary path or identifier)
    file_reference: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    interaction: Mapped["Interaction"] = relationship(back_populates="input_metadata")

    def __repr__(self) -> str:
        return f"<InputMetadata(id={self.id}, type={self.input_type})>"