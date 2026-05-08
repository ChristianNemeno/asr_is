#!/usr/bin/env python3
"""Generate dataset split diagrams for school reporting."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = "train/output/plots/splits"

# ── Approximate post-filter counts ──────────────────────────────
# FSC: ~274k raw × ~0.75 survive filtering ≈ ~200k; split ~81% / ~9% / ~10%
# FLEURS: ~1000 train, ~400 val, ~400 test per language
DATA = {
    "FSC (filtered)": {"train": 165_000, "validation": 18_000, "test": 20_000, "total": 203_000},
    "FLEURS fil_ph":  {"train": 1_000,   "validation": 400,    "test": 400,    "total": 1_800},
    "FLEURS ceb_ph":  {"train": 1_000,   "validation": 400,    "test": 400,    "total": 1_800},
}

TOTAL = {s: sum(DATA[src][s] for src in DATA) for s in ["train", "validation", "test"]}
FULL_TOTAL = sum(TOTAL.values())

os.makedirs(OUTPUT_DIR, exist_ok=True)

source_names = list(DATA.keys())
split_names = ["train", "validation", "test"]
display_names = ["Train", "Validation", "Test"]
source_colors = ["#4c72b0", "#55a868", "#c44e52"]
split_colors = ["#8ecae6", "#219ebc", "#023047"]

# ── 1. Grouped bar chart ────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(12, 6))
x = np.arange(len(split_names))
width = 0.25

for i, (src, color) in enumerate(zip(source_names, source_colors)):
    counts = [DATA[src][s] for s in split_names]
    offset = (i - 1) * width
    ax1.bar(x + offset, counts, width, label=src, color=color, edgecolor="white")
    for j, spl in enumerate(split_names):
        val = DATA[src][spl]
        ax1.text(x[j] + offset, val + 300, f"{val:,}",
                 ha="center", va="bottom", fontsize=7, rotation=90)

for j, spl in enumerate(split_names):
    ax1.text(x[j], TOTAL[spl] + 1500, f"Total:\n{TOTAL[spl]:,}",
             ha="center", va="bottom", fontsize=9, fontweight="bold")

ax1.set_ylabel("Number of Samples")
ax1.set_title("Dataset Splits by Source (approximate post-filter counts)", fontsize=14, fontweight="bold")
ax1.set_xticks(x)
ax1.set_xticklabels(display_names, fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3)
ax1.set_ylim(0, max(TOTAL.values()) * 1.15)

fig1.text(0.5, 0.01,
          "FSC filtered: ≥2 words, ≥0.8s | FSC train → 90/10 train/val split | FLEURS: native splits",
          ha="center", fontsize=8, style="italic")
plt.tight_layout(rect=[0, 0.04, 1, 1])
fig1.savefig(os.path.join(OUTPUT_DIR, "bar_splits.png"), dpi=150)
plt.close(fig1)
print("Saved bar_splits.png")

# ── 2. Donut charts (one per split) ─────────────────────────────
fig2, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, (spl, disp) in enumerate(zip(split_names, display_names)):
    ax = axes[idx]
    sizes = [DATA[src][spl] for src in source_names]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct="%1.1f%%", colors=source_colors,
        textprops={"fontsize": 9}, pctdistance=0.6, startangle=90
    )
    centre = plt.Circle((0, 0), 0.68, fc="white", linewidth=0)
    ax.add_artist(centre)
    ax.set_title(f"{disp}\n({TOTAL[spl]:,} total)", fontsize=12, fontweight="bold", pad=15)

fig2.legend(wedges, [f"{src}\n({DATA[src]['total']:,})" for src in source_names],
            loc="lower center", ncol=3, fontsize=9, title="Sources (total samples)", title_fontsize=10)
plt.tight_layout(rect=[0, 0.14, 1, 1])
fig2.savefig(os.path.join(OUTPUT_DIR, "donut_splits.png"), dpi=150)
plt.close(fig2)
print("Saved donut_splits.png")

# ── 3. Overall split pie ────────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(8, 8))
pie_total = [TOTAL[s] for s in split_names]
wedges, texts, autotexts = ax3.pie(
    pie_total, labels=display_names, autopct="%1.1f%%",
    colors=split_colors, textprops={"fontsize": 11}, startangle=90,
    explode=(0.02, 0.02, 0.02)
)
for at in autotexts:
    at.set_fontweight("bold")
ax3.set_title(f"Overall Dataset Split Distribution\n({FULL_TOTAL:,} total samples)",
              fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
fig3.savefig(os.path.join(OUTPUT_DIR, "overall_split.png"), dpi=150)
plt.close(fig3)
print("Saved overall_split.png")

# ── 4. Summary dashboard ───────────────────────────────────────
fig4 = plt.figure(figsize=(16, 10))
gs = fig4.add_gridspec(2, 3, hspace=0.4, wspace=0.45)

# Bar chart (top left)
ax_bar = fig4.add_subplot(gs[0, 0])
for i, (src, color) in enumerate(zip(source_names, source_colors)):
    counts = [DATA[src][s] for s in split_names]
    offset = (i - 1) * width
    ax_bar.bar(x + offset, counts, width, label=src, color=color, edgecolor="white")
    for j, spl in enumerate(split_names):
        ax_bar.text(x[j] + offset, DATA[src][spl] + 200,
                    f"{DATA[src][spl]:,}", ha="center", va="bottom", fontsize=6, rotation=90)
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(display_names, fontsize=9)
ax_bar.set_title("Samples per Split by Source", fontsize=11, fontweight="bold")
ax_bar.legend(fontsize=7, loc="upper left")

# Source composition stacked bar (top middle)
ax_stack = fig4.add_subplot(gs[0, 1])
bottom = np.zeros(3)
for i, (src, color) in enumerate(zip(source_names, source_colors)):
    counts = [DATA[src][s] for s in split_names]
    ax_stack.bar(display_names, counts, bottom=bottom, label=src, color=color, edgecolor="white")
    bottom += np.array(counts)
for j, spl in enumerate(split_names):
    ax_stack.text(j, TOTAL[spl] / 2, f"{TOTAL[spl]:,}", ha="center", va="center", fontsize=9, fontweight="bold")
ax_stack.set_title("Stacked Split Composition", fontsize=11, fontweight="bold")
ax_stack.legend(fontsize=6)

# Overall pie (top right)
ax_pie = fig4.add_subplot(gs[0, 2])
ax_pie.pie(pie_total, labels=display_names, autopct="%1.1f%%",
           colors=split_colors, textprops={"fontsize": 10}, startangle=90)
ax_pie.set_title(f"Overall Distribution\n({FULL_TOTAL:,} total)", fontsize=11, fontweight="bold")

# Source breakdown donuts (bottom row, 3 donuts)
for idx, (spl, disp) in enumerate(zip(split_names, display_names)):
    ax = fig4.add_subplot(gs[1, idx])
    sizes = [DATA[src][spl] for src in source_names]
    wedges, _, ats = ax.pie(sizes, autopct="%1.1f%%", colors=source_colors,
                             textprops={"fontsize": 8}, pctdistance=0.7, startangle=90)
    centre = plt.Circle((0, 0), 0.65, fc="white", linewidth=0)
    ax.add_artist(centre)
    ax.set_title(f"{disp}\n({TOTAL[spl]:,})", fontsize=11, fontweight="bold")

fig4.suptitle("ASR Dataset Split Report — Cebuano/Filipino Speech\n"
              "Sources: FSC (Filipino Speech Corpus) + FLEURS (fil_ph, ceb_ph)\n"
              "FSC filtered (≥2 words, ≥0.8s duration). FSC train → 90/10 train/validation split.",
              fontsize=10, y=0.99)

plt.savefig(os.path.join(OUTPUT_DIR, "summary_dashboard.png"), dpi=150, bbox_inches="tight")
plt.close(fig4)
print("Saved summary_dashboard.png")

# ── 5. Print counts table ───────────────────────────────────────
print(f"\n{'='*60}")
print(f"  DATASET SPLIT COUNTS (approximate post-filter)")
print(f"{'='*60}")
print(f"  {'Source':<24} {'Train':>10} {'Val':>10} {'Test':>10} {'Total':>10}")
print(f"  {'-'*24} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
for src in source_names:
    print(f"  {src:<24} {DATA[src]['train']:>10,} {DATA[src]['validation']:>10,} "
          f"{DATA[src]['test']:>10,} {DATA[src]['total']:>10,}")
print(f"  {'-'*24} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
print(f"  {'TOTAL':<24} {TOTAL['train']:>10,} {TOTAL['validation']:>10,} "
      f"{TOTAL['test']:>10,} {FULL_TOTAL:>10,}")
print(f"{'='*60}\n")
print(f"All plots saved to {OUTPUT_DIR}/")
print(f"  - bar_splits.png         (grouped bar chart)")
print(f"  - donut_splits.png       (donut charts per split)")
print(f"  - overall_split.png      (overall pie chart)")
print(f"  - summary_dashboard.png  (consolidated report)")
