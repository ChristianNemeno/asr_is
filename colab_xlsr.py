# %% [markdown]
# Fine-tune XLS-R 300M on Filipino Speech (Tagalog + Cebuano)
# Copy this whole file into a single Colab cell and run.
# ~3-4 hours on T4.

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
from typing import Union
from datasets import load_dataset, Audio, DatasetDict, concatenate_datasets
from transformers import (
    Wav2Vec2CTCTokenizer, Wav2Vec2FeatureExtractor, Wav2Vec2Processor,
    Wav2Vec2ForCTC, TrainingArguments, Trainer,
)
import evaluate

# ═══════════════════════════════════════════════════════════════
# CONFIG — edit these
# ═══════════════════════════════════════════════════════════════
MODEL_ID = "facebook/wav2vec2-xls-r-300m"
OUTPUT_DIR = "/content/drive/MyDrive/asr_filipino/xlsr"
BATCH_SIZE = 8
GRAD_ACCUM = 2
NUM_EPOCHS = 30
USE_FSC = True
USE_FLEURS = True
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

# ── Build character vocab ─────────────────────────────────────
def extract_vocab(batch):
    all_text = " ".join(batch["text"])
    vocab = sorted(list(set(all_text)))
    return {"vocab": [vocab], "all_text": [all_text]}

vt = ds["train"].map(extract_vocab, batched=True, batch_size=-1, keep_in_memory=True, remove_columns=ds["train"].column_names)
vte = ds["test"].map(extract_vocab, batched=True, batch_size=-1, keep_in_memory=True, remove_columns=ds["test"].column_names)
vocab_list = sorted(set(vt["vocab"][0]) | set(vte["vocab"][0]))
vocab_dict = {ch: idx for idx, ch in enumerate(vocab_list)}
vocab_dict["|"] = vocab_dict[" "]; del vocab_dict[" "]
vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)
print(f"Vocab size: {len(vocab_dict)}")

vocab_path = os.path.join(OUTPUT_DIR, "vocab.json")
with open(vocab_path, "w") as f:
    json.dump(vocab_dict, f)

# ── Processor ─────────────────────────────────────────────────
tokenizer = Wav2Vec2CTCTokenizer(vocab_path, unk_token="[UNK]", pad_token="[PAD]", word_delimiter_token="|")
feature_extractor = Wav2Vec2FeatureExtractor(feature_size=1, sampling_rate=16000, padding_value=0.0, do_normalize=True, return_attention_mask=True)
processor = Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)

# ── Preprocess ────────────────────────────────────────────────
def prep(batch):
    audio = batch["audio"]
    batch["input_values"] = processor(audio["array"], sampling_rate=audio["sampling_rate"]).input_values[0]
    with processor.as_target_processor():
        batch["labels"] = processor(batch["text"]).input_ids
    return batch

ds = ds.map(prep, remove_columns=ds["train"].column_names)

# ── Collator ──────────────────────────────────────────────────
@dataclass
class Collator:
    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True
    def __call__(self, features):
        input_features = [{"input_values": f["input_values"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]
        batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(label_features, padding=self.padding, return_tensors="pt")
        batch["labels"] = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        return batch

# ── Metrics ───────────────────────────────────────────────────
wer_m = evaluate.load("wer")
cer_m = evaluate.load("cer")
def compute_metrics(pred):
    pl = pred.predictions; pid = np.argmax(pl, axis=-1)
    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id
    ps = processor.batch_decode(pid)
    ls = processor.batch_decode(pred.label_ids, group_tokens=False)
    return {"wer": 100 * wer_m.compute(predictions=ps, references=ls), "cer": 100 * cer_m.compute(predictions=ps, references=ls)}

# ── Model ─────────────────────────────────────────────────────
model = Wav2Vec2ForCTC.from_pretrained(
    MODEL_ID, attention_dropout=0.0, hidden_dropout=0.0, feat_proj_dropout=0.0,
    mask_time_prob=0.05, layerdrop=0.0, ctc_loss_reduction="mean",
    pad_token_id=processor.tokenizer.pad_token_id, vocab_size=len(processor.tokenizer),
)
model.freeze_feature_extractor()

# ── Train ─────────────────────────────────────────────────────
args = TrainingArguments(
    output_dir=os.path.join(OUTPUT_DIR, "checkpoints"),
    group_by_length=True,
    per_device_train_batch_size=BATCH_SIZE, gradient_accumulation_steps=GRAD_ACCUM,
    eval_strategy="steps", num_train_epochs=NUM_EPOCHS, gradient_checkpointing=True, fp16=True,
    save_steps=400, eval_steps=400, logging_steps=400,
    learning_rate=3e-4, warmup_steps=500, save_total_limit=3,
    load_best_model_at_end=True, metric_for_best_model="wer", greater_is_better=False,
    report_to=["tensorboard"],
)

trainer = Trainer(
    args=args, model=model, data_collator=Collator(processor), compute_metrics=compute_metrics,
    train_dataset=ds["train"], eval_dataset=ds["validation"], tokenizer=processor.feature_extractor,
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
