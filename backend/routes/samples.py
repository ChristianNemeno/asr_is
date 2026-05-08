import json
import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/samples", tags=["samples"])

SAMPLES_DIR = os.path.join("..", "fleurs_samples")
MANIFEST_PATH = os.path.join(SAMPLES_DIR, "manifest.json")

_manifest_cache: list[dict] | None = None


def _load_manifest() -> list[dict]:
    global _manifest_cache
    if _manifest_cache is None:
        if not os.path.isfile(MANIFEST_PATH):
            return []
        with open(MANIFEST_PATH) as f:
            _manifest_cache = json.load(f)
    return _manifest_cache


@router.get("")
async def list_samples():
    manifest = _load_manifest()
    return [
        {
            "filename": m["filename"],
            "language": m["language"],
            "language_code": m.get("language_code", ""),
            "label": m["label"],
            "duration_sec": m["duration_sec"],
            "url": f"/api/samples/audio/{m['filename']}",
        }
        for m in manifest
    ]


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.isfile(path):
        return JSONResponse({"error": "file not found"}, status_code=404)
    return FileResponse(path, media_type="audio/wav")
