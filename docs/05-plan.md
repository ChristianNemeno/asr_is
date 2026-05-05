# Project Plan: Fine-Tuning ASR Models for Cebuano Speech Recognition

## Objective

Fine-tune two ASR model architectures — **Whisper** (encoder-decoder, used by WhisperX) and **Wav2Vec2/XLS-R** (encoder-only, CTC) — on the Cebuano Speech Dataset, evaluate their performance, and report findings.

## Model Selection (Focused — 2 Models Only)

To keep resource usage and training time manageable, pick **one model per architecture** at comparable size:

| Architecture | Model | Params | VRAM | Why This One |
|---|---|---|---|---|
| Encoder-Decoder | `openai/whisper-small` | 244M | 8-16 GB | Standard in HF fine-tuning blog; 63%→32% WER on Hindi with just 8h |
| Encoder-Only (CTC) | `facebook/wav2vec2-xls-r-300m` | 317M | 8-16 GB | Go-to for low-resource ASR; designed for exactly this scenario |

**Why these sizes?**
- They're comparable (~244M vs ~317M) → fair comparison
- Both fit on a single consumer GPU (8-16 GB VRAM)
- Both have proven results on low-resource languages in HF documentation
- Training time: ~3-6 hours each on an A100, ~6-12 hours on a T4/V100

## Comparison Matrix (the core finding)

|  | Whisper-small | XLS-R 300M |
|---|---|---|
| **Base** (zero-shot, 0h training) | WER a% / CER b% | WER c% / CER d% |
| **Fine-tuned** (86h Cebuano) | WER a'% / CER b'% | WER c'% / CER d'% |

**What this tells you:**
1. **Within each model**: How much does fine-tuning help? (Δ = base − fine-tuned)
2. **Between architectures**: Which performs better? Encoder-decoder (Whisper) or CTC (XLS-R)?
3. **For Cebuano specifically**: Is it a viable low-resource ASR target?

## Timeline / Phases

---

### Phase 1: Environment & Data Setup

**Duration**: 1-2 days

**Tasks**:
- [ ] Set up Python environment with `transformers`, `datasets`, `evaluate`, `jiwer`, `soundfile`, `librosa`, `accelerate`
- [ ] Download `Speech-data/Cebuano-Speech-Dataset` (108h, 807 files)
- [ ] Verify dataset integrity: check file counts, sample rates, durations
- [ ] Create train (80%) / validation (10%) / test (10%) split
- [ ] Apply text normalization (lowercase, remove special chars)
- [ ] Resample all audio to 16kHz

**Deliverable**: Clean, split dataset ready for training

---

### Phase 2: Baseline Evaluation

**Duration**: 1 day

**Tasks**:
- [ ] Run zero-shot inference with `openai/whisper-small` on test set
- [ ] Run zero-shot inference with `facebook/wav2vec2-xls-r-300m` on test set
- [ ] Compute baseline WER and CER for each
- [ ] Document baseline results

**Deliverable**: Baseline WER/CER numbers

---

### Phase 3: Fine-Tune Whisper-small

**Duration**: 2-4 days

**Tasks**:
- [ ] Load `openai/whisper-small` with `WhisperForConditionalGeneration`
- [ ] Preprocess dataset: extract log-Mel spectrograms, tokenize labels
- [ ] Configure `Seq2SeqTrainingArguments` (LR=1e-5, batch=16, max_steps=5000)
- [ ] Train with `Seq2SeqTrainer`
- [ ] Monitor training loss and eval WER via TensorBoard
- [ ] Save best checkpoint (lowest WER)
- [ ] Evaluate final model on test set

**Deliverable**: Fine-tuned Whisper model + WER/CER metrics

---

### Phase 4: Fine-Tune Wav2Vec2 / XLS-R

**Duration**: 2-4 days

**Tasks**:
- [ ] Build Cebuano character vocabulary from dataset transcriptions
- [ ] Create `Wav2Vec2CTCTokenizer` and `Wav2Vec2Processor`
- [ ] Load `facebook/wav2vec2-xls-r-300m` with `Wav2Vec2ForCTC`
- [ ] Freeze CNN feature extractor
- [ ] Preprocess dataset (raw waveform, CTC tokenization)
- [ ] Configure `TrainingArguments` (LR=3e-4, epochs=30)
- [ ] Train with `Trainer`
- [ ] Monitor training via TensorBoard
- [ ] Evaluate final model on test set

