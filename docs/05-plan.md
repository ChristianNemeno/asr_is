# Project Plan: Fine-Tuning ASR Models for Cebuano Speech Recognition

## Objective

Fine-tune two ASR model architectures — **Whisper** (encoder-decoder, used by WhisperX) and **Wav2Vec2/XLS-R** (encoder-only, CTC) — on the Cebuano Speech Dataset, evaluate their performance, and report findings.

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
- [ ] Run zero-shot inference with `openai/whisper-medium` on test set
- [ ] Run zero-shot inference with `openai/whisper-large-v3` on test set
- [ ] Run zero-shot inference with `facebook/wav2vec2-xls-r-300m` on test set
- [ ] Compute baseline WER and CER for each model
- [ ] Document baseline results

**Deliverable**: Baseline WER/CER table

---

### Phase 3: Fine-Tune Whisper

**Duration**: 2-4 days (depending on GPU)

**Tasks**:
- [ ] Load `openai/whisper-small` with `WhisperForConditionalGeneration`
- [ ] Preprocess dataset: extract log-Mel spectrograms, tokenize labels
- [ ] Configure `Seq2SeqTrainingArguments` (LR=1e-5, batch=16, max_steps=5000)
- [ ] Train with `Seq2SeqTrainer`
- [ ] Monitor training loss and eval WER via TensorBoard
- [ ] Save best checkpoint (lowest WER)
- [ ] Evaluate final model on test set
- [ ] (Optional) Fine-tune `whisper-medium` if time permits

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
- [ ] Compile WER/CER results table (baseline vs fine-tuned, Whisper vs XLS-R)
- [ ] Create learning curve plots (WER vs steps)
- [ ] Generate sample transcription comparisons
- [ ] Perform error analysis: break down substitutions/deletions/insertions
- [ ] Measure RTF (Real-Time Factor) for inference speed
- [ ] Document hyperparameters, training time, GPU usage
- [ ] Write conclusions: which model performed better, why, recommendations

**Deliverable**: Final report with findings

---

## GPU Requirements

| Phase | Min VRAM | Recommended VRAM |
|-------|----------|-------------------|
| Whisper-small fine-tuning | 8 GB | 16 GB |
| Whisper-medium fine-tuning | 16 GB | 24 GB |
| XLS-R 300M fine-tuning | 8 GB | 16 GB |
| XLS-R 1B fine-tuning | 16 GB | 24 GB |

Cloud options: Colab Pro+ (A100), RunPod, Lambda Labs, or local GPU.

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
│   └── evaluate_baseline.py # Zero-shot evaluation
├── whisper/
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── wav2vec2/
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── whisperx/
│   └── pipeline.py          # WhisperX integration
├── analysis/
│   ├── compare_models.py    # WER comparison script
│   └── plot_learning.py     # Visualizations
└── results/
    ├── baseline.json
    ├── whisper_results.json
    ├── wav2vec2_results.json
    └── final_report.md
```

## Key Decisions to Make

1. **Which Whisper size to fine-tune?**
   - `small` (244M) — fastest, baseline
   - `medium` (769M) — better quality, more VRAM
   - Recommend: start with `small`, scale to `medium` if time/GPU permits

2. **Which XLS-R size?**
   - `300M` is the sweet spot for 108h of data
   - `1B` or `2B` likely overkill and may overfit

3. **Whisper language token for Cebuano?**
   - Check if Whisper supports `"cebuano"` language token
   - If not, use auto-detection or the closest supported language

4. **Alignment model for WhisperX?**
   - WhisperX needs a phoneme-based ASR model for forced alignment
   - Cebuano-specific alignment model may not exist — may need to skip or use a multilingual model

## Expected Comparison Table (to fill in)

| Model | Train Data | WER (%) | CER (%) | RTF | Training Time |
|-------|-----------|---------|---------|-----|---------------|
| Whisper-small (zero-shot) | None | TBD | TBD | TBD | 0h |
| Whisper-medium (zero-shot) | None | TBD | TBD | TBD | 0h |
| Whisper-large-v3 (zero-shot) | None | TBD | TBD | TBD | 0h |
| XLS-R 300M (zero-shot) | None | TBD | TBD | TBD | 0h |
| Whisper-small (fine-tuned) | 86h | TBD | TBD | TBD | TBD |
| Whisper-medium (fine-tuned) | 86h | TBD | TBD | TBD | TBD |
| XLS-R 300M (fine-tuned) | 86h | TBD | TBD | TBD | TBD |

## Risk Factors

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient GPU memory | Cannot train | Use smaller model, gradient checkpointing, reduce batch size |
| Poor zero-shot WER (>80%) | Low confidence in approach | Expected for low-resource language; fine-tuning should help |
| Overfitting (108h is small) | Poor generalization | Add dropout, SpecAugment, reduce epochs |
| Whisper doesn't support Cebuano token | Tokenizer issues | Use auto-detect language or nearest supported language |
| No Cebuano alignment model for WhisperX | No word timestamps | Find phoneme model on HF, or skip alignment phase |
| Dataset quality issues | Poor model quality | Manual inspection, filter noisy samples |
