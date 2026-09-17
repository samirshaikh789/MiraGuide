# MiraGuide API Reference

## Base URL
```
Development: http://localhost:8787
Production: https://api.miraguide.app
```

## Authentication
Currently uses request ID tracking. API keys planned for future.

### Headers
| Header | Required | Description |
|--------|----------|-------------|
| `X-Request-ID` | No | Client-generated UUID for tracing |
| `Content-Type` | Yes | `application/json` or `multipart/form-data` |

## Response Format

All responses use a standard envelope:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "error_code": null,
  "request_id": "uuid",
  "demo_mode": true
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "error": "Human-readable message",
  "error_code": "VALIDATION_ERROR",
  "request_id": "uuid",
  "details": {}
}
```

## Endpoints

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "demo_mode": true,
    "database": "connected",
    "ai_providers": {
      "vision": true,
      "text": true,
      "ocr": true,
      "stt": true,
      "tts": true
    }
  }
}
```

---

### Sessions

#### Create Session
```
POST /api/v1/sessions
```

**Request:**
```json
{
  "user_id": "optional-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "created_at": "2026-01-17T...",
    "updated_at": "2026-01-17T...",
    "context_data": null
  }
}
```

#### Get Session
```
GET /api/v1/sessions/{session_id}
```

#### Delete Session
```
DELETE /api/v1/sessions/{session_id}
```

---

### Analyze Endpoints

#### Analyze Image — See & Understand / Visual Q&A
```
POST /api/v1/analyze/image
```

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Image file (JPG, PNG, WebP, GIF) |
| `session_id` | String | No | Existing session UUID |
| `question` | String | No | Question about image (Visual Q&A) |
| `detail_level` | String | No | `brief`, `standard`, `detailed` |

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "interaction_id": "uuid",
    "ai_response": {
      "intent": "see_understand",
      "summary": "I can see a well-lit indoor hallway...",
      "details": ["Detail 1", "Detail 2"],
      "entities": [{"type": "scene", "label": "Hallway", "confidence": 0.9}],
      "important_information": [{"label": "Exit", "value": "Door on left", "priority": 1}],
      "confidence": 0.85,
      "needs_clarification": false,
      "response_mode": "text_and_voice",
      "follow_up_suggestions": ["What's on the left?", "Read the sign"],
      "provider": "openai",
      "model": "gpt-4o",
      "processing_time_ms": 1200,
      "demo_mode": false
    },
    "decision": {
      "intent": "see_understand",
      "confidence": 0.9,
      "requires_clarification": false,
      "response_mode": "text_and_voice",
      "safety_concerns": [],
      "recommended_workflow": "analyze_image",
      "context_used": false
    }
  }
}
```

#### Analyze Document — Read & Explain
```
POST /api/v1/analyze/document
```

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Document image |
| `session_id` | String | No | Session UUID |
| `simplify_level` | String | No | `simple`, `very-simple`, `child` |

**Response:** Same structure, `intent: "read_explain"`

#### Analyze Form — Form Assist
```
POST /api/v1/analyze/form
```

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Form image |
| `session_id` | String | No | Session UUID |
| `explain_fields` | String | No | `true`/`false` |

**Response:** `intent: "form_assist"`, entities contain field definitions

#### Ask Question — Visual Q&A Follow-up
```
POST /api/v1/analyze/ask
```

**Request (JSON):**
```json
{
  "session_id": "uuid",
  "question": "What does the sign say?",
  "include_context": true
}
```

**Response:** `intent: "visual_qa"`, uses session context

#### Simplify Text
```
POST /api/v1/analyze/simplify
```

**Request (JSON):**
```json
{
  "text": "The implementation is contingent upon funding...",
  "level": "simple",
  "session_id": "optional-uuid"
}
```

**Response:** `intent: "simplify"`

#### Summarize Text
```
POST /api/v1/analyze/summarize
```

**Request (JSON):**
```json
{
  "text": "Long text to summarize...",
  "session_id": "optional-uuid"
}
```

**Response:** `intent: "summarize"`, `details` contains key points

#### Chat
```
POST /api/v1/analyze/chat
```

**Request (JSON):**
```json
{
  "message": "How can you help me?",
  "session_id": "optional-uuid"
}
```

**Response:** `intent: "chat"`, routes to appropriate feature

---

### Voice Endpoints

#### Transcribe Audio
```
POST /api/v1/voice/transcribe
```

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audio` | File | Yes | Audio file (WAV, MP3, WebM, OGG) |
| `session_id` | String | No | Session UUID |
| `language` | String | No | Language code (e.g., `en`) |

**Response:** `intent: "chat"`, transcription in `summary`

#### Synthesize Speech
```
POST /api/v1/voice/synthesize
```

**Request (JSON):**
```json
{
  "text": "Text to speak",
  "voice": "alloy",
  "speed": 1.0,
  "session_id": "optional-uuid"
}
```

**Response:** Includes `audio_base64` and `audio_mime_type`

---

### Interactions

#### Get Session Interactions
```
GET /api/v1/interactions/session/{session_id}?page=1&page_size=20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 5,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

#### Get Interaction
```
GET /api/v1/interactions/{interaction_id}
```

---

### Providers

#### List Available Providers
```
GET /api/v1/analyze/providers
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vision": ["demo", "openai"],
    "text": ["demo", "openai"],
    "ocr": ["demo", "openai"],
    "stt": ["demo", "openai"],
    "tts": ["demo", "openai"]
  }
}
```

---

## Structured AI Response

All analyze endpoints return `StructuredAIResponse`:

```typescript
interface StructuredAIResponse {
  intent: "see_understand" | "read_explain" | "form_assist" | 
          "visual_qa" | "simplify" | "summarize" | "communicate" | "chat" | "unknown";
  summary: string;
  details: string[];
  entities: Entity[];
  important_information: ImportantInformation[];
  confidence: number;           // 0.0 - 1.0
  needs_clarification: boolean;
  clarification_question: string | null;
  safety_note: string | null;
  response_mode: "text" | "voice" | "text_and_voice" | "visual";
  follow_up_suggestions: string[];
  provider: string;
  model: string;
  processing_time_ms: number;
  demo_mode: boolean;
}

interface Entity {
  type: string;           // "field", "button", "text_block", "sign", "scene"
  label: string;          // Human-readable label
  value: string | null;   // Extracted value
  confidence: number;     // 0.0 - 1.0
  bounding_box: {x, y, width, height} | null;
}

interface ImportantInformation {
  label: string;
  value: string;
  priority: number;       // 1-5
  source: string | null;  // "vision" | "ocr" | "context"
}
```

## Decision Engine Result

```typescript
interface DecisionEngineResult {
  intent: string;
  confidence: number;
  requires_clarification: boolean;
  clarification_question: string | null;
  response_mode: string;
  safety_concerns: string[];
  recommended_workflow: string;
  context_used: boolean;
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `FILE_TOO_LARGE` | 413 | File exceeds 8MB (images) or 25MB (audio) |
| `INVALID_FILE_TYPE` | 400 | Unsupported MIME type |
| `SESSION_NOT_FOUND` | 404 | Session ID doesn't exist |
| `AI_PROVIDER_ERROR` | 502 | Provider returned error |
| `DATABASE_ERROR` | 500 | Persistence failure |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/analyze/*` | 30 req/min |
| `/voice/*` | 20 req/min |
| `/sessions` | 60 req/min |
| `/health` | 120 req/min |

## WebSocket (Planned)

Real-time updates for long-running operations:

```
WS /api/v1/ws/{session_id}
```

Events:
- `analysis.started`
- `analysis.progress`
- `analysis.completed`
- `analysis.failed`