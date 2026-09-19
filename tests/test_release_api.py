"""Release regression coverage: deterministic and independent of real OCR/Redis."""
from io import BytesIO
from PIL import Image
from tests.test_api import client, auth

def image_bytes(fmt="PNG"):
    output=BytesIO(); Image.new("RGB",(20,20),"white").save(output,format=fmt); return output.getvalue()

def test_duplicate_invalid_login_and_me():
    headers=auth("release-auth@example.com")
    assert client.post("/api/v1/auth/register",json={"email":"release-auth@example.com","password":"password123"}).status_code==409
    assert client.post("/api/v1/auth/login",json={"email":"release-auth@example.com","password":"wrongpass"}).status_code==401
    assert client.get("/api/v1/auth/me",headers=headers).status_code==200
    assert client.get("/api/v1/auth/me",headers={"Authorization":"Bearer malformed"}).status_code==401

def test_mime_magic_and_malformed_upload_rejections():
    h=auth("release-upload@example.com")
    assert client.post("/api/v1/documents",headers=h,files={"file":("file.pdf",b"not-a-pdf","application/pdf")}).status_code==422
    assert client.post("/api/v1/documents",headers=h,files={"file":("file.png",image_bytes(),"application/pdf")}).status_code==415
    assert client.post("/api/v1/documents",headers=h,files={"file":("file.png",b"not-image","image/png")}).status_code==422

def test_image_types_queue_without_invoking_host_ocr(monkeypatch):
    import app.main as module
    h=auth("release-image@example.com")
    monkeypatch.setattr(module,"process_document",lambda db,document_id:None)
    for filename,fmt,mime in [("q.png","PNG","image/png"),("q.jpg","JPEG","image/jpeg"),("q.jpeg","JPEG","image/jpeg")]:
        response=client.post("/api/v1/documents",headers=h,files={"file":(filename,image_bytes(fmt),mime)})
        assert response.status_code==202

def test_document_ownership_is_non_enumerable():
    import fitz
    pdf=fitz.open(); pdf.new_page().insert_text((50,50),"Q1. Owned question\nA. One\nB. Two")
    owner=auth("owner-release@example.com"); other=auth("other-release@example.com")
    created=client.post("/api/v1/documents",headers=owner,files={"file":("owned.pdf",pdf.tobytes(),"application/pdf")}).json()["document_id"]
    assert client.get(f"/api/v1/documents/{created}",headers=other).status_code==404
    assert client.get(f"/api/v1/documents/{created}/questions",headers=other).status_code==404

def test_not_found_and_structured_error():
    h=auth("release-404@example.com")
    response=client.get("/api/v1/questions/no-such-question",headers=h)
    assert response.status_code==404 and response.json()["error"]["code"]=="QUESTION_NOT_FOUND"
