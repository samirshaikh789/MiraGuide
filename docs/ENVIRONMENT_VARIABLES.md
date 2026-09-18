# MiraGuide Environment Variables

## Variables Recognized by Backend

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8787 | Server port |
| DEMO_MODE | true | Demo mode (no real AI keys needed) |
| DATABASE_URL | sqlite+aiosqlite:///./miraguide.db | Async DB URL |
| VISION_PROVIDER | demo | demo, openai, gemini |
| TEXT_PROVIDER | demo | demo, openai, gemini, anthropic |
| OCR_PROVIDER | demo | demo, openai, gemini |
| STT_PROVIDER | demo | demo, openai |
| TTS_PROVIDER | demo | demo, openai |
| OPENAI_API_KEY | - | OpenAI key (sk-...) |
| OPENAI_MODEL | gpt-4o-mini | Text model |
| OPENAI_VISION_MODEL | gpt-4o | Vision model |
| GEMINI_API_KEY | - | Google Gemini API key |
| GEMINI_MODEL | gemini-1.5-flash | Gemini model |
| ANTHROPIC_API_KEY | - | Claude API key |
| ANTHROPIC_MODEL | claude-3-haiku-20240307 | Claude model |
| CORS_ORIGINS | http://localhost:5173,... | Allowed origins |

## Quick Start (No Keys Needed)

DEMO_MODE is true by default. No .env file required.

`ash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787
`

## NOTE on root .env

The root .env file uses AI_API_KEY and AI_MODEL which are NOT read by the backend.
The backend reads OPENAI_API_KEY, GEMINI_API_KEY, etc. as shown above.
