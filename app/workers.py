from celery import Celery
from app.core.config import settings
from app.db import SessionLocal
from app.services import process_document
celery = Celery("docuquest",broker=settings.redis_url,backend=settings.redis_url)
celery.conf.task_routes={"app.workers.process_task":{"queue":"documents"}}
@celery.task(bind=True,autoretry_for=(ConnectionError,),retry_backoff=True,max_retries=3)
def process_task(self, document_id: str):
    db=SessionLocal()
    try: process_document(db,document_id)
    finally: db.close()
