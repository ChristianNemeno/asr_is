# %% [markdown]
# Fine-Tune XLS-R 300M on Cebuano Speech Dataset (Colab)
# %% [markdown]
## 1. Mount Google Drive & Install Dependencies
# %%
from google.colab import drive
drive.mount('/content/drive')

# %%
!pip install -q transformers datasets evaluate jiwer soundfile librosa accelerate tensorboard

# %%
import os
import re
import json
import torch
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Union
from datasets import load_dataset, Audio, DatasetDict
from transformers import (
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor,
    Wav2Vec2Processor,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Trainer,
)
import evaluate

# %% [markdown]
## 2. Configuration
# %%
MODEL_ID = "facebook/wav2vec2-xls-r-300m"
OUTPUT_DIR = "/content/drive/MyDrive/asr_cebuano/xlsr-300m-cebuano"
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

BATCH_SIZE = 8
GRAD_ACCUM = 2
LEARNING_RATE = 3e-4
WARMUP_STEPS = 500
NUM_EPOCHS = 30
SAVE_STEPS = 400
EVAL_STEPS = 400
LOGGING_STEPS = 400

# %% [markdown]
## 3. Load & Preprocess Dataset
# %%
ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")
ds = ds.cast_column("audio", Audio(sampling_rate=16000))
ds = ds.rename_column("audio_text", "sentence")

def normalize(batch):
    text = batch["sentence"].lower()
    text = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return {"sentence": text}

ds = ds.map(normalize)

train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)
dataset = DatasetDict({
    "train": train_test["train"],
    "validation": test_valid["train"],
    "test": test_valid["test"],
})
print(f"Train: {len(dataset['train'])}, Val: {len(dataset['validation'])}, Test: {len(dataset['test'])}")

# %% [markdown]
## 4. Build Cebuano Vocabulary & Tokenizer
# %%
def extract_chars(batch):
    all_text = " ".join(batch["sentence"])
    vocab = sorted(list(set(all_text)))
    return {"vocab": [vocab], "all_text": [all_text]}

vocab_train = dataset["train"].map(
    extract_chars, batched=True, batch_size=-1,
    keep_in_memory=True, remove_columns=dataset["train"].column_names
)
vocab_test = dataset["test"].map(
    extract_chars, batched=True, batch_size=-1,
    keep_in_memory=True, remove_columns=dataset["test"].column_names
)

vocab_list = sorted(set(vocab_train["vocab"][0]) | set(vocab_test["vocab"][0]))
vocab_dict = {ch: idx for idx, ch in enumerate(vocab_list)}

# Replace space with visible delimiter, add special tokens
vocab_dict["|"] = vocab_dict[" "]
del vocab_dict[" "]
vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)
print(f"Vocabulary size: {len(vocab_dict)}")

with open("vocab.json", "w") as f:
    json.dump(vocab_dict, f)

# %% [markdown]
## 5. Create Processor
# %%
tokenizer = Wav2Vec2CTCTokenizer(
    "vocab.json",
    unk_token="[UNK]",
    pad_token="[PAD]",
    word_delimiter_token="|",
)

feature_extractor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    padding_value=0.0,
    do_normalize=True,
    return_attention_mask=True,
)

processor = Wav2Vec2Processor(
    feature_extractor=feature_extractor,
    tokenizer=tokenizer,
)

# %% [markdown]
## 6. Preprocess for Training
# %%
def prepare_dataset(batch):
    audio = batch["audio"]
    batch["input_values"] = processor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_values[0]
    with processor.as_target_processor():
        batch["labels"] = processor(batch["sentence"]).input_ids
    return batch

dataset = dataset.map(prepare_dataset, remove_columns=dataset["train"].column_names)

# %% [markdown]
## 7. Data Collator
# %%
@dataclass
class DataCollatorCTCWithPadding:
    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True

    def __call__(self, features):
        input_features = [{"input_values": f["input_values"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]

        batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(label_features, padding=self.padding, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        batch["labels"] = labels
        return batch

data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)

# %% [markdown]
## 8. Evaluation Metrics
# %%
wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = np.argmax(pred_logits, axis=-1)
    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str = processor.batch_decode(pred_ids)
    label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

    return {
        "wer": 100 * wer_metric.compute(predictions=pred_str, references=label_str),
        "cer": 100 * cer_metric.compute(predictions=pred_str, references=label_str),
    }

# %% [markdown]
## 9. Load Model
# %%
model = Wav2Vec2ForCTC.from_pretrained(
    MODEL_ID,
    attention_dropout=0.0,
    hidden_dropout=0.0,
    feat_proj_dropout=0.0,
    mask_time_prob=0.05,
    layerdrop=0.0,
    ctc_loss_reduction="mean",
    pad_token_id=processor.tokenizer.pad_token_id,
    vocab_size=len(processor.tokenizer),
)
model.freeze_feature_extractor()

# %% [markdown]
## 10. Training Arguments
# %%
training_args = TrainingArguments(
    output_dir=CHECKPOINT_DIR,
    group_by_length=True,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    eval_strategy="steps",
    num_train_epochs=NUM_EPOCHS,
    gradient_checkpointing=True,
    fp16=True,
    save_steps=SAVE_STEPS,
    eval_steps=EVAL_STEPS,
    logging_steps=LOGGING_STEPS,
    learning_rate=LEARNING_RATE,
    warmup_steps=WARMUP_STEPS,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
    report_to=["tensorboard"],
)

# %% [markdown]
## 11. Train
# %%
trainer = Trainer(
    model=model,
    data_collator=data_collator,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=processor.feature_extractor,
)

trainer.train()

# %% [markdown]
## 12. Save to Google Drive
# %%
model.save_pretrained(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")

# %% [markdown]
## 13. Evaluate on Test Set
# %%
test_results = trainer.evaluate(dataset["test"])
print(f"Test WER: {test_results['eval_wer']:.2f}%")
print(f"Test CER: {test_results['eval_cer']:.2f}%")

with open(os.path.join(OUTPUT_DIR, "test_results.json"), "w") as f:
    json.dump(test_results, f, indent=2)
