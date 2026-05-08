# AGENTS.md

## Architecture

- **`backend/`** — FastAPI API serving training documentation, model info, hyperparameters, and visualizations. Run from `backend/` directory.
- **`frontend/`** — React + Vite + TypeScript training showcase dashboard. Vite proxies `/api` → `localhost:8000`.
- **`train/`** — Whisper fine-tuning, evaluation, and visualization scripts. **`train_whisper.py`** is the canonical training code. Wav2Vec2/XLS-R training was **deprecated** in favor of Whisper-only.
- **`train/output/`** — All training artifacts: checkpoints, TensorBoard logs, `metrics.csv`, plots, and error analysis. This is the data source the frontend/backend serve.
- **`docs/`** — Project documentation (datasets, training guides, metrics, plan).
- `colab_whisper.py` — Colab script (uses `# %%` cell separators) that produced the initial checkpoint. Superseded by `train/train_whisper.py` for local training.
- `inspect_fleurs.py` — Exports WAV samples from FLEURS for manual listening.

## Commands

```bash
# Backend (Python 3.12 venv at env/)
source env/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend && npm install && npm run dev     # dev on :5173
cd frontend && npm run build                   # tsc + vite build
cd frontend && npm run preview                 # preview production build

# Docker (production deployment)
docker compose up -d --build                   # build & start all services
docker compose logs -f backend                 # tail backend logs
docker compose down                            # stop all

# Training (run from repo root, not train/)
pip install -r train/requirements.txt
python train/train_whisper.py --force-scratch   # train from scratch
python train/train_whisper.py --resume <path>   # resume from checkpoint

# Observability (in separate terminal during training)
tensorboard --logdir train/output/whisper/checkpoints/runs

# Visualization (after training)
python train/data_exploration.py               # dataset stats before training
python train/visualize.py                      # training curves from metrics
python train/error_analysis.py                 # per-sample error breakdown
python train/compare_models.py --plot          # baseline vs fine-tuned
python train/visualize_splits.py               # dataset split diagrams (hardcoded approximations)
```

## Training workflow

- **Dataset**: Filipino Speech Corpus (`sapinsapin/filipinospeechcorpus`) + FLEURS (`fil_ph`, `ceb_ph`). NOT the Cebuano Speech Dataset used by `docs/`.
- **Config is hardcoded**: batch size, learning rate, max steps, etc. are module-level constants in `train_whisper.py` (lines ~68–76), not CLI flags. Edit the script to change them.
- **Train**: `python train/train_whisper.py --force-scratch` (refuses to overwrite without the flag).
- **Monitor**: TensorBoard logs to `train/output/whisper/checkpoints/runs/`. A `metrics.csv` is also written per-step by the `MetricsCSVCallback`.
- **Checkpoints saved every 500 steps** — all preserved (no `save_total_limit`), final best model at `train/output/whisper/`.
- **Plots output**: `train/output/plots/` contains `data_exploration/`, `training_curves/`, `error_analysis/`, `model_comparison/`, `splits/`.

## Gotchas

- **Transformers must be exactly 5.0.0** to load the checkpoint. The checkpoint config records `transformers_version: "5.0.0"`. Newer versions (5.8+) add a `proj_out` layer to Whisper that the checkpoint lacks, causing a shape mismatch. The `requirements.txt` files say `>=4.40.0` but you must pin to `5.0.0`.
- **`train/` was never completed.** `train_whisper.py` and `compare_models.py` exist, but `config.py` and `train_wav2vec2.py` were never implemented.
- **No tests, linters, or typecheck** configuration exists anywhere in the repo.
- **`get_model_manager()` in `backend/services/model_service.py` is a singleton.** Once loaded, it loads two models (baseline + fine-tuned) into memory. Restart to reload models.
- **`colab_whisper.py` uses `# %%` cell separators** — it is a Colab notebook, not a regular Python script. Do not run it directly.
- **Backend is run from `backend/` directory with `../train/output/...` relative paths.** The `docker-compose.yml` mounts host directories so these resolve correctly inside the container.
