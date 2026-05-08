# ASR Training Showcase — Frontend & Backend Plan

## Architecture Overview

```
Browser (React + Vite :5173)
  │
  ├── /api/*  →  FastAPI backend :8000
  │                │
  │                ├── ModelManager (two Whisper-small instances: baseline + fine-tuned)
  │                ├── Static files (fleurs_samples/, train/output/plots/)
  │                └── Data files (metrics.csv, test_results.json, error_analysis.json, etc.)
  │
  └── vite proxy: /api → localhost:8000
```

---

## Backend (`backend/`)

### ModelManager — replaces the current singleton `model_service.py`

Loads both models at startup (~2 GB VRAM total):

| Instance | Source | Size |
|----------|--------|------|
| `baseline_model` + `baseline_processor` | `openai/whisper-small` (Hub download) | ~950MB |
| `finetuned_model` + `finetuned_processor` | `train/output/whisper` (local checkpoint) | ~950MB |

- Both preloaded at startup — instant transcription
- Wav2Vec2 code **removed entirely**
- No singleton pattern — both models accessible from one manager

### fleurs_samples labels

Static manifest: `fleurs_samples/manifest.json` maps filename → language, transcription, duration.

### API Endpoints

#### Models info

```
GET /api/models
```
```json
{
  "baseline": {
    "id": "openai/whisper-small",
    "parameters": 244000000,
    "architecture": "WhisperForConditionalGeneration",
    "task": "transcribe"
  },
  "finetuned": {
    "id": "whisper-small-cebuano",
    "test_wer": 18.28,
    "test_cer": 6.79,
    "train_steps": 5000,
    "dataset": "FSC + FLEURS (fil_ph, ceb_ph)"
  }
}
```

#### Sample dataset (fleurs_samples)

```
GET /api/samples
```
```json
[
  {
    "filename": "ceb_ph_00.wav",
    "language": "Cebuano",
    "label": "ang bata nagdula sa gawas",
    "duration_sec": 3.2,
    "url": "/api/samples/audio/ceb_ph_00.wav"
  }
]
```

```
GET /api/samples/audio/{filename}
```
→ WAV binary

#### Dual-model transcription

```
POST /api/transcribe
```
```json
{
  "baseline": {
    "text": "...",
    "wer": 45.2,
    "cer": 18.1
  },
  "finetuned": {
    "text": "...",
    "wer": 12.3,
    "cer": 4.5
  }
}
```

#### Hyperparameters

```
GET /api/training/hyperparams
```
```json
{
  "base_model": "openai/whisper-small",
  "parameters": 244000000,
  "per_device_train_batch_size": 8,
  "gradient_accumulation_steps": 2,
  "effective_batch_size": 16,
  "learning_rate": 1e-5,
  "warmup_steps": 500,
  "max_steps": 5000,
  "gradient_checkpointing": true,
  "mixed_precision": "fp16",
  "generation_max_length": 225,
  "seed": 42
}
```

#### Training metrics & curves

```
GET /api/training/metrics
```
```json
{
  "test_wer": 18.28,
  "test_cer": 6.79,
  "train_steps": 5000,
  "per_language": {
    "tagalog": {"mean_wer": 20.74, "n": 2410},
    "cebuano": {"mean_wer": 20.16, "n": 541}
  },
  "error_breakdown": {
    "substitutions": 6117,
    "deletions": 936,
    "insertions": 2557,
    "hits": 40279
  },
  "n_samples": 2951
}
```

```
GET /api/training/curves
```
→ `metrics.csv` as JSON array

#### Sample transcriptions

```
GET /api/training/samples
```
→ Best 5, median 5, worst 5 from `sample_transcriptions.csv`

#### Plot images

```
GET /api/plots/{category}/{filename}
```
→ Serves PNG/SVG from `train/output/plots/{category}/{filename}`

---

## Frontend (`frontend/`)

Single scrollable page, dark theme. 7 sections in vertical order.

### Section 1 — Hero
Big stat cards: WER 18.3%, CER 6.8%, 5,000 steps, ~70h data.

### Section 2 — Model Overview
Narrative + table about the pretrained base model (whisper-small architecture, parameters, training data, what fine-tuning changed).

### Section 3 — Dataset
Audio player list of 40 fleurs_samples, filterable by language (Tagalog/Cebuano). Each row: play button, language badge, label text, duration. Dataset split charts below.

### Section 4 — Hyperparameters
Table of training config (model, batch size, LR, warmup, max steps, etc.).

### Section 5 — Live Comparison
Upload WAV → side-by-side transcription boxes: Baseline (zero-shot) vs Fine-tuned. Optional reference text for WER/CER.

### Section 6 — Training Curves
Embedded PNG images: 4-panel loss/WER/CER/LR plot, gradient norm, test metrics bar chart.

### Section 7 — Error Analysis
Embedded charts: WER distribution, per-language WER, error breakdown. Table of sample transcriptions (5 best, 5 median, 5 worst).

---

## Implementation Order

| Step | What |
|------|------|
| 1 | Create `fleurs_samples/manifest.json` |
| 2 | Backend: `ModelManager` (dual model loading) |
| 3 | Backend: `/api/training/*` endpoints (metrics, curves, hyperparams, samples) |
| 4 | Backend: `/api/samples` + audio serving |
| 5 | Backend: `/api/transcribe` dual-model endpoint |
| 6 | Backend: `/api/plots/*` static file serving |
| 7 | Frontend: Section 1 (Hero) + Section 4 (Hyperparams) + Section 6 (Curves) + Section 7 (Error Analysis) |
| 8 | Frontend: Section 2 (Model Overview) |
| 9 | Frontend: Section 3 (Dataset Browser) |
| 10 | Frontend: Section 5 (Live Comparison) |