**Deliverable**: Fine-tuned XLS-R model + WER/CER metrics

---

### Phase 5: WhisperX Integration (Bonus)

**Duration**: 1 day

**Tasks**:
- [ ] Install WhisperX
- [ ] Replace default Whisper model with fine-tuned Cebuano model
- [ ] Test word-level alignment (requires Cebuano phoneme alignment model — may need to find one on Hugging Face)
- [ ] Test VAD preprocessing
- [ ] Compare timestamp accuracy vs vanilla Whisper

**Deliverable**: WhisperX pipeline with fine-tuned Cebuano model (or assessment of feasibility)

---

### Phase 6: Analysis & Reporting

**Duration**: 2-3 days

**Tasks**:
- [ ] Compile the 2x2 comparison table (base vs fine-tuned × Whisper vs XLS-R)
- [ ] Create learning curve plots (WER vs steps for both models)
- [ ] Generate sample transcription comparisons (side-by-side: reference, Whisper, XLS-R)
- [ ] Perform error analysis: break down substitutions/deletions/insertions with `jiwer.process_words`
- [ ] Measure RTF (Real-Time Factor) for inference speed of both models
- [ ] Document hyperparameters, training time, GPU usage
- [ ] Write conclusions: which model performed better, why, recommendations

**Deliverable**: Final report with findings

---

## File Structure

```
asr_is/
├── docs/
│   ├── 01-dataset.md
│   ├── 02-whisper-finetune.md
│   ├── 03-wav2vec2-finetune.md
│   ├── 04-metrics.md
│   └── 05-plan.md
├── download.py              # Dataset download script
├── baseline/
│   └── evaluate_baseline.py # Zero-shot evaluation (both models)
├── whisper/
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── wav2vec2/
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── whisperx/
│   └── pipeline.py          # WhisperX integration (bonus)
├── analysis/
│   ├── compare_models.py    # WER comparison & error analysis
│   └── plot_learning.py     # Learning curves visualization
└── results/
    ├── baseline.json
    ├── whisper_results.json
    ├── wav2vec2_results.json
    └── final_report.md
```

## GPU Requirements

| Phase | Min VRAM | Recommended VRAM |
|-------|----------|-------------------|
| Whisper-small fine-tuning | 8 GB | 16 GB |
| XLS-R 300M fine-tuning | 8 GB | 16 GB |

If you hit OOM: reduce `per_device_train_batch_size` (16→8→4) and increase `gradient_accumulation_steps` (1→2→4).

Cloud options: Colab (T4 free, A100 with Pro+), RunPod, Lambda Labs, or local GPU.

## Key Decisions to Make

1. **Whisper language token for Cebuano?**
   - Check if Whisper supports `"cebuano"` language token
   - If not, use auto-detection or the closest supported language

2. **Alignment model for WhisperX?**
   - WhisperX needs a phoneme-based ASR model for forced alignment
   - Cebuano-specific alignment model may not exist — may need to skip or use a multilingual model

## Expected Comparison Table (to fill in)

| Model | Condition | WER (%) | CER (%) | RTF | Training Time |
|-------|-----------|---------|---------|-----|---------------|
| Whisper-small | Base (zero-shot) | TBD | TBD | TBD | 0h |
| Whisper-small | Fine-tuned (86h) | TBD | TBD | TBD | TBD |
| XLS-R 300M | Base (zero-shot) | TBD | TBD | TBD | 0h |
| XLS-R 300M | Fine-tuned (86h) | TBD | TBD | TBD | TBD |

## Risk Factors

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient GPU memory | Cannot train | Reduce batch size, use gradient checkpointing, fp16 |
| Poor zero-shot WER (>80%) | Low confidence in approach | Expected for low-resource language; fine-tuning should help |
| Overfitting (108h is small) | Poor generalization | Add dropout, SpecAugment, reduce epochs |
| Whisper doesn't support Cebuano token | Tokenizer issues | Use auto-detect language or nearest supported language |
| No Cebuano alignment model for WhisperX | No word timestamps | Find phoneme model on HF, or skip alignment phase |
| Dataset quality issues | Poor model quality | Manual inspection, filter noisy samples | |
