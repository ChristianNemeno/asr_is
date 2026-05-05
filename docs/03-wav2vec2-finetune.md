# Fine-Tuning Wav2Vec2 / XLS-R for Cebuano ASR

> Based on: [Fine-Tune XLS-R for Multi-Lingual ASR](https://huggingface.co/blog/fine-tune-xlsr-wav2vec2)
> and the official [Hugging Face ASR guide](https://huggingface.co/docs/transformers/tasks/asr)

## Architecture Overview

Wav2Vec2 / XLS-R is an **encoder-only** model trained with CTC:
1. **CNN Feature Encoder**: Raw audio → latent speech representations (downsampled ~320x)
2. **Transformer**: Contextualizes latent representations
3. **CTC Linear Head**: Maps hidden states → character/phone tokens

Key differences from Whisper:
- **No decoder** — output is at frame level, not autoregressive
- Uses **CTC loss** (Connectionist Temporal Classification)
- Must **build a custom vocabulary** from the dataset
- Simpler architecture, often better for very low-resource languages
- **XLS-R** is the multilingual variant (128 languages, 436K hrs pre-training)

## Pre-Trained Checkpoints

| Model | Parameters | Pre-training Data | HF Path |
|-------|-----------|-------------------|---------|
| XLS-R 300M | 317M | 436K hours, 128 langs | `facebook/wav2vec2-xls-r-300m` |
| XLS-R 1B | 965M | 436K hours, 128 langs | `facebook/wav2vec2-xls-r-1b` |
| XLS-R 2B | 2.16B | 436K hours, 128 langs | `facebook/wav2vec2-xls-r-2b` |
| Wav2Vec2 base | 95M | 960h LibriSpeech (English) | `facebook/wav2vec2-base` |

**Recommendation**: Use `facebook/wav2vec2-xls-r-300m` — multilingual, reasonable size.

> **Note**: XLS-R pre-training includes 128 languages. Philippine languages may not be explicitly covered, but cross-lingual transfer is a key strength of XLS-R.

## Step-by-Step Fine-Tuning

### 1. Install Dependencies

```bash
pip install transformers datasets evaluate jiwer soundfile librosa accelerate
```

### 2. Load Dataset

```python
from datasets import load_dataset, Audio, DatasetDict

ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")
ds = ds.cast_column("audio", Audio(sampling_rate=16000))
ds = ds.rename_column("audio_text", "sentence")

# Remove metadata columns
ds = ds.remove_columns(["gender", "duration", "format"])

# Split
train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)

dataset = DatasetDict({
    "train": train_test["train"],
    "validation": test_valid["train"],
    "test": test_valid["test"],
})
```

### 3. Text Normalization

```python
import re

chars_to_remove = r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»]'

def normalize_text(batch):
    text = batch["sentence"]
    text = re.sub(chars_to_remove, '', text).lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return {"sentence": text}

dataset = dataset.map(normalize_text)
```

### 4. Build Custom Vocabulary

Unlike Whisper, Wav2Vec2 needs a tokenizer built from the dataset:

```python
def extract_all_chars(batch):
    all_text = " ".join(batch["sentence"])
    vocab = sorted(list(set(all_text)))
    return {"vocab": [vocab], "all_text": [all_text]}

vocab_train = dataset["train"].map(
    extract_all_chars, batched=True, batch_size=-1,
    keep_in_memory=True, remove_columns=dataset["train"].column_names
)
vocab_test = dataset["test"].map(
    extract_all_chars, batched=True, batch_size=-1,
    keep_in_memory=True, remove_columns=dataset["test"].column_names
)

vocab_list = sorted(set(vocab_train["vocab"][0]) | set(vocab_test["vocab"][0]))
vocab_dict = {ch: idx for idx, ch in enumerate(vocab_list)}

# Add special tokens
vocab_dict["|"] = vocab_dict[" "]  # word delimiter (space → |)
del vocab_dict[" "]
vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)

print(f"Vocabulary size: {len(vocab_dict)}")
```

### 5. Create Tokenizer & Processor

```python
import json

with open("vocab.json", "w") as f:
    json.dump(vocab_dict, f)

from transformers import Wav2Vec2CTCTokenizer, Wav2Vec2FeatureExtractor, Wav2Vec2Processor

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
```

### 6. Preprocess Data

```python
def prepare_dataset(batch):
    audio = batch["audio"]

    # Extract features (normalize raw waveform)
    batch["input_values"] = processor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_values[0]
    batch["input_length"] = len(batch["input_values"])

    # Tokenize labels
    with processor.as_target_processor():
        batch["labels"] = processor(batch["sentence"]).input_ids
    return batch

dataset = dataset.map(
    prepare_dataset,
    remove_columns=dataset["train"].column_names,
)
```

### 7. Data Collator (CTC-specific)

```python
import torch
from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorCTCWithPadding:
    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_values": f["input_values"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]

        batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")

        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(label_features, padding=self.padding, return_tensors="pt")

        # Replace padding with -100 (CTC ignores these)
        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )
        batch["labels"] = labels
        return batch

data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)
```

### 8. Evaluation Metrics

```python
import numpy as np
import evaluate

wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = np.argmax(pred_logits, axis=-1)

    # Replace -100 with pad_token_id
    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

    # Decode (group_tokens=False for reference to avoid CTC collapsing)
    pred_str = processor.batch_decode(pred_ids)
    label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

    wer = 100 * wer_metric.compute(predictions=pred_str, references=label_str)
    cer = 100 * cer_metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer, "cer": cer}
```

### 9. Load Model

```python
from transformers import Wav2Vec2ForCTC

model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-xls-r-300m",
    attention_dropout=0.0,
    hidden_dropout=0.0,
    feat_proj_dropout=0.0,
    mask_time_prob=0.05,         # SpecAugment
    mask_feature_prob=0.0,       # SpecAugment
    layerdrop=0.0,
    ctc_loss_reduction="mean",
    pad_token_id=processor.tokenizer.pad_token_id,
    vocab_size=len(processor.tokenizer),
)

# Freeze CNN feature extractor (already well-trained)
model.freeze_feature_extractor()
```

### 10. Training Arguments

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./wav2vec2-xlsr-cebuano",
    group_by_length=True,          # group similar-length samples
    per_device_train_batch_size=16,
    gradient_accumulation_steps=2,
    eval_strategy="steps",
    num_train_epochs=30,
    gradient_checkpointing=True,
    fp16=True,                     # use bf16 for Ampere+ GPUs
    save_steps=400,
    eval_steps=400,
    logging_steps=400,
    learning_rate=3e-4,
    warmup_steps=500,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
    report_to=["tensorboard"],
)
```

### 11. Train

```python
from transformers import Trainer

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
```

### 12. Evaluate on Test Set

```python
results = trainer.evaluate(dataset["test"])
print(f"Test WER: {results['eval_wer']:.2f}%")
print(f"Test CER: {results['eval_cer']:.2f}%")
```

## Inference with Fine-Tuned Model

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

def transcribe(audio_path):
    import soundfile as sf
    speech, sr = sf.read(audio_path)

    inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    pred_ids = torch.argmax(logits, dim=-1)[0]
    transcription = processor.decode(pred_ids)
    return transcription

print(transcribe("path/to/audio.wav"))
```

## Hyperparameter Tuning

| Parameter | Starting Value | Notes |
|-----------|---------------|-------|
| Learning rate | 3e-4 | CTC often needs higher LR than seq2seq |
| Epochs | 30 | CTC convergence is slower |
| Batch size | 16 | Reduce if OOM |
| mask_time_prob | 0.05 | SpecAugment; increase to 0.1 if overfitting |
| Attention dropout | 0.0 | Increase to 0.1 if overfitting |
| Hidden dropout | 0.0 | Increase to 0.1 if overfitting |
| Freeze feature extractor | True | CNN is well pre-trained; unfreeze only with large datasets |

## CTC Decoding with Language Model

For better results, add a language model for beam search decoding:

```bash
pip install pyctcdecode
```

```python
# Build a KenLM n-gram language model from Cebuano text
from pyctcdecode import build_ctcdecoder

labels = list(processor.tokenizer.get_vocab().keys())
labels = [l for l in labels if l not in ["[PAD]", "[UNK]"]]

decoder = build_ctcdecoder(
    labels=labels,
    kenlm_model_path="cebuano_5gram.arpa",  # pre-built LM
)

# Use in compute_metrics or inference
decoded = decoder.decode(logits.cpu().numpy())
```

## Expected Results

- XLS-R zero-shot on unseen language: **80-100% WER** (very poor)
- After fine-tuning on 86h of Cebuano: Expect **25-50% WER**
- With LM decoding: Additional **5-15% relative improvement**
- Wav2Vec2 typically needs **more fine-tuning data** than Whisper for comparable results
