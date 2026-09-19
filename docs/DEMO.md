# Demonstration Guide & Evidence (All 10 Assessment Scenarios)

This document provides step-by-step verification evidence and instructions for each of the 10 required demonstration scenarios outlined in Section 12 of the specification.

You can verify these scenarios using:
- The **DocuQuest Interactive Web Dashboard** at `/` (or `/demo`), OR
- The Swagger UI at `/docs`, OR
- The curl / Postman commands below.

---

## Prerequisites: Quick Authentication

Obtain a JWT token:
```bash
# 1. Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@docuquest.ai","password":"Password123!"}'

# 2. Login to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@docuquest.ai","password":"Password123!"}' | jq -r .access_token)
```

---

## Scenario 1: Uploading a PDF
- **Input Fixture**: `sample_documents/clean_questions.pdf`
- **Action**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@sample_documents/clean_questions.pdf;type=application/pdf"
  ```
- **Result**: HTTP 202 Accepted, returns `document_id` and initial status `"QUEUED"`.

---

## Scenario 2: Uploading an Image
- **Input Fixture**: `sample_documents/low_quality_question.png`
- **Action**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@sample_documents/low_quality_question.png;type=image/png"
  ```
- **Result**: HTTP 202 Accepted. The pipeline detects image MIME type, creates a single page entry, and routes through PIL image preprocessing (grayscale, contrast, upscale) and Tesseract OCR.

---

## Scenario 3: Processing a Scanned / Low-Quality Document
- **Input Fixture**: `sample_documents/scanned_questions.pdf` / `low_quality_question.png`
- **Evidence**:
  - The pipeline detects that the PDF page has `< 10` native characters.
  - Automatically invokes `_ocr(pixmap)` with OCR engine.
  - Page record in `document_pages` is marked with `extraction_method="ocr"` and `ocr_used=true`.

---

## Scenario 4: Extracting Multiple Questions
- **Input Fixture**: `sample_documents/clean_questions.pdf`
- **Action**: Query `GET /api/v1/documents/{document_id}/questions`
- **Result**: Returns multiple questions:
  - `Q1`: "Which letter follows A?"
  - `Q2`: "Select the primary color."
- Structured output file: [`sample_outputs/clean_questions_output.json`](../sample_outputs/clean_questions_output.json)

---

## Scenario 5: Handling a Question Spanning Multiple Pages
- **Input Fixture**: `sample_documents/multipage_question.pdf`
  - Page 1 contains: `Q12. Which option completes this question?\nA. Alpha\nB. Beta`
  - Page 2 contains continuation options: `C. Gamma\nD. Delta`
- **Action**: Query `GET /api/v1/documents/{document_id}/questions`
- **Result**:
  - Question number: `"12"`
  - Options extracted: `A`, `B`, `C`, `D`
  - Provenance: `"pages": [1, 2]`
- Structured output file: [`sample_outputs/multipage_question_output.json`](../sample_outputs/multipage_question_output.json)

---

## Scenario 6: Extracting Question Options
- **Input Fixture**: `sample_documents/clean_questions.pdf`
- **Result**: Each question produces an `options` array where each option has:
  ```json
  {
    "key": "A",
    "text": "Red",
    "confidence": 0.95
  }
  ```
- All standard multiple-choice formats (`A.`, `(A)`, `a)`, etc.) are parsed.

---

## Scenario 7: Detecting and Associating an Answer Key

### A. Same-Document Answer Key:
- Detected automatically when section headers (`Answer Key`, `Solutions`) are present.
- Matched directly during document processing (`Q1 -> A`, `Q2 -> A`).

### B. Cross-Document Answer Key:
- **Input Fixtures**: `sample_documents/question_paper.pdf` and `sample_documents/answer_key.pdf`.
- **Action**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/documents/$PAPER_DOC_ID/relationships" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"target_document_id\":\"$KEY_DOC_ID\",\"relationship_type\":\"ANSWER_KEY\"}"
  ```
- **Result**: Re-triggers cross-document correlation. Question answers are updated to `"status": "MATCHED"` with `"source_document_id": "$KEY_DOC_ID"`.
- Structured output file: [`sample_outputs/cross_document_matching_output.json`](../sample_outputs/cross_document_matching_output.json)

---

## Scenario 8: Showing Uncertain / Low-Confidence Extraction
- **Input Fixture**: `sample_documents/low_quality_question.png`
- **Evidence**:
  - If question options are incomplete or OCR confidence is below threshold (`< 0.85`), question extraction status is set to `PARTIAL` or `REVIEW_REQUIRED`.
  - A `ReviewItem` record is created in the database and accessible via `GET /api/v1/documents/{document_id}/review-items`:
  ```json
  {
    "issue_type": "LOW_CONFIDENCE",
    "reason": "Incomplete options or low OCR confidence",
    "confidence": 0.52
  }
  ```
- Structured output file: [`sample_outputs/scanned_or_low_quality_output.json`](../sample_outputs/scanned_or_low_quality_output.json)

---

## Scenario 9: Retrieving Final Structured Question Data
- **Action**: `GET /api/v1/documents/{document_id}/questions` or `GET /api/v1/questions/{question_id}`
- **Structured Schema Delivered**:
  ```json
  {
    "id": "uuid",
    "question_number": "1",
    "question": "Which letter follows A?",
    "question_type": "MCQ",
    "options": [
      { "key": "A", "text": "B", "confidence": 0.95 },
      { "key": "B", "text": "C", "confidence": 0.95 }
    ],
    "answer": {
      "value": "A",
      "status": "MATCHED",
      "confidence": 0.94
    },
    "source": {
      "document_id": "uuid",
      "pages": [1]
    },
    "confidence": 0.95,
    "status": "SUCCESS",
    "warnings": []
  }
  ```

---

## Scenario 10: Handling Invalid or Unsupported Documents
- **Input Fixture**: `sample_documents/invalid_document.txt`
- **Action**:
  ```bash
  curl -i -X POST "http://localhost:8000/api/v1/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@sample_documents/invalid_document.txt;type=text/plain"
  ```
- **Result**: Rejected immediately with HTTP 415:
  ```json
  {
    "error": {
      "code": "UNSUPPORTED_FILE_TYPE",
      "message": "Only PDF, JPG, JPEG and PNG files are supported."
    }
  }
  ```
- Also tested: MIME spoofing (`.png` containing text) returns HTTP 422 `MALFORMED_DOCUMENT`.
- Structured error output: [`sample_outputs/invalid_document_error.json`](../sample_outputs/invalid_document_error.json)
