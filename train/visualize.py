#!/usr/bin/env python3
"""
Generate publication-ready training curves from a completed training run.

Usage:
    python train/visualize.py                          # reads train/output/whisper/
    python train/visualize.py --output-dir /some/path  # custom model dir

Sources (tried in order):
    1. metrics.csv  (if present)
    2. trainer_state.json  from best checkpoint

Output: <output_dir>/plots/training_curves/
"""

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted", context="notebook")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
})


def find_best_checkpoint(output_dir: str) -> str | None:
    """Locate the checkpoint dir referenced as best in trainer_state.json."""
    ckpt_dir = os.path.join(output_dir, "checkpoints")
    if not os.path.isdir(ckpt_dir):
        return None
    for entry in sorted(os.listdir(ckpt_dir), reverse=True):
        sub = os.path.join(ckpt_dir, entry)
        if os.path.isdir(sub) and entry.startswith("checkpoint-"):
            ts_path = os.path.join(sub, "trainer_state.json")
            if os.path.isfile(ts_path):
                return sub
    return None


def load_from_csv(output_dir: str) -> dict | None:
    csv_path = os.path.join(output_dir, "metrics.csv")
    if not os.path.isfile(csv_path):
        return None
    import csv
    data: dict[str, list] = {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            for key, val in row.items():
                if key not in data:
                    data[key] = []
                try:
                    data[key].append(float(val))
                except (ValueError, TypeError):
                    data[key].append(val)
    return data if data else None


def load_from_trainer_state(output_dir: str) -> dict | None:
    ckpt = find_best_checkpoint(output_dir)
    if not ckpt:
        return None
    ts_path = os.path.join(ckpt, "trainer_state.json")
    if not os.path.isfile(ts_path):
        return None
    with open(ts_path) as f:
        state = json.load(f)
    log_history = state.get("log_history", [])
    if not log_history:
        return None

    data: dict[str, list] = {"step": [], "epoch": []}
    all_keys = set()
    for entry in log_history:
        for k in entry:
            all_keys.add(k)
    for k in sorted(all_keys):
        data[k] = []

    for entry in log_history:
        for k in all_keys:
            val = entry.get(k)
            data[k].append(val if val is not None else np.nan)
    return data


def _first_valid(xs, keys):
    for k in keys:
        if k in xs and xs[k] and any(v is not None and not (isinstance(v, float) and np.isnan(v)) for v in xs[k]):
            return k
    return None


def _clean(x, y):
    """Return (x, y) with NaN entries removed."""
    mask = np.isfinite(y) if hasattr(np, "isfinite") else [yy is not None and yy == yy for yy in y]
    return [xv for xv, m in zip(x, y) if m], [yv for yv, m in zip(y, y) if m]


def plot_training_curves(data: dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    step_key = _first_valid(data, ("step", "Step"))
    if not step_key:
        print("No step data found in log history.")
        return

    steps = data[step_key]

    # ── Combined 4-panel figure ──────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Loss
    ax = axes[0, 0]
    loss_key = _first_valid(data, ("loss", "Loss"))
    eval_loss_key = _first_valid(data, ("eval_loss", "eval/loss"))
    if loss_key:
        sx, sy = _clean(steps, data[loss_key])
        ax.plot(sx, sy, linewidth=0.8, alpha=0.7, color="steelblue", label="Train loss")
    if eval_loss_key:
        sx, sy = _clean(steps, data[eval_loss_key])
        ax.plot(sx, sy, "o-", markersize=3, linewidth=1.2, color="darkorange", label="Eval loss")
    ax.set_xlabel("Step")
    ax.set_ylabel("Loss")
    ax.set_title("Loss")
    if loss_key or eval_loss_key:
        ax.legend()

    # WER
    ax = axes[0, 1]
    wer_key = _first_valid(data, ("eval_wer", "eval/wer"))
    if wer_key:
        sx, sy = _clean(steps, data[wer_key])
        ax.plot(sx, sy, "o-", markersize=4, linewidth=1.2, color="crimson")
        best_step = sx[np.argmin(sy)]
        best_val = min(sy)
        ax.axvline(best_step, color="gray", linestyle="--", alpha=0.5)
        ax.annotate(f"Best: {best_val:.2f}% @ step {int(best_step)}",
                    xy=(best_step, best_val), fontsize=8, color="gray")
    ax.set_xlabel("Step")
    ax.set_ylabel("WER (%)")
    ax.set_title("Word Error Rate")

    # CER
    ax = axes[1, 0]
    cer_key = _first_valid(data, ("eval_cer", "eval/cer"))
    if cer_key:
        sx, sy = _clean(steps, data[cer_key])
        ax.plot(sx, sy, "s-", markersize=4, linewidth=1.2, color="darkgreen")
        best_step = sx[np.argmin(sy)]
        best_val = min(sy)
        ax.axvline(best_step, color="gray", linestyle="--", alpha=0.5)
        ax.annotate(f"Best: {best_val:.2f}% @ step {int(best_step)}",
                    xy=(best_step, best_val), fontsize=8, color="gray")
    ax.set_xlabel("Step")
    ax.set_ylabel("CER (%)")
    ax.set_title("Character Error Rate")

    # Learning rate
    ax = axes[1, 1]
    lr_key = _first_valid(data, ("learning_rate", "learning_rate"))
    if lr_key:
        sx, sy = _clean(steps, data[lr_key])
        ax.plot(sx, sy, linewidth=1.2, color="purple")
        ax.fill_between(sx, 0, sy, alpha=0.1, color="purple")
    ax.set_xlabel("Step")
    ax.set_ylabel("LR")
    ax.set_title("Learning Rate Schedule")

    fig.suptitle("Training Curves — Whisper-small Fine-tuning", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "training_curves.png"))
    fig.savefig(os.path.join(out_dir, "training_curves.svg"))
    plt.close(fig)
    print("  ✓ training_curves.png/.svg")

    # ── Gradient norm ────────────────────────────────────────
    gn_key = _first_valid(data, ("grad_norm", "grad_norm"))
    if gn_key:
        fig, ax = plt.subplots(figsize=(8, 3))
        sx, sy = _clean(steps, data[gn_key])
        ax.plot(sx, sy, linewidth=0.7, color="dimgray", alpha=0.8)
        ax.set_xlabel("Step")
        ax.set_ylabel("Gradient norm")
        ax.set_title("Gradient Norm")
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "gradient_norm.png"))
        fig.savefig(os.path.join(out_dir, "gradient_norm.svg"))
        plt.close(fig)
        print("  ✓ gradient_norm.png/.svg")

    # ── Final test metrics bar (from test_results.json) ─────
    test_path = os.path.join(output_dir, "test_results.json")
    if os.path.isfile(test_path):
        with open(test_path) as f:
            test = json.load(f)
        fig, ax = plt.subplots(figsize=(5, 3))
        metrics_bar = {"WER": test.get("eval_wer", 0), "CER": test.get("eval_cer", 0)}
        bars = ax.bar(list(metrics_bar.keys()), list(metrics_bar.values()), color=["crimson", "darkgreen"], width=0.4)
        for bar, val in zip(bars, metrics_bar.values()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.2f}%",
                    ha="center", fontsize=11, fontweight="bold")
        ax.set_ylabel("%")
        ax.set_title("Final Test Set Metrics")
        ax.set_ylim(0, max(metrics_bar.values()) * 1.3 + 2)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "test_metrics.png"))
        fig.savefig(os.path.join(out_dir, "test_metrics.svg"))
        plt.close(fig)
        print("  ✓ test_metrics.png/.svg")


def main():
    parser = argparse.ArgumentParser(description="Generate training curve plots")
    parser.add_argument("--model-dir", type=str, default="train/output/whisper",
                        help="Path to trained model output (default: train/output/whisper)")
    args = parser.parse_args()

    global output_dir
    output_dir = args.model_dir
    out_dir = os.path.join(output_dir, "plots", "training_curves")

    data = load_from_csv(output_dir)
    if data:
        print(f"Loaded metrics from metrics.csv ({len(data.get('step', []))} rows)")
    else:
        data = load_from_trainer_state(output_dir)
        if data:
            print(f"Loaded metrics from trainer_state.json ({len(data.get('step', []))} log entries)")
        else:
            print(f"ERROR: No metrics found in {output_dir}/metrics.csv or trainer_state.json")
            sys.exit(1)

    print(f"Saving plots to {out_dir}/")
    plot_training_curves(data, out_dir)
    print("Done.")


if __name__ == "__main__":
    main()
