from app.services import parse_questions, answer_entries, extract_pages, OCRResult

def test_numbering_options_and_multipage_continuation():
    pages=[(1,"Question 01) Select\n(a) Alpha\n(b) Beta",0,"native_pdf",1.0),(2,"(c) Gamma\n(d) Delta",0,"native_pdf",1.0)]
    questions=parse_questions(pages)
    assert questions[0]["number"]=="1" and questions[0]["pages"]==[1,2]

def test_answer_key_requires_heading_and_supports_variants():
    pages=[(1,"Answer Key\nQ1: B\n2. C",0,"native_pdf",1.0)]
    assert answer_entries(pages)=={"1":("B",1),"2":("C",1)}

def test_image_ocr_provider_path(monkeypatch,tmp_path):
    from PIL import Image
    import app.services as services
    image=tmp_path/"exam.png"; Image.new("RGB",(30,30),"white").save(image)
    monkeypatch.setattr(services,"_ocr",lambda _: OCRResult("Q1. OCR question",.81))
    page=extract_pages(str(image),"png")[0]
    assert page[1]=="Q1. OCR question" and page[3]=="ocr" and page[4]==.81
