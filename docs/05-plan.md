# Project Plan: Fine-Tuning Whisper for Filipino ASR

> **Updated**: Full observability pipeline added. Checkpoints are now all preserved. Visualization scripts generate publication-ready plots.

## Objective

Fine-tune `openai/whisper-small` on Filipino speech (Tagalog + Cebuano, via FSC + FLEURS) and compare performance against the zero-shot baseline.

## Model

| Model | Parameters | VRAM |
|-------|-----------|------|
| `openai/whisper-small` | 244M | 8-16 GB |

Fits on a single consumer GPU. Training time: ~2-3 hours on T4, ~6-12 hours on CPU.

## Dataset

**Filipino Speech Corpus** (`sapinsapin/filipinospeechcorpus`, ~50h Tagalog, MIT) + **FLEURS** (`google/fleurs`, `fil_ph` + `ceb_ph`, ~20h, CC-BY).

See `docs/01-dataset.md` for full details.

## Comparison Matrix

| Model | Condition | WER | CER |
|-------|-----------|-----|-----|
| Whisper-small | Zero-shot | TBD | TBD |
| Whisper-small | Fine-tuned | TBD | TBD |

## Timeline / Phases

### Phase 1: Environment & Data Setup ✓

- [x] Set up Python environment (`env/`, Python 3.12)
- [x] Identify datasets: FSC + FLEURS for training (Cebuano Speech Dataset available but not used)
- [x] Text normalization, 16kHz resampling, train/validation/test split

### Phase 2: Initial Training (Colab) ✓

- [x] `colab_whisper.py` — fine-tune whisper-small on Colab (T4)
- [x] Trained to step 2500/5000 — WER 19.67%, CER 7.98%
- [x] Superseded by local training pipeline

### Phase 3: Local Training & Observability Setup ✓

- [x] `train/train_whisper.py` — local training script with `--force-scratch` / `--resume`
- [x] `MetricsCSVCallback` — per-step metrics written to `metrics.csv`
- [x] All checkpoints preserved (no `save_total_limit`)
- [x] `train/compare_models.py` — baseline vs fine-tuned evaluation + `--plot` flag
- [x] `train/data_exploration.py` — dataset visualization before training
- [x] `train/visualize.py` — training curves from log history / CSV
- [x] `train/error_analysis.py` — per-sample error breakdown and visualizations
- [x] `train/visualize_splits.py` — dataset split diagrams (hardcoded approximate counts)
- [x] Pinned `transformers==5.0.0` for checkpoint compatibility
- [x] TensorBoard integration (`report_to=["tensorboard"]`)
- [x] `matplotlib` and `seaborn` added for publication-quality plots

### Phase 4: Training

- [ ] Run: `python train/train_whisper.py --force-scratch`
- [ ] Monitor with TensorBoard: `tensorboard --logdir train/output/whisper/checkpoints/runs`
- [ ] Metrics auto-saved to `train/output/whisper/metrics.csv`

### Phase 5: Evaluation & Analysis

- [ ] Dataset exploration: `python train/data_exploration.py`
- [ ] Training curves: `python train/visualize.py`
- [ ] Error analysis: `python train/error_analysis.py`
- [ ] Model comparison: `python train/compare_models.py --plot`
- [ ] All plots output to `train/output/plots/`

### Phase 6: (Bonus) WhisperX Integration

- [ ] Test word-level timestamps with WhisperX
- [ ] Cebuano phoneme alignment model may not exist — feasibility assessment only

## File Structure (Actual)

```
asr_is/
├── backend/                          # FastAPI API serving training docs, model info, visualizations
│   ├── main.py
│   ├── routes/transcribe.py
│   └── services/
├── frontend/                         # React + Vite UI
├── train/                            # Training, evaluation & visualization
│   ├── train_whisper.py              # Fine-tuning script (local, --resume/--force-scratch)
│   ├── compare_models.py             # Baseline vs fine-tuned comparison (+ --plot)
│   ├── data_exploration.py           # Dataset visualization before training
│   ├── visualize.py                  # Training curves from metrics
│   ├── error_analysis.py             # Per-sample error analysis and plots
│   ├── requirements.txt
│   └── output/                       # All training artifacts
│       ├── whisper/                  # Model, checkpoints, metrics
│       │   ├── metrics.csv           # Per-step training/eval metrics
│       │   ├── sample_transcriptions.csv
│       │   ├── test_results.json
│       │   ├── error_analysis.json
│       │   └── checkpoints/
│       │       ├── checkpoint-500/
│       │       ├── checkpoint-1000/
│       │       └── ... (all preserved)
│   └── plots/                    # Generated visualizations
│       ├── data_exploration/
│       ├── training_curves/
│       ├── error_analysis/
│       ├── model_comparison/
│       └── splits/
├── docs/
│   ├── 01-dataset.md
│   ├── 02-whisper-finetune.md
│   ├── 03-wav2vec2-finetune.md  (deprecated)
│   ├── 04-metrics.md
│   └── 05-plan.md
├── colab_whisper.py                  # Original Colab script (superseded)
└── env/                              # Python 3.12 venv
```

## Observability Workflow

```bash
# 1. Explore dataset before training (optional, ~1 min)
python train/data_exploration.py

# 2. Start training
python train/train_whisper.py --force-scratch

# 3. Monitor in separate terminal
tensorboard --logdir train/output/whisper/checkpoints/runs

# 4. After training completes: generate all plots
python train/visualize.py
python train/error_analysis.py
python train/compare_models.py --plot
python train/visualize_splits.py
```

## GPU Requirements

| Phase | Min VRAM | Recommended VRAM |
|-------|----------|-------------------|
| Whisper-small fine-tuning | 8 GB | 16 GB |

If OOM: reduce `per_device_train_batch_size` (8 → 4) and increase `gradient_accumulation_steps` (2 → 4).

Cloud options: Colab (T4 free, A100 with Pro+), RunPod, Lambda Labs, or local GPU.

## Key Decisions Made

1. **Whisper-only**: Wav2Vec2/XLS-R dropped — time/resource trade-off.
2. **Dataset**: FSC + FLEURS (Filipino/Tagalog + Cebuano), not Cebuano Speech Dataset. Multi-language training improves generalization.
3. **Language token**: `language=None` on generation config — auto-detect. Whisper has `<|tl|>` for Tagalog.
4. **Transformers version**: Pinned to 5.0.0 for checkpoint compatibility.
5. **Effective batch size**: 16 (batch=8, grad_accum=2).
6. **All checkpoints preserved**: `save_total_limit=None` — every 500-step checkpoint kept.
7. **Plots in both PNG and SVG**: PNG for embedding, SVG for publication.

## Risk Factors

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient GPU memory | Cannot train | Reduce batch size, gradient checkpointing, fp16 |
| Checkpoint version mismatch | Won't load | Pinned `transformers==5.0.0` |
| Overfitting (FSC+FLEURS ~70h) | Poor generalization | Dropout, SpecAugment, save best model |
| No Cebuano alignment model for WhisperX | No word timestamps | Skip or use multilingual alignment model |
