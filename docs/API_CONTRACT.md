# MiraGuide API Contract

Base URL: http://localhost:8787

## Sessions

### POST /api/v1/sessions
Request: {} or {user_id: string}
Response: ResponseEnvelope<{id, user_id, created_at, updated_at, context_data}>

### GET /api/v1/sessions/{session_id}
Response: ResponseEnvelope<SessionResponse>

### DELETE /api/v1/sessions/{session_id}
Response: ResponseEnvelope<{message}>

## Analyze

All analyze endpoints return: ResponseEnvelope<{session_id, interaction_id, ai_response, decision}>

ai_response shape: {intent, summary, details[], entities[], important_information[], confidence, needs_clarification, clarification_question, safety_note, response_mode, follow_up_suggestions[], provider, model, processing_time_ms, demo_mode}

### POST /api/v1/analyze/image (multipart/form-data)
Fields: image (file, required), session_id (string), question (string), detail_level (brief|standard|detailed)

### POST /api/v1/analyze/document (multipart/form-data)
Fields: image (file, required), session_id (string), simplify_level (simple|very-simple|child)

### POST /api/v1/analyze/form (multipart/form-data)
Fields: image (file, required), session_id (string), explain_fields (true|false)

### POST /api/v1/analyze/ask (application/json)
Body: {session_id (UUID, required), question (string, required), include_context (bool)}

### POST /api/v1/analyze/chat (application/json)
Body: {message (string, required), session_id (UUID)}

### POST /api/v1/analyze/simplify (application/json)
Body: {text (string, required), level (simple|very-simple|child), session_id (UUID)}

### POST /api/v1/analyze/summarize (application/json)
Body: {text (string, required), session_id (UUID)}

### GET /api/v1/analyze/providers
Response: ResponseEnvelope<{vision[], text[], ocr[], stt[], tts[]}>

## Voice

### POST /api/v1/voice/transcribe (multipart/form-data)
Fields: audio (file, required), session_id (string), language (string)

### POST /api/v1/voice/synthesize (application/json)
Body: {text (string, required), voice (string), speed (float), session_id (UUID)}
Response: ResponseEnvelope<{session_id, interaction_id, ai_response, decision, audio_base64, audio_mime_type}>

## Interactions

### GET /api/v1/interactions/session/{session_id}?page=1&page_size=20
Response: ResponseEnvelope<PaginatedResponse<InteractionResponse>>

### GET /api/v1/interactions/{interaction_id}
Response: ResponseEnvelope<InteractionResponse>

## Health

### GET /api/health
Response: {status, version, demo_mode, database, ai_providers} (flat, NOT wrapped in ResponseEnvelope)

## ResponseEnvelope Shape

{success: bool, data: T, error: string|null, error_code: string|null, request_id: string|null, demo_mode: bool}

## Error Responses

400 Bad Request: Invalid file type or bad input
404 Not Found: Session or interaction not found
413 Request Entity Too Large: File > 8MB
422 Unprocessable Entity: Missing required fields
500 Internal Server Error: AI processing failure
