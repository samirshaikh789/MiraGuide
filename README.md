# MiraGuide

**AI-powered multimodal accessibility assistant** — helping people with disabilities understand visual, textual, and contextual information and complete everyday digital tasks.

## Overview

MiraGuide is an end-to-end accessibility assistant that goes beyond simple image captioning. It implements a full multimodal pipeline:

```
User Input
    ↓
Multimodal Perception
    ↓
Information Extraction
    ↓
Intent Detection
    ↓
Context Understanding
    ↓
Task Reasoning
    ↓
Accessibility Decision Engine
    ↓
Confidence / Safety Evaluation
    ↓
Response Generation
    ↓
Text / Voice / Visual Assistance
```

## Core Workflows

### 1. See & Understand
Upload or capture an image → Get accessibility-focused description → Ask follow-up questions

### 2. Read & Explain
Upload document/sign image → OCR extracts text → AI explains/simplifies/summarizes

### 3. Form Assist
Upload form image → AI identifies fields, labels, required status → Step-by-step guidance

### 4. Ask About What You See
Ask follow-up questions about previously analyzed content using session context

## Technology Stack

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Radix UI primitives
- TanStack Query (React Query)
- React Router v6
- React Hook Form + Zod

### Backend
- Python 3.11+
- FastAPI
- Pydantic v2 + Pydantic Settings
- SQLAlchemy 2.0 (async) + Alembic
- SQLite (dev) / PostgreSQL (prod)

### AI Providers (pluggable)
- OpenAI (GPT-4o, Whisper, TTS)
- Google Gemini (planned)
- Anthropic Claude (planned)
- Demo providers (built-in, no API keys needed)

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- (Optional) PostgreSQL 16+ for production

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8787
# API at http://localhost:8787
# Docs at http://localhost:8787/docs
```

### With Docker
```bash
docker-compose up -d
```

## Project Structure

```
miraguide/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/       # UI components (Radix-based)
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client + query client
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utilities
│   └── ...
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # API routes
│   │   ├── core/             # Configuration
│   │   ├── db/               # Database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── alembic/              # Migrations
│   └── tests/
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session |
| POST | `/api/v1/analyze/image` | Analyze image (See/Visual Q&A) |
| POST | `/api/v1/analyze/document` | Analyze document (Read) |
| POST | `/api/v1/analyze/form` | Analyze form (Form Assist) |
| POST | `/api/v1/analyze/ask` | Ask follow-up question |
| POST | `/api/v1/analyze/simplify` | Simplify text |
| POST | `/api/v1/analyze/summarize` | Summarize text |
| POST | `/api/v1/analyze/chat` | General chat |
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

## Accessibility Decision Engine

Core differentiator that determines:
- **Intent** from input (image, document, question)
- **Confidence** in intent detection
- **Response mode** (text, voice, both)
- **Whether clarification needed** (low confidence)
- **Safety concerns** (uncertain form fields, critical text)

## Demo Mode

When no AI API keys are configured, runs in demo mode with simulated but realistic responses. All demo responses are clearly marked with `demo_mode: true` and include a notice.

## Configuration

Backend `.env`:
```env
# AI Providers (optional for demo)
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=

# Database
DATABASE_URL=sqlite+aiosqlite:///./miraguide.db

# Server
PORT=8787
DEMO_MODE=true
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
docker build -t miraguide-backend ./backend
docker build -t miraguide-frontend ./frontend
docker-compose up -d
```

## Accessibility

MiraGuide itself is built to be accessible:
- Semantic HTML
- Proper heading hierarchy
- Keyboard navigation
- Visible focus styles
- ARIA attributes where needed
- High contrast mode
- Reduced motion support
- Large interaction targets
- Screen reader compatible

## License

Proprietary — MiraGuide Project