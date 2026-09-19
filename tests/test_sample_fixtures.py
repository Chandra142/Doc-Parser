from pathlib import Path
from tests.test_api import client, auth

ROOT = Path(__file__).resolve().parents[1] / "sample_documents"

def upload(headers, filename, content_type="application/pdf"):
    return client.post("/api/v1/documents",headers=headers,files={"file":(filename,(ROOT / filename).read_bytes(),content_type)})

def test_generated_clean_fixture_processes_with_answers():
    headers=auth("fixture-clean@example.com")
    response=upload(headers,"clean_questions.pdf")
    assert response.status_code==202
    questions=client.get(f"/api/v1/documents/{response.json()['document_id']}/questions",headers=headers).json()
    assert len(questions)==2 and questions[0]["answer"]["value"]=="A"

def test_generated_multipage_fixture_preserves_one_question_and_pages():
    headers=auth("fixture-pages@example.com")
    response=upload(headers,"multipage_question.pdf")
    questions=client.get(f"/api/v1/documents/{response.json()['document_id']}/questions",headers=headers).json()
    assert len(questions)==1 and questions[0]["question_number"]=="12"
    assert questions[0]["source"]["pages"]==[1,2]

def test_generated_cross_document_fixture_matches_answers():
    headers=auth("fixture-key@example.com")
    paper=upload(headers,"question_paper.pdf").json()["document_id"]
    key=upload(headers,"answer_key.pdf").json()["document_id"]
    relationship=client.post(f"/api/v1/documents/{paper}/relationships",headers=headers,json={"target_document_id":key,"relationship_type":"ANSWER_KEY"})
    assert relationship.status_code==201
    questions=client.get(f"/api/v1/documents/{paper}/questions",headers=headers).json()
    assert [q["answer"]["value"] for q in questions[:2]]==["B","A"]
    assert questions[0]["answer"]["status"]=="MATCHED"
