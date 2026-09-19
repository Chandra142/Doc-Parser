# Design decisions

- PostgreSQL is the production persistence target; SQLite supports a no-service local test loop.
- Celery/Redis decouples upload latency from processing. `CELERY_EAGER=true` is only for local testing.
- PyMuPDF is first because native PDF text is more accurate and cheaper than OCR.
- OCR and LLM integration are optional provider seams to prevent API keys and heavyweight ML dependencies from blocking startup.
- Confidence is conservative: structurally complete MCQs score .95; incomplete extraction gets .72 and review. Thresholds should become settings in a later iteration.
