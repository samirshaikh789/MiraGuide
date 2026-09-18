"""OpenAI Provider Implementation"""

import asyncio
import base64
import json
import time
from typing import Any, Dict, List, Optional

import httpx
from openai import AsyncOpenAI

from app.services.providers import (
    VisionProvider,
    TextProvider,
    OCRProvider,
    SpeechToTextProvider,
    TextToSpeechProvider,
    ProviderResult,
)
from app.schemas.ai import (
    StructuredAIResponse,
    IntentType,
    ResponseMode,
    Entity,
    ImportantInformation,
)
from app.core.config import get_settings


class OpenAIProvider(VisionProvider, TextProvider, OCRProvider, SpeechToTextProvider, TextToSpeechProvider):
    """OpenAI provider for all AI capabilities."""

    def __init__(self):
        settings = get_settings()
        super().__init__("openai", demo_mode=False)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.vision_model = settings.OPENAI_VISION_MODEL

    def _encode_image(self, image_data: bytes) -> str:
        """Encode image to base64."""
        return base64.b64encode(image_data).decode("utf-8")

    def _build_vision_prompt(self, task: str, detail_level: str = "standard") -> str:
        """Build prompt for vision tasks."""
        base_prompt = """You are MiraGuide, an AI accessibility assistant helping people with disabilities understand visual information.

Your response MUST be a valid JSON object matching this exact schema:
{
  "intent": "see_understand" | "read_explain" | "form_assist" | "visual_qa",
  "summary": "Human-readable summary (1-2 sentences)",
  "details": ["detail 1", "detail 2"],
  "entities": [{"type": "entity_type", "label": "Label", "value": "value", "confidence": 0.0-1.0, "bounding_box": {"x": 0.0, "y": 0.0, "width": 0.0, "height": 0.0}}],
  "important_information": [{"label": "Label", "value": "Value", "priority": 1-5, "source": "vision|ocr|context"}],
  "confidence": 0.0-1.0,
  "needs_clarification": true|false,
  "clarification_question": "Question if needed",
  "safety_note": "Safety warning if applicable",
  "response_mode": "text" | "voice" | "text_and_voice" | "visual",
  "follow_up_suggestions": ["suggestion 1", "suggestion 2"]
}

Guidelines:
- Be concise but thorough
- Prioritize actionable information
- Express uncertainty honestly
- Flag safety concerns
- Include follow-up suggestions
- For forms: identify field labels, types, required status
- For documents: extract key information, dates, actions needed
- For scenes: describe layout, obstacles, text, symbols"""

        if task == "see_understand":
            return base_prompt + f"\n\nTask: Describe this scene for accessibility. Detail level: {detail_level}."
        elif task == "visual_qa":
            return base_prompt + "\n\nTask: Answer the user's question about this image based on what you see."
        elif task == "form_assist":
            return base_prompt + "\n\nTask: Analyze this form. Identify all fields, labels, types, required status, and instructions."
        elif task == "ocr":
            return base_prompt + "\n\nTask: Extract all text from this image. Preserve structure and formatting."
        return base_prompt

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        prompt: Optional[str] = None,
        detail_level: str = "standard",
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            base64_image = self._encode_image(image_data)

            system_prompt = self._build_vision_prompt("see_understand", detail_level)
            user_content = prompt or "Describe this image for accessibility purposes."

            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high" if detail_level == "detailed" else "auto",
                                },
                            },
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType(parsed.get("intent", "see_understand")),
                summary=parsed.get("summary", ""),
                details=parsed.get("details", []),
                entities=[Entity(**e) for e in parsed.get("entities", [])],
                important_information=[ImportantInformation(**i) for i in parsed.get("important_information", [])],
                confidence=parsed.get("confidence", 0.8),
                needs_clarification=parsed.get("needs_clarification", False),
                clarification_question=parsed.get("clarification_question"),
                safety_note=parsed.get("safety_note"),
                response_mode=ResponseMode(parsed.get("response_mode", "text")),
                follow_up_suggestions=parsed.get("follow_up_suggestions", []),
                provider="openai",
                model=self.vision_model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Vision error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def answer_visual_question(
        self,
        image_data: bytes,
        mime_type: str,
        question: str,
        context: Optional[str] = None,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            base64_image = self._encode_image(image_data)

            system_prompt = self._build_vision_prompt("visual_qa")
            user_content = f"Question: {question}"
            if context:
                user_content += f"\n\nPrevious context: {context}"

            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                            },
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType.VISUAL_QA,
                summary=parsed.get("summary", ""),
                details=parsed.get("details", []),
                entities=[Entity(**e) for e in parsed.get("entities", [])],
                important_information=[ImportantInformation(**i) for i in parsed.get("important_information", [])],
                confidence=parsed.get("confidence", 0.8),
                needs_clarification=parsed.get("needs_clarification", False),
                clarification_question=parsed.get("clarification_question"),
                safety_note=parsed.get("safety_note"),
                response_mode=ResponseMode(parsed.get("response_mode", "text")),
                follow_up_suggestions=parsed.get("follow_up_suggestions", []),
                provider="openai",
                model=self.vision_model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Visual QA error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            default_system = """You are MiraGuide, an AI accessibility assistant. Help users with disabilities by:
1. Routing them to the right feature (see, read, form, ask, simplify, communicate)
2. Answering questions about accessibility
3. Being concise and helpful
4. Expressing uncertainty when appropriate

Respond in JSON format matching StructuredAIResponse schema."""
            messages = [{"role": "system", "content": system_prompt or default_system}]
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.4,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType(parsed.get("intent", "chat")),
                summary=parsed.get("summary", ""),
                details=parsed.get("details", []),
                entities=[Entity(**e) for e in parsed.get("entities", [])],
                important_information=[ImportantInformation(**i) for i in parsed.get("important_information", [])],
                confidence=parsed.get("confidence", 0.8),
                needs_clarification=parsed.get("needs_clarification", False),
                clarification_question=parsed.get("clarification_question"),
                safety_note=parsed.get("safety_note"),
                response_mode=ResponseMode(parsed.get("response_mode", "text")),
                follow_up_suggestions=parsed.get("follow_up_suggestions", []),
                provider="openai",
                model=self.model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Chat error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def simplify(
        self,
        text: str,
        level: str = "simple",
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            level_prompts = {
                "simple": "Simplify this text to a 6th grade reading level. Keep all key information.",
                "very-simple": "Simplify this text to a 4th grade reading level. Use very short sentences.",
                "child": "Explain this text as if to a 10-year-old. Use simple words and analogies.",
            }

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": level_prompts.get(level, level_prompts["simple"])},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType.SIMPLIFY,
                summary=f"Text simplified to {level} level",
                details=parsed.get("details", [parsed.get("summary", "")]),
                entities=[],
                important_information=[ImportantInformation(**i) for i in parsed.get("important_information", [])],
                confidence=parsed.get("confidence", 0.85),
                needs_clarification=parsed.get("needs_clarification", False),
                response_mode=ResponseMode.TEXT,
                provider="openai",
                model=self.model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Simplify error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def summarize(
        self,
        text: str,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Summarize this text concisely. Extract key points. Return JSON with summary and key_points array."},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType.SUMMARIZE,
                summary=parsed.get("summary", ""),
                details=parsed.get("key_points", []),
                entities=[],
                important_information=[
                    ImportantInformation(label="Summary", value=parsed.get("summary", ""), priority=1, source="text")
                ] + [
                    ImportantInformation(label=f"Key Point {i+1}", value=p, priority=2, source="text")
                    for i, p in enumerate(parsed.get("key_points", []))
                ],
                confidence=parsed.get("confidence", 0.85),
                needs_clarification=False,
                response_mode=ResponseMode.TEXT,
                provider="openai",
                model=self.model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Summarize error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def communicate(
        self,
        message: str,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Convert the user's rough message into a clear, polite communication message for accessibility needs. Return JSON with the message."},
                    {"role": "user", "content": message},
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.4,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType.COMMUNICATE,
                summary=parsed.get("message", ""),
                details=[parsed.get("message", "")],
                entities=[],
                important_information=[
                    ImportantInformation(label="Communication Message", value=parsed.get("message", ""), priority=1, source="text")
                ],
                confidence=parsed.get("confidence", 0.9),
                needs_clarification=False,
                response_mode=ResponseMode.TEXT_AND_VOICE,
                provider="openai",
                model=self.model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI Communicate error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def extract_text(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            base64_image = self._encode_image(image_data)

            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": self._build_vision_prompt("ocr")},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this image. Preserve formatting."},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            structured = StructuredAIResponse(
                intent=IntentType.READ_EXPLAIN,
                summary=f"Extracted text from image",
                details=parsed.get("details", [parsed.get("summary", "")]),
                entities=[Entity(**e) for e in parsed.get("entities", [])],
                important_information=[ImportantInformation(**i) for i in parsed.get("important_information", [])],
                confidence=parsed.get("confidence", 0.8),
                needs_clarification=parsed.get("needs_clarification", False),
                response_mode=ResponseMode.TEXT,
                provider="openai",
                model=self.vision_model,
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
                raw_response=content,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI OCR error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def extract_structured(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        return await self.analyze_image(image_data, mime_type, prompt="Analyze this form/document structure", detail_level="detailed")

    async def transcribe(
        self,
        audio_data: bytes,
        mime_type: str,
        language: str = "en",
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            # Save to temp file for API
            import tempfile
            ext = ".wav" if "wav" in mime_type else ".mp3" if "mp3" in mime_type else ".webm"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            with open(temp_path, "rb") as f:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language,
                    response_format="json",
                )

            import os
            os.unlink(temp_path)

            structured = StructuredAIResponse(
                intent=IntentType.CHAT,
                summary=f"Transcribed audio ({len(transcript.text)} chars)",
                details=[transcript.text],
                entities=[],
                important_information=[
                    ImportantInformation(label="Transcription", value=transcript.text, priority=1, source="stt")
                ],
                confidence=0.9,
                needs_clarification=False,
                response_mode=ResponseMode.TEXT,
                provider="openai",
                model="whisper-1",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            return ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
            )

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI STT error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> ProviderResult:
        start = time.perf_counter()
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice or "alloy",
                input=text,
                speed=speed,
            )

            audio_data = response.content

            structured = StructuredAIResponse(
                intent=IntentType.CHAT,
                summary=f"Synthesized speech ({len(audio_data)} bytes)",
                details=[f"Voice: {voice or 'alloy'}", f"Speed: {speed}x"],
                entities=[],
                important_information=[
                    ImportantInformation(label="Audio", value=f"[Generated audio: {len(audio_data)} bytes]", priority=1, source="tts")
                ],
                confidence=1.0,
                needs_clarification=False,
                response_mode=ResponseMode.VOICE,
                provider="openai",
                model="tts-1",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
                demo_mode=False,
            )

            # Store audio data in raw_response for retrieval
            result = ProviderResult(
                success=True,
                data=structured,
                processing_time_ms=structured.processing_time_ms,
            )
            result.raw_response = audio_data
            return result

        except Exception as e:
            return ProviderResult(
                success=False,
                error=f"OpenAI TTS error: {str(e)}",
                processing_time_ms=int((time.perf_counter() - start) * 1000),
            )