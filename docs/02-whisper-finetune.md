# Fine-Tuning Whisper for Cebuano ASR

> Based on: [Fine-Tune Whisper For Multilingual ASR with Transformers](https://huggingface.co/blog/fine-tune-whisper)
> and the official [Hugging Face ASR guide](https://huggingface.co/docs/transformers/tasks/asr)

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

**Recommendation for Cebuano (108h)**: Start with `whisper-small` — good balance of quality and resource usage.

## Step-by-Step Fine-Tuning

### 1. Install Dependencies

```bash
pip install transformers datasets evaluate jiwer soundfile librosa accelerate
pip install gradio  # optional: for demo
```

### 2. Load Dataset

```python
from datasets import load_dataset, Audio, DatasetDict

ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")
ds = ds.cast_column("audio", Audio(sampling_rate=16000))

# Rename 'audio_text' to 'sentence' for consistency
ds = ds.rename_column("audio_text", "sentence")

# Split
train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)

dataset = DatasetDict({
    "train": train_test["train"],
    "validation": test_valid["train"],
    "test": test_valid["test"],
})
```

### 3. Load Whisper Processor

The `WhisperProcessor` bundles the feature extractor and tokenizer:

```python
from transformers import WhisperProcessor

processor = WhisperProcessor.from_pretrained(
    "openai/whisper-small",
    language="Cebuano",
    task="transcribe"
)
```

> **Note**: If Whisper doesn't have a "Cebuano" language token, use `language=None` and let it auto-detect, or check available tokens with `processor.tokenizer.get_vocab()`.

### 4. Preprocess Data

Whisper expects:
- Audio padded/truncated to **30 seconds**
- Transcriptions encoded with **language + task prefix tokens**

```python
def prepare_dataset(batch):
    audio = batch["audio"]

    # Extract log-Mel spectrogram features
    batch["input_features"] = processor.feature_extractor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_features[0]

    # Encode target text to label ids
    batch["labels"] = processor.tokenizer(batch["sentence"]).input_ids
    return batch

dataset = dataset.map(prepare_dataset, remove_columns=dataset["train"].column_names)
```

### 5. Data Collator

```python
import torch
from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # Audio inputs: just convert to tensors (already padded to 30s)
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # Text labels: pad to max length in batch
        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # Replace padding with -100 (ignored in loss)
        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )

        # Remove BOS token if appended (it gets added during generation)
        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

data_collator = DataCollatorSpeechSeq2SeqWithPadding(
    processor=processor,
    decoder_start_token_id=processor.tokenizer.convert_tokens_to_ids("<|startoftranscript|>"),
)
```

### 6. Load Model

```python
from transformers import WhisperForConditionalGeneration

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

# Optional: Force language and task tokens
model.generation_config.language = "cebuano"  # or auto-detect
model.generation_config.task = "transcribe"
model.generation_config.forced_decoder_ids = None
```

### 7. Evaluation Metrics

```python
import evaluate

wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # Replace -100 with pad_token_id
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

    # Decode predictions and references
    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    wer = 100 * wer_metric.compute(predictions=pred_str, references=label_str)
    cer = 100 * cer_metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer, "cer": cer}
```

### 8. Training Arguments

```python
from transformers import Seq2SeqTrainingArguments

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-cebuano",
    per_device_train_batch_size=16,
    gradient_accumulation_steps=1,
    learning_rate=1e-5,
    warmup_steps=500,
    max_steps=5000,
    gradient_checkpointing=True,
    fp16=True,                       # use bf16=True for Ampere+ GPUs
    eval_strategy="steps",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=1000,
    eval_steps=1000,
    logging_steps=25,
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,               # set True to push to HF Hub
    report_to=["tensorboard"],
)
```

### 9. Train

```python
from transformers import Seq2SeqTrainer

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
```

### 10. Evaluate on Test Set

```python
results = trainer.evaluate(dataset["test"])
print(f"Test WER: {results['eval_wer']:.2f}%")
print(f"Test CER: {results['eval_cer']:.2f}%")
```

## Using with WhisperX Pipeline

After fine-tuning Whisper, integrate with WhisperX for word-level timestamps:

```python
import whisperx

device = "cuda"
audio_file = "path/to/audio.wav"

# Load YOUR fine-tuned Whisper model into WhisperX
model = whisperx.load_model(
    "path/to/whisper-small-cebuano",  # local path
    device=device,
    compute_type="float16",
)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=16)

# Align with Wav2Vec2 (requires language-specific alignment model)
# For Cebuano, you may need to find or train a phoneme alignment model
# model_a, metadata = whisperx.load_align_model(
#     language_code="ceb",  # ISO 639-3 code
#     device=device,
# )
# result = whisperx.align(result["segments"], model_a, metadata, audio, device)

print(result["segments"])
```

## Hyperparameter Tuning Suggestions

| Parameter | Starting Value | Notes |
|-----------|---------------|-------|
| Learning rate | 1e-5 | Reduce to 5e-6 if unstable |
| Batch size | 16 | Reduce if OOM, increase grad_accum |
| Warmup steps | 500 | ~10% of total steps |
| Max steps | 5000 | Adjust based on dataset size |
| Dropout | Default | Increase to 0.1 if overfitting |
| Gradient checkpointing | True | Saves memory |

## Expected Results

For a low-resource language like Cebuano with 108h of data:
- **Baseline Whisper-small** (zero-shot): ~40-80% WER (depends on pre-training coverage)
- **After fine-tuning**: Expect ~15-40% WER
- Best results with `whisper-medium` or `large-v3` + more data
