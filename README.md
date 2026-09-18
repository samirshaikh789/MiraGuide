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

## System Architecture & Workflows

MiraGuide ke enterprise-grade architecture, multimodal processing pipeline aur decision engine ke technical flowcharts:

---

### 1. High-Level System Architecture
MiraGuide ka end-to-end layered architecture jo User Interface se lekar Database tak sabhi components ko organize karta hai:
- **User Interfaces & API Layer:** Mobile/Web apps, API Gateway, Authentication aur Session Management.
- **Input Processing & AI Intelligence Core:** OCR, Speech-to-Text aur Multimodal Vision-Language Model ke sath Intent Detection aur Confidence Estimation.
- **Response Generation & Persistence:** TTS, Visual Highlighting, Simplification Engine aur Relational Database (PostgreSQL/SQLite).

![High-Level System Architecture](https://github.com/samirshaikh789/MiraGuide/blob/main/Images/High-Level%20System%20Architecture.png?raw=true)

---

### 2. Detailed AI Processing Architecture
Multimodal inputs ko 4-stage pipeline ke zariye action me badalne ka process:
- **Stage 1 (Multimodal Input):** Image, camera frames, screenshots, voice aur text input.
- **Stage 2 (Perception):** OCR extraction, object detection, document understanding aur STT transcription.
- **Stage 3 (Intelligence - Core Differentiator):** Intent detection, multimodal reasoning, task interpretation aur safety checks.
- **Stage 4 (Assistance):** Natural language explanations, simplified instructions, visual highlights aur audio output.

![Detailed AI Processing Architecture][(docs/images/Detailed%20AI%20Processing%20Architecture.png)](https://github.com/samirshaikh789/MiraGuide/blob/main/Images/Detailed%20AI%20Processing%20Architecture.png?raw=true)

---

### 3. End-to-End User Flowchart
User perspective se application ke interaction ka flow:
- User mode choose karke input provide karta hai (Camera, Screen, Voice, Text).
- AI model intent aur context analyze karta hai.
- **Confidence Check:** Agar confidence high hai, toh direct answer/guidance (text/voice) di jaati hai; agar uncertain hai, toh user se clarification maangi jaati hai, jisse conversation context bana rahe.

![End-to-End User Flowchart][(docs/images/End-to-End%20User%20Flowchart.png)](https://github.com/samirshaikh789/MiraGuide/blob/main/Images/End-to-End%20User%20Flowchart.png?raw=true)

---

### 4. Accessibility Assistance Decision Flow
MiraGuide ka core decision-making aur safety validation framework:
- **Accessibility Decision Engine:** User intent aur accessibility needs ko pehchan kar candidate assistance generate karta hai.
- **Safety Branch:** Sensitive ya high-risk content detect hone par conservative safe output provide karta hai.
- **Confidence Verification:** Low-confidence cases me verification loop trigger karta hai taaki galat guidance na di jaye.

![Accessibility Assistance Decision Flow][(docs/images/Accessibility%20Assistance%20Decision%20Flow.png)](https://github.com/samirshaikh789/MiraGuide/blob/main/Images/Accessibility%20Assistance%20Decision%20Flow.png?raw=true)

---

### 5. System Context Diagram
MiraGuide platform ke external services aur data boundaries ka overall overview:
- **Input Channels:** Camera, microphone, screenshot aur text inputs.
- **External AI Services:** Multimodal AI Model, OCR Engine, Speech-to-Text aur Text-to-Speech APIs.
- **Storage:** User preferences, session metadata aur interaction history ka centralized data flow.

![System Context Diagram][(docs/images/System%20Context%20Diagram.png)](https://github.com/samirshaikh789/MiraGuide/blob/main/Images/System%20Context%20Diagram.png?raw=true)

## License

Proprietary — MiraGuide Project
