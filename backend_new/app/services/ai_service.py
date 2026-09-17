"""Main AI Service - Orchestrates providers, decision engine, and sessions"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_db
from app.models.user import User
from app.models.session import (
    Session,
    Interaction,
    InputMetadata,
    InputType,
    IntentType,
    ProcessingStatus,
)
from app.schemas.ai import (
    StructuredAIResponse,
    DecisionEngineResult,
    IntentType as SchemaIntentType,
    ResponseMode,
)
from app.services.providers import provider_registry, ProviderResult
from app.services.decision_engine import decision_engine, AccessibilityDecisionEngine
from app.services.demo_providers import register_demo_providers

logger = logging.getLogger(__name__)


class AIService:
    """Main AI service orchestrating all AI capabilities."""

    def __init__(self):
        self.settings = get_settings()
        self._initialized = False

    async def initialize(self):
        """Initialize providers and register demo providers."""
        if self._initialized:
            return

        # Always register demo providers as fallback
        register_demo_providers()

        # Register real providers if API keys available
        if self.settings.OPENAI_API_KEY:
            try:
                from app.services.openai_provider import OpenAIProvider
                openai_provider = OpenAIProvider()
                provider_registry.register_vision("openai", openai_provider, default=True)
                provider_registry.register_text("openai", openai_provider, default=True)
                provider_registry.register_ocr("openai", openai_provider, default=True)
                provider_registry.register_stt("openai", openai_provider, default=True)
                provider_registry.register_tts("openai", openai_provider, default=True)
                logger.info("Registered OpenAI providers")
            except Exception as e:
                logger.warning(f"Failed to register OpenAI providers: {e}")

        # TODO: Add Gemini and Anthropic providers when implemented

        self._initialized = True
        logger.info(f"AI Service initialized. Demo mode: {self.settings.DEMO_MODE}")

    async def _get_or_create_user(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None,
    ) -> User:
        """Get existing user or create new one."""
        if user_id:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user

        # Create new user
        user = User(id=user_id or uuid.uuid4())
        db.add(user)
        await db.flush()
        return user

    async def _get_or_create_session(
        self,
        db: AsyncSession,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> Session:
        """Get existing session or create new one (auto-creates user if needed)."""
        if session_id:
            result = await db.execute(select(Session).where(Session.id == session_id))
            session = result.scalar_one_or_none()
            if session:
                return session

        # Need a valid user first (FK constraint)
        user = await self._get_or_create_user(db, user_id)

        # Create new session
        session = Session(user_id=user.id)
        db.add(session)
        await db.flush()
        return session

    async def _save_interaction(
        self,
        db: AsyncSession,
        session: Session,
        input_type: InputType,
        intent: IntentType,
        question: Optional[str],
        ai_response: StructuredAIResponse,
        decision: DecisionEngineResult,
        input_metadata: List[InputMetadata],
        processing_time_ms: int,
        request_id: str,
    ) -> Interaction:
        """Save interaction to database."""
        interaction = Interaction(
            session_id=session.id,
            input_type=input_type,
            intent=intent,
            question=question,
            response=ai_response.summary,
            structured_response=ai_response.model_dump_json(),
            confidence=ai_response.confidence,
            needs_clarification=ai_response.needs_clarification,
            clarification_question=ai_response.clarification_question,
            safety_note=ai_response.safety_note,
            request_id=request_id,
            processing_time_ms=processing_time_ms,
        )
        db.add(interaction)
        await db.flush()

        # Link input metadata
        for meta in input_metadata:
            meta.interaction_id = interaction.id
            db.add(meta)

        # Update session context with latest interaction summary
        session.context_data = self._build_context(session, interaction)
        session.updated_at = datetime.utcnow()

        await db.commit()
        return interaction

    def _build_context(self, session: Session, latest: Interaction) -> str:
        """Build context string from session interactions."""
        # Include last 3 interactions
        recent = session.interactions[-3:] if session.interactions else []
        context_parts = []
        for interaction in recent:
            if interaction.structured_response:
                try:
                    import json
                    data = json.loads(interaction.structured_response)
                    context_parts.append(
                        f"[{interaction.intent.value}] {data.get('summary', interaction.response)}"
                    )
                except Exception:
                    context_parts.append(f"[{interaction.intent.value}] {interaction.response}")
        return "\n".join(context_parts)

    def _create_input_metadata(
        self,
        input_type: InputType,
        mime_type: Optional[str],
        size_bytes: int,
        file_reference: Optional[str] = None,
    ) -> InputMetadata:
        """Create input metadata record."""
        return InputMetadata(
            input_type=input_type.value,
            mime_type=mime_type,
            size_bytes=size_bytes,
            processing_status=ProcessingStatus.COMPLETED,
            file_reference=file_reference,
        )

    async def _run_provider_with_fallback(
        self,
        provider_type: str,
        method_name: str,
        *args,
        **kwargs,
    ) -> ProviderResult:
        """Run provider method with fallback to demo."""
        provider = provider_registry.get_text()  # Default to text provider for now

        # Get the specific provider
        if provider_type == "vision":
            provider = provider_registry.get_vision()
        elif provider_type == "text":
            provider = provider_registry.get_text()
        elif provider_type == "ocr":
            provider = provider_registry.get_ocr()
        elif provider_type == "stt":
            provider = provider_registry.get_stt()
        elif provider_type == "tts":
            provider = provider_registry.get_tts()

        method = getattr(provider, method_name, None)
        if not method:
            return ProviderResult(success=False, error=f"Method {method_name} not found on {provider_type} provider")

        try:
            result = await method(*args, **kwargs)
            if result.success:
                return result
        except Exception as e:
            logger.warning(f"Provider {provider_type}.{method_name} failed: {e}")

        # Fallback to demo
        demo_provider = provider_registry.get_vision("demo") if provider_type == "vision" else \
                       provider_registry.get_text("demo") if provider_type == "text" else \
                       provider_registry.get_ocr("demo") if provider_type == "ocr" else \
                       provider_registry.get_stt("demo") if provider_type == "stt" else \
                       provider_registry.get_tts("demo")

        demo_method = getattr(demo_provider, method_name)
        return await demo_method(*args, **kwargs)

    # --- Public API Methods ---

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        question: Optional[str] = None,
        detail_level: str = "standard",
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """
        Analyze an image - See & Understand workflow or Visual Q&A.
        """
        await self.initialize()

        # Use provided database session or create our own
        if db is not None:
            session = await self._get_or_create_session(db, session_id, user_id)
            return await self._analyze_image_with_session(
                db, session, image_data, mime_type, question, detail_level, request_id
            )
        else:
            async for db_session in get_db():
                session = await self._get_or_create_session(db_session, session_id, user_id)
                return await self._analyze_image_with_session(
                    db_session, session, image_data, mime_type, question, detail_level, request_id
                )

        # Should never reach here
        raise RuntimeError("Database session not available")

    async def _analyze_image_with_session(
        self,
        db: AsyncSession,
        session: Session,
        image_data: bytes,
        mime_type: str,
        question: Optional[str],
        detail_level: str,
        request_id: Optional[str],
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Internal method to analyze image with a given database session."""
        # Determine intent
        has_form = False  # Could detect from image analysis
        intent_type = IntentType.VISUAL_QA if question else IntentType.SEE_UNDERSTAND

        # Run decision engine
        decision = await decision_engine.process_request(
            question=question,
            has_image=True,
            has_document=False,
            has_form=has_form,
            session=session,
        )

        # Call vision provider
        if question:
            provider_result = await self._run_provider_with_fallback(
                "vision", "answer_visual_question",
                image_data, mime_type, question, session.context_data
            )
        else:
            provider_result = await self._run_provider_with_fallback(
                "vision", "analyze_image",
                image_data, mime_type, None, detail_level
            )

        if not provider_result.success:
            # Return error response
            ai_response = StructuredAIResponse(
                intent=intent_type,
                summary="I couldn't analyze this image. Please try again.",
                details=[provider_result.error or "Unknown error"],
                confidence=0.0,
                needs_clarification=True,
                clarification_question="Could you try uploading a clearer image?",
                provider="error",
                model="none",
                processing_time_ms=provider_result.processing_time_ms,
                demo_mode=False,
            )
            decision.requires_clarification = True
            decision.clarification_question = ai_response.clarification_question
        else:
            ai_response = provider_result.data

        # Evaluate with decision engine
        context = type('Context', (), {
            'session_context': session.context_data,
            'user_question': question,
        })()
        adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
            ai_response, context
        )

        # Save interaction
        input_meta = self._create_input_metadata(
            InputType.IMAGE, mime_type, len(image_data)
        )
        interaction = await self._save_interaction(
            db, session, InputType.IMAGE, adjusted_response.intent,
            question, adjusted_response, final_decision,
            [input_meta], adjusted_response.processing_time_ms,
            request_id or str(uuid.uuid4())
        )

        return adjusted_response, final_decision, session, interaction

    async def analyze_document(
        self,
        image_data: bytes,
        mime_type: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        simplify_level: str = "simple",
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """
        Analyze a document - Read & Explain workflow.
        """
        await self.initialize()

        # Use provided database session or create our own
        if db is not None:
            session = await self._get_or_create_session(db, session_id, user_id)
            return await self._analyze_document_with_session(
                db, session, image_data, mime_type, simplify_level, request_id
            )
        else:
            async for db_session in get_db():
                session = await self._get_or_create_session(db_session, session_id, user_id)
                return await self._analyze_document_with_session(
                    db_session, session, image_data, mime_type, simplify_level, request_id
                )

        # Should never reach here
        raise RuntimeError("Database session not available")

    async def _analyze_document_with_session(
        self,
        db: AsyncSession,
        session: Session,
        image_data: bytes,
        mime_type: str,
        simplify_level: str,
        request_id: Optional[str],
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        decision = await decision_engine.process_request(
            question=None,
            has_image=False,
            has_document=True,
            has_form=False,
            session=session,
        )

        # Extract text via OCR
        ocr_result = await self._run_provider_with_fallback(
            "ocr", "extract_text", image_data, mime_type
        )

        if not ocr_result.success:
            ai_response = StructuredAIResponse(
                intent=IntentType.READ_EXPLAIN,
                summary="I couldn't extract text from this document.",
                details=[ocr_result.error or "Unknown error"],
                confidence=0.0,
                needs_clarification=True,
                clarification_question="Could you try a clearer photo of the document?",
                provider="error",
                model="none",
                processing_time_ms=ocr_result.processing_time_ms,
                demo_mode=False,
            )
            decision.requires_clarification = True
            decision.clarification_question = ai_response.clarification_question
        else:
            ai_response = ocr_result.data
            ai_response.intent = IntentType.READ_EXPLAIN

            # Also simplify if requested
            if simplify_level != "simple":
                simplify_result = await self._run_provider_with_fallback(
                    "text", "simplify", ai_response.summary, simplify_level
                )
                if simplify_result.success:
                    ai_response = simplify_result.data
                    ai_response.intent = IntentType.READ_EXPLAIN

        # Evaluate
        context = type('Context', (), {'session_context': session.context_data})()
        adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
            ai_response, context
        )

        # Save
        input_meta = self._create_input_metadata(
            InputType.DOCUMENT, mime_type, len(image_data)
        )
        interaction = await self._save_interaction(
            db, session, InputType.DOCUMENT, adjusted_response.intent,
            None, adjusted_response, final_decision,
            [input_meta], adjusted_response.processing_time_ms,
            request_id or str(uuid.uuid4())
        )

        return adjusted_response, final_decision, session, interaction

    async def analyze_form(
        self,
        image_data: bytes,
        mime_type: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        explain_fields: bool = True,
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """
        Analyze a form - Form Assist workflow.
        """
        await self.initialize()

        # Use provided database session or create our own
        if db is not None:
            session = await self._get_or_create_session(db, session_id, user_id)
            return await self._analyze_form_with_session(
                db, session, image_data, mime_type, explain_fields, request_id
            )
        else:
            async for db_session in get_db():
                session = await self._get_or_create_session(db_session, session_id, user_id)
                return await self._analyze_form_with_session(
                    db_session, session, image_data, mime_type, explain_fields, request_id
                )

        # Should never reach here
        raise RuntimeError("Database session not available")

    async def _analyze_form_with_session(
        self,
        db: AsyncSession,
        session: Session,
        image_data: bytes,
        mime_type: str,
        explain_fields: bool,
        request_id: Optional[str],
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Internal method to analyze a form image."""
        decision = await decision_engine.process_request(
            question=None,
            has_image=False,
            has_document=False,
            has_form=True,
            session=session,
        )

        # Use OCR structured extraction for form fields
        ocr_result = await self._run_provider_with_fallback(
            "ocr", "extract_structured", image_data, mime_type
        )

        if not ocr_result.success:
            ai_response = StructuredAIResponse(
                intent=IntentType.FORM_ASSIST,
                summary="I couldn't analyze this form.",
                details=[ocr_result.error or "Unknown error"],
                confidence=0.0,
                needs_clarification=True,
                clarification_question="Could you try a clearer photo of the form?",
                provider="error",
                model="none",
                processing_time_ms=ocr_result.processing_time_ms,
                demo_mode=False,
            )
            decision.requires_clarification = True
            decision.clarification_question = ai_response.clarification_question
        else:
            ai_response = ocr_result.data
            ai_response.intent = IntentType.FORM_ASSIST

        # Evaluate
        context = type('Context', (), {'session_context': session.context_data})()
        adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
            ai_response, context
        )

        # Save
        input_meta = self._create_input_metadata(
            InputType.FORM, mime_type, len(image_data)
        )
        interaction = await self._save_interaction(
            db, session, InputType.FORM, adjusted_response.intent,
            None, adjusted_response, final_decision,
            [input_meta], adjusted_response.processing_time_ms,
            request_id or str(uuid.uuid4())
        )

        return adjusted_response, final_decision, session, interaction

    async def ask_question(
        self,
        question: str,
        session_id: UUID,
        include_context: bool = True,
        request_id: Optional[str] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """
        Ask a question about previous visual context - Visual Q&A follow-up.
        """
        await self.initialize()

        async for db in get_db():
            result = await db.execute(select(Session).where(Session.id == session_id))
            session = result.scalar_one_or_none()
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Get context from session
            context_data = session.context_data if include_context else None

            # Determine if this is a follow-up to visual content
            has_visual_context = bool(session.context_data)
            intent_type = IntentType.VISUAL_QA if has_visual_context else IntentType.CHAT

            decision = await decision_engine.process_request(
                question=question,
                has_image=False,
                has_document=False,
                has_form=False,
                session=session,
            )

            # Use text provider with context
            provider_result = await self._run_provider_with_fallback(
                "text", "chat", question, context_data
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=intent_type,
                    summary="I couldn't process your question.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    needs_clarification=True,
                    clarification_question="Could you try rephrasing your question?",
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
                decision.requires_clarification = True
                decision.clarification_question = ai_response.clarification_question
            else:
                ai_response = provider_result.data
                ai_response.intent = intent_type

            # Evaluate
            context = type('Context', (), {'session_context': context_data, 'user_question': question})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            # Save
            input_meta = self._create_input_metadata(
                InputType.QUESTION, "text/plain", len(question.encode())
            )
            interaction = await self._save_interaction(
                db, session, InputType.QUESTION, adjusted_response.intent,
                question, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        raise RuntimeError("Database session not available")

    async def simplify_text(
        self,
        text: str,
        level: str = "simple",
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Simplify text."""
        await self.initialize()

        async def _do(db_: AsyncSession):
            session = await self._get_or_create_session(db_, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "text", "simplify", text, level
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.SIMPLIFY,
                    summary="I couldn't simplify this text.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
            else:
                ai_response = provider_result.data

            context = type('Context', (), {'session_context': session.context_data})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.TEXT, "text/plain", len(text.encode())
            )
            interaction = await self._save_interaction(
                db_, session, InputType.TEXT, adjusted_response.intent,
                None, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        if db is not None:
            return await _do(db)

        async for db_ in get_db():
            return await _do(db_)

        raise RuntimeError("Database session not available")

    async def summarize_text(
        self,
        text: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Summarize text."""
        await self.initialize()

        async def _do(db_: AsyncSession):
            session = await self._get_or_create_session(db_, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "text", "summarize", text
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.SUMMARIZE,
                    summary="I couldn't summarize this text.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
            else:
                ai_response = provider_result.data

            context = type('Context', (), {'session_context': session.context_data})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.TEXT, "text/plain", len(text.encode())
            )
            interaction = await self._save_interaction(
                db_, session, InputType.TEXT, adjusted_response.intent,
                None, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        if db is not None:
            return await _do(db)

        async for db_ in get_db():
            return await _do(db_)

        raise RuntimeError("Database session not available")

    async def communicate(
        self,
        message: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Generate communication message."""
        await self.initialize()

        async def _do(db_: AsyncSession):
            session = await self._get_or_create_session(db_, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "text", "communicate", message
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.COMMUNICATE,
                    summary="I couldn't generate a message.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
            else:
                ai_response = provider_result.data

            context = type('Context', (), {'session_context': session.context_data})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.TEXT, "text/plain", len(message.encode())
            )
            interaction = await self._save_interaction(
                db_, session, InputType.TEXT, adjusted_response.intent,
                None, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        if db is not None:
            return await _do(db)

        async for db_ in get_db():
            return await _do(db_)

        raise RuntimeError("Database session not available")

    async def chat(
        self,
        message: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """General chat."""
        await self.initialize()

        async def _do(db_: AsyncSession):
            session = await self._get_or_create_session(db_, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "text", "chat", message, session.context_data
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.CHAT,
                    summary="I couldn't process your message.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
            else:
                ai_response = provider_result.data

            context = type('Context', (), {'session_context': session.context_data, 'user_question': message})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.TEXT, "text/plain", len(message.encode())
            )
            interaction = await self._save_interaction(
                db_, session, InputType.TEXT, adjusted_response.intent,
                message, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        if db is not None:
            return await _do(db)

        async for db_ in get_db():
            return await _do(db_)

        raise RuntimeError("Database session not available")

    async def transcribe(
        self,
        audio_data: bytes,
        mime_type: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        language: str = "en",
        request_id: Optional[str] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction]:
        """Transcribe audio."""
        await self.initialize()

        async for db in get_db():
            session = await self._get_or_create_session(db, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "stt", "transcribe", audio_data, mime_type, language
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.CHAT,
                    summary="I couldn't transcribe the audio.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
            else:
                ai_response = provider_result.data

            context = type('Context', (), {'session_context': session.context_data})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.VOICE, mime_type, len(audio_data)
            )
            interaction = await self._save_interaction(
                db, session, InputType.VOICE, adjusted_response.intent,
                None, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction

        raise RuntimeError("Database session not available")

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult, Session, Interaction, bytes]:
        """Synthesize speech."""
        await self.initialize()

        async for db in get_db():
            session = await self._get_or_create_session(db, session_id, user_id)

            provider_result = await self._run_provider_with_fallback(
                "tts", "synthesize", text, voice, speed
            )

            if not provider_result.success:
                ai_response = StructuredAIResponse(
                    intent=IntentType.CHAT,
                    summary="I couldn't synthesize speech.",
                    details=[provider_result.error or "Unknown error"],
                    confidence=0.0,
                    provider="error",
                    model="none",
                    processing_time_ms=provider_result.processing_time_ms,
                    demo_mode=False,
                )
                audio_data = b""
            else:
                ai_response = provider_result.data
                audio_data = provider_result.raw_response or b""

            context = type('Context', (), {'session_context': session.context_data})()
            adjusted_response, final_decision = await decision_engine.evaluate_ai_response(
                ai_response, context
            )

            input_meta = self._create_input_metadata(
                InputType.VOICE, "audio/mpeg", len(audio_data)
            )
            interaction = await self._save_interaction(
                db, session, InputType.VOICE, adjusted_response.intent,
                None, adjusted_response, final_decision,
                [input_meta], adjusted_response.processing_time_ms,
                request_id or str(uuid.uuid4())
            )

            return adjusted_response, final_decision, session, interaction, audio_data

        raise RuntimeError("Database session not available")


# Global instance
ai_service = AIService()