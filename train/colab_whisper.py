# %% [markdown]
# Fine-Tune Whisper-small on Cebuano Speech Dataset (Colab)
# %% [markdown]
## 1. Mount Google Drive & Install Dependencies
# %%
from google.colab import drive
drive.mount('/content/drive')

# %%
!pip install -q transformers datasets evaluate jiwer soundfile librosa accelerate tensorboard

# %%
import os
import torch
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Union
from datasets import load_dataset, Audio, DatasetDict
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
import evaluate

# %% [markdown]
## 2. Configuration
# %%
MODEL_ID = "openai/whisper-small"
OUTPUT_DIR = "/content/drive/MyDrive/asr_cebuano/whisper-small-cebuano"
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

BATCH_SIZE = 8
GRAD_ACCUM = 2  # effective batch = 16
LEARNING_RATE = 1e-5
WARMUP_STEPS = 500
MAX_STEPS = 5000
SAVE_STEPS = 500
EVAL_STEPS = 500
LOGGING_STEPS = 50

# %% [markdown]
## 3. Load & Preprocess Dataset
# %%
ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")
ds = ds.cast_column("audio", Audio(sampling_rate=16000))
ds = ds.rename_column("audio_text", "sentence")

import re
def normalize(batch):
    text = batch["sentence"].lower()
    text = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return {"sentence": text}

ds = ds.map(normalize)

# Split
train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)
dataset = DatasetDict({
    "train": train_test["train"],
    "validation": test_valid["train"],
    "test": test_valid["test"],
})

print(f"Train: {len(dataset['train'])} samples")
print(f"Validation: {len(dataset['validation'])} samples")
print(f"Test: {len(dataset['test'])} samples")

# %% [markdown]
## 4. Load Processor & Model
# %%
processor = WhisperProcessor.from_pretrained(MODEL_ID)
model = WhisperForConditionalGeneration.from_pretrained(MODEL_ID)

model.generation_config.language = None  # auto-detect
model.generation_config.task = "transcribe"
model.generation_config.forced_decoder_ids = None

# %% [markdown]
## 5. Preprocess for Training
# %%
def prepare_dataset(batch):
    audio = batch["audio"]
    batch["input_features"] = processor.feature_extractor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_features[0]
    batch["labels"] = processor.tokenizer(batch["sentence"]).input_ids
    return batch

dataset = dataset.map(prepare_dataset, remove_columns=dataset["train"].column_names)

# %% [markdown]
## 6. Data Collator
# %%
@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features):
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        if (labels[:, 0] == model.config.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

# %% [markdown]
## 7. Evaluation Metrics
# %%
wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    return {
        "wer": 100 * wer_metric.compute(predictions=pred_str, references=label_str),
        "cer": 100 * cer_metric.compute(predictions=pred_str, references=label_str),
    }

# %% [markdown]
## 8. Training Arguments
# %%
training_args = Seq2SeqTrainingArguments(
    output_dir=CHECKPOINT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    learning_rate=LEARNING_RATE,
    warmup_steps=WARMUP_STEPS,
    max_steps=MAX_STEPS,
    gradient_checkpointing=True,
    fp16=True,
    eval_strategy="steps",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=SAVE_STEPS,
    eval_steps=EVAL_STEPS,
    logging_steps=LOGGING_STEPS,
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    report_to=["tensorboard"],
    save_total_limit=3,
    push_to_hub=False,
)

# %% [markdown]
## 9. Train
# %%
trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.feature_extractor,
)

trainer.train()

# %% [markdown]
## 10. Save Final Model to Google Drive
# %%
model.save_pretrained(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")

# %% [markdown]
## 11. Evaluate on Test Set
# %%
test_results = trainer.evaluate(dataset["test"])
print(f"Test WER: {test_results['eval_wer']:.2f}%")
print(f"Test CER: {test_results['eval_cer']:.2f}%")

import json
with open(os.path.join(OUTPUT_DIR, "test_results.json"), "w") as f:
    json.dump(test_results, f, indent=2)
