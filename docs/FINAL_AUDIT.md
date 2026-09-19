# Final audit

## Environment and commands

Windows host, Python 3.11. `pytest -q` completed with **13 passed**. `python -m compileall -q app migrations`, `alembic upgrade head`, `docker compose config --quiet`, Postman JSON parsing, and SQLAlchemy table inspection all passed.

The expected tables exist: users, documents, document_pages, processing_jobs, questions, question_options, question_sources, answers, review_items, and document_relationships.

## Verified application behavior

- Registration, duplicate registration, login failure, `/me`, missing/malformed token handling, and ownership isolation are covered by tests.
- Upload extension, MIME, magic-byte/decode and malformed-file failures return structured HTTP errors.
- Native-PDF parsing, options, same-document and cross-document answer-key entries, multi-page continuation, OCR provider path, and extraction metadata are covered by deterministic tests.
- Alembic has applied the extraction-method migration and OpenAPI loads successfully.
- The Postman collection includes current document, question, answer, review, image-upload and relationship URLs and validates as JSON.

## Docker and runtime status

`docker compose config --quiet` passed. `docker info` reports that Docker Desktop's Linux daemon is unavailable; therefore the Compose stack, real Redis/Celery task execution, live API workflow, and physical Tesseract execution could not be run on this host. This is a blocked verification, not a pass.

## Security review

No repository API keys, production tokens, or production credentials were found. Secrets are environment-configured; checked-in default values are explicitly development-only. Passwords use bcrypt, JWTs are signed, protected data is ownership-checked, stored filenames are server generated, and errors do not expose traces. Malware scanning, TLS/rate limiting and production object-store encryption remain deployment hardening work.

## Known limitations

The deterministic OCR-provider test mocks the provider because the host lacks Tesseract; the Dockerfile installs it for container use. A reproducible generator has created synthetic PDF/PNG/text inputs under `sample_documents/`; no extraction outputs are presented as runtime evidence. LLM extraction is not implemented. Confidence rules are transparent but deliberately simple. Cross-document matching passes fixture-backed API testing but awaits real stack integration verification.
