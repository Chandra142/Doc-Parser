"""
Regression test: OCR text must be reconstructed with line breaks.

Previously TesseractOCRProvider joined all words into a single flat string,
which caused parse_questions() to see one long line starting with non-numeric
text, so the QUESTION regex never matched and questions were always empty.
"""
import io
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_regression.db")
os.environ.setdefault("CELERY_EAGER", "true")

import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, engine

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

client = TestClient(app)


def _auth(email="reg@test.com"):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def _make_question_image() -> bytes:
    """Create a synthetic PNG with question text on multiple lines."""
    img = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(img)
    lines = [
        "1. What is the capital of France?",
        "A) Berlin",
        "B) Madrid",
        "C) Paris",
        "D) Rome",
        "Answer Key",
        "1 - C",
    ]
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black")
        y += 35
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_line_reconstruction_yields_questions():
    """
    Regression: after OCR, the extracted text must have newlines so that
    parse_questions() can match question-starting lines.
    If TesseractOCRProvider joins all words with spaces (old bug), this test
    returns an empty list.
    """
    h = _auth()
    png_bytes = _make_question_image()
    res = client.post(
        "/api/v1/documents",
        headers=h,
        files={"file": ("question.png", png_bytes, "image/png")},
    )
    assert res.status_code == 202, res.text
    doc_id = res.json()["document_id"]

    questions = client.get(f"/api/v1/documents/{doc_id}/questions", headers=h).json()

    # Must find at least one question
    assert isinstance(questions, list), "Expected a list of questions"
    assert len(questions) >= 1, (
        "No questions detected from image -- OCR line reconstruction bug may have regressed. "
        f"Got: {questions!r}"
    )
    q = questions[0]
    assert q["question_number"] == "1"
    assert "France" in q["question"]
