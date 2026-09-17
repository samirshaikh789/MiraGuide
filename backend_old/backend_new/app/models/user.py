"""User and Accessibility Preference Models"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
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
    preferences: Mapped[Optional["AccessibilityPreference"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id})>"


class AccessibilityPreference(Base):
    """User accessibility preferences."""

    __tablename__ = "accessibility_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    # Visual
    font_scale: Mapped[float] = mapped_column(default=1.0)
    high_contrast: Mapped[bool] = mapped_column(default=False)
    dark_mode: Mapped[bool] = mapped_column(default=False)
    reduce_motion: Mapped[bool] = mapped_column(default=False)
    larger_buttons: Mapped[bool] = mapped_column(default=False)

    # Audio
    auto_read: Mapped[bool] = mapped_column(default=False)
    speech_rate: Mapped[float] = mapped_column(default=1.0)
    voice_navigation: Mapped[bool] = mapped_column(default=False)

    # Interface
    simplified_interface: Mapped[bool] = mapped_column(default=False)
    language: Mapped[str] = mapped_column(String(10), default="en")

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
    user: Mapped["User"] = relationship(back_populates="preferences")

    def __repr__(self) -> str:
        return f"<AccessibilityPreference(user_id={self.user_id})>"