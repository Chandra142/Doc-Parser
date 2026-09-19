---
title: DocuQuest - Document Intelligence & Exam Extraction
emoji: 📑
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# DocuQuest

> **Document Intelligence & Question Extraction Service**  
> Ingests examination material across PDF and image formats (PNG, JPG, JPEG), extracts structured questions and multiple-choice options across single/multiple pages, correlates answer keys, provides confidence scoring, and flags uncertain items for human review.

---

## 🌟 Features & Highlights

- **Multi-Format Ingestion**: Supports digital PDFs, scanned PDFs, and raster images (PNG, JPG, JPEG) up to 20MB with magic-byte and MIME verification.
- **Hybrid Extraction Pipeline**:
  - High-speed native vector text extraction via **PyMuPDF (`fitz`)**.
  - Automatic fallback to **Tesseract OCR** with image preprocessing (grayscale, contrast boost, thresholding, 2x upscaling) for scanned pages and images.
- **Advanced Question Parsing**:
  - Regex-based recognition of multiple question numbering schemas (`Q1.`, `Question 01)`, `1.`).
  - Robust option parsing (`(A)`, `A.`, etc.).
  - **Multi-Page Question Continuation**: Preserves active question context when questions or options cross page boundaries, accurately tracking provenance (`"pages": [1, 2]`).
- **Answer Key Correlation**:
  - **Same-Document Matching**: Detects answer key sections and correlates solutions to questions.
  - **Cross-Document Association**: Links separate Question Papers and Answer Keys via `/relationships` to associate answers with document/page provenance.
- **Confidence Scoring & Human Review**:
  - Transparent confidence calculation based on structure, options, and OCR scores.
  - Automatically raises `ReviewItem` alerts for low-confidence or incomplete extractions.
- **Interactive Web Demo Dashboard**:
  - Embedded web UI at `/` and `/demo` to test all scenarios directly in any browser.
- **Enterprise Security**:
  - Bcrypt password hashing and HMAC-SHA256 JWT bearer tokens.
  - Strict ownership isolation on all document resources (IDOR protection).
  - Server-side UUID file naming to prevent path traversal.

---

## 🌐 Live Demo & Free Cloud Deployment

### 1. Interactive Web UI
Visit the service root URL (`/` or `/demo`):
- **1-Click Demo Login** button (no manual typing required).
- Built-in test buttons for all 10 assessment scenarios.
- Live progress polling and visual question card viewer.
- Interactive Swagger UI available at `/docs`.

### 2. Free Cloud Deployment (Render / Hugging Face)
This repository is configured for immediate zero-cost cloud deployment:
- **Render**: Connect your GitHub repository to [Render](https://render.com). It automatically detects [`render.yaml`](render.yaml) and provisions a free Docker web service with Tesseract pre-installed.
- **Hugging Face Spaces**: Create a free Docker Space on [Hugging Face](https://huggingface.co/spaces) and push this repository (provides 16GB RAM + 2 vCPUs at zero cost).
- Detailed step-by-step instructions: see [Deployment Guide](docs/DEPLOYMENT.md).

---

## 🚀 Quickstart & Local Setup

### Option A: Self-Contained Local Run (No external services needed)
```bash
# 1. Install dependencies
pip install -e .[dev]

# 2. Run with SQLite and Eager In-Process Queue
export DATABASE_URL="sqlite:///./docuquest.db"
export CELERY_EAGER="true"
uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000` in your browser.

### Option B: Production Multi-Container Stack (Docker Compose)
```bash
cp .env.example .env
docker compose up --build
```
This starts:
- **FastAPI Web App** on `http://localhost:8000`
- **PostgreSQL 16** on `localhost:5432`
- **Redis 7** on `localhost:6379`
- **Celery Worker** on the `documents` queue

---

## 📁 Repository Structure

```
DocuQuest/
├── app/
│   ├── core/           # Security, JWT, and Pydantic configuration
│   ├── static/         # Interactive Web Demo UI (HTML/Tailwind)
│   ├── db.py           # SQLAlchemy database session engine
│   ├── deps.py         # Auth & ownership verification dependencies
│   ├── main.py         # FastAPI routes, lifespan, and error handlers
│   ├── models.py       # SQLAlchemy ORM models
│   ├── services.py     # Ingestion, OCR, and question extraction pipeline
│   └── workers.py      # Celery task definitions
├── docs/
│   ├── ARCHITECTURE.md # Architecture diagram & modular monolith design
│   ├── DEMO.md         # Evidence & walkthrough for all 10 required scenarios
│   ├── DEPLOYMENT.md   # Free cloud deployment guide (Render, HF Spaces)
│   ├── DESIGN_DECISIONS.md
│   ├── PROCESSING_PIPELINE.md
│   └── REQUIREMENT_MATRIX.md
├── migrations/         # Alembic database migrations
├── postman/
│   └── collection.json # Postman API test collection
├── sample_documents/   # Synthetic test documents (PDF, PNG, text)
├── sample_outputs/     # Extracted JSON sample outputs (Deliverable #4)
├── scripts/
│   ├── generate_sample_documents.py # Input fixture generator
│   └── generate_sample_outputs.py   # Output extraction generator
├── tests/              # Pytest test suite (13 automated tests)
├── Dockerfile          # Container specification with Tesseract OCR
├── docker-compose.yml  # Multi-service stack (API, Worker, Postgres, Redis)
├── render.yaml         # 1-Click Render Blueprint configuration
└── pyproject.toml      # Project metadata and dependencies
```

---

## 🧪 Automated Tests

Run the comprehensive test suite:
```bash
pytest -v
```

The suite includes 13 test cases covering:
- Authentication & duplicate registration rejection
- File extension, MIME type, and corrupted file validation
- Single-page and multi-page question extraction & continuation
- Answer key detection (embedded and cross-document)
- Low-confidence scoring & review items
- IDOR ownership isolation (non-enumerable documents)
- Synthetic fixture verification

---

## 📋 Assessment Scenarios Matrix

| Scenario | Tested In | Evidence / Output |
|---|---|---|
| 1. Uploading a PDF | `test_api.py`, Web UI | [`sample_outputs/clean_questions_output.json`](sample_outputs/clean_questions_output.json) |
| 2. Uploading an image | `test_release_api.py`, Web UI | [`sample_outputs/scanned_or_low_quality_output.json`](sample_outputs/scanned_or_low_quality_output.json) |
| 3. Scanned document OCR | `test_pipeline.py`, Web UI | Processed via PIL + Tesseract pipeline |
| 4. Extracting multiple questions | `test_api.py`, Web UI | Questions Q1 and Q2 extracted with options |
| 5. Multi-page question continuation | `test_pipeline.py`, `test_sample_fixtures.py` | [`sample_outputs/multipage_question_output.json`](sample_outputs/multipage_question_output.json) |
| 6. Extracting question options | `test_pipeline.py`, Web UI | Standardized key/text/confidence array |
| 7. Answer key association | `test_sample_fixtures.py`, Web UI | [`sample_outputs/cross_document_matching_output.json`](sample_outputs/cross_document_matching_output.json) |
| 8. Uncertain / low-confidence items | `test_pipeline.py`, Web UI | `ReviewItem` generated with `LOW_CONFIDENCE` reason |
| 9. Structured question output | `test_api.py`, Web UI | Normalized JSON response conforming to spec |
| 10. Invalid document handling | `test_release_api.py`, Web UI | [`sample_outputs/invalid_document_error.json`](sample_outputs/invalid_document_error.json) |

For complete command examples and raw output verification, see [`docs/DEMO.md`](docs/DEMO.md).
