# Cebuano Speech Dataset

## Source

- **Hugging Face**: `Speech-data/Cebuano-Speech-Dataset`
- **Website**: https://speech-data.ai/datasets/cebuano/
- **License**: CC BY-NC-ND 4.0

## Dataset Overview

| Property | Value |
|----------|-------|
| Total Audio | 108 hours |
| Number of Files | 807 |
| Total Size | ~135 MB |
| Formats | MP3, WAV |
| Language | Cebuano (Bisaya) |
| Gender Split | 49% Female / 51% Male |
| Age Range | 18 - 50+ years |
| Speaker Regions | Cebu, Mindanao, Bohol, Leyte (Philippines) |

## Loading the Dataset

```python
from datasets import load_dataset, Audio

ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")

# Inspect splits
print(ds)
print(ds["train"][0])
```

Expected columns:
- `AudioID` — unique identifier
- `audio_text` — transcription text (Cebuano)
- `gender` — speaker gender
- `duration` — audio duration
- `format` — file format (MP3/WAV)
- `audio` — audio data (loaded via Datasets Audio feature)

## Data Preprocessing Steps

### 1. Resample Audio to 16kHz
Both Whisper and Wav2Vec2/XLS-R expect 16kHz audio:

```python
from datasets import Audio

ds = ds.cast_column("audio", Audio(sampling_rate=16_000))
```

### 2. Text Normalization

Cebuano uses the Latin alphabet. Normalization steps:
- Convert to lowercase
- Remove special characters (`,.?!;:""'` etc.) — keep only letters, spaces, apostrophes
- Handle any diacritics if present (Cebuano uses ñ, though rare in modern text)
- Strip extra whitespace

```python
import re

def normalize_text(batch):
    text = batch["audio_text"].lower()
    text = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\']', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return {"audio_text": text}

ds = ds.map(normalize_text)
```

### 3. Train/Validation/Test Split

```python
train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)

from datasets import DatasetDict
dataset = DatasetDict({
    "train": train_test["train"],
    "validation": test_valid["train"],
    "test": test_valid["test"],
})
```

### 4. Audio Inspection

Before training, inspect audio properties:

```python
import numpy as np

durations = []
for sample in dataset["train"]:
    arr = sample["audio"]["array"]
    sr = sample["audio"]["sampling_rate"]
    durations.append(len(arr) / sr)

print(f"Min duration: {min(durations):.2f}s")
print(f"Max duration: {max(durations):.2f}s")
print(f"Mean duration: {np.mean(durations):.2f}s")
print(f"Total hours: {sum(durations)/3600:.2f}h")
```

## Cebuano Language Notes

- Cebuano (Bisaya) is the second most spoken language in the Philippines (~21M speakers)
- It uses the Latin alphabet (A-Z, plus Ñ/ñ in formal writing)
- Word order is typically VSO (Verb-Subject-Object)
- Agglutinative language with complex verbal morphology
- Common words: `ako` (I), `ikaw` (you), `siya` (he/she), `maayong buntag` (good morning)

## Dataset Limitations

- Relatively small at 108 hours (low-resource)
- Single dataset — no external validation source
- CC BY-NC-ND license restricts commercial use
- Speaker diversity limited to 4 Philippine regions
- Recording quality may vary across samples
