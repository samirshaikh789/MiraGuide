# MiraGuide Architecture

## System Overview

MiraGuide follows a modular monolith architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Pages       │  │  Components  │  │  Services (API)      │  │
│  │  - See       │  │  - Radix UI  │  │  - TanStack Query    │  │
│  │  - Read      │  │  - Forms     │  │  - Auth              │  │
│  │  - Form      │  │  - Layout    │  │  - Voice             │  │
│  │  - Ask       │  │  - Feedback  │  │  - Session           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
│  ┌──────────────┐  ┌────────────────────────────────────────┐  │
│  │  API Routes  │  │         Core Services                  │  │
│  │  /analyze    │  │  ┌──────────────────────────────────┐  │  │
│  │  /voice      │  │  │ AI Service                       │  │  │
│  │  /sessions   │  │  │  - Orchestrates providers        │  │  │
│  │  /health     │  │  │  - Session/Context management    │  │  │
│  └──────────────┘  │  └──────────────────────────────────┘  │  │
│                    │  ┌──────────────────────────────────┐  │  │
│                    │  │ Decision Engine                  │  │  │
│                    │  │  - Intent detection              │  │  │
│                    │  │  - Confidence evaluation         │  │  │
│                    │  │  - Clarification logic           │  │  │
│                    │  │  - Response mode selection       │  │  │
│                    │  └──────────────────────────────────┘  │  │
│                    │  ┌──────────────────────────────────┐  │  │
│                    │  │ Provider Registry                │  │  │
│                    │  │  - VisionProvider                │  │  │
│                    │  │  - TextProvider                  │  │  │
│                    │  │  - OCRProvider                   │  │  │
│                    │  │  - STTProvider                   │  │  │
│                    │  │  - TTSProvider                   │  │  │
│                    │  └──────────────────────────────────┘  │  │
│                    │  ┌──────────────────────────────────┐  │  │
│                    │  │ Database (SQLAlchemy + SQLite)   │  │  │
│                    │  │  - Users / Preferences           │  │  │
│                    │  │  - Sessions / Interactions       │  │  │
│                    │  │  - Input Metadata                │  │  │
│                    │  └──────────────────────────────────┘  │  │
│                    └────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`app/api/v1/`)
- **analyze.py** — Core workflow endpoints (image, document, form, ask, simplify, summarize, chat)
- **voice.py** — STT/TTS endpoints
- **sessions.py** — Session CRUD
- **interactions.py** — Interaction history
- **health.py** — Health check + provider status

### 2. AI Service (`app/services/ai_service.py`)
Main orchestrator that:
- Initializes providers (demo + real)
- Manages session lifecycle
- Coordinates provider calls
- Persists interactions
- Builds context for follow-ups

### 3. Decision Engine (`app/services/decision_engine.py`)
Determines:
- **Intent** from multimodal input
- **Confidence** scores
- **Response mode** (text/voice/both)
- **Clarification needs** (low confidence)
- **Safety flags**

### 4. Provider Abstractions (`app/services/providers.py`)
- **VisionProvider** — Image analysis, visual Q&A
- **TextProvider** — Chat, simplify, summarize, communicate
- **OCRProvider** — Text extraction, structured extraction
- **STTProvider** — Speech to text
- **TTSProvider** — Text to speech

### 5. Provider Implementations
- **Demo Providers** — Simulated responses (default, no API keys)
- **OpenAI Provider** — GPT-4o, Whisper, TTS (production)

### 6. Database Models (`app/models/`)
- **User** — Core user entity
- **AccessibilityPreference** — User settings
- **Session** — Conversation context
- **Interaction** — Single request/response
- **InputMetadata** — File upload tracking

### 6. Schemas (`app/schemas/`)
- **ai.py** — Structured AI requests/responses
- **base.py** — Base response envelopes

## Data Flow

### See & Understand / Visual Q&A
```
POST /analyze/image
    │
    ▼
Validate file (type, size)
    │
    ▼
DecisionEngine.detect_intent(question, has_image=True)
    │
    ▼
VisionProvider.analyze_image() OR answer_visual_question()
    │
    ▼
DecisionEngine.evaluate_confidence(ai_response, context)
    │
    ▼
Persist Interaction + Session context
    │
    ▼
Return StructuredAIResponse + DecisionEngineResult
```

### Read & Explain
```
POST /analyze/document
    │
    ▼
OCRProvider.extract_text()
    │
    ▼
TextProvider.simplify() (if requested)
    │
    ▼
DecisionEngine.evaluate_confidence()
    │
    ▼
Persist + Return
```

### Form Assist
```
POST /analyze/form
    │
    ▼
VisionProvider.analyze_image(prompt="form analysis")
    │
    ▼
DecisionEngine (form_assist intent)
    │
    ▼
Persist + Return field entities + explanations
```

### Follow-up Question
```
POST /analyze/ask (session_id + question)
    │
    ▼
Retrieve Session context
    │
    ▼
DecisionEngine.detect_intent(question, has_image=False, has_document=False, session)
    │
    ▼
TextProvider.chat(question, context=session.context_data)
    │
    ▼
DecisionEngine.evaluate_confidence()
    │
    ▼
Persist + Return
```

## Session Context

Sessions maintain context across interactions:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "context_data": "[see_understand] Door on left, stairs ahead\n[visual_qa] Sign says 'Exit'",
  "created_at": "2026-01-17T...",
  "updated_at": "2026-01-17T..."
}
```

Context is automatically updated after each interaction and passed to providers for follow-up questions.

## Provider Registry

```python
provider_registry = ProviderRegistry()
# Auto-registers demo providers at import time
provider_registry.register_vision("openai", OpenAIProvider(), default=True)
```

## Structured AI Response

All AI outputs conform to `StructuredAIResponse`:

```python
class StructuredAIResponse(BaseModel):
    intent: IntentType
    summary: str
    details: List[str]
    entities: List[Entity]
    important_information: List[ImportantInformation]
    confidence: float
    needs_clarification: bool
    clarification_question: Optional[str]
    safety_note: Optional[str]
    response_mode: ResponseMode
    follow_up_suggestions: List[str]
    provider: str
    model: str
    processing_time_ms: int
    demo_mode: bool
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "User-friendly message",
  "error_code": "VALIDATION_ERROR",
  "request_id": "uuid",
  "details": {}
}
```

Error codes:
- `VALIDATION_ERROR` — Invalid request data
- `FILE_TOO_LARGE` — Upload exceeds size limit
- `INVALID_FILE_TYPE` — Unsupported MIME type
- `SESSION_NOT_FOUND` — Session ID doesn't exist
- `AI_PROVIDER_ERROR` — Provider returned error
- `DATABASE_ERROR` — Persistence failure
- `INTERNAL_ERROR` — Unexpected server error

## Security

- File upload validation (MIME type, size, magic bytes)
- Request ID tracing
- CORS configuration
- No secrets in logs
- Temporary file cleanup
- Input sanitization

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests (when added)
cd frontend
npm test
```

## Deployment

### Development
```bash
# Backend
uvicorn app.main:app --reload --port 8787

# Frontend
npm run dev
```

### Production (Docker)
```bash
docker-compose up -d
```

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./miraguide.db` |
| `OPENAI_API_KEY` | OpenAI API key | (demo mode) |
| `GEMINI_API_KEY` | Google Gemini API key | (demo mode) |
| `ANTHROPIC_API_KEY` | Anthropic API key | (demo mode) |
| `SECRET_KEY` | Session encryption | `change-me` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |
| `DEMO_MODE` | Use demo providers | `true` |