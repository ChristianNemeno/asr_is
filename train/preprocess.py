import re
from datasets import load_dataset, Audio, DatasetDict


def load_and_split_dataset():
    ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")
    ds = ds.cast_column("audio", Audio(sampling_rate=16000))
    ds = ds.rename_column("audio_text", "sentence")

    keep_cols = ["audio", "sentence"]
    drop_cols = [c for c in ds["train"].column_names if c not in keep_cols]
    ds = ds.remove_columns(drop_cols)

    train_test = ds["train"].train_test_split(test_size=0.2, seed=42)
    test_valid = train_test["test"].train_test_split(test_size=0.5, seed=42)

    return DatasetDict({
        "train": train_test["train"],
        "validation": test_valid["train"],
        "test": test_valid["test"],
    })


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_dataset(dataset: DatasetDict) -> DatasetDict:
    def _normalize(batch):
        return {"sentence": normalize_text(batch["sentence"])}

    return dataset.map(_normalize)


def print_stats(dataset: DatasetDict):
    for split in dataset:
        durations = []
        for sample in dataset[split]:
            arr = sample["audio"]["array"]
            sr = sample["audio"]["sampling_rate"]
            durations.append(len(arr) / sr)

        total_sec = sum(durations)
        print(f"{split}: {len(durations)} samples, "
              f"min={min(durations):.1f}s, max={max(durations):.1f}s, "
              f"mean={total_sec/len(durations):.1f}s, total={total_sec/3600:.1f}h")
