#!/usr/bin/env python3
"""
Pick N random test samples, transcribe with baseline + fine-tuned,
compute per-sample WER/CER, save comparison CSV.

Usage:
    python train/sample_comparison.py                  # 20 samples, seed 42
    python train/sample_comparison.py --samples 10     # custom count
"""

import argparse
import csv
import os
import random
import re
import sys
import torch
import evaluate
from tqdm import tqdm
from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset
from transformers import WhisperProcessor, WhisperForConditionalGeneration

sys.path.insert(0, os.path.dirname(__file__))

SEED = 42
OUTPUT_DIR = "train/output/whisper"


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

    fleurs_langs = {"fil_ph": "tagalog", "ceb_ph": "cebuano"}
    for lang in ["fil_ph", "ceb_ph"]:
        print(f"Loading FLEURS {lang}...")
        fl = load_dataset("google/fleurs", lang, trust_remote_code=True)
        fl = fl.cast_column("audio", Audio(sampling_rate=16000))
        fl = fl.rename_column("transcription", "text")
        fl = fl.map(lambda b: {"text": norm(b["text"])})
        fl = fl.map(lambda b: {"language": fleurs_langs[lang]})
        fl = fl.select_columns(["audio", "text", "language"])
        datasets.append(fl)

    ds = DatasetDict({
        s: concatenate_datasets([d[s] for d in datasets])
        for s in ["train", "validation", "test"]
    })
    return ds


def main():
    parser = argparse.ArgumentParser(
        description="Compare baseline vs fine-tuned on random test samples"
    )
    parser.add_argument(
        "--samples", type=int, default=20,
        help="Number of random test samples (default: 20)"
    )
    parser.add_argument(
        "--model", type=str, default="train/output/whisper",
        help="Fine-tuned model path (default: train/output/whisper)"
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # ── Load test set ──────────────────────────────────────────
    ds = load_test_dataset()
    test = ds["test"]
    total = len(test)
    n = min(args.samples, total)
    indices = sorted(random.Random(SEED).sample(range(total), n))
    print(f"Sampled {n} from {total} test samples (seed={SEED})")

    # ── Load models ────────────────────────────────────────────
    print("\nLoading baseline model: openai/whisper-small ...")
    processor_base = WhisperProcessor.from_pretrained("openai/whisper-small")
    model_base = WhisperForConditionalGeneration.from_pretrained(
        "openai/whisper-small"
    ).to(device)
    model_base.eval()

    print(f"Loading fine-tuned model: {args.model} ...")
    processor_ft = WhisperProcessor.from_pretrained(args.model)
    model_ft = WhisperForConditionalGeneration.from_pretrained(args.model).to(device)
    model_ft.eval()

    # ── Per-sample inference ───────────────────────────────────
    wer_m = evaluate.load("wer")
    cer_m = evaluate.load("cer")

    rows = []

    for idx in tqdm(indices, desc="Evaluating"):
        sample = test[idx]
        audio = sample["audio"]
        ref = sample["text"]
        lang = sample.get("language") or "tagalog"

        input_features = processor_base.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            pred_base = model_base.generate(input_features)
            pred_ft = model_ft.generate(input_features)

        text_base = norm(processor_base.tokenizer.batch_decode(
            pred_base, skip_special_tokens=True
        )[0])
        text_ft = norm(processor_ft.tokenizer.batch_decode(
            pred_ft, skip_special_tokens=True
        )[0])

        bw = wer_m.compute(predictions=[text_base], references=[ref])
        bc = cer_m.compute(predictions=[text_base], references=[ref])
        fw = wer_m.compute(predictions=[text_ft], references=[ref])
        fc = cer_m.compute(predictions=[text_ft], references=[ref])
        rows.append({
            "reference": ref,
            "language": lang,
            "baseline_prediction": text_base,
            "baseline_wer": round(bw * 100, 2) if bw is not None else 0.0,
            "baseline_cer": round(bc * 100, 2) if bc is not None else 0.0,
            "finetuned_prediction": text_ft,
            "finetuned_wer": round(fw * 100, 2) if fw is not None else 0.0,
            "finetuned_cer": round(fc * 100, 2) if fc is not None else 0.0,
        })

    # ── Print table ────────────────────────────────────────────
    print(f"\n{'='*100}")
    print(f"{'#':>3} {'lang':10} {'baseline WER':>12} {'baseline CER':>12} {'fine-tuned WER':>14} {'fine-tuned CER':>14} {'Δ WER':>6}")
    print(f"{'='*100}")
    def f(v):
        return float(v) if v is not None else 0.0

    for i, r in enumerate(rows, 1):
        bw = f(r["baseline_wer"])
        bc = f(r["baseline_cer"])
        fw = f(r["finetuned_wer"])
        fc = f(r["finetuned_cer"])
        delta = bw - fw
        print(f"{i:>3} {str(r['language'] or ''):10} {bw:>10.1f}% {bc:>10.1f}% {fw:>12.1f}% {fc:>12.1f}% {delta:>+5.1f}%")
    print(f"{'='*100}")
    avgs = [sum(f(r[k]) for r in rows) / len(rows) for k in ("baseline_wer", "baseline_cer", "finetuned_wer", "finetuned_cer")]
    print(f"{'AVG':>3} {'':10} {avgs[0]:>10.1f}% {avgs[1]:>10.1f}% {avgs[2]:>12.1f}% {avgs[3]:>12.1f}% {avgs[0] - avgs[2]:>+5.1f}%")

    # ── Save CSV ───────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "sample_comparison.csv")
    fieldnames = [
        "rank", "language", "reference",
        "baseline_prediction", "baseline_wer", "baseline_cer",
        "finetuned_prediction", "finetuned_wer", "finetuned_cer",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for i, r in enumerate(rows, 1):
            r["rank"] = i
            writer.writerow(r)
    print(f"\nSaved to {csv_path}")


if __name__ == "__main__":
    main()
