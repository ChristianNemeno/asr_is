import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/plots", tags=["plots"])

PLOTS_DIR = os.path.join("..", "train", "output", "plots")


@router.get("/{path:path}")
async def serve_plot(path: str):
    full = os.path.join(PLOTS_DIR, path)
    if not os.path.isfile(full):
        return JSONResponse({"error": "plot not found"}, status_code=404)

    if path.endswith(".svg"):
        return FileResponse(full, media_type="image/svg+xml")
    return FileResponse(full)
