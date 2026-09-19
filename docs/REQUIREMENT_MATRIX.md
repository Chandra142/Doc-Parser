# Requirement matrix

| Requirement | Implementation | Verification / test | Status |
|---|---|---|---|
| Authentication and ownership | JWT + ownership dependency | API regression tests | PASS |
| Upload validation | extension, MIME, magic/decode and size checks | API regression tests | PASS |
| Native PDF questions/options | PyMuPDF + parser | API/pipeline tests | PASS |
| Image/scanned OCR | Tesseract provider, preprocessing, hybrid fallback | mocked provider-path test; Docker runtime blocked | PARTIAL |
| Multi-page questions | active-question page continuation | pipeline test | PASS |
| Same-document answer keys | context-aware answer parser | pipeline/API tests | PASS |
| Cross-document answer keys | relationship-triggered matcher + provenance fields | fixture-backed API test; no Docker runtime integration | PARTIAL |
| Confidence/review | configurable thresholds and review persistence | parser tests | PARTIAL |
| PostgreSQL/Alembic | SQLAlchemy model + two migrations | migration/table inspection | PASS |
| Redis/Celery async | Celery worker and Compose broker | static configuration only | BLOCKED - local Docker daemon unavailable |
| Swagger/Postman | FastAPI OpenAPI and collection | OpenAPI import/config review | PASS |
| Docker runtime | API/worker/PostgreSQL/Redis Compose configuration | `docker compose config --quiet` | BLOCKED - local Docker daemon unavailable |
| Synthetic input fixture corpus | generated PDF/PNG/text inputs under `sample_documents/` | fixture-backed API tests | PASS |
