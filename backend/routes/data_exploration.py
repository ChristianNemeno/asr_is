import json
import os
import re
from collections import Counter

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/training", tags=["data-exploration"])

_cache: dict | None = None


def _load_fleurs_manifest() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "fleurs_samples", "manifest.json")
    path = os.path.normpath(path)
    if not os.path.isfile(path):
        return {}
    with open(path) as f:
        manifest = json.load(f)

    durations = [m["duration_sec"] for m in manifest]
    word_counts = [len(m["label"].split()) for m in manifest]
    languages = ["Tagalog" if m["language"] == "Tagalog" else "Cebuano" for m in manifest]

    return {
        "durations": durations,
        "word_counts": word_counts,
        "languages": languages,
        "source": "fleurs_samples/manifest.json",
    }


def _make_histogram(values: list[float], bin_count: int = 12) -> list[dict]:
    if not values:
        return []
    vmin = min(values)
    vmax = max(values)
    if vmin == vmax:
        return [{"range": f"{vmin:.1f}", "count": len(values)}]
    step = (vmax - vmin) / bin_count
    bins = []
    for i in range(bin_count):
        lo = vmin + i * step
        hi = vmin + (i + 1) * step
        count = sum(1 for v in values if lo <= v < hi)
        if i == bin_count - 1:
            count += sum(1 for v in values if v == vmax)
        label = f"{lo:.0f}-{hi:.0f}" if step >= 1 else f"{lo:.1f}-{hi:.1f}"
        bins.append({"range": label, "count": count})
    return bins


@router.get("/data-exploration")
async def get_data_exploration():
    global _cache
    if _cache is not None:
        return _cache

    raw = _load_fleurs_manifest()

    if not raw:
        return JSONResponse({"error": "manifest.json not found"}, status_code=404)

    durations = _make_histogram(raw["durations"])
    word_counts = _make_histogram(raw["word_counts"])

    _cache = {
        "source": raw["source"],
        "total_samples": len(raw["durations"]),
        "durations": durations,
        "word_counts": word_counts,
        "languages": raw["languages"],
    }
    return _cache
