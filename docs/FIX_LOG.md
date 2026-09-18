# MiraGuide Backend Fix Log

## Fix 1 - Async SQLAlchemy Greenlet Error
- Date: 2026-09-18
- File: backend/app/api/v1/analyze.py
- Error: greenlet_spawn has not been called
- Root cause: Routes used async for db in get_db() instead of Depends(get_db)
- Fix: Added db: AsyncSession = Depends(get_db) to image/document/form routes
- Verified: PASS

## Fix 2 - Missing db Parameter in ask_question()
- Date: 2026-09-18
- File: backend/app/services/ai_service.py
- Error: AIService.ask_question() got an unexpected keyword argument db
- Fix: Added db: Optional[AsyncSession] = None parameter
- Verified: PASS

## Fix 3 - Missing has_form Parameter in detect_intent()
- Date: 2026-09-18
- File: backend/app/services/decision_engine.py
- Error: name has_form is not defined
- Fix: Added has_form: bool = False to detect_intent() signature
- Verified: PASS

## Fix 4 - Async Lazy-Load of session.interactions
- Date: 2026-09-18
- File: backend/app/services/decision_engine.py
- Risk: Would cause greenlet error on sessions with 2+ interactions
- Fix: Removed session.interactions access; use session.context_data
- Verified: PASS

## Fix 5 - datetime.utcnow() Deprecation
- File: backend/app/services/ai_service.py
- Change: datetime.utcnow() changed to datetime.now(timezone.utc)

## Fix 6 - pyproject.toml TOML Syntax
- File: backend/pyproject.toml
- Change: Fixed per-file-ignores to use [tool.ruff.per-file-ignores] section

## Fix 7 - Test Assertions
- File: backend/tests/test_backend.py
- Change: Fixed health and session test assertions to match real response shapes
