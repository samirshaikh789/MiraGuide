# MiraGuide Backend

FastAPI-based backend for MiraGuide - AI-powered multimodal accessibility assistant.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                  │
├─────────────────────────────────────────────────────────────┤
│  /api/v1/sessions    /api/v1/analyze    /api/v1/voice      │
│  /api/v1/interactions                                          │
├─────────────────────────────────────────────────────────────┤
│                    AI Service Layer                          │
│  ┌─────────────┐  ┌─────────────────────────────────────┐  │
│  │ Decision    │  │ Provider Abstractions               │  │
│  │ Engine      │  │ • VisionProvider                    │  │
│  │             │  │ • TextProvider                      │  │
│  │ • Intent    │  │ • OCRProvider                       │  │
│  │ • Confidence│  │ • SpeechToTextProvider              │  │
│  │ • Clarify   │  │ • TextToSpeechProvider              │  │
│  │ • Response  │  │                                     │  │
│  │   Mode      │  │  Implementations:                   │  │
│  └─────────────┘  │  • DemoProvider (default)           │  │
│                   │  • OpenAIProvider                   │  │
│                   │  • GeminiProvider (planned)         │  │
│                   │  • AnthropicProvider (planned)      │  │
│                   └─────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer (PostgreSQL + SQLAlchemy)    │
│  • Users & AccessibilityPreferences                        │
│  • Sessions & Interactions                                 │
│  • InputMetadata                                           │
└─────────────────────────────────────────────────────────────┘
```

## Core Workflows

### 1. See & Understand (`POST /api/v1/analyze/image`)
Upload an image → Get accessibility-focused description

### 2. Read & Explain (`POST /api/v1/analyze/document`)
Upload document → OCR extracts text → AI explains/simplifies

### 3. Form Assist (`POST /api/v1/analyze/form`)
Upload form → AI identifies fields, labels, structure → Explains each field

### 4. Visual Q&A (`POST /api/v1/analyze/ask`)
Session + Question → AI uses visual context to answer

### 5. Follow-up Questions
All workflows support session-based context for follow-ups

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- (Optional) OpenAI API key for real AI

### Installation

```bash
cd backend_new
pip install -e ".[dev]"
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your settings
```

### Database

```bash
# Run migrations
alembic upgrade head
```

### Run Development Server

```bash
uvicorn app.main:app --reload --port 8787
```

### With Docker

```bash
docker-compose up -d
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |
| POST | `/api/v1/analyze/image` | Analyze image (See/Visual Q&A) |
| POST | `/api/v1/analyze/document` | Analyze document (Read) |
| POST | `/api/v1/analyze/form` | Analyze form (Form Assist) |
| POST | `/api/v1/analyze/ask` | Ask about visual context |
| POST | `/api/v1/analyze/simplify` | Simplify text |
| POST | `/api/v1/analyze/summarize` | Summarize text |
| POST | `/api/v1/analyze/chat` | Chat with assistant |
| POST | `/api/v1/voice/transcribe` | Speech to text |
| POST | `/api/v1/voice/synthesize` | Text to speech |
| GET | `/api/v1/interactions/session/{id}` | Get session history |

## Structured AI Responses

All AI endpoints return `StructuredAIResponse`:

```json
{
  "intent": "see_understand",
  "summary": "Human-readable summary",
  "details": ["Detail 1", "Detail 2"],
  "entities": [{"type": "field", "label": "Name", "value": "", "confidence": 0.9}],
  "important_information": [{"label": "Field", "value": "Name (required)", "priority": 1}],
  "confidence": 0.85,
  "needs_clarification": false,
  "clarification_question": null,
  "safety_note": null,
  "response_mode": "text_and_voice",
  "follow_up_suggestions": ["What's on the left?", "Read the sign"],
  "provider": "openai",
  "model": "gpt-4o",
  "processing_time_ms": 1200,
  "demo_mode": false
}
```

## Decision Engine

The Accessibility Decision Engine determines:
- **Intent** from input (image, document, question, etc.)
- **Confidence** in the intent detection
- **Response mode** (text, voice, both)
- **Whether clarification needed** (low confidence)
- **Safety concerns** (uncertain form fields, critical text)

## Demo Mode

When no AI API keys are configured, the system runs in **demo mode** with simulated but realistic responses. All demo responses are clearly marked with `demo_mode: true` and include a notice.

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Deployment

### Production Checklist
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure real AI provider API keys
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` for your frontend
- [ ] Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- [ ] Set up monitoring/logging
- [ ] Configure SSL/TLS

### Docker
```bash
docker build -t miraguide-backend ./backend_new
docker run -p 8787:8787 --env-file .env miraguide-backend
```

## Frontend Integration

The frontend should:
1. Create a session on app start (`POST /api/v1/sessions`)
2. Include `session_id` in all analyze requests for context
3. Use `X-Request-ID` header for request tracing
4. Handle `demo_mode` flag in responses
5. Display `clarification_question` when `needs_clarification` is true
6. Use `important_information` for key details display
7. Respect `response_mode` for voice output

## License

Proprietary - MiraGuide Project