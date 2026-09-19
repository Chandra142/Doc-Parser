import io
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, token_for, verify_password
from app.db import Base, engine, get_db
from app.deps import current_user, owned_document
from app.models import (
    Document,
    DocumentPage,
    DocumentRelationship,
    ProcessingJob,
    Question,
    QuestionOption,
    QuestionSource,
    ReviewItem,
    User,
)
from app.services import (
    LocalStorage,
    _match_related,
    process_document,
    validate_content,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
SAMPLES_DIR = Path(__file__).resolve().parents[1] / "sample_documents"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Developer fallback; Alembic migration is the production path
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="DocuQuest",
    version="0.1.0",
    description="Asynchronous examination document extraction service.",
    lifespan=lifespan,
)

# Enable CORS for web dashboards and third-party consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount sample documents and static assets if they exist
if SAMPLES_DIR.exists():
    app.mount(
        "/sample_documents",
        StaticFiles(directory=str(SAMPLES_DIR)),
        name="sample_documents",
    )

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(HTTPException)
async def errors(_, exc):
    detail = (
        exc.detail
        if isinstance(exc.detail, dict)
        else {"code": "HTTP_ERROR", "message": str(exc.detail)}
    )
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(Register):
    pass


class RelationshipIn(BaseModel):
    target_document_id: str
    relationship_type: str = Field(
        pattern="^(QUESTION_PAPER|ANSWER_KEY|SUPPLEMENT)$"
    )


@app.get("/", summary="Web Demo UI or API Root")
def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "name": "DocuQuest",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/demo", summary="Interactive Demo Dashboard")
def demo():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(404, detail="Demo UI not found.")


@app.get("/health", summary="Liveness check")
def health():
    return {"status": "ok"}


@app.get("/ready", summary="Readiness check")
def ready(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ready"}


@app.post("/api/v1/auth/register", status_code=201, summary="Register a user")
def register(data: Register, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(
            409,
            detail={
                "code": "EMAIL_EXISTS",
                "message": "Email is already registered.",
            },
        )
    user = User(
        email=data.email.lower(), password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    return {"id": user.id, "email": user.email}


@app.post("/api/v1/auth/login", summary="Obtain JWT")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
            },
        )
    return {"access_token": token_for(user.id), "token_type": "bearer"}


@app.get("/api/v1/auth/me", summary="Current user")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}


@app.post("/api/v1/documents", status_code=202, summary="Upload and queue document")
def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    name = file.filename or "upload"
    ext = Path(name).suffix.lower()
    allowed = {
        ".pdf": "pdf",
        ".jpg": "jpg",
        ".jpeg": "jpeg",
        ".png": "png",
    }
    if ext not in allowed:
        raise HTTPException(
            415,
            detail={
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": "Only PDF, JPG, JPEG and PNG files are supported.",
            },
        )

    accepted_mime = {
        "pdf": {"application/pdf"},
        "jpg": {"image/jpeg"},
        "jpeg": {"image/jpeg"},
        "png": {"image/png"},
    }
    if (
        file.content_type
        and file.content_type.lower() not in accepted_mime[allowed[ext]]
    ):
        raise HTTPException(
            415,
            detail={
                "code": "INVALID_MIME_TYPE",
                "message": "Declared MIME type does not match the supported file type.",
            },
        )

    data = file.file.read(settings.max_upload_size_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            413,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": "Upload exceeds configured size limit.",
            },
        )

    try:
        validate_content(data, allowed[ext])
    except ValueError as exc:
        raise HTTPException(
            422,
            detail={"code": "MALFORMED_DOCUMENT", "message": str(exc)},
        )

    filename, path = LocalStorage().save(io.BytesIO(data), name)
    doc = Document(
        filename=filename,
        original_filename=Path(name).name,
        file_type=allowed[ext],
        file_size=len(data),
        storage_path=path,
        status="QUEUED",
        uploaded_by=user.id,
    )
    db.add(doc)
    db.flush()

    job = ProcessingJob(document_id=doc.id, status="QUEUED")
    db.add(job)
    db.commit()

    if settings.celery_eager:
        process_document(db, doc.id)
    else:
        try:
            from app.workers import process_task

            process_task.delay(doc.id)
        except Exception as exc:
            doc.status = job.status = "FAILED"
            job.error_message = "Unable to queue processing job."
            db.commit()
            raise HTTPException(
                503,
                detail={
                    "code": "QUEUE_UNAVAILABLE",
                    "message": "Document could not be queued for processing.",
                },
            ) from exc

    return {"document_id": doc.id, "status": "QUEUED", "job_id": job.id}


