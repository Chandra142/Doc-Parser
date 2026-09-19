FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR and English training data
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for Hugging Face Spaces compatibility (UID 1000)
RUN useradd -m -u 1000 user

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -e .

# Copy application source code
COPY . .

# Ensure storage directory exists and assign full ownership to non-root user
RUN mkdir -p data/uploads && chown -R user:user /app

# Switch to non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    CELERY_EAGER=true \
    DATABASE_URL=sqlite:////app/data/docuquest.db

EXPOSE 7860

# Bind dynamically to the port provided by the host environment ($PORT) or fallback to 7860 for Hugging Face
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
