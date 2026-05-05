"""
Evaluate zero-shot (base) performance of Whisper-small and XLS-R 300M
on the Cebuano test set. Run this locally before training.
"""
import torch
import evaluate
from tqdm import tqdm
from datasets import Audio

from preprocess import load_and_split_dataset, normalize_dataset

wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")


def evaluate_whisper_baseline(dataset):
    from transformers import WhisperProcessor, WhisperForConditionalGeneration

    model_id = "openai/whisper-small"
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
        ref = sample["sentence"]

        predictions.append(pred)
        references.append(ref)

    wer = 100 * wer_metric.compute(predictions=predictions, references=references)
    cer = 100 * cer_metric.compute(predictions=predictions, references=references)
    return {"wer": wer, "cer": cer, "predictions": predictions, "references": references}


def evaluate_xlsr_baseline(dataset):
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

    model_id = "facebook/wav2vec2-xls-r-300m"
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
        ref = sample["sentence"]

        predictions.append(pred)
        references.append(ref)

    wer = 100 * wer_metric.compute(predictions=predictions, references=references)
    cer = 100 * cer_metric.compute(predictions=predictions, references=references)
    return {"wer": wer, "cer": cer, "predictions": predictions, "references": references}


def main():
    print("Loading and preprocessing dataset...")
    dataset = load_and_split_dataset()
    dataset = normalize_dataset(dataset)

    print("\n--- Whisper-small baseline ---")
    whisper_results = evaluate_whisper_baseline(dataset)
    print(f"WER: {whisper_results['wer']:.2f}%")
    print(f"CER: {whisper_results['cer']:.2f}%")

    print("\n--- XLS-R 300M baseline ---")
    xlsr_results = evaluate_xlsr_baseline(dataset)
    print(f"WER: {xlsr_results['wer']:.2f}%")
    print(f"CER: {xlsr_results['cer']:.2f}%")

    import json
    results = {"whisper_small": whisper_results, "xlsr_300m": xlsr_results}
    with open("results/baseline.json", "w") as f:
        json.dump({k: {"wer": v["wer"], "cer": v["cer"]}
                    for k, v in results.items()}, f, indent=2)
    print("\nSaved to results/baseline.json")


if __name__ == "__main__":
    main()
