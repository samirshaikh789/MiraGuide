"""Services package initialization"""

from app.services.providers import (
    BaseProvider,
    VisionProvider,
    TextProvider,
    OCRProvider,
    SpeechToTextProvider,
    TextToSpeechProvider,
    ProviderResult,
    ProviderRegistry,
    provider_registry,
)
from app.services.demo_providers import register_demo_providers
from app.services.decision_engine import (
    AccessibilityDecisionEngine,
    DecisionEngineResult,
    decision_engine,
)
from app.services.ai_service import AIService, ai_service

__all__ = [
    # Providers
    "BaseProvider",
    "VisionProvider",
    "TextProvider",
    "OCRProvider",
    "SpeechToTextProvider",
    "TextToSpeechProvider",
    "ProviderResult",
    "ProviderRegistry",
    "provider_registry",
    "register_demo_providers",
    # Decision Engine
    "AccessibilityDecisionEngine",
    "DecisionEngineResult",
    "decision_engine",
    # AI Service
    "AIService",
    "ai_service",
]