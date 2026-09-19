# Deployment Guide for DocuQuest

This guide details how to deploy **DocuQuest** for free on popular cloud platforms as well as in production with Docker Compose.

---

## 🚀 Option 1: Deploy for Free on Render (Recommended)

Render offers free web service hosting with Docker support, automatic HTTPS certificates, and Git auto-deploy.

### Quick 1-Click / Blueprint Steps:
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy DocuQuest service"
   git push origin main
   ```
2. **Open Render**:
   - Navigate to [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** &rarr; **Blueprint** (or **Web Service**).
   - Select your GitHub repository.
   - Render will automatically detect [`render.yaml`](../render.yaml) and configure:
     - **Runtime**: Docker
     - **Plan**: Free
     - **Health Check**: `/health`
     - **Environment Variables**: `CELERY_EAGER=true`, `DATABASE_URL=sqlite:///./docuquest.db`, `OCR_PROVIDER=tesseract`.
3. **Click Apply / Create**:
   - Render builds the Docker image (installs Python dependencies + Tesseract OCR).
   - Once deployed, you receive an automatic live URL (e.g., `https://docuquest.onrender.com`).
   - Visit the root URL `/` to open the **DocuQuest Interactive Demo UI** or `/docs` for Swagger UI.

---

## 🤗 Option 2: Deploy Free on Hugging Face Spaces (16GB RAM, No Cold Sleep)

Hugging Face Spaces offers completely free Docker hosting with **16GB RAM and 2 vCPUs**, making it exceptionally fast for OCR workloads.

### Steps:
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set:
   - **Space Name**: `docuquest`
   - **License**: MIT / Apache 2.0
   - **Space SDK**: **Docker** (Blank)
3. Clone the Space repo or push this repository directly:
   ```bash
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/docuquest
   git push space main
   ```
4. Hugging Face builds your Docker container and exposes port `7860` (our [`Dockerfile`](../Dockerfile) automatically binds to `${PORT:-8000}`, which Hugging Face sets to `7860`).
5. Your app is live instantly with an HTTPS domain.

---

## 🚂 Option 3: Deploy on Railway or Koyeb

1. **Railway**:
   - Go to [railway.app](https://railway.app).
   - Click **New Project** &rarr; **Deploy from GitHub repo**.
   - Railway will detect the `Dockerfile` and deploy automatically.
   - Set environment variable `CELERY_EAGER=true` in the project settings.
2. **Koyeb**:
   - Go to [koyeb.com](https://www.koyeb.com).
   - Click **Create App** &rarr; **GitHub**.
   - Select Docker builder; port `8000`.

---

## 🐳 Option 4: Full Multi-Service Production Stack (Docker Compose)

For high-concurrency production deployments with separated Celery workers and dedicated Redis/PostgreSQL services:

```bash
# 1. Prepare environment
cp .env.example .env

# 2. Spin up Postgres, Redis, Celery Worker, and FastAPI API
docker compose up --build -d

# 3. Apply database migrations
docker compose exec api alembic upgrade head
```

Services:
- **FastAPI Web Service**: `http://localhost:8000`
- **PostgreSQL**: Port 5432
- **Redis Queue**: Port 6379
- **Celery Worker**: Queue `documents` (concurrency scaled via `docker compose up --scale worker=3`)

---

## Environment Variables Reference

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./docuquest.db` | SQLAlchemy database URI (Postgres or SQLite) |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker and backend URL |
| `CELERY_EAGER` | `false` (`true` on free tiers) | In-process execution toggle (no Redis needed if `true`) |
| `JWT_SECRET` | `unsafe-development-secret` | HMAC secret for signing JWT auth tokens |
| `OCR_PROVIDER` | `tesseract` | OCR engine (`tesseract`) |
| `MAX_UPLOAD_SIZE_MB` | `20` | Upload limit for PDFs and images |
| `PORT` | `8000` | Port for the uvicorn web server |
