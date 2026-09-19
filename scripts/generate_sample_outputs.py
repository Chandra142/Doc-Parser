"""Generate sample extracted outputs for deliverable #4 of the assignment."""
import json
import os
import shutil
from pathlib import Path

# Configure environment for deterministic local execution
os.environ["DATABASE_URL"] = "sqlite:///./sample_outputs_gen.db"
os.environ["CELERY_EAGER"] = "true"

from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "sample_documents"
OUTPUTS_DIR = ROOT / "sample_outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client = TestClient(app)

    # Register & login
    client.post(
        "/api/v1/auth/register",
        json={"email": "evaluator@docuquest.ai", "password": "password123"},
    )
    auth_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "evaluator@docuquest.ai", "password": "password123"},
    )
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Helper function to upload and get questions
    def process_and_extract(filename, content_type="application/pdf"):
        file_path = SAMPLES_DIR / filename
        data = file_path.read_bytes()
        up_resp = client.post(
            "/api/v1/documents",
            headers=headers,
            files={"file": (filename, data, content_type)},
        )
        if up_resp.status_code != 202:
            return {"upload_error": up_resp.json()}

        doc_id = up_resp.json()["document_id"]
        status_resp = client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
        questions_resp = client.get(
            f"/api/v1/documents/{doc_id}/questions", headers=headers
        )
        reviews_resp = client.get(
            f"/api/v1/documents/{doc_id}/review-items", headers=headers
        )

        return {
            "document_id": doc_id,
            "filename": filename,
            "job_status": status_resp.json(),
            "extracted_questions": questions_resp.json(),
            "review_items": reviews_resp.json(),
        }

    print("Generating sample output for clean_questions.pdf...")
    clean_output = process_and_extract("clean_questions.pdf")
    (OUTPUTS_DIR / "clean_questions_output.json").write_text(
        json.dumps(clean_output, indent=2), encoding="utf-8"
    )

    print("Generating sample output for multipage_question.pdf...")
    multipage_output = process_and_extract("multipage_question.pdf")
    (OUTPUTS_DIR / "multipage_question_output.json").write_text(
        json.dumps(multipage_output, indent=2), encoding="utf-8"
    )

    print("Generating sample output for cross_document_matching...")
    paper_file = SAMPLES_DIR / "question_paper.pdf"
    paper_up = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("question_paper.pdf", paper_file.read_bytes(), "application/pdf")},
    ).json()
    paper_id = paper_up["document_id"]

    key_file = SAMPLES_DIR / "answer_key.pdf"
    key_up = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("answer_key.pdf", key_file.read_bytes(), "application/pdf")},
    ).json()
    key_id = key_up["document_id"]

    # Link relationship
    link_resp = client.post(
        f"/api/v1/documents/{paper_id}/relationships",
        headers=headers,
        json={"target_document_id": key_id, "relationship_type": "ANSWER_KEY"},
    )

    cross_questions = client.get(
        f"/api/v1/documents/{paper_id}/questions", headers=headers
    ).json()
    cross_doc_output = {
        "question_paper_document_id": paper_id,
        "answer_key_document_id": key_id,
        "relationship": link_resp.json(),
        "extracted_questions_with_matched_answers": cross_questions,
    }
    (OUTPUTS_DIR / "cross_document_matching_output.json").write_text(
        json.dumps(cross_doc_output, indent=2), encoding="utf-8"
    )

    print("Generating sample output for invalid_document.txt (unsupported file rejection)...")
    invalid_file = SAMPLES_DIR / "invalid_document.txt"
    invalid_resp = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("invalid_document.txt", invalid_file.read_bytes(), "text/plain")},
    )
    (OUTPUTS_DIR / "invalid_document_error.json").write_text(
        json.dumps(
            {
                "status_code": invalid_resp.status_code,
                "response_body": invalid_resp.json(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Generating sample output for low_quality_question.png (OCR review scenario)...")
    import app.services as services
    original_ocr = services._ocr
    services._ocr = lambda _: services.OCRResult(
        "Q1. Low quality question\nA. Alpha\nB. Beta\nC. Gamma\nD. Delta", 0.52
    )
    try:
        ocr_output = process_and_extract("low_quality_question.png", "image/png")
        (OUTPUTS_DIR / "scanned_or_low_quality_output.json").write_text(
            json.dumps(ocr_output, indent=2), encoding="utf-8"
        )
    finally:
        services._ocr = original_ocr

    print(f"Sample outputs successfully generated in {OUTPUTS_DIR}")

    # Cleanup temporary generator db
    engine.dispose()
    temp_db = Path("./sample_outputs_gen.db")
    try:
        if temp_db.exists():
            temp_db.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
