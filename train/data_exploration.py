#!/usr/bin/env python3
"""
Explore and visualize the training dataset before training.

Usage:
    python train/data_exploration.py

Output: train/output/plots/data_exploration/
"""

import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torchaudio
from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset

sys.path.insert(0, os.path.dirname(__file__))

OUT_DIR = os.path.join("train", "output", "plots", "data_exploration")
SEED = 42

sns.set_theme(style="whitegrid", palette="muted", context="notebook")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def norm(text: str) -> str:
    t = text.lower()
    t = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def load_raw() -> tuple[dict, dict]:
    """Load FSC + FLEURS without feature extraction, return metadata dicts."""
    print("Loading FSC...")
    fsc = load_dataset("sapinsapin/filipinospeechcorpus")
    fsc = fsc.cast_column("audio", Audio(sampling_rate=16000))
    fsc = fsc.filter(lambda x: x["num_words"] >= 2 and x["duration"] >= 0.8)
    fsc = fsc.rename_column("sentence", "text")
    fsc = fsc.map(lambda b: {"text": norm(b["text"])})
    fsc = fsc.select_columns(["audio", "text"])

    fleurs_ds = []
    for lang in ["fil_ph", "ceb_ph"]:
        print(f"Loading FLEURS {lang}...")
        fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
        fl = fl.cast_column("audio", Audio(sampling_rate=16000))
        fl = fl.rename_column("transcription", "text")
        fl = fl.map(lambda b: {"text": norm(b["text"])})
        fl = fl.select_columns(["audio", "text"])
        fleurs_ds.append(fl)

    return fsc, fleurs_ds


def collect_stats(fsc, fleurs_list) -> dict:
    """Gather durations, word counts, and source labels for every sample."""
    durations: list[float] = []
    word_counts: list[int] = []
    source: list[str] = []
    names: list[str] = ["FSC"] + [f"FLEURS {d['train'][0].get('audio', '') or d['train'][0]['text']}" for d in fleurs_list]

    for i, ds in enumerate(fleurs_list):
        for split in ds.keys():
            for row in ds[split]:
                arr = row["audio"]["array"]
                sr = row["audio"]["sampling_rate"]
                durations.append(len(arr) / sr)
                word_counts.append(len(row["text"].split()))
                source.append(names[i + 1])

    for split in fsc.keys():
        for row in fsc[split]:
            arr = row["audio"]["array"]
            sr = row["audio"]["sampling_rate"]
            durations.append(len(arr) / sr)
            word_counts.append(len(row["text"].split()))
            source.append(names[0])

    return {"durations": durations, "word_counts": word_counts, "source": source}


def plot_duration_histogram(stats: dict):
    fig, ax = plt.subplots(figsize=(8, 4))
    for label in sorted(set(stats["source"])):
        vals = [v for v, s in zip(stats["durations"], stats["source"]) if s == label]
        ax.hist(vals, bins=50, alpha=0.6, label=f"{label} (n={len(vals)})")
    ax.set_xlabel("Duration (seconds)")
    ax.set_ylabel("Sample count")
    ax.set_title("Audio Duration Distribution by Dataset")
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(OUT_DIR, "duration_histogram.png"))
    fig.savefig(os.path.join(OUT_DIR, "duration_histogram.svg"))
    plt.close(fig)


def plot_wordcount_histogram(stats: dict):
    fig, ax = plt.subplots(figsize=(8, 4))
    for label in sorted(set(stats["source"])):
        vals = [v for v, s in zip(stats["word_counts"], stats["source"]) if s == label]
        ax.hist(vals, bins=40, alpha=0.6, label=f"{label} (n={len(vals)})")
    ax.set_xlabel("Word count")
    ax.set_ylabel("Sample count")
    ax.set_title("Transcription Word Count Distribution")
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(OUT_DIR, "wordcount_histogram.png"))
    fig.savefig(os.path.join(OUT_DIR, "wordcount_histogram.svg"))
    plt.close(fig)


def plot_composition(stats: dict):
    from collections import Counter
    counts = Counter(stats["source"])
    labels, values = zip(*sorted(counts.items()))
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = sns.color_palette("muted", len(labels))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%", colors=colors,
        startangle=90, pctdistance=0.75,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Dataset Composition")
    fig.savefig(os.path.join(OUT_DIR, "dataset_composition.png"))
    fig.savefig(os.path.join(OUT_DIR, "dataset_composition.svg"))
    plt.close(fig)


def plot_waveform_samples(fsc, fleurs_list):
    """Plot waveform + mel spectrogram for 3 random samples from the training set."""
    from matplotlib.gridspec import GridSpec
    import torchaudio

    samples: list[tuple[str, np.ndarray, int, str]] = []  # (label, audio, sr, text)

    # Pick 1 from each source's train split
    for ds, prefix in [(fsc, "FSC")] + list(zip(fleurs_list, ["FLEURS fil_ph", "FLEURS ceb_ph"])):
        idx = np.random.RandomState(SEED).randint(0, len(ds["train"]))
        row = ds["train"][idx]
        samples.append((prefix, row["audio"]["array"], row["audio"]["sampling_rate"], row["text"]))

    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(len(samples), 2, figure=fig, hspace=0.6, wspace=0.3)

    for i, (label, audio, sr, text) in enumerate(samples):
        time = np.arange(len(audio)) / sr
        text_short = text[:80] + "..." if len(text) > 80 else text

        # Waveform
        ax_wav = fig.add_subplot(gs[i, 0])
        ax_wav.plot(time, audio, linewidth=0.5, color="steelblue")
        ax_wav.set_xlabel("Time (s)")
        ax_wav.set_ylabel("Amplitude")
        ax_wav.set_title(f"{label}\n{text_short}", fontsize=9)

        # Mel spectrogram
        ax_mel = fig.add_subplot(gs[i, 1])
        mel_transform = torchaudio.transforms.MelSpectrogram(sample_rate=sr, n_fft=1024, n_mels=80)
        mel = mel_transform(torchaudio.functional.resample(
            torch.tensor(audio).float().unsqueeze(0), sr, 16000
        )).squeeze().numpy()
        ax_mel.imshow(np.log1p(mel), aspect="auto", origin="lower", cmap="viridis")
        ax_mel.set_xlabel("Time frames")
        ax_mel.set_ylabel("Mel bins")
        ax_mel.set_title(f"{label} — Mel Spectrogram", fontsize=9)

    fig.suptitle("Sample Waveforms and Mel Spectrograms", fontsize=14, y=1.01)
    fig.savefig(os.path.join(OUT_DIR, "sample_waveforms.png"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT_DIR, "sample_waveforms.svg"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Output directory: {OUT_DIR}")

    fsc, fleurs_list = load_raw()
    stats = collect_stats(fsc, fleurs_list)

    print(f"\nTotal samples: {len(stats['durations'])}")
    print(f"  Duration: min={min(stats['durations']):.1f}s  max={max(stats['durations']):.1f}s  "
          f"mean={np.mean(stats['durations']):.1f}s  median={np.median(stats['durations']):.1f}s")
    print(f"  Words:    min={min(stats['word_counts'])}  max={max(stats['word_counts'])}  "
          f"mean={np.mean(stats['word_counts']):.1f}  median={np.median(stats['word_counts']):.0f}")

    print("\nGenerating plots...")
    plot_duration_histogram(stats)
    print("  ✓ duration_histogram")
    plot_wordcount_histogram(stats)
    print("  ✓ wordcount_histogram")
    plot_composition(stats)
    print("  ✓ dataset_composition")
    plot_waveform_samples(fsc, fleurs_list)
    print("  ✓ sample_waveforms")
    print(f"\nDone. Plots saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
