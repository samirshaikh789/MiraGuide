"""Demo AI Providers - Used when no real API keys are configured"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from app.services.providers import (
    VisionProvider,
    TextProvider,
    OCRProvider,
    SpeechToTextProvider,
    TextToSpeechProvider,
    ProviderResult,
    provider_registry,
)
from app.schemas.ai import (
    StructuredAIResponse,
    IntentType,
    ResponseMode,
    Entity,
    ImportantInformation,
)


class DemoVisionProvider(VisionProvider):
    """Demo vision provider - returns realistic but simulated responses."""

    def __init__(self):
        super().__init__("demo", demo_mode=True)
        self._responses = {
            "see_understand": [
                "I can see a well-lit indoor hallway. There's a door on the left marked 'Exit' and a staircase ahead on the right with a handrail. The floor appears to be tile. I cannot verify exact distances or obstacles from this image.",
                "This appears to be a kitchen counter with various items. I can see a microwave on the left, a coffee maker in the center, and some cabinets above. There's text on the microwave but it's too small to read clearly.",
                "The image shows a street crossing with a pedestrian signal. The walk signal is showing a white walking figure. There are tactile paving strips at the curb. Traffic appears to be stopped.",
            ],
            "visual_qa": [
                "Based on the image, the sign says 'Restroom' with an arrow pointing left. There's also a wheelchair accessible symbol below it.",
                "This section appears to be about emergency exits. The text reads 'Emergency Exit Only - Alarm Will Sound'.",
                "The important information here is the date: 'Effective January 15, 2025' and the notice about changed hours.",
            ],
            "form_assist": [
                "This appears to be a medical intake form. I can identify several fields: 1) Patient Name (required), 2) Date of Birth (required), 3) Insurance Provider, 4) Reason for Visit (required), 5) Known Allergies. There are checkboxes for medical history.",
                "This is a job application form. Fields include: Full Name, Email, Phone, Position Applied For, Availability, Resume Upload. Required fields are marked with asterisks.",
            ],
        }

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        prompt: Optional[str] = None,
        detail_level: str = "standard",
    ) -> ProviderResult:
        await asyncio.sleep(0.5)  # Simulate processing

        # Determine intent from prompt or default
        if prompt and any(w in prompt.lower() for w in ["form", "field", "application"]):
            intent = IntentType.FORM_ASSIST
            responses = self._responses["form_assist"]
        else:
            intent = IntentType.SEE_UNDERSTAND
            responses = self._responses["see_understand"]

        summary = random.choice(responses)

        response = StructuredAIResponse(
            intent=intent,
            summary=summary,
            details=[
                "This is a simulated description for demo purposes",
                "Real AI would analyze the actual image content",
                f"Detail level: {detail_level}",
            ],
            entities=[
                Entity(
                    type="scene",
                    label="Overall scene",
                    value=summary[:100],
                    confidence=0.7,
                )
            ],
            important_information=[
                ImportantInformation(
                    label="Demo Notice",
                    value="This is a simulated result for the MiraGuide demo; please verify important details independently.",
                    priority=1,
                    source="demo",
                )
            ],
            confidence=0.7,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-vision",
            processing_time_ms=500,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=500,
            demo_mode=True,
        )

    async def answer_visual_question(
        self,
        image_data: bytes,
        mime_type: str,
        question: str,
        context: Optional[str] = None,
    ) -> ProviderResult:
        await asyncio.sleep(0.5)

        responses = self._responses["visual_qa"]
        summary = random.choice(responses)

        response = StructuredAIResponse(
            intent=IntentType.VISUAL_QA,
            summary=summary,
            details=[
                f"Question: {question}",
                "This is a simulated answer for demo purposes",
                "Real AI would analyze the image and question together",
            ],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Answer",
                    value=summary,
                    priority=1,
                    source="demo",
                ),
                ImportantInformation(
                    label="Demo Notice",
                    value="This is a simulated result for the MiraGuide demo; please verify important details independently.",
                    priority=1,
                    source="demo",
                ),
            ],
            confidence=0.7,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-vision",
            processing_time_ms=500,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=500,
            demo_mode=True,
        )


class DemoTextProvider(TextProvider):
    """Demo text provider."""

    def __init__(self):
        super().__init__("demo", demo_mode=True)

    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> ProviderResult:
        await asyncio.sleep(0.3)

        lower = message.lower()
        if "help" in lower or "what can" in lower:
            reply = "I can help you: 1) Understand images and scenes, 2) Read and extract text from documents, 3) Fill out forms, 4) Answer questions about what you see, 5) Simplify difficult text, 6) Communicate needs. What would you like to try?"
        elif "see" in lower or "image" in lower or "picture" in lower:
            reply = "For understanding images, use the 'See & Understand' feature. You can upload a photo or take one with your camera."
        elif "read" in lower or "text" in lower or "document" in lower:
            reply = "Use 'Read & Explain' to extract text from documents, signs, or labels. Then I can simplify or summarize it."
        elif "form" in lower:
            reply = "Upload a form image to 'Form Assist' and I'll explain each field and what information is needed."
        else:
            reply = "I'm here to help with accessibility tasks. Try asking about an image, document, or form."

        response = StructuredAIResponse(
            intent=IntentType.CHAT,
            summary=reply,
            details=[reply],
            entities=[],
            important_information=[],
            confidence=0.8,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-text",
            processing_time_ms=300,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=300,
            demo_mode=True,
        )

    async def simplify(
        self,
        text: str,
        level: str = "simple",
    ) -> ProviderResult:
        await asyncio.sleep(0.3)

        prefixes = {
            "simple": "Simplified: ",
            "very-simple": "Very simply: ",
            "child": "In simple words: ",
        }
        prefix = prefixes.get(level, "Simplified: ")

        # Simple word replacement for demo
        simplified = text
        replacements = {
            "contingent upon": "depending on",
            "implementation": "making it happen",
            "utilize": "use",
            "facilitate": "help",
            "pursuant to": "following",
            "in accordance with": "following",
            "subsequently": "later",
            "nevertheless": "but",
        }
        for old, new in replacements.items():
            simplified = simplified.replace(old, new).replace(old.capitalize(), new.capitalize())

        if len(simplified) > 200:
            simplified = simplified[:180] + "..."

        response = StructuredAIResponse(
            intent=IntentType.SIMPLIFY,
            summary=f"Text simplified to {level} level",
            details=[f"{prefix}{simplified}"],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Simplified Text",
                    value=f"{prefix}{simplified}",
                    priority=1,
                    source="demo",
                )
            ],
            confidence=0.8,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-text",
            processing_time_ms=300,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=300,
            demo_mode=True,
        )

    async def summarize(
        self,
        text: str,
    ) -> ProviderResult:
        await asyncio.sleep(0.3)

        sentences = text.split(". ")
        summary = sentences[0] + "." if sentences else text[:100]

        response = StructuredAIResponse(
            intent=IntentType.SUMMARIZE,
            summary=summary,
            details=[summary, "Read the key information first.", "Ask for help if any detail is unclear."],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Summary",
                    value=summary,
                    priority=1,
                    source="demo",
                ),
                ImportantInformation(
                    label="Key Point 1",
                    value="Read the key information first.",
                    priority=2,
                    source="demo",
                ),
                ImportantInformation(
                    label="Key Point 2",
                    value="Ask for help if any detail is unclear.",
                    priority=2,
                    source="demo",
                ),
            ],
            confidence=0.8,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-text",
            processing_time_ms=300,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=300,
            demo_mode=True,
        )

    async def communicate(
        self,
        message: str,
    ) -> ProviderResult:
        await asyncio.sleep(0.3)

        lower = message.lower()
        if "pain" in lower and "stomach" in lower:
            reply = "I have pain in my stomach. Could you please help me explain this to a healthcare professional?"
        elif "help" in lower:
            reply = "I need help. Could you please assist me?"
        elif "hungry" in lower:
            reply = "I am hungry. Could you help me get something to eat?"
        elif "thirsty" in lower:
            reply = "I am thirsty. Could I have something to drink?"
        else:
            reply = f"Could you please help me with this: {message}?"

        response = StructuredAIResponse(
            intent=IntentType.COMMUNICATE,
            summary=reply,
            details=[reply],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Communication Message",
                    value=reply,
                    priority=1,
                    source="demo",
                )
            ],
            confidence=0.8,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT_AND_VOICE,
            provider="demo",
            model="demo-text",
            processing_time_ms=300,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=300,
            demo_mode=True,
        )


class DemoOCRProvider(OCRProvider):
    """Demo OCR provider."""

    def __init__(self):
        super().__init__("demo", demo_mode=True)
        self._texts = [
            "The library will remain closed on Sunday due to maintenance. We apologize for any inconvenience.",
            "EMERGENCY EXIT ONLY - Alarm will sound if opened. Use main entrance for regular access.",
            "Please fill out all required fields marked with *. Name: _______ Date of Birth: _______ Insurance: _______",
            "CAUTION: Wet Floor. Please use alternate route. Maintenance in progress.",
            "Your prescription: Amoxicillin 500mg. Take 1 capsule 3 times daily for 7 days. With food.",
        ]

    async def extract_text(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        await asyncio.sleep(0.5)

        text = random.choice(self._texts)

        response = StructuredAIResponse(
            intent=IntentType.READ_EXPLAIN,
            summary=f"Extracted {len(text)} characters of text",
            details=[text],
            entities=[
                Entity(
                    type="text_block",
                    label="Extracted Text",
                    value=text,
                    confidence=0.7,
                )
            ],
            important_information=[
                ImportantInformation(
                    label="Extracted Text",
                    value=text,
                    priority=1,
                    source="ocr",
                ),
                ImportantInformation(
                    label="Demo Notice",
                    value="This is a simulated OCR result for the MiraGuide demo; verify critical text against the original document.",
                    priority=1,
                    source="demo",
                ),
            ],
            confidence=0.7,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-ocr",
            processing_time_ms=500,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=500,
            demo_mode=True,
        )

    async def extract_structured(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        await asyncio.sleep(0.5)

        text = random.choice(self._texts)

        response = StructuredAIResponse(
            intent=IntentType.FORM_ASSIST,
            summary="Form structure detected",
            details=[text],
            entities=[
                Entity(type="field", label="Name", value="", confidence=0.8),
                Entity(type="field", label="Date of Birth", value="", confidence=0.8),
                Entity(type="field", label="Insurance", value="", confidence=0.7),
            ],
            important_information=[
                ImportantInformation(
                    label="Detected Fields",
                    value="Name (required), Date of Birth (required), Insurance",
                    priority=1,
                    source="ocr",
                ),
            ],
            confidence=0.7,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-ocr",
            processing_time_ms=500,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=500,
            demo_mode=True,
        )


class DemoSTTProvider(SpeechToTextProvider):
    """Demo speech-to-text provider."""

    def __init__(self):
        super().__init__("demo", demo_mode=True)
        self._transcripts = [
            "What does this sign say?",
            "Can you read this document for me?",
            "Help me understand this form.",
            "What is in this image?",
        ]

    async def transcribe(
        self,
        audio_data: bytes,
        mime_type: str,
        language: str = "en",
    ) -> ProviderResult:
        await asyncio.sleep(0.5)

        text = random.choice(self._transcripts)

        response = StructuredAIResponse(
            intent=IntentType.CHAT,
            summary=f"Transcribed: {text}",
            details=[text],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Transcription",
                    value=text,
                    priority=1,
                    source="stt",
                ),
                ImportantInformation(
                    label="Demo Notice",
                    value="This is a simulated transcription for the MiraGuide demo.",
                    priority=1,
                    source="demo",
                ),
            ],
            confidence=0.7,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider="demo",
            model="demo-stt",
            processing_time_ms=500,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=500,
            demo_mode=True,
        )


class DemoTTSProvider(TextToSpeechProvider):
    """Demo text-to-speech provider."""

    def __init__(self):
        super().__init__("demo", demo_mode=True)

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> ProviderResult:
        await asyncio.sleep(0.2)

        # In demo mode, we return a data URI for a silent audio
        # Real implementation would return actual audio bytes
        response = StructuredAIResponse(
            intent=IntentType.CHAT,
            summary="Speech synthesized (demo mode)",
            details=[f"Text: {text[:100]}...", f"Voice: {voice or 'default'}", f"Speed: {speed}x"],
            entities=[],
            important_information=[
                ImportantInformation(
                    label="Audio",
                    value="[Demo mode - no actual audio generated]",
                    priority=1,
                    source="demo",
                )
            ],
            confidence=1.0,
            needs_clarification=False,
            response_mode=ResponseMode.VOICE,
            provider="demo",
            model="demo-tts",
            processing_time_ms=200,
            demo_mode=True,
        )

        return ProviderResult(
            success=True,
            data=response,
            processing_time_ms=200,
            demo_mode=True,
        )


def register_demo_providers():
    """Register all demo providers."""
    provider_registry.register_vision("demo", DemoVisionProvider(), default=True)
    provider_registry.register_text("demo", DemoTextProvider(), default=True)
    provider_registry.register_ocr("demo", DemoOCRProvider(), default=True)
    provider_registry.register_stt("demo", DemoSTTProvider(), default=True)
    provider_registry.register_tts("demo", DemoTTSProvider(), default=True)