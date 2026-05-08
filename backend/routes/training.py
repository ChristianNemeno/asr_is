import csv
import json
import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/training", tags=["training"])

OUTPUT_DIR = os.path.join("..", "train", "output", "whisper")


def _read_json(filename: str) -> dict:
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(path):
        return {}
    with open(path) as f:
        return json.load(f)


@router.get("/models")
async def get_models():
    test = _read_json("test_results.json")
    error = _read_json("error_analysis.json")
    return {
        "baseline": {
            "id": "openai/whisper-small",
            "parameters": 244000000,
            "architecture": "WhisperForConditionalGeneration",
            "task": "transcribe",
        },
        "finetuned": {
            "id": "whisper-small-cebuano",
            "test_wer": round(test.get("eval_wer", 0), 2),
            "test_cer": round(test.get("eval_cer", 0), 2),
            "train_steps": 5000,
            "dataset": "FSC + FLEURS (fil_ph, ceb_ph)",
            "per_language": error.get("per_language", {}),
        },
    }


@router.get("/hyperparams")
async def get_hyperparams():
    return {
        "base_model": "openai/whisper-small",
        "parameters": 244000000,
        "per_device_train_batch_size": 8,
        "gradient_accumulation_steps": 2,
        "effective_batch_size": 16,
        "learning_rate": 1e-5,
        "warmup_steps": 500,
        "max_steps": 5000,
        "gradient_checkpointing": True,
        "mixed_precision": "fp16",
        "generation_max_length": 225,
        "seed": 42,
    }


@router.get("/metrics")
async def get_metrics():
    test = _read_json("test_results.json")
    error = _read_json("error_analysis.json")
    return {
        "test_wer": round(test.get("eval_wer", 0), 2),
        "test_cer": round(test.get("eval_cer", 0), 2),
        "train_steps": 5000,
        "per_language": error.get("per_language", {}),
        "error_breakdown": error.get("error_breakdown", {}),
        "n_samples": error.get("n_samples", 0),
    }


@router.get("/curves")
async def get_curves():
    csv_path = os.path.join(OUTPUT_DIR, "metrics.csv")
    if not os.path.isfile(csv_path):
        return JSONResponse({"error": "metrics.csv not found"}, status_code=404)

    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            parsed = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v) if v else None
                except ValueError:
                    parsed[k] = v
            rows.append(parsed)
    return rows


@router.get("/samples")
async def get_sample_transcriptions():
    csv_path = os.path.join(OUTPUT_DIR, "sample_transcriptions.csv")
    if not os.path.isfile(csv_path):
        return JSONResponse({"error": "sample_transcriptions.csv not found"}, status_code=404)

    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rows.append({
                "rank": int(row.get("rank", 0)),
                "wer": round(float(row.get("wer", 0)), 2),
                "cer": round(float(row.get("cer", 0)), 2),
                "language": row.get("language", ""),
                "reference": row.get("reference", ""),
                "prediction": row.get("prediction", ""),
            })
    return rows
