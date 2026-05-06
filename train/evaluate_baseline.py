#!/usr/bin/env python3
"""
Evaluate zero-shot (baseline) performance of Whisper and XLS-R
on Filipino speech test sets. Run before fine-tuning to establish
a lower bound.

Usage:
    # Edit config.py to choose dataset, then:
    python evaluate_baseline.py
"""

import json
import torch
import evaluate
from tqdm import tqdm

from train.config import config
from train.preprocess import load_and_prepare_datasets

wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")


def evaluate_whisper_baseline(dataset, model_id="openai/whisper-small"):
    from transformers import WhisperProcessor, WhisperForConditionalGeneration

    processor = WhisperProcessor.from_pretrained(model_id)
    model = WhisperForConditionalGeneration.from_pretrained(model_id)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    predictions, references = [], []
    for sample in tqdm(dataset["test"], desc="Whisper baseline"):
        audio = sample["audio"]
        input_features = processor.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"],
            return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            pred_ids = model.generate(input_features)

        pred = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)[0]
        ref = sample["text"]

        predictions.append(pred)
        references.append(ref)

    wer = 100 * wer_metric.compute(predictions=predictions, references=references)
    cer = 100 * cer_metric.compute(predictions=predictions, references=references)
    return {"wer": wer, "cer": cer}


def evaluate_xlsr_baseline(dataset, model_id="facebook/wav2vec2-xls-r-300m"):
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

    processor = Wav2Vec2Processor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    predictions, references = [], []
    for sample in tqdm(dataset["test"], desc="XLS-R baseline"):
        audio = sample["audio"]
        inputs = processor(
            audio["array"], sampling_rate=16000,
            return_tensors="pt", padding=True
        ).to(device)

        with torch.no_grad():
            logits = model(**inputs).logits

        pred_ids = torch.argmax(logits, dim=-1)[0]
        pred = processor.decode(pred_ids)
        ref = sample["text"]

        predictions.append(pred)
        references.append(ref)

    wer = 100 * wer_metric.compute(predictions=predictions, references=references)
    cer = 100 * cer_metric.compute(predictions=predictions, references=references)
    return {"wer": wer, "cer": cer}


def main():
    print(f"Loading {config.dataset} dataset...")
    dataset = load_and_prepare_datasets(config)
    print()

    import os
    os.makedirs("results", exist_ok=True)

    results = {}

    print("--- Whisper-small baseline ---")
    whisper_results = evaluate_whisper_baseline(dataset)
    print(f"WER: {whisper_results['wer']:.2f}%")
    print(f"CER: {whisper_results['cer']:.2f}%")
    results["whisper_small"] = whisper_results

    print("\n--- XLS-R 300M baseline ---")
    xlsr_results = evaluate_xlsr_baseline(dataset)
    print(f"WER: {xlsr_results['wer']:.2f}%")
    print(f"CER: {xlsr_results['cer']:.2f}%")
    results["xlsr_300m"] = xlsr_results

    path = f"results/baseline_{config.dataset}.json"
    with open(path, "w") as f:
        json.dump({k: {"wer": v["wer"], "cer": v["cer"]} for k, v in results.items()}, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
