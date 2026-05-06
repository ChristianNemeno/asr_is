#!/usr/bin/env python3
"""
Run on Google Colab. Upload this file + the train/ folder to
Google Drive, then open a Colab notebook and paste:

    !pip install transformers datasets>=3.0,<4.0 evaluate jiwer \
               soundfile librosa accelerate tensorboard torchcodec
    !cp -r /content/drive/MyDrive/asr_is/train ./train
    !cp /content/drive/MyDrive/asr_is/run_on_colab.py .
    from run_on_colab import main; main()

Or run this file directly:
    !python /content/drive/MyDrive/asr_is/run_on_colab.py
"""

import os
import sys
import torch

# ── config (edit these before uploading) ──────────────────────────────

DATASET = "all"            # "fsc" | "fleurs_ceb" | "fleurs_fil" | "all"
MODEL_ID = "openai/whisper-small"  # or "facebook/wav2vec2-xls-r-300m"
BATCH_SIZE = 8             # T4 has 16 GB — use larger batch than local
GRAD_ACCUM = 2

# ── training ──────────────────────────────────────────────────────────

def main():
    # Mount Drive
    from google.colab import drive
    drive.mount("/content/drive")

    # Add Drive to Python path so we can import train/
    project_dir = "/content/drive/MyDrive/asr_is"
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Override config
    from train.config import TrainConfig
    cfg = TrainConfig(
        dataset=DATASET,
        model_id=MODEL_ID,
        batch_size=BATCH_SIZE,
        grad_accum=GRAD_ACCUM,
    )

    # Pick and run the right trainer
    if "whisper" in cfg.model_id.lower():
        from train.train_whisper import main as train_main
    else:
        from train.train_wav2vec2 import main as train_main

    # Patch config singleton
    import train.config as config_module
    config_module.config = cfg

    train_main()
