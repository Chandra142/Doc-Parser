---
title: DocuQuest
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# DocuQuest 📄

**DocuQuest** is a simple and smart tool that can read test papers or exams (like PDFs or pictures) and pull out the questions and answers for you automatically.

It looks at your documents, finds the multiple-choice questions, and even checks the answer keys! If it gets confused about something, it flags it so a human can double-check.

---

## 🌟 What Can It Do?

- **Reads Different Files**: You can upload regular PDFs, scanned documents, or even photos (PNG, JPG) of a test.
- **Smart Text Reading**: If the file is digital, it reads it instantly. If it's a picture or a scan, it uses smart image-reading (OCR) to figure out the text.
- **Understands Questions**: It knows how to spot a question (like "Q1." or "1)") and its options (like A, B, C, D). If a question gets cut off at the bottom of a page, it knows how to combine it with the next page!
- **Finds the Answers**: It can match the questions with the answer key, even if the answer key is on a different page or in a different file.
- **Confidence Checker**: It tells you how sure it is about what it read. If it's not very sure, it asks you to review it.
- **Easy Web Interface**: There is a built-in website where you can test everything with just a few clicks.
- **Secure**: Your files are safe and kept private to your account.

---

## 🌐 Try It Out / Cloud Setup

### 1. Web Demo
You can try it out by going to the main page (`/` or `/demo`).
- Easy 1-click login.
- Test buttons to try out all the features.
- See how questions are pulled from documents live!

### 2. Run It in the Cloud for Free
You can run this project on free cloud platforms like **Render** or **Hugging Face Spaces**. Just follow our [Deployment Guide](docs/DEPLOYMENT.md) to set it up without spending any money.

---

## 🚀 How to Run It on Your Computer

### The Easy Way (Local Run)
```bash
# 1. Install what it needs
pip install -e .[dev]

# 2. Start it up
export DATABASE_URL="sqlite:///./docuquest.db"
export CELERY_EAGER="true"
uvicorn app.main:app --reload --port 8000
```
Then, open `http://localhost:8000` in your web browser.

### The Advanced Way (Using Docker)
If you know how to use Docker, you can run everything easily:
```bash
cp .env.example .env
docker compose up --build
```
This runs the web app, database, and background workers all together!

---

## 📁 What's Inside the Folder?

- `app/` - The main code for the website and document reading.
- `docs/` - Guides on how the app is built and how to use it.
- `migrations/` - Database setup files.
- `sample_documents/` & `sample_outputs/` - Example PDFs and what the app pulls out of them.
- `tests/` - Automated checks to make sure the code works.

---

## 🧪 Testing the Code

Want to make sure everything is working? Run the tests:
```bash
pytest -v
```

This checks things like uploading files, reading multiple pages, and keeping files secure.