@app.get("/api/v1/documents", summary="List owned documents")
def documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return (
        db.scalars(
            select(Document)
            .where(Document.uploaded_by == user.id)
            .offset(skip)
            .limit(min(limit, 100))
        )
        .all()
    )


@app.get("/api/v1/documents/{document_id}", summary="Get document")
def document(doc: Document = Depends(owned_document)):
    return doc


@app.get("/api/v1/documents/{document_id}/status", summary="Get processing status")
def document_status(
    doc: Document = Depends(owned_document), db: Session = Depends(get_db)
):
    return db.scalar(
        select(ProcessingJob)
        .where(ProcessingJob.document_id == doc.id)
        .order_by(ProcessingJob.created_at.desc())
    )


def qout(q: Question) -> dict:
    return {
        "id": q.id,
        "question_number": q.question_number,
        "question": q.question_text,
        "question_type": q.question_type,
        "options": [
            {
                "key": o.option_key,
                "text": o.option_text,
                "confidence": o.confidence,
            }
            for o in q.options
        ],
        "answer": (
            None
            if not q.answer
            else {
                "value": q.answer.answer,
                "status": q.answer.status,
                "confidence": q.answer.confidence,
            }
        ),
        "source": {
            "document_id": q.document_id,
            "pages": [s.page_number for s in q.sources],
        },
        "confidence": q.confidence,
        "status": q.extraction_status,
        "warnings": (
            ["Extraction requires review"]
            if q.extraction_status == "REVIEW_REQUIRED"
            else []
        ),
    }


@app.get("/api/v1/documents/{document_id}/questions", summary="List extracted questions")
def questions(
    doc: Document = Depends(owned_document), db: Session = Depends(get_db)
):
    return [
        qout(q)
        for q in db.scalars(
            select(Question).where(Question.document_id == doc.id)
        ).all()
    ]


@app.get("/api/v1/questions/{question_id}", summary="Get question")
def question(
    question_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(
            404,
            detail={"code": "QUESTION_NOT_FOUND", "message": "Question not found."},
        )
    owned_document(q.document_id, db, user)
    return qout(q)


@app.get("/api/v1/questions/{question_id}/answer", summary="Get question answer")
def answer(
    question_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(
            404,
            detail={"code": "QUESTION_NOT_FOUND", "message": "Question not found."},
        )
    owned_document(q.document_id, db, user)
    return q.answer


@app.get("/api/v1/documents/{document_id}/review-items", summary="List review items")
def reviews(
    doc: Document = Depends(owned_document), db: Session = Depends(get_db)
):
    return db.scalars(
        select(ReviewItem)
        .join(Question)
        .where(Question.document_id == doc.id)
    ).all()


@app.post(
    "/api/v1/documents/{document_id}/relationships",
    status_code=201,
    summary="Link related documents",
)
def relationship(
    data: RelationshipIn,
    doc: Document = Depends(owned_document),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    target = owned_document(data.target_document_id, db, user)
    r = DocumentRelationship(
        source_document_id=doc.id,
        target_document_id=target.id,
        relationship_type=data.relationship_type,
    )
    db.add(r)
    db.flush()
    _match_related(db, doc.id)
    db.commit()
    return r


@app.get("/api/v1/documents/{document_id}/relationships", summary="List document links")
def relationships(
    doc: Document = Depends(owned_document), db: Session = Depends(get_db)
):
    return db.scalars(
        select(DocumentRelationship).where(
            (DocumentRelationship.source_document_id == doc.id)
            | (DocumentRelationship.target_document_id == doc.id)
        )
    ).all()

