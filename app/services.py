import io
import re
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import fitz
from PIL import Image, ImageEnhance, ImageOps
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Answer,
    Document,
    DocumentPage,
    DocumentRelationship,
    ProcessingJob,
    Question,
    QuestionOption,
    QuestionSource,
    ReviewItem,
)

QUESTION = re.compile(
    r"(?im)^\s*(?:q(?:uestion)?\s*\.?\s*)?(\d{1,4})\s*[\.)\]:\-]+\s*(.+)$"
)
OPTION = re.compile(r"(?im)^\s*(?:\(?([A-Da-d])\)|([A-Da-d])[\.)])\s*(.+)$")
ANSWER_HEADING = re.compile(r"(?i)\b(answer\s*(?:key|sheet)|solutions?)\b")
ANSWER = re.compile(r"(?im)^\s*(?:q\.?\s*)?(\d{1,4})\s*[\.:\-)]+\s*\(?([A-Da-d])\)?\s*$")


@dataclass
class OCRResult:
    text: str
    confidence: float | None
    rotation: int = 0


class BaseOCRProvider:
    def extract(self, image: Image.Image) -> OCRResult:
        raise NotImplementedError


class TesseractOCRProvider(BaseOCRProvider):
    def extract(self, image: Image.Image) -> OCRResult:
        try:
            import pytesseract

            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT, config="--psm 6"
            )
        except Exception as exc:
            raise RuntimeError("Tesseract OCR is unavailable") from exc

        # Reconstruct proper line breaks from Tesseract block/line metadata.
        # Previously all words were joined with " ".join() into one flat string,
        # which caused parse_questions()'s splitlines() to see a single line
        # starting with non-numeric text, so the QUESTION regex never matched.
        lines: dict[tuple, list[str]] = {}
        scores = []
        for word, score, block, line_num in zip(
            data["text"], data["conf"], data["block_num"], data["line_num"]
        ):
            if word.strip():
                key = (block, line_num)
                lines.setdefault(key, []).append(word)
                try:
                    if float(score) >= 0:
                        scores.append(float(score) / 100)
                except ValueError:
                    pass

        reconstructed = "\n".join(
            " ".join(words) for words in lines.values()
        )
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return OCRResult(text=reconstructed, confidence=avg_score)


def get_ocr_provider() -> BaseOCRProvider:
    if settings.ocr_provider.lower() == "tesseract":
        return TesseractOCRProvider()
    raise RuntimeError(f"Unsupported OCR provider: {settings.ocr_provider}")


def preprocess(image: Image.Image) -> Image.Image:
    image = ImageOps.grayscale(image)
    if settings.ocr_upscale_factor > 1:
        image = image.resize(
            (
                image.width * settings.ocr_upscale_factor,
                image.height * settings.ocr_upscale_factor,
            )
        )
    return ImageEnhance.Contrast(image).enhance(1.8).point(lambda v: 255 if v > 150 else 0)


def _ocr(image: Image.Image) -> OCRResult:
    return get_ocr_provider().extract(preprocess(image))


class StorageProvider:
    def save(self, src: io.BytesIO, original: str) -> tuple[str, str]:
        raise NotImplementedError
    def get_file_content(self, path: str) -> bytes:
        raise NotImplementedError

class LocalStorage(StorageProvider):
    def save(self, src: io.BytesIO, original: str) -> tuple[str, str]:
        settings.storage_path.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4()}{Path(original).suffix.lower()}"
        target = settings.storage_path / name
        with target.open("wb") as out:
            shutil.copyfileobj(src, out)
        return name, str(target.resolve())
    def get_file_content(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

class S3Storage(StorageProvider):
    def __init__(self):
        import boto3
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
            endpoint_url=settings.s3_endpoint_url
        )
        self.bucket = settings.s3_bucket_name
    def save(self, src: io.BytesIO, original: str) -> tuple[str, str]:
        name = f"{uuid.uuid4()}{Path(original).suffix.lower()}"
        self.s3.upload_fileobj(src, self.bucket, name)
        return name, name
    def get_file_content(self, path: str) -> bytes:
        out = io.BytesIO()
        self.s3.download_fileobj(self.bucket, path, out)
        return out.getvalue()

def get_storage() -> StorageProvider:
    if settings.storage_backend == "s3":
        return S3Storage()
    return LocalStorage()


def validate_content(data: bytes, kind: str) -> None:
    if kind == "pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError("Malformed PDF signature")
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            doc.close()
        except Exception as exc:
            raise ValueError("Malformed PDF") from exc
    else:
        try:
            Image.open(io.BytesIO(data)).verify()
        except Exception as exc:
            raise ValueError("Malformed image") from exc


def extract_pages(path: str, file_type: str) -> list[tuple[int, str, int, str, float | None]]:
    data = get_storage().get_file_content(path)
    if file_type == "pdf":
        doc = fitz.open(stream=data, filetype="pdf")
        result = []
        try:
            if not doc.page_count:
                raise ValueError("PDF contains no pages")
            for i, page in enumerate(doc):
                text = page.get_text("text").strip()
                if len(re.sub(r"\s+", "", text)) >= settings.native_text_min_chars:
                    result.append((i + 1, text, page.rotation, "native_pdf", 1.0))
                else:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr = _ocr(img)
                    result.append((i + 1, ocr.text, page.rotation, "ocr", ocr.confidence))
            return result
        finally:
            doc.close()

    with Image.open(io.BytesIO(data)) as image:
        ocr = _ocr(image.copy())
        return [(1, ocr.text, 0, "ocr", ocr.confidence)]


