"""Generate deterministic synthetic input fixtures; these are not extraction outputs."""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1] / "sample_documents"
ROOT.mkdir(exist_ok=True)

def pdf(name: str, pages: list[str], raster: bool = False) -> None:
    document = fitz.open()
    for text in pages:
        page = document.new_page()
        if raster:
            image = Image.new("RGB", (1600, 900), "white")
            ImageDraw.Draw(image).multiline_text((80, 80), text, fill="black", spacing=14)
            image_path = ROOT / f".{name}-{page.number}.png"
            image.save(image_path)
            page.insert_image(page.rect, filename=str(image_path))
            image_path.unlink()
        else:
            page.insert_text((72, 72), text, fontsize=12)
    document.save(ROOT / name)
    document.close()

questions = """Q1. Which letter follows A?
A. B
B. C
C. D
D. E

Q2. Select the primary color.
A. Red
B. Black
C. White
D. Gray

Answer Key
1 - A
2 - A"""
pdf("clean_questions.pdf", [questions])
pdf("scanned_questions.pdf", ["Q1. OCR question\nA. Alpha\nB. Beta\nC. Gamma\nD. Delta\n\nQ2. OCR second question\nA. One\nB. Two"], raster=True)
pdf("multipage_question.pdf", ["Q12. Which option completes this question?\nA. Alpha\nB. Beta", "C. Gamma\nD. Delta"])
pdf("question_paper.pdf", ["Q1. First question\nA. Alpha\nB. Beta\n\nQ2. Second question\nA. One\nB. Two\n\nQ3. Unmatched question\nA. Yes\nB. No"])
pdf("answer_key.pdf", ["Answer Key\n1 - B\n2 - A"])
image = Image.new("RGB", (1000, 400), "white")
ImageDraw.Draw(image).multiline_text((50, 50), "Q1. Low quality question\nA. Alpha\nB. Beta\nC. Gamma\nD. Delta", fill="gray", spacing=10)
image.resize((500, 200)).filter(ImageFilter.GaussianBlur(1.1)).save(ROOT / "low_quality_question.png")
(ROOT / "invalid_document.txt").write_text("This is intentionally unsupported fixture input.\n", encoding="utf-8")

if __name__ == "__main__":
    print(f"Generated fixtures in {ROOT}")
