# MiraGuide Feature Matrix

**Date:** 2026-09-17  
**Status:** Current state vs. Target MVP

---

## Feature Completeness Matrix

| Feature | UI Exists | API Exists | Backend Works | DB Works | AI Works | E2E Works | Status |
|---------|-----------|------------|---------------|----------|----------|-----------|--------|
| **Image Analysis (See & Understand)** | ✅ VisionPage | ✅ `/api/ai/analyze-image` | ❌ Mock only | ❌ No DB | ❌ Mock | ❌ Broken | Mock only |
| **OCR / Read Text** | ✅ ReadTextPage | ✅ `/api/ocr` | ❌ Mock only | ❌ No DB | ❌ Mock | ❌ Broken | Mock only |
| **Form Assist** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Visual Q&A (Ask About What You See)** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Voice Input (Browser STT)** | ✅ VoicePage, CaptionsPage | N/A (browser) | N/A | N/A | ⚠️ Browser only | ⚠️ Partial | Browser only |
| **Voice Output (Browser TTS)** | ✅ All pages | N/A (browser) | N/A | N/A | ✅ Works | ✅ Works | Browser TTS |
| **Voice Input (Backend STT)** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Voice Output (Backend TTS)** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Sessions** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ No DB | N/A | ❌ Missing | **Not implemented** |
| **Follow-up Context** | ⚠️ Chat only | ❌ Missing | ❌ Missing | ❌ No DB | ❌ Missing | ❌ Broken | Partial (chat only) |
| **Accessibility Settings** | ✅ SettingsPage | ❌ No API | N/A | localStorage | N/A | ✅ Works | Frontend only |
| **Accessibility Decision Engine** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Structured AI Output** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Confidence / Safety Evaluation** | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing | **Not implemented** |
| **Text Simplification** | ✅ UnderstandPage | ✅ `/api/ai/simplify-text` | ❌ Mock only | ❌ No DB | ❌ Mock | ❌ Broken | Mock only |
| **Summarization** | ✅ UnderstandPage | ✅ `/api/summarize` | ❌ Mock only | ❌ No DB | ❌ Mock | ❌ Broken | Mock only |
| **Communication Board** | ✅ CommunicatePage | ✅ `/api/ai/communicate` | ❌ Mock only | localStorage | ❌ Mock | ⚠️ Partial | Mock only |
| **Live Captions** | ✅ CaptionsPage | N/A (browser) | N/A | localStorage | Browser STT | ✅ Works | Browser only |
| **Sound Alerts (Demo)** | ✅ SoundAlertsPage | N/A | N/A | N/A | Demo sim | ✅ Works | Demo only |
| **Emergency Help Flow** | ✅ EmergencyPage | N/A | N/A | N/A | N/A | ✅ Works | Frontend only |

---

## Workflow Coverage

| Workflow | Steps | Current Coverage |
|----------|-------|------------------|
| **A: See & Understand** | Upload → Validate → Process → Multimodal Analysis → Understand → Accessible Explanation → Structured Result → Follow-up | 2/7 steps (UI + mock API) |
| **B: Read & Explain** | Input → OCR → Content Understanding → Simplification → Accessible Response → Follow-up | 2/6 steps (UI + mock API) |
| **C: Form Assist** | Upload Form → Identify Fields/Labels/Instructions/Structure → Explain Form → Field-by-field → Follow-up | 0/6 steps (Missing entirely) |
| **D: Ask About What You See** | Visual Input + Question + Context → Combined Processing → Response → Follow-up | 0/4 steps (Missing entirely) |

---

## Technical Debt Summary

| Area | Current | Target | Gap |
|------|---------|--------|-----|
| Backend Language | Node.js/Express | Python/FastAPI | **Complete rewrite** |
| Database | None (localStorage) | PostgreSQL + SQLAlchemy | **New implementation** |
| AI Integration | Mock service | Provider abstractions + real AI | **New implementation** |
| API Structure | Flat `/api/*` | Versioned `/api/v1/*` | **Restructure** |
| Validation | None | Pydantic (backend) + Zod (frontend) | **New implementation** |
| Routing | Hash-based | React Router | **Replace** |
| State Management | React hooks + localStorage | TanStack Query + React state | **Replace** |
| Forms | Native HTML | React Hook Form + Zod | **Add** |
| UI Components | Custom Tailwind | shadcn/ui + Radix | **Replace** |
| Authentication | None | Session-based (future) | **Design needed** |
| File Security | Basic (8MB, memory) | MIME validation, temp files, cleanup | **Enhance** |
| Error Handling | Basic try/catch | Structured error codes, request IDs | **Enhance** |

---

## Priority Repair Order

### P0 — Blockers (Week 1)
- [ ] Python/FastAPI backend scaffold
- [ ] PostgreSQL + SQLAlchemy + Alembic setup
- [ ] AI Provider abstractions (Vision, Text, OCR, Speech)
- [ ] Request validation (Pydantic)
- [ ] Structured error handling

### P1 — Core Workflows (Week 1-2)
- [ ] VisionProvider + `/api/v1/analyze/image`
- [ ] OCRProvider + `/api/v1/analyze/document`
- [ ] Form analysis + `/api/v1/analyze/form`
- [ ] Visual Q&A + `/api/v1/analyze/ask`
- [ ] Accessibility Decision Engine

### P2 — Persistence & Context (Week 2)
- [ ] Session management (`/api/v1/sessions`)
- [ ] Interaction history + context retrieval
- [ ] User preferences in DB

### P3 — Frontend Integration (Week 2-3)
- [ ] TanStack Query setup
- [ ] React Router migration
- [ ] React Hook Form + Zod
- [ ] shadcn/ui + Radix migration
- [ ] MiraGuide branding

### P4 — Voice (Week 3)
- [ ] Backend STT/TTS providers
- [ ] Frontend integration (fallback to browser)

### P5 — Polish & Demo (Week 3-4)
- [ ] E2E demo test
- [ ] Accessibility audit
- [ ] Deployment config
- [ ] Documentation