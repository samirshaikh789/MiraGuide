"""AI Provider Abstractions"""

import abc
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.schemas.ai import (
    StructuredAIResponse,
    IntentType,
    ResponseMode,
    Entity,
    ImportantInformation,
)
from app.core.config import get_settings


@dataclass
class ProviderResult:
    """Result from a provider call."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None
    processing_time_ms: int = 0
    demo_mode: bool = False


class BaseProvider(abc.ABC):
    """Base class for all AI providers."""

    def __init__(self, name: str, demo_mode: bool = False):
        self.name = name
        self.demo_mode = demo_mode
        self.settings = get_settings()

    def _create_demo_response(self, intent: IntentType, summary: str) -> StructuredAIResponse:
        """Create a demo response."""
        return StructuredAIResponse(
            intent=intent,
            summary=summary,
            details=["Demo response - not from real AI"],
            entities=[],
            important_information=[],
            confidence=0.5,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT,
            provider=self.name,
            model="demo",
            processing_time_ms=0,
            demo_mode=True,
        )

    def _time_operation(self, func):
        """Time an operation."""
        start = time.perf_counter()
        result = func()
        elapsed = int((time.perf_counter() - start) * 1000)
        return result, elapsed


class VisionProvider(BaseProvider):
    """Abstract vision provider for image analysis."""

    @abc.abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        prompt: Optional[str] = None,
        detail_level: str = "standard",
    ) -> ProviderResult:
        """Analyze an image."""
        pass

    @abc.abstractmethod
    async def answer_visual_question(
        self,
        image_data: bytes,
        mime_type: str,
        question: str,
        context: Optional[str] = None,
    ) -> ProviderResult:
        """Answer a question about an image."""
        pass


class TextProvider(BaseProvider):
    """Abstract text provider for text processing."""

    @abc.abstractmethod
    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> ProviderResult:
        """Chat with the model."""
        pass

    @abc.abstractmethod
    async def simplify(
        self,
        text: str,
        level: str = "simple",
    ) -> ProviderResult:
        """Simplify text to a reading level."""
        pass

    @abc.abstractmethod
    async def summarize(
        self,
        text: str,
    ) -> ProviderResult:
        """Summarize text."""
        pass

    @abc.abstractmethod
    async def communicate(
        self,
        message: str,
    ) -> ProviderResult:
        """Generate a communication message."""
        pass


class OCRProvider(BaseProvider):
    """Abstract OCR provider for text extraction."""

    @abc.abstractmethod
    async def extract_text(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        """Extract text from image."""
        pass

    @abc.abstractmethod
    async def extract_structured(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ProviderResult:
        """Extract structured text (forms, tables, etc.)."""
        pass


class SpeechToTextProvider(BaseProvider):
    """Abstract speech-to-text provider."""

    @abc.abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        mime_type: str,
        language: str = "en",
    ) -> ProviderResult:
        """Transcribe audio to text."""
        pass


class TextToSpeechProvider(BaseProvider):
    """Abstract text-to-speech provider."""

    @abc.abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> ProviderResult:
        """Synthesize speech from text."""
        pass


# --- Provider Registry ---

class ProviderRegistry:
    """Registry for managing AI providers."""

    def __init__(self):
        self._vision_providers: Dict[str, VisionProvider] = {}
        self._text_providers: Dict[str, TextProvider] = {}
        self._ocr_providers: Dict[str, OCRProvider] = {}
        self._stt_providers: Dict[str, SpeechToTextProvider] = {}
        self._tts_providers: Dict[str, TextToSpeechProvider] = {}

        self._default_vision: Optional[str] = None
        self._default_text: Optional[str] = None
        self._default_ocr: Optional[str] = None
        self._default_stt: Optional[str] = None
        self._default_tts: Optional[str] = None

    def register_vision(self, name: str, provider: VisionProvider, default: bool = False):
        self._vision_providers[name] = provider
        if default or self._default_vision is None:
            self._default_vision = name

    def register_text(self, name: str, provider: TextProvider, default: bool = False):
        self._text_providers[name] = provider
        if default or self._default_text is None:
            self._default_text = name

    def register_ocr(self, name: str, provider: OCRProvider, default: bool = False):
        self._ocr_providers[name] = provider
        if default or self._default_ocr is None:
            self._default_ocr = name

    def register_stt(self, name: str, provider: SpeechToTextProvider, default: bool = False):
        self._stt_providers[name] = provider
        if default or self._default_stt is None:
            self._default_stt = name

    def register_tts(self, name: str, provider: TextToSpeechProvider, default: bool = False):
        self._tts_providers[name] = provider
        if default or self._default_tts is None:
            self._default_tts = name

    def get_vision(self, name: Optional[str] = None) -> VisionProvider:
        name = name or self._default_vision or "demo"
        if name not in self._vision_providers:
            raise ValueError(f"Vision provider '{name}' not found")
        return self._vision_providers[name]

    def get_text(self, name: Optional[str] = None) -> TextProvider:
        name = name or self._default_text or "demo"
        if name not in self._text_providers:
            raise ValueError(f"Text provider '{name}' not found")
        return self._text_providers[name]

    def get_ocr(self, name: Optional[str] = None) -> OCRProvider:
        name = name or self._default_ocr or "demo"
        if name not in self._ocr_providers:
            raise ValueError(f"OCR provider '{name}' not found")
        return self._ocr_providers[name]

    def get_stt(self, name: Optional[str] = None) -> SpeechToTextProvider:
        name = name or self._default_stt or "demo"
        if name not in self._stt_providers:
            raise ValueError(f"STT provider '{name}' not found")
        return self._stt_providers[name]

    def get_tts(self, name: Optional[str] = None) -> TextToSpeechProvider:
        name = name or self._default_tts or "demo"
        if name not in self._tts_providers:
            raise ValueError(f"TTS provider '{name}' not found")
        return self._tts_providers[name]

    @property
    def available_vision(self) -> List[str]:
        return list(self._vision_providers.keys())

    @property
    def available_text(self) -> List[str]:
        return list(self._text_providers.keys())

    @property
    def available_ocr(self) -> List[str]:
        return list(self._ocr_providers.keys())

    @property
    def available_stt(self) -> List[str]:
        return list(self._stt_providers.keys())

    @property
    def available_tts(self) -> List[str]:
        return list(self._tts_providers.keys())


# Global registry instance
provider_registry = ProviderRegistry()

# Register demo providers immediately at module load time
from app.services.demo_providers import register_demo_providers
register_demo_providers()