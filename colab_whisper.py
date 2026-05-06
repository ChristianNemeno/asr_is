# %% [markdown]
# Fine-tune Whisper-small on Filipino Speech (Tagalog + Cebuano)
# Copy this whole file into a single Colab cell and run.
# ~2-3 hours on T4.

# %%
from google.colab import drive
drive.mount('/content/drive')

# %%
!pip install -q transformers "datasets>=3.0,<4.0" evaluate jiwer soundfile librosa accelerate tensorboard torchcodec

# %%
import os, re, json
import torch
import numpy as np
from dataclasses import dataclass
from typing import Any
from datasets import load_dataset, Audio, DatasetDict, concatenate_datasets
from transformers import WhisperProcessor, WhisperForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer
import evaluate

# ═══════════════════════════════════════════════════════════════
# CONFIG — edit these
# ═══════════════════════════════════════════════════════════════
MODEL_ID = "openai/whisper-small"
OUTPUT_DIR = "/content/drive/MyDrive/asr_filipino/whisper"
BATCH_SIZE = 8
GRAD_ACCUM = 2
MAX_STEPS = 5000
USE_FSC = True       # Filipino Speech Corpus (Tagalog, ~50h, MIT)
USE_FLEURS = True    # FLEURS ceb_ph + fil_ph (~20h, CC-BY)
# ═══════════════════════════════════════════════════════════════

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load & normalize ──────────────────────────────────────────
def norm(text):
    t = text.lower()
    t = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

datasets = []
if USE_FSC:
    print("Loading FSC...")
    fsc = load_dataset("sapinsapin/filipinospeechcorpus")
    fsc = fsc.cast_column("audio", Audio(sampling_rate=16000))
    fsc = fsc.filter(lambda x: x["num_words"] >= 2 and x["duration"] >= 0.8)
    fsc = fsc.rename_column("sentence", "text")
    fsc = fsc.map(lambda b: {"text": norm(b["text"])})
    fsc = fsc.select_columns(["audio", "text"])
    tt = fsc["train"].train_test_split(test_size=0.1, seed=42)
    fsc = DatasetDict({"train": tt["train"], "validation": tt["test"], "test": fsc["test"]})
    datasets.append(fsc)

if USE_FLEURS:
    for lang in ["fil_ph", "ceb_ph"]:
        print(f"Loading FLEURS {lang}...")
        fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
        fl = fl.cast_column("audio", Audio(sampling_rate=16000))
        fl = fl.rename_column("transcription", "text")
        fl = fl.map(lambda b: {"text": norm(b["text"])})
        fl = fl.select_columns(["audio", "text"])
        datasets.append(fl)

if len(datasets) >= 2:
    ds = DatasetDict({s: concatenate_datasets([d[s] for d in datasets]) for s in ["train", "validation", "test"]})
else:
    ds = datasets[0]

for s in ds: print(f"{s}: {len(ds[s])}")

# ── Preprocess ────────────────────────────────────────────────
processor = WhisperProcessor.from_pretrained(MODEL_ID)

def prep(batch):
    audio = batch["audio"]
    batch["input_features"] = processor.feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]
    batch["labels"] = processor.tokenizer(batch["text"]).input_ids
    return batch

ds = ds.map(prep, remove_columns=ds["train"].column_names)

# ── Data collator ─────────────────────────────────────────────
@dataclass
class Collator:
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

# ── Metrics ───────────────────────────────────────────────────
wer_m = evaluate.load("wer")
cer_m = evaluate.load("cer")
def compute_metrics(pred):
    pid = pred.predictions
    lid = np.where(pred.label_ids != -100, pred.label_ids, processor.tokenizer.pad_token_id)
    ps = processor.tokenizer.batch_decode(pid, skip_special_tokens=True)
    ls = processor.tokenizer.batch_decode(lid, skip_special_tokens=True)
    return {"wer": 100 * wer_m.compute(predictions=ps, references=ls), "cer": 100 * cer_m.compute(predictions=ps, references=ls)}

# ── Model ─────────────────────────────────────────────────────
model = WhisperForConditionalGeneration.from_pretrained(MODEL_ID)
model.generation_config.language = None
model.generation_config.task = "transcribe"
model.generation_config.forced_decoder_ids = None

# ── Train ─────────────────────────────────────────────────────
args = Seq2SeqTrainingArguments(
    output_dir=os.path.join(OUTPUT_DIR, "checkpoints"),
    per_device_train_batch_size=BATCH_SIZE, gradient_accumulation_steps=GRAD_ACCUM,
    learning_rate=1e-5, warmup_steps=500, max_steps=MAX_STEPS,
    gradient_checkpointing=True, fp16=True, eval_strategy="steps",
    per_device_eval_batch_size=BATCH_SIZE, predict_with_generate=True,
    generation_max_length=225, save_steps=500, eval_steps=500, logging_steps=50,
    load_best_model_at_end=True, metric_for_best_model="wer", greater_is_better=False,
    report_to=["tensorboard"], save_total_limit=3,
)

trainer = Seq2SeqTrainer(
    args=args,
    model=model,
    train_dataset=ds["train"],
    eval_dataset=ds["validation"],
    data_collator=Collator(processor),
    compute_metrics=compute_metrics,
    processing_class=processor.feature_extractor,  # ← new argument
)
trainer.train()

# ── Save & eval ───────────────────────────────────────────────
model.save_pretrained(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print(f"Saved to {OUTPUT_DIR}")

res = trainer.evaluate(ds["test"])
print(f"Test WER: {res['eval_wer']:.2f}%  CER: {res['eval_cer']:.2f}%")
with open(os.path.join(OUTPUT_DIR, "test_results.json"), "w") as f:
    json.dump(res, f, indent=2)
