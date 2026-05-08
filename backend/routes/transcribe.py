import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from services.model_service import get_model_manager
from services.metrics import compute_metrics, error_breakdown

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    reference: str = Form(None),
):
    manager = get_model_manager()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        baseline = manager.transcribe(tmp_path, "baseline")
        finetuned = manager.transcribe(tmp_path, "finetuned")
    finally:
        os.unlink(tmp_path)

    response = {
        "baseline": {"text": baseline["text"]},
        "finetuned": {"text": finetuned["text"]},
    }

    if reference:
        response["baseline"]["wer"] = round(
            compute_metrics([baseline["text"]], [reference])["wer"], 2
        )
        response["baseline"]["cer"] = round(
            compute_metrics([baseline["text"]], [reference])["cer"], 2
        )
        response["baseline"]["error_breakdown"] = error_breakdown(
            baseline["text"], reference
        )
        response["finetuned"]["wer"] = round(
            compute_metrics([finetuned["text"]], [reference])["wer"], 2
        )
        response["finetuned"]["cer"] = round(
            compute_metrics([finetuned["text"]], [reference])["cer"], 2
        )
        response["finetuned"]["error_breakdown"] = error_breakdown(
            finetuned["text"], reference
        )

    return response
