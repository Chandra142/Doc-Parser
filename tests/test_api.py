import os
os.environ["DATABASE_URL"]="sqlite:///./test_docuquest.db"
os.environ["CELERY_EAGER"]="true"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base,engine
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
client=TestClient(app)
def auth(email="a@example.com"):
    client.post("/api/v1/auth/register",json={"email":email,"password":"password123"})
    return {"Authorization":"Bearer "+client.post("/api/v1/auth/login",json={"email":email,"password":"password123"}).json()["access_token"]}
def test_auth_and_upload_rejection():
    assert client.get("/api/v1/documents").status_code==401
    h=auth(); r=client.post("/api/v1/documents",headers=h,files={"file":("x.txt",b"nope","text/plain")}); assert r.status_code==415
def test_pdf_extraction():
    import fitz
    pdf=fitz.open(); p=pdf.new_page(); p.insert_text((72,72),"Q1. Pick one\nA. Alpha\nB. Beta\nAnswer Key\n1 - B"); data=pdf.tobytes()
    h=auth("b@example.com"); up=client.post("/api/v1/documents",headers=h,files={"file":("exam.pdf",data,"application/pdf")}); assert up.status_code==202
    questions=client.get(f"/api/v1/documents/{up.json()['document_id']}/questions",headers=h).json(); assert questions[0]["options"][0]["key"]=="A"; assert questions[0]["answer"]["value"]=="B"
