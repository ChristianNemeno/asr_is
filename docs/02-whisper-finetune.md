# Fine-Tuning Whisper for Filipino & Cebuano ASR

> Based on: [Fine-Tune Whisper For Multilingual ASR with Transformers](https://huggingface.co/blog/fine-tune-whisper)
> and the official [Hugging Face ASR guide](https://huggingface.co/docs/transformers/tasks/asr)

## Quick Start (Project Scripts)

The project includes ready-to-run scripts. See `AGENTS.md` for full commands.

```bash
# Resume from checkpoint (step 2500/5000, WER 19.67%)
python train/train_whisper.py --resume checkpoint/checkpoint-2500

# Train from scratch
python train/train_whisper.py

# Compare baseline vs fine-tuned
python train/compare_models.py
python train/compare_models.py --model train/output/whisper
```

**Important**: `train/train_whisper.py` uses the **Filipino Speech Corpus + FLEURS** dataset (Tagalog + Cebuano), not the Cebuano Speech Dataset.

**Note**: A Colab checkpoint at `checkpoint/checkpoint-2500/` was produced by `colab_whisper.py`. If that directory no longer exists, train from scratch with `python train/train_whisper.py --force-scratch`.

**Version pin**: The checkpoint was trained with `transformers==5.0.0`. Newer versions (5.8+) add a `proj_out` layer to Whisper that the checkpoint lacks, causing a shape mismatch. The `requirements.txt` files say `>=4.40.0` but you must pin to `5.0.0`.

---

## Architecture Overview

Whisper is an encoder-decoder Transformer (Seq2Seq):
1. **Feature Extractor**: Converts raw audio → log-Mel spectrogram (80-channel)
2. **Encoder**: Processes spectrogram → hidden state representations
3. **Decoder**: Autoregressively generates text tokens, conditioned on encoder states + previous tokens

Training uses **cross-entropy loss** (not CTC).

## Recommended Pre-Trained Checkpoints

| Model | Parameters | Size | HF Path |
|-------|-----------|------|---------|
| tiny | 39M | ~150MB | `openai/whisper-tiny` |
| base | 74M | ~290MB | `openai/whisper-base` |
| small | 244M | ~950MB | `openai/whisper-small` |
| medium | 769M | ~3GB | `openai/whisper-medium` |
| large-v3 | 1.55B | ~6GB | `openai/whisper-large-v3` |

This project uses `whisper-small`.

## Reference Implementation

The step-by-step below mirrors the logic in `train/train_whisper.py`. It is preserved as a reference for understanding the training pipeline.

### 1. Install Dependencies

```bash
pip install -r train/requirements.txt
```

### 2. Load Dataset (FSC + FLEURS)

The training script loads two datasets and merges them:

```python
from datasets import load_dataset, Audio, DatasetDict, concatenate_datasets

# Filipino Speech Corpus (~50h Tagalog)
fsc = load_dataset("sapinsapin/filipinospeechcorpus")
fsc = fsc.cast_column("audio", Audio(sampling_rate=16000))
fsc = fsc.filter(lambda x: x["num_words"] >= 2 and x["duration"] >= 0.8)

# FLEURS (fil_ph + ceb_ph, ~20h)
for lang in ["fil_ph", "ceb_ph"]:
    fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
    fl = fl.cast_column("audio", Audio(sampling_rate=16000))
    datasets.append(fl)

# Concatenate per split
ds = DatasetDict({
    s: concatenate_datasets([d[s] for d in datasets])
    for s in ["train", "validation", "test"]
})
```

### 3. Load Whisper Processor

```python
from transformers import WhisperProcessor

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
```

### 4. Preprocess Data

```python
def prep(batch):
    audio = batch["audio"]
    batch["input_features"] = processor.feature_extractor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_features[0]
    batch["labels"] = processor.tokenizer(batch["text"]).input_ids
    return batch

ds = ds.map(prep, remove_columns=ds["train"].column_names)
```

### 5. Data Collator

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class DataCollator:
    processor: Any
    def __call__(self, features):
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch
```

### 6. Load Model

```python
from transformers import WhisperForConditionalGeneration

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
model.generation_config.language = None
model.generation_config.task = "transcribe"
model.generation_config.forced_decoder_ids = None
```

### 7. Metrics

```python
import evaluate
import numpy as np

wer_m = evaluate.load("wer")
cer_m = evaluate.load("cer")

def compute_metrics(pred):
    pid = pred.predictions
    lid = np.where(pred.label_ids != -100, pred.label_ids, processor.tokenizer.pad_token_id)
    ps = processor.tokenizer.batch_decode(pid, skip_special_tokens=True)
    ls = processor.tokenizer.batch_decode(lid, skip_special_tokens=True)
    return {
        "wer": 100 * wer_m.compute(predictions=ps, references=ls),
        "cer": 100 * cer_m.compute(predictions=ps, references=ls),
    }
```

### 8. Training Arguments (as used in this project)

```python
from transformers import Seq2SeqTrainingArguments

args = Seq2SeqTrainingArguments(
    output_dir="train/output/whisper/checkpoints",
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,
    learning_rate=1e-5,
    warmup_steps=500,
    max_steps=5000,
    gradient_checkpointing=True,
    fp16=True,                        # auto-disabled on CPU
    eval_strategy="steps",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=500,
    eval_steps=500,
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    report_to=["tensorboard"],
    save_total_limit=None,            # all checkpoints preserved
    seed=42,
)
```

> **Config is hardcoded** in `train_whisper.py` (lines ~68–76 and ~195–217), not CLI flags. Edit the script to change hyperparameters.

### 9. Train

```python
from transformers import Seq2SeqTrainer

trainer = Seq2SeqTrainer(
    args=args,
    model=model,
    train_dataset=ds["train"],
    eval_dataset=ds["validation"],
    data_collator=DataCollator(processor),
    compute_metrics=compute_metrics,
    processing_class=processor.feature_extractor,
)

# Resume from checkpoint
trainer.train(resume_from_checkpoint="checkpoint/checkpoint-2500")
```

### 10. Save & Evaluate

```python
model.save_pretrained("train/output/whisper")
processor.save_pretrained("train/output/whisper")

res = trainer.evaluate(ds["test"])
print(f"Test WER: {res['eval_wer']:.2f}%  CER: {res['eval_cer']:.2f}%")
```

## Expected Results (FSC + FLEURS, 5000 steps)

| Model | WER | CER |
|-------|-----|-----|
| Whisper-small (zero-shot) | TBD | TBD |
| Whisper-small (fine-tuned) | TBD | TBD |

> Run `python train/compare_models.py --plot` to compute actual comparison.

## Hyperparameter Reference

| Parameter | Value | Notes |
|-----------|-------|-------|
| Learning rate | 1e-5 | Reduce to 5e-6 if unstable |
| Batch size | 8 | With grad_accum=2 → effective 16 |
| Warmup steps | 500 | 10% of max_steps |
| Max steps | 5000 | Effective 3 epochs on FSC+FLEURS |
| Mixed precision | fp16 | Disabled automatically on CPU |
| Gradient checkpointing | True | Saves VRAM |