def parse_questions(pages: list[tuple]) -> list[dict]:
    chunks = []
    current = None
    in_answer_section = False

    for page, text, *_ in pages:
        for line in text.splitlines():
            line = re.sub(r"\s+", " ", line).strip()
            if ANSWER_HEADING.search(line):
                in_answer_section = True
                continue
            if in_answer_section:
                continue

            m = QUESTION.match(line)
            if m and not ANSWER_HEADING.search(line):
                if current:
                    chunks.append(current)
                current = {
                    "number": m.group(1).lstrip("0") or "0",
                    "lines": [m.group(2)],
                    "pages": [page],
                }
            elif current and line and not ANSWER_HEADING.match(line):
                current["lines"].append(line)
                if page not in current["pages"]:
                    current["pages"].append(page)

    if current:
        chunks.append(current)
    return chunks


def answer_entries(pages: list[tuple]) -> dict[str, tuple[str, int]]:
    active = False
    entries = {}
    for page, text, *_ in pages:
        for line in text.splitlines():
            if ANSWER_HEADING.search(line):
                active = True
                continue
            m = ANSWER.match(line)
            if m and (active or entries):
                entries[m.group(1).lstrip("0") or "0"] = (m.group(2).upper(), page)
    return entries


def _match_related(db: Session, doc_id: str) -> None:
    relationships = db.query(DocumentRelationship).filter_by(
        source_document_id=doc_id, relationship_type="ANSWER_KEY"
    )
    for rel in relationships:
        target_pages = db.query(DocumentPage).filter_by(document_id=rel.target_document_id)
        entries = answer_entries(
            [
                (
                    p.page_number,
                    p.extracted_text,
                    p.rotation,
                    p.extraction_method,
                    p.ocr_confidence,
                )
                for p in target_pages
            ]
        )
        for q in db.query(Question).filter_by(document_id=doc_id):
            if q.question_number in entries:
                value, page = entries[q.question_number]
                a = q.answer or Answer(
                    question_id=q.id, answer=None, confidence=0, status="UNCERTAIN"
                )
                a.answer = value
                a.status = "MATCHED"
                a.confidence = 0.96
                a.source_document_id = rel.target_document_id
                a.source_page = page
                db.add(a)


def process_document(db: Session, document_id: str) -> None:
    doc = db.get(Document, document_id)
    job = (
        db.query(ProcessingJob)
        .filter_by(document_id=document_id)
        .order_by(ProcessingJob.created_at.desc())
        .first()
    )
    if not doc or not job:
        return

    try:
        doc.status = job.status = "PROCESSING"
        job.started_at = datetime.utcnow()
        job.progress = 10
        db.commit()

        pages = extract_pages(doc.storage_path, doc.file_type)
        for n, text, rotation, method, ocr_conf in pages:
            db.add(
                DocumentPage(
                    document_id=doc.id,
                    page_number=n,
                    extracted_text=text,
                    extraction_method=method,
                    ocr_used=(method == "ocr"),
                    ocr_confidence=ocr_conf,
                    rotation=rotation,
                )
            )

        doc.status = "EXTRACTING"
        job.progress = 55
        db.commit()

        answers = answer_entries(pages)

        for item in parse_questions(pages):
            options = []
            body = []
            for line in item["lines"]:
                om = OPTION.match(line)
                if om:
                    options.append(
                        ((om.group(1) or om.group(2)).upper(), om.group(3))
                    )
                else:
                    body.append(line)

            ocrs = [
                p[4]
                for p in pages
                if p[0] in item["pages"] and p[4] is not None
            ]
            confidence = round(
                min(
                    1.0,
                    0.55
                    + (0.25 if options else 0.05)
                    + (0.1 if len(item["pages"]) > 1 else 0.05)
                    + (0.1 * (sum(ocrs) / len(ocrs)) if ocrs else 0),
                ),
                2,
            )

            if confidence >= settings.confidence_success_threshold:
                state = "SUCCESS"
            elif confidence >= settings.confidence_partial_threshold:
                state = "PARTIAL"
            else:
                state = "REVIEW_REQUIRED"

            q = Question(
                document_id=doc.id,
                question_number=item["number"],
                question_text=" ".join(body),
                question_type="MCQ" if options else "UNKNOWN",
                confidence=confidence,
                extraction_status=state,
            )
            db.add(q)
            db.flush()

            for key, text in options:
                db.add(
                    QuestionOption(
                        question_id=q.id,
                        option_key=key,
                        option_text=text,
                        confidence=confidence,
                    )
                )

            for page in item["pages"]:
                db.add(
                    QuestionSource(
                        question_id=q.id,
                        document_id=doc.id,
                        page_number=page,
                        source_text=" ".join(item["lines"]),
                    )
                )

            ap = answers.get(item["number"])
            db.add(
                Answer(
                    question_id=q.id,
                    answer=ap[0] if ap else None,
                    confidence=0.94 if ap else 0.0,
                    status="MATCHED" if ap else "NOT_FOUND",
                    source_document_id=doc.id if ap else None,
                    source_page=ap[1] if ap else None,
                )
            )

            if state != "SUCCESS":
                db.add(
                    ReviewItem(
                        question_id=q.id,
                        issue_type="LOW_CONFIDENCE",
                        reason="Incomplete options or low OCR confidence",
                        confidence=confidence,
                    )
                )

        _match_related(db, doc.id)
        for rel in db.query(DocumentRelationship).filter_by(
            target_document_id=doc.id, relationship_type="ANSWER_KEY"
        ):
            _match_related(db, rel.source_document_id)

        doc.status = job.status = "COMPLETED"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception:
        db.rollback()
        doc = db.get(Document, document_id)
        job = db.get(ProcessingJob, job.id)
        if doc and job:
            doc.status = job.status = "FAILED"
            job.error_message = "Processing failed. Inspect server logs."
            db.commit()
        raise

