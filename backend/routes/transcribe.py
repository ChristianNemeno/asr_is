import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Query
from services.model_service import get_model_service
from services.metrics import compute_metrics, error_breakdown

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Query("whisper", description="Model to use: whisper or wav2vec2"),
    reference: str = Form(None, description="Optional reference text for WER/CER"),
):
    model_dir = os.getenv(
        "MODEL_DIR_WHISPER" if model == "whisper" else "MODEL_DIR_WAV2VEC2",
        f"models/{'whisper-small-cebuano' if model == 'whisper' else 'xlsr-300m-cebuano'}"
    )

    service = get_model_service(model_dir)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = service.transcribe(tmp_path)
    finally:
        os.unlink(tmp_path)

    response = {
        "text": result["text"],
        "model_type": result["model_type"],
    }

    if reference:
        metrics = compute_metrics([result["text"]], [reference])
        breakdown = error_breakdown(result["text"], reference)
        response["metrics"] = metrics
        response["error_breakdown"] = breakdown

    return response


@router.get("/health")
async def health():
    return {"status": "ok"}
