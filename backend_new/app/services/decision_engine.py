"""Accessibility Decision Engine - Core differentiator for MiraGuide"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from app.schemas.ai import (
    DecisionEngineResult,
    IntentType,
    ResponseMode,
    StructuredAIResponse,
)
from app.models.session import Session, Interaction
from app.services.providers import provider_registry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


@dataclass
class DecisionContext:
    """Context for decision making."""

    user_question: Optional[str] = None
    has_image: bool = False
    has_document: bool = False
    has_form: bool = False
    session_context: Optional[str] = None
    previous_intent: Optional[IntentType] = None
    user_preferences: Optional[Dict] = None


class AccessibilityDecisionEngine:
    """
    Core decision engine that determines:
    - User intent
    - Task type
    - Relevant information
    - Response format
    - Whether clarification is needed
    - Whether confidence is sufficient
    """

    # Intent detection keywords
    INTENT_KEYWORDS = {
        IntentType.SEE_UNDERSTAND: [
            "see", "describe", "what is", "what's in", "scene", "surroundings",
            "environment", "look at", "image", "picture", "photo", "camera",
            "around me", "where am i", "what do you see"
        ],
        IntentType.READ_EXPLAIN: [
            "read", "text", "document", "sign", "label", "notice", "letter",
            "extract", "ocr", "what does it say", "what's written", "menu",
            "receipt", "prescription", "instructions"
        ],
        IntentType.FORM_ASSIST: [
            "form", "application", "fill out", "fill in", "field", "fields",
            "required", "optional", "checkbox", "dropdown", "select",
            "submit", "application form", "registration"
        ],
        IntentType.VISUAL_QA: [
            "what does this", "what is this", "which", "where is", "find",
            "locate", "identify", "tell me about", "explain this",
            "what about", "more about", "detail"
        ],
        IntentType.SIMPLIFY: [
            "simplify", "make simpler", "easier to understand", "plain language",
            "plain english", "dumb down", "explain simply", "break down"
        ],
        IntentType.SUMMARIZE: [
            "summarize", "summary", "key points", "main points", "tl;dr",
            "short version", "condense", "brief"
        ],
        IntentType.COMMUNICATE: [
            "communicate", "say", "tell them", "message", "phrase",
            "help me say", "help me tell", "express", "convey"
        ],
    }

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.85
    MEDIUM_CONFIDENCE = 0.65
    LOW_CONFIDENCE = 0.45

    def __init__(self):
        pass  # providers are fetched lazily to avoid init-order issues

    async def detect_intent(
        self,
        question: Optional[str],
        has_image: bool,
        has_document: bool,
        session: Optional[Session] = None,
    ) -> Tuple[IntentType, float]:
        """
        Detect user intent from question and context.
        Returns (intent, confidence).
        """
        # If there's a visual question with image/document, it's visual QA
        if question and (has_image or has_document):
            # Check if it's specifically about a form
            if has_document and any(kw in question.lower() for kw in ["form", "field", "fill"]):
                return IntentType.FORM_ASSIST, 0.9

            # Visual Q&A takes precedence when there's a question + visual input
            return IntentType.VISUAL_QA, 0.85

        # If image without question -> See & Understand
        if has_image and not question:
            return IntentType.SEE_UNDERSTAND, 0.9

        # If document without question -> Read & Explain
        if has_document and not question:
            return IntentType.READ_EXPLAIN, 0.9

        # If form without question -> Form Assist
        if has_form:
            return IntentType.FORM_ASSIST, 0.9

        # Text-only question - use keyword matching
        if question:
            return self._keyword_intent_detection(question)

        # Default to chat
        return IntentType.CHAT, 0.5

    def _keyword_intent_detection(self, question: str) -> Tuple[IntentType, float]:
        """Detect intent from keywords in question."""
        question_lower = question.lower()
        scores: Dict[IntentType, int] = {intent: 0 for intent in IntentType}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in question_lower:
                    scores[intent] += 1

        # Get highest scoring intent
        if max(scores.values()) > 0:
            best_intent = max(scores, key=scores.get)
            # Confidence based on keyword matches
            confidence = min(0.5 + (scores[best_intent] * 0.15), 0.85)
            return best_intent, confidence

        return IntentType.CHAT, 0.5

    async def evaluate_confidence(
        self,
        ai_response: StructuredAIResponse,
        context: DecisionContext,
    ) -> Tuple[float, bool, Optional[str]]:
        """
        Evaluate if AI response confidence is sufficient.
        Returns (adjusted_confidence, needs_clarification, clarification_question).
        """
        base_confidence = ai_response.confidence

        # Adjust based on context
        adjustments = 0.0

        # Lower confidence for demo mode
        if ai_response.demo_mode:
            adjustments -= 0.2

        # Lower confidence if safety note present
        if ai_response.safety_note:
            adjustments -= 0.1

        # Lower confidence for complex intents without clarification
        if ai_response.intent in [IntentType.FORM_ASSIST, IntentType.VISUAL_QA]:
            if not ai_response.entities and not ai_response.important_information:
                adjustments -= 0.15

        # Higher confidence if context was used
        if context.session_context:
            adjustments += 0.05

        adjusted = max(0.0, min(1.0, base_confidence + adjustments))

        # Determine if clarification needed
        needs_clarification = False
        clarification_question = None

        if adjusted < self.MEDIUM_CONFIDENCE:
            needs_clarification = True
            clarification_question = self._generate_clarification_question(
                ai_response.intent, adjusted
            )
        elif ai_response.intent == IntentType.FORM_ASSIST and adjusted < self.HIGH_CONFIDENCE:
            # Forms need high confidence
            needs_clarification = True
            clarification_question = "I'm not completely certain about all the fields. Would you like me to explain what I found, or would you prefer to try a clearer image?"

        return adjusted, needs_clarification, clarification_question

    def _generate_clarification_question(
        self,
        intent: IntentType,
        confidence: float,
    ) -> str:
        """Generate appropriate clarification question."""
        questions = {
            IntentType.SEE_UNDERSTAND: "Could you tell me what specific aspect you'd like me to focus on?",
            IntentType.READ_EXPLAIN: "Would you like me to read the full text or just the key information?",
            IntentType.FORM_ASSIST: "Should I explain each field one by one, or give you an overview first?",
            IntentType.VISUAL_QA: "Could you rephrase your question or tell me what specific detail you're looking for?",
            IntentType.SIMPLIFY: "What reading level would work best for you?",
            IntentType.SUMMARIZE: "Would you like a brief summary or more detail?",
            IntentType.COMMUNICATE: "Who is this message for, and what's the most important thing to convey?",
        }
        return questions.get(intent, "Could you clarify what you'd like help with?")

    def determine_response_mode(
        self,
        intent: IntentType,
        confidence: float,
        user_preferences: Optional[Dict] = None,
    ) -> ResponseMode:
        """Determine the best response mode."""
        # Check user preferences
        if user_preferences:
            if user_preferences.get("voice_navigation") or user_preferences.get("auto_read"):
                if intent in [IntentType.SEE_UNDERSTAND, IntentType.READ_EXPLAIN, IntentType.VISUAL_QA]:
                    return ResponseMode.TEXT_AND_VOICE

        # Default modes by intent
        mode_map = {
            IntentType.SEE_UNDERSTAND: ResponseMode.TEXT_AND_VOICE,
            IntentType.READ_EXPLAIN: ResponseMode.TEXT_AND_VOICE,
            IntentType.FORM_ASSIST: ResponseMode.TEXT,
            IntentType.VISUAL_QA: ResponseMode.TEXT_AND_VOICE,
            IntentType.SIMPLIFY: ResponseMode.TEXT,
            IntentType.SUMMARIZE: ResponseMode.TEXT,
            IntentType.COMMUNICATE: ResponseMode.TEXT_AND_VOICE,
            IntentType.CHAT: ResponseMode.TEXT,
        }
        return mode_map.get(intent, ResponseMode.TEXT)

    async def process_request(
        self,
        question: Optional[str],
        has_image: bool,
        has_document: bool,
        has_form: bool,
        session: Optional[Session] = None,
        user_preferences: Optional[Dict] = None,
    ) -> DecisionEngineResult:
        """
        Main entry point: process a request through the decision engine.
        """
        # Get session context
        session_context = None
        previous_intent = None
        if session:
            session_context = session.context_data
            # Get last interaction intent
            if session.interactions:
                last = session.interactions[-1]
                if last.intent:
                    previous_intent = last.intent

        # Detect intent
        intent, intent_confidence = await self.detect_intent(
            question, has_image, has_document, session
        )

        # Create context
        context = DecisionContext(
            user_question=question,
            has_image=has_image,
            has_document=has_document,
            has_form=has_form,
            session_context=session_context,
            previous_intent=previous_intent,
            user_preferences=user_preferences,
        )

        # Determine response mode
        response_mode = self.determine_response_mode(intent, intent_confidence, user_preferences)

        # Check for safety concerns
        safety_concerns = []
        if intent == IntentType.FORM_ASSIST and intent_confidence < self.HIGH_CONFIDENCE:
            safety_concerns.append("Form field detection uncertain - verify with original")
        if intent == IntentType.READ_EXPLAIN and intent_confidence < self.MEDIUM_CONFIDENCE:
            safety_concerns.append("Text extraction confidence low - verify critical information")

        # Determine recommended workflow
        workflow_map = {
            IntentType.SEE_UNDERSTAND: "analyze_image",
            IntentType.READ_EXPLAIN: "analyze_document",
            IntentType.FORM_ASSIST: "analyze_form",
            IntentType.VISUAL_QA: "answer_visual_question",
            IntentType.SIMPLIFY: "simplify_text",
            IntentType.SUMMARIZE: "summarize_text",
            IntentType.COMMUNICATE: "communicate",
            IntentType.CHAT: "chat",
        }

        return DecisionEngineResult(
            intent=intent,
            confidence=intent_confidence,
            requires_clarification=intent_confidence < self.MEDIUM_CONFIDENCE,
            clarification_question=self._generate_clarification_question(intent, intent_confidence)
            if intent_confidence < self.MEDIUM_CONFIDENCE
            else None,
            response_mode=response_mode,
            safety_concerns=safety_concerns,
            recommended_workflow=workflow_map.get(intent, "chat"),
            context_used=bool(session_context),
        )

    async def evaluate_ai_response(
        self,
        ai_response: StructuredAIResponse,
        context: DecisionContext,
    ) -> Tuple[StructuredAIResponse, DecisionEngineResult]:
        """
        Evaluate an AI response and potentially adjust it.
        Returns (adjusted_response, decision_result).
        """
        # Evaluate confidence
        adjusted_confidence, needs_clarification, clarification_question = await self.evaluate_confidence(
            ai_response, context
        )

        # Adjust response if needed
        if needs_clarification and not ai_response.needs_clarification:
            ai_response.needs_clarification = True
            ai_response.clarification_question = clarification_question
            ai_response.confidence = adjusted_confidence

        # Create decision result
        decision = DecisionEngineResult(
            intent=ai_response.intent,
            confidence=adjusted_confidence,
            requires_clarification=needs_clarification,
            clarification_question=clarification_question,
            response_mode=ai_response.response_mode,
            safety_concerns=[ai_response.safety_note] if ai_response.safety_note else [],
            recommended_workflow="",
            context_used=bool(context.session_context),
        )

        return ai_response, decision


# Global instance
decision_engine = AccessibilityDecisionEngine()