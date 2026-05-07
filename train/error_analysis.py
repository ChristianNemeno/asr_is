#!/usr/bin/env python3
"""
Error analysis on the test set using a fine-tuned model.

Usage:
    python train/error_analysis.py
    python train/error_analysis.py --model-dir train/output/whisper

Output:
    train/output/plots/error_analysis/    — plots (PNG + SVG)
    <model_dir>/sample_transcriptions.csv — best/worst/median samples
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset
from tqdm import tqdm
from transformers import WhisperProcessor, WhisperForConditionalGeneration

sys.path.insert(0, os.path.dirname(__file__))

SEED = 42
PLOT_DIR = os.path.join("train", "output", "plots", "error_analysis")

sns.set_theme(style="whitegrid", palette="muted", context="notebook")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})


def norm(text: str) -> str:
    t = text.lower()
    t = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def load_test_dataset(include_metadata: bool = False):
    """Load FSC + FLEURS test split, optionally preserving language metadata."""
    datasets = []

    print("Loading FSC...")
    fsc = load_dataset("sapinsapin/filipinospeechcorpus")
    fsc = fsc.cast_column("audio", Audio(sampling_rate=16000))
    fsc = fsc.filter(lambda x: x["num_words"] >= 2 and x["duration"] >= 0.8)
    fsc = fsc.rename_column("sentence", "text")
    fsc = fsc.map(lambda b: {"text": norm(b["text"])})
    fsc = fsc.select_columns(["audio", "text"])
    tt = fsc["train"].train_test_split(test_size=0.1, seed=SEED)
    fsc = DatasetDict({"train": tt["train"], "validation": tt["test"], "test": fsc["test"]})
    if include_metadata:
        fsc = fsc.map(lambda b: {"language": "tagalog"})
    datasets.append(fsc)

    fleurs_langs = {"fil_ph": "tagalog", "ceb_ph": "cebuano"}
    for lang in ["fil_ph", "ceb_ph"]:
        print(f"Loading FLEURS {lang}...")
        fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
        fl = fl.cast_column("audio", Audio(sampling_rate=16000))
        fl = fl.rename_column("transcription", "text")
        fl = fl.map(lambda b: {"text": norm(b["text"])})
        fl = fl.select_columns(["audio", "text"])
        if include_metadata:
            fl = fl.map(lambda b: {"language": fleurs_langs[lang]})
        datasets.append(fl)

    ds = DatasetDict({s: concatenate_datasets([d[s] for d in datasets]) for s in ["train", "validation", "test"]})
    return ds


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    from jiwer import wer
    return wer(reference, hypothesis)


def char_error_rate(reference: str, hypothesis: str) -> float:
    from jiwer import cer
    return cer(reference, hypothesis)


def error_breakdown(ref: str, hyp: str) -> dict:
    from jiwer import process_words
    out = process_words(ref, hyp)
    return {
        "substitutions": out.substitutions,
        "deletions": out.deletions,
        "insertions": out.insertions,
        "hits": out.hits,
    }


def run_inference(model_dir: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Loading model from {model_dir}")

    processor = WhisperProcessor.from_pretrained(model_dir)
    model = WhisperForConditionalGeneration.from_pretrained(model_dir).to(device)

    ds = load_test_dataset(include_metadata=True)
    print(f"Test samples: {len(ds['test'])}")

    results: list[dict] = []
    total_s, total_d, total_i, total_h = 0, 0, 0, 0
    lang_wer: dict[str, list[float]] = defaultdict(list)

    for sample in tqdm(ds["test"], desc="Inference"):
        audio = sample["audio"]
        input_features = processor.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            pred_ids = model.generate(input_features)
        pred_text = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)[0]
        ref_text = sample["text"]
        lang = sample.get("language", "unknown")

        wer_val = word_error_rate(ref_text, pred_text)
        cer_val = char_error_rate(ref_text, pred_text)
        eb = error_breakdown(ref_text, pred_text)

        total_s += eb["substitutions"]
        total_d += eb["deletions"]
        total_i += eb["insertions"]
        total_h += eb["hits"]

        lang_wer[lang].append(wer_val)

        results.append({
            "reference": ref_text,
            "prediction": pred_text,
            "wer": wer_val,
            "cer": cer_val,
            "language": lang,
            "substitutions": eb["substitutions"],
            "deletions": eb["deletions"],
            "insertions": eb["insertions"],
            "hits": eb["hits"],
        })

    return results, {"total_s": total_s, "total_d": total_d, "total_i": total_i, "total_h": total_h}, lang_wer


def plot_wer_distribution(results: list[dict]):
    wers = [r["wer"] for r in results]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.hist(wers, bins=40, color="crimson", alpha=0.7, edgecolor="white")
    mean_wer = np.mean(wers)
    median_wer = np.median(wers)
    ax.axvline(mean_wer, color="black", linestyle="--", linewidth=1, label=f"Mean WER: {mean_wer:.1%}")
    ax.axvline(median_wer, color="gray", linestyle=":", linewidth=1, label=f"Median WER: {median_wer:.1%}")
    ax.set_xlabel("WER")
    ax.set_ylabel("Sample count")
    ax.set_title("Per-Sample WER Distribution")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "wer_distribution.png"))
    fig.savefig(os.path.join(PLOT_DIR, "wer_distribution.svg"))
    plt.close(fig)
    print("  ✓ wer_distribution.png/.svg")


def plot_error_breakdown(totals: dict):
    categories = ["Substitutions", "Deletions", "Insertions", "Hits"]
    values = [totals["total_s"], totals["total_d"], totals["total_i"], totals["total_h"]]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#95a5a6"]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(categories, values, color=colors, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.02,
                str(val), ha="center", fontsize=10)
    ax.set_ylabel("Count")
    ax.set_title("Aggregate Error Breakdown (S/D/I/H)")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "error_breakdown.png"))
    fig.savefig(os.path.join(PLOT_DIR, "error_breakdown.svg"))
    plt.close(fig)
    print("  ✓ error_breakdown.png/.svg")


def plot_per_language(lang_wer: dict[str, list[float]]):
    if len(lang_wer) <= 1:
        print("  (skipped — only one language in test set)")
        return

    fig, ax = plt.subplots(figsize=(6, 3.5))
    positions = np.arange(len(lang_wer))
    labels = sorted(lang_wer.keys())
    means = [np.mean(lang_wer[l]) for l in labels]
    bar_colors = sns.color_palette("muted", len(labels))

    bars = ax.bar(labels, [m * 100 for m in means], color=bar_colors, width=0.4)
    for bar, mean_val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{mean_val * 100:.1f}%", ha="center", fontsize=10, fontweight="bold")

    ax.set_ylabel("WER (%)")
    ax.set_title("WER by Language")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "wer_by_language.png"))
    fig.savefig(os.path.join(PLOT_DIR, "wer_by_language.svg"))
    plt.close(fig)
    print("  ✓ wer_by_language.png/.svg")


def save_transcriptions_csv(results: list[dict], output_dir: str):
    sorted_results = sorted(results, key=lambda r: r["wer"])
    n = len(sorted_results)

    # Best 5, worst 5, median 5
    indices = list(range(5)) + list(range(n // 2 - 2, n // 2 + 3)) + list(range(n - 5, n))
    selected = [sorted_results[i] for i in indices]
    # Deduplicate (in case small dataset)
    seen = set()
    unique = []
    for r in selected:
        key = (r["reference"], r["prediction"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    csv_path = os.path.join(output_dir, "sample_transcriptions.csv")
    fieldnames = ["rank", "wer", "cer", "language", "reference", "prediction"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        rank = 1
        for r in unique:
            r["rank"] = rank
            writer.writerow(r)
            rank += 1
    print(f"  ✓ sample_transcriptions.csv ({rank - 1} samples)")


def main():
    parser = argparse.ArgumentParser(description="Error analysis on test set")
    parser.add_argument("--model-dir", type=str, default="train/output/whisper",
                        help="Path to trained model directory")
    args = parser.parse_args()

    if not os.path.isdir(args.model_dir):
        print(f"ERROR: Model directory not found: {args.model_dir}")
        sys.exit(1)

    os.makedirs(PLOT_DIR, exist_ok=True)

    results, totals, lang_wer = run_inference(args.model_dir)

    avg_wer = np.mean([r["wer"] for r in results])
    avg_cer = np.mean([r["cer"] for r in results])
    print(f"\nOverall  WER: {avg_wer:.2%}  CER: {avg_cer:.2%}")
    for lang, wers in sorted(lang_wer.items()):
        print(f"  {lang:10s} WER: {np.mean(wers):.2%}  (n={len(wers)})")

    print(f"\nSaving plots to {PLOT_DIR}/")
    plot_wer_distribution(results)
    plot_error_breakdown(totals)
    plot_per_language(lang_wer)
    save_transcriptions_csv(results, args.model_dir)

    # Also save a full JSON for reproducibility
    json_path = os.path.join(args.model_dir, "error_analysis.json")
    summary = {
        "avg_wer": avg_wer,
        "avg_cer": avg_cer,
        "per_language": {lang: {"mean_wer": np.mean(wers), "n": len(wers)} for lang, wers in lang_wer.items()},
        "error_breakdown": totals,
        "n_samples": len(results),
    }
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, default=float)
    print(f"  ✓ error_analysis.json")

    print("Done.")


if __name__ == "__main__":
    main()
