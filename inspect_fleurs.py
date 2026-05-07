#!/usr/bin/env python3
"""
Export 20 FLEURS samples per language (fil_ph, ceb_ph) as WAV files
and print a table so you can listen and compare audio vs label.
"""

import os
import random
import subprocess
import sys

import soundfile as sf
from datasets import load_dataset

SEED = 42
N_SAMPLES = 20
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fleurs_samples")

os.makedirs(OUT_DIR, exist_ok=True)
random.seed(SEED)


def export_samples(lang: str) -> list[dict]:
    ds = load_dataset("google/fleurs", lang, trust_remote_code=True, split="train")
    indices = random.sample(range(len(ds)), N_SAMPLES)
    samples = []
    for i, idx in enumerate(sorted(indices)):
        row = ds[idx]
        path = os.path.join(OUT_DIR, f"{lang}_{i:02d}.wav")
        sf.write(path, row["audio"]["array"], row["audio"]["sampling_rate"])
        dur = len(row["audio"]["array"]) / row["audio"]["sampling_rate"]
        samples.append({"i": i, "path": path, "label": row["transcription"], "dur": dur})
    return samples


def main():
    for lang in ["fil_ph", "ceb_ph"]:
        print(f"\n{'='*70}")
        print(f"  {lang.upper()} — {N_SAMPLES} samples")
        print(f"{'='*70}")
        print(f"{'#':>3}  {'dur':>5}  {'label'}")
        print(f"{'-'*3}  {'-'*5}  {'-'*55}")

        samples = export_samples(lang)
        for s in samples:
            print(f"{s['i']:>3}  {s['dur']:4.1f}s  {s['label']}")

        print(f"\nFiles saved to {OUT_DIR}/")

    print(f"\nListen with:  aplay {OUT_DIR}/fil_ph_00.wav")
    print(f"              aplay {OUT_DIR}/ceb_ph_00.wav")

    # Auto-play if --play flag passed
    if "--play" in sys.argv:
        for lang in ["fil_ph", "ceb_ph"]:
            for i in range(N_SAMPLES):
                path = os.path.join(OUT_DIR, f"{lang}_{i:02d}.wav")
                print(f"\n► {lang} #{i} — ENTER to play, q to skip language")
                if input().strip().lower() == "q":
                    break
                subprocess.run(["aplay", path], stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
