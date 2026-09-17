"""Tests for MiraGuide Backend"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.schemas.ai import IntentType, ResponseMode


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]
        assert "version" in data["data"]
        assert "demo_mode" in data["data"]


class TestSessionsEndpoint:
    """Test sessions endpoints."""

    def test_create_session(self):
        response = client.post("/api/v1/sessions", json={})
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "session_id" in str(data["data"])

    def test_get_session(self):
        # Create session first
        create_resp = client.post("/api/v1/sessions", json={})
        session_id = create_resp.json()["data"]["id"]

        # Get session
        response = client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == session_id

    def test_delete_session(self):
        create_resp = client.post("/api/v1/sessions", json={})
        session_id = create_resp.json()["data"]["id"]

        response = client.delete(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200

        # Verify deleted
        get_resp = client.get(f"/api/v1/sessions/{session_id}")
        assert get_resp.status_code == 404


class TestAnalyzeEndpoints:
    """Test analyze endpoints."""

    def test_analyze_image_missing_file(self):
        response = client.post("/api/v1/analyze/image")
        assert response.status_code == 422  # Missing file

    def test_analyze_document_missing_file(self):
        response = client.post("/api/v1/analyze/document")
        assert response.status_code == 422

    def test_analyze_form_missing_file(self):
        response = client.post("/api/v1/analyze/form")
        assert response.status_code == 422

    def test_ask_question_missing_session(self):
        response = client.post(
            "/api/v1/analyze/ask",
            json={"session_id": "00000000-0000-0000-0000-000000000000", "question": "test"}
        )
        assert response.status_code == 404

    def test_simplify_text(self):
        response = client.post(
            "/api/v1/analyze/simplify",
            json={"text": "This is a complex sentence that needs simplification.", "level": "simple"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ai_response" in data["data"]

    def test_summarize_text(self):
        response = client.post(
            "/api/v1/analyze/summarize",
            json={"text": "This is a long text that should be summarized. It has multiple sentences. The summary should be shorter."}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ai_response" in data["data"]

    def test_chat(self):
        response = client.post(
            "/api/v1/analyze/chat",
            json={"message": "Hello, how can you help me?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ai_response" in data["data"]


class TestVoiceEndpoints:
    """Test voice endpoints."""

    def test_transcribe_missing_file(self):
        response = client.post("/api/v1/voice/transcribe")
        assert response.status_code == 422

    def test_synthesize(self):
        response = client.post(
            "/api/v1/voice/synthesize",
            json={"text": "Hello world", "speed": 1.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "audio_base64" in data["data"]


class TestInteractionsEndpoint:
    """Test interactions endpoints."""

    def test_get_session_interactions(self):
        # Create session
        create_resp = client.post("/api/v1/sessions", json={})
        session_id = create_resp.json()["data"]["id"]

        # Get interactions (should be empty initially)
        response = client.get(f"/api/v1/interactions/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 0


class TestProvidersEndpoint:
    """Test providers listing."""

    def test_list_providers(self):
        response = client.get("/api/v1/analyze/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vision" in data["data"]
        assert "text" in data["data"]
        assert "ocr" in data["data"]
        assert "stt" in data["data"]
        assert "tts" in data["data"]
        # Demo providers should always be available
        assert "demo" in data["data"]["vision"]


class TestStructuredAIResponse:
    """Test structured AI response schema."""

    def test_structured_response_validation(self):
        from app.schemas.ai import StructuredAIResponse, Entity, ImportantInformation

        response = StructuredAIResponse(
            intent=IntentType.SEE_UNDERSTAND,
            summary="Test summary",
            details=["Detail 1", "Detail 2"],
            entities=[
                Entity(type="object", label="Door", value="Exit door", confidence=0.9)
            ],
            important_information=[
                ImportantInformation(label="Exit", value="Door on left", priority=1, source="vision")
            ],
            confidence=0.9,
            needs_clarification=False,
            response_mode=ResponseMode.TEXT_AND_VOICE,
            provider="demo",
            model="demo-vision",
            processing_time_ms=500,
            demo_mode=True,
        )

        assert response.intent == IntentType.SEE_UNDERSTAND
        assert response.confidence == 0.9
        assert len(response.entities) == 1
        assert len(response.important_information) == 1


class TestDecisionEngine:
    """Test decision engine."""

    @pytest.mark.asyncio
    async def test_intent_detection(self):
        from app.services.decision_engine import decision_engine

        # Test See & Understand
        intent, conf = await decision_engine.detect_intent(None, True, False, None)
        assert intent == IntentType.SEE_UNDERSTAND
        assert conf > 0.8

        # Test Read & Explain
        intent, conf = await decision_engine.detect_intent(None, False, True, None)
        assert intent == IntentType.READ_EXPLAIN
        assert conf > 0.8

        # Test Visual Q&A
        intent, conf = await decision_engine.detect_intent("What does this say?", True, False, None)
        assert intent == IntentType.VISUAL_QA

        # Test Form Assist
        intent, conf = await decision_engine.detect_intent(None, False, False, None, has_form=True)
        assert intent == IntentType.FORM_ASSIST


class TestDemoProviders:
    """Test demo providers."""

    @pytest.mark.asyncio
    async def test_demo_vision_provider(self):
        from app.services.demo_providers import DemoVisionProvider

        provider = DemoVisionProvider()
        result = await provider.analyze_image(b"fake_image_data", "image/jpeg")

        assert result.success is True
        assert result.demo_mode is True
        assert result.data is not None
        assert result.data.intent in [IntentType.SEE_UNDERSTAND, IntentType.FORM_ASSIST]

    @pytest.mark.asyncio
    async def test_demo_text_provider(self):
        from app.services.demo_providers import DemoTextProvider

        provider = DemoTextProvider()
        result = await provider.chat("Help me read a document")

        assert result.success is True
        assert result.demo_mode is True
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_demo_ocr_provider(self):
        from app.services.demo_providers import DemoOCRProvider

        provider = DemoOCRProvider()
        result = await provider.extract_text(b"fake_image", "image/jpeg")

        assert result.success is True
        assert result.demo_mode is True
        assert result.data is not None
        assert result.data.intent == IntentType.READ_EXPLAIN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])