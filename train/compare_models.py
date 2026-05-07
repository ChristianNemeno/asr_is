#!/usr/bin/env python3
"""
Compare baseline (non-fine-tuned) vs fine-tuned Whisper-small
on the Filipino speech test set (FSC + FLEURS).

Usage:
    python train/compare_models.py                              # text comparison
    python train/compare_models.py --plot                       # text + bar chart
    python train/compare_models.py --model train/output/whisper # custom model path
"""

import argparse
import re
import sys
import os

import torch
import evaluate
from tqdm import tqdm
from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset
from transformers import WhisperProcessor, WhisperForConditionalGeneration

sys.path.insert(0, os.path.dirname(__file__))

SEED = 42


def norm(text: str) -> str:
    t = text.lower()
    t = re.sub(r'[\,\?\.\!\-\;\:\"\“\%\‘\”\'\’\«\»\(\)\[\]]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def load_test_dataset() -> DatasetDict:
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
    datasets.append(fsc)

    for lang in ["fil_ph", "ceb_ph"]:
        print(f"Loading FLEURS {lang}...")
        fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
        fl = fl.cast_column("audio", Audio(sampling_rate=16000))
        fl = fl.rename_column("transcription", "text")
        fl = fl.map(lambda b: {"text": norm(b["text"])})
        fl = fl.select_columns(["audio", "text"])
        datasets.append(fl)

    ds = DatasetDict({s: concatenate_datasets([d[s] for d in datasets]) for s in ["train", "validation", "test"]})
    return ds


def evaluate_model(model, processor, dataset, label: str, device: str):
    wer_m = evaluate.load("wer")
    cer_m = evaluate.load("cer")

    predictions, references = [], []
    for sample in tqdm(dataset["test"], desc=f"Evaluating {label}"):
        audio = sample["audio"]
        input_features = processor.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            pred_ids = model.generate(input_features)

        pred = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)[0]
        ref = sample["text"]

        predictions.append(pred)
        references.append(ref)

    wer = 100 * wer_m.compute(predictions=predictions, references=references)
    cer = 100 * cer_m.compute(predictions=predictions, references=references)
    return {"wer": wer, "cer": cer}


def main():
    parser = argparse.ArgumentParser(description="Compare baseline vs fine-tuned Whisper-small")
    parser.add_argument(
        "--model",
        type=str,
        default="train/output/whisper",
        help="Path to fine-tuned model (default: train/output/whisper)",
    )
    parser.add_argument("--plot", action="store_true", help="Generate comparison bar chart")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    ds = load_test_dataset()
    for s in ds:
        print(f"  {s}: {len(ds[s])} samples")

    # ── Baseline ───────────────────────────────────────────────
    print("\n--- Baseline: openai/whisper-small (zero-shot) ---")
    processor_base = WhisperProcessor.from_pretrained("openai/whisper-small")
    model_base = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small").to(device)
    baseline = evaluate_model(model_base, processor_base, ds, "baseline", device)
    print(f"Baseline WER: {baseline['wer']:.2f}%  CER: {baseline['cer']:.2f}%")

    # ── Fine-tuned ─────────────────────────────────────────────
    print(f"\n--- Fine-tuned: {args.model} ---")
    if not os.path.isdir(args.model):
        print(f"ERROR: Model path not found: {args.model}")
        sys.exit(1)

    processor_ft = WhisperProcessor.from_pretrained(args.model)
    model_ft = WhisperForConditionalGeneration.from_pretrained(args.model).to(device)
    finetuned = evaluate_model(model_ft, processor_ft, ds, "fine-tuned", device)
    print(f"Fine-tuned WER: {finetuned['wer']:.2f}%  CER: {finetuned['cer']:.2f}%")

    # ── Comparison ─────────────────────────────────────────────
    wer_delta = baseline["wer"] - finetuned["wer"]
    cer_delta = baseline["cer"] - finetuned["cer"]
    wer_reduction = (wer_delta / baseline["wer"] * 100) if baseline["wer"] > 0 else 0
    cer_reduction = (cer_delta / baseline["cer"] * 100) if baseline["cer"] > 0 else 0

    print("\n" + "=" * 60)
    print("                     WER          CER")
    print("  Baseline     {:8.2f}%    {:8.2f}%".format(baseline["wer"], baseline["cer"]))
    print("  Fine-tuned   {:8.2f}%    {:8.2f}%".format(finetuned["wer"], finetuned["cer"]))
    print("  Delta       {:8.2f}%    {:8.2f}%".format(wer_delta, cer_delta))
    print("  Reduction   {:7.1f}%     {:7.1f}%".format(wer_reduction, cer_reduction))
    print("=" * 60)

    if args.plot:
        plot_comparison(baseline, finetuned, args.model)


def plot_comparison(baseline: dict, finetuned: dict, model_path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out_dir = os.path.join("train", "output", "plots", "model_comparison")
    os.makedirs(out_dir, exist_ok=True)

    metrics = ["WER", "CER"]
    baseline_vals = [baseline["wer"], baseline["cer"]]
    finetuned_vals = [finetuned["wer"], finetuned["cer"]]

    x = np.arange(len(metrics))
    width = 0.3

    fig, ax = plt.subplots(figsize=(5, 4))
    bars1 = ax.bar(x - width / 2, baseline_vals, width, label="Baseline (zero-shot)", color="#3498db")
    bars2 = ax.bar(x + width / 2, finetuned_vals, width, label="Fine-tuned", color="#e74c3c")

    ax.set_ylabel("%")
    ax.set_title("Baseline vs Fine-tuned Whisper-small")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(fontsize=9)

    for bars, vals in [(bars1, baseline_vals), (bars2, finetuned_vals)]:
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

    wer_delta = baseline["wer"] - finetuned["wer"]
    cer_delta = baseline["cer"] - finetuned["cer"]
    fig.text(0.5, 0.01, f"WER reduction: {wer_delta:.1f} pp  |  CER reduction: {cer_delta:.1f} pp",
             ha="center", fontsize=9, color="gray")

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(os.path.join(out_dir, "model_comparison.png"))
    fig.savefig(os.path.join(out_dir, "model_comparison.svg"))
    plt.close(fig)
    print(f"\nComparison chart saved to {out_dir}/")


if __name__ == "__main__":
    main()
