# Processing pipeline

Upload → validate/secure storage → `Document` + `ProcessingJob` → Celery queue → native text extraction → OCR-needed page marking → normalization/boundary detection → option and continuation parsing → answer-key matching → confidence/review persistence.

The deterministic parser keeps an active question across page changes until a new credible question heading is seen. Answer matches require a number and answer-key heading; otherwise no answer is silently assigned.
