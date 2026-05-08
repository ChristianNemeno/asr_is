# Training Showcase — Change Report

## Summary

Pivoted the frontend and backend from a simple transcription tool to a **training showcase dashboard** displaying the fine-tuned Whisper-small model, hyperparameters, dataset samples, training curves, error analysis, and a live baseline vs fine-tuned comparison.

---

## Backend

### Modified

| File | Description |
|------|-------------|
| [`backend/main.py`](../backend/main.py) | Updated title to "Cebuano ASR Training Showcase", registered 3 new routers (`training`, `samples`, `plots`) |
| [`backend/services/model_service.py`](../backend/services/model_service.py) | Replaced singleton `ModelService` with `ModelManager` that loads **both** baseline (`openai/whisper-small`) and fine-tuned (`train/output/whisper`) models at startup. Removed all Wav2Vec2 code. `get_model_manager()` returns the dual-model manager. |
| [`backend/routes/transcribe.py`](../backend/routes/transcribe.py) | Rewrote `/api/transcribe` to run both models on the uploaded audio and return side-by-side results. Accepts optional `reference` for per-model WER/CER + error breakdown. |

### New

| File | Description |
|------|-------------|
| [`backend/routes/training.py`](../backend/routes/training.py) | `GET /api/training/models` — model info + final WER/CER. `GET /api/training/hyperparams` — training config table. `GET /api/training/metrics` — test metrics + error breakdown + per-language stats. `GET /api/training/curves` — `metrics.csv` as JSON array. `GET /api/training/samples` — best/worst/median transcriptions. |
| [`backend/routes/samples.py`](../backend/routes/samples.py) | `GET /api/samples` — lists 40 FLEURS audio files with filename, language, label, duration, and playback URL. `GET /api/samples/audio/{filename}` — serves WAV binary. Reads from [`fleurs_samples/manifest.json`](../fleurs_samples/manifest.json). |
| [`backend/routes/plots.py`](../backend/routes/plots.py) | `GET /api/plots/{path}` — serves PNG/SVG from [`train/output/plots/`](../train/output/plots/). |

### API Endpoints (full list)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/training/models` | Model info (baseline + fine-tuned with test WER/CER) |
| `GET` | `/api/training/hyperparams` | Training config (batch size, LR, steps, etc.) |
| `GET` | `/api/training/metrics` | Final test metrics, per-language breakdown, error counts |
| `GET` | `/api/training/curves` | `metrics.csv` as JSON (step-by-step loss/WER/CER/LR) |
| `GET` | `/api/training/samples` | Sample transcriptions (best/median/worst) |
| `GET` | `/api/samples` | FLEURS audio sample listing |
| `GET` | `/api/samples/audio/{filename}` | Serve WAV file |
| `POST` | `/api/transcribe` | Dual-model transcription with optional reference |
| `GET` | `/api/plots/{path}` | Serve plot images (PNG/SVG) |
| `GET` | `/api/health` | Health check (unchanged) |

---

## Frontend

### Modified

| File | Description |
|------|-------------|
| [`frontend/index.html`](../frontend/index.html) | Updated `<title>` to "Whisper-small — Filipino & Cebuano ASR Training Showcase" |
| [`frontend/src/App.tsx`](../frontend/src/App.tsx) | Complete rewrite. Fetches all backend APIs on mount, composes 7 sections vertically. Removed Wav2Vec2 model selector. |
| [`frontend/src/App.css`](../frontend/src/App.css) | Complete rewrite. Dark theme with styles for hero, model overview grid, dataset browser, hyperparams table, comparison side-by-side, embedded plots, and sample transcriptions table. |

### New

| File | Section | Description |
|------|---------|-------------|
| [`frontend/src/components/Hero.tsx`](../frontend/src/components/Hero.tsx) | 1 | Stat cards: WER, CER, training steps, data size |
| [`frontend/src/components/ModelOverview.tsx`](../frontend/src/components/ModelOverview.tsx) | 2 | Narrative about Whisper architecture + static spec table (pretrained model, params, loss, output tokens) |
| [`frontend/src/components/DatasetBrowser.tsx`](../frontend/src/components/DatasetBrowser.tsx) | 3 | Audio player list (40 samples), filterable by language, embedded split chart |
| [`frontend/src/components/Hyperparams.tsx`](../frontend/src/components/Hyperparams.tsx) | 4 | Clean key-value table of training config |
| [`frontend/src/components/LiveComparison.tsx`](../frontend/src/components/LiveComparison.tsx) | 5 | File upload + dual side-by-side transcription boxes with WER/CER + S/D/I/H breakdown |
| [`frontend/src/components/TrainingCurves.tsx`](../frontend/src/components/TrainingCurves.tsx) | 6 | Embedded PNG images: 4-panel curves, gradient norm, test metrics |
| [`frontend/src/components/ErrorAnalysis.tsx`](../frontend/src/components/ErrorAnalysis.tsx) | 7 | Per-language stat cards, embedded charts (WER distribution, language breakdown, error breakdown), sample transcriptions table |

### Unchanged / removed

- [`frontend/src/main.tsx`](../frontend/src/main.tsx) — untouched
- [`frontend/src/components/Transcriber.tsx`](../frontend/src/components/Transcriber.tsx) — orphaned (no longer imported by App). Can be deleted.

---

## Data

| File | Description |
|------|-------------|
| [`fleurs_samples/manifest.json`](../fleurs_samples/manifest.json) | 40 entries mapping exported WAV filenames to language, transcription label, and duration. Generated from `google/fleurs` with seed=42 (matching `inspect_fleurs.py`). |

---

## Docs

| File | Description |
|------|-------------|
| [`docs/06-frontend-backend-plan.md`](../docs/06-frontend-backend-plan.md) | Full architecture plan with endpoint specs, component tree, and implementation order |
| [`AGENTS.md`](../AGENTS.md) | Updated to reflect training showcase focus, removed stale `download.py` ref, added `visualize_splits.py`, noted hardcoded training config |
| [`docs/01-dataset.md`](../docs/01-dataset.md) | Removed `download.py` references |
| [`docs/02-whisper-finetune.md`](../docs/02-whisper-finetune.md) | Fixed training args to match actual code, added Cebuano to title |
| [`docs/04-metrics.md`](../docs/04-metrics.md) | Removed XLS-R rows from comparison table |
| [`docs/05-plan.md`](../docs/05-plan.md) | Updated backend description, removed `download.py`, added `visualize_splits.py`, added `splits/` plots dir |

---

## How to run

```bash
# Backend (loads both models ~2 GB VRAM)
source env/bin/activate
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (vite proxies /api → :8000)
cd frontend && npm run dev
# → http://localhost:5173
```

The frontend is a single scrollable page. All 7 sections render with backend data. The Live Comparison section requires the backend to be running with models loaded.
