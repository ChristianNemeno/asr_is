# whisper-small — Filipino & Cebuano ASR

Fine-tuned `openai/whisper-small` on Filipino Speech Corpus (Tagalog) + FLEURS (Tagalog & Cebuano). Training showcase with live baseline vs fine-tuned comparison, dataset browser, training curves, and error analysis.

## Quick Start

```bash
# Backend (Python 3.12)
source env/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (React + Vite)
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

## Docker

```bash
docker compose up -d --build
# → http://localhost:8080
```

Requires NVIDIA GPU + nvidia-container-toolkit. Backend loads two Whisper-small models (~2 GB VRAM).
