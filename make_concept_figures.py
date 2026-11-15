#!/usr/bin/env python3
"""Conceptual figures: d=2 non-identifiability witness and DELVE pipeline.

The witness geometry is drawn from the formal definitions:
  sigma(z)=1[z1>=0], T(z1,z2)=(-z2,z1), sigma'(z)=1[z2<=0].
Numerical verification (uniform disk) places the disagreement on quadrants
I and III, total probability 1/2.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, FancyBboxPatch, FancyArrowPatch, Circle

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 9,
})

C_ENV1 = "#9ec5e8"   # environment 1
C_ENV0 = "#e8e8e8"   # environment 0
C_DIS = "#c0392b"    # disagreement marker


# ---------------------------------------------------------------------------
# Figure 1: d=2 witness
# ---------------------------------------------------------------------------
def witness_figure():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7))

    def frame(ax, title):
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.55)
        ax.set_aspect("equal")
        ax.axis("off")
        # coordinate axes with arrows
        ax.annotate("", xy=(1.25, 0), xytext=(-1.25, 0),
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="#555555"))
        ax.annotate("", xy=(0, 1.25), xytext=(0, -1.25),
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="#555555"))
        ax.text(1.28, -0.05, r"$z_1$", fontsize=9)
        ax.text(0.06, 1.26, r"$z_2$", fontsize=9)
        ax.text(0, 1.42, title, ha="center", fontsize=9.5)

    # panel (a): sigma = 1[z1 >= 0]
    ax = axes[0]
    frame(ax, r"(a) $\sigma(z)=\mathbb{1}[z_1\geq 0]$")
    ax.add_patch(Wedge((0, 0), 1, -90, 90, facecolor=C_ENV1, edgecolor="none"))
    ax.add_patch(Wedge((0, 0), 1, 90, 270, facecolor=C_ENV0, edgecolor="none"))
    ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor="black", lw=1.0))
    ax.plot([0, 0], [-1, 1], color="#333333", lw=1.0)
    ax.text(0.62, 0.05, r"env 1", fontsize=8.5)
    ax.text(-1.05, 0.05, r"env 0", fontsize=8.5)

    # panel (b): sigma' = 1[z2 <= 0]; disagreement on QI and QIII
    ax = axes[1]
    frame(ax, r"(b) $\sigma_T(z)=\mathbb{1}[z_2\leq 0]=\sigma(T)$")
    ax.add_patch(Wedge((0, 0), 1, 180, 360, facecolor=C_ENV1, edgecolor="none"))
    ax.add_patch(Wedge((0, 0), 1, 0, 180, facecolor=C_ENV0, edgecolor="none"))
    # disagreement quadrants I (0-90) and III (180-270)
    for a0, a1 in ((0, 90), (180, 270)):
        ax.add_patch(Wedge((0, 0), 1, a0, a1, facecolor="none",
                           edgecolor=C_DIS, hatch="////", lw=0.0,
                           alpha=0.5))
    ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor="black", lw=1.0))
    ax.plot([-1, 1], [0, 0], color="#333333", lw=1.0)
    # quarter-turn arrow for T (counterclockwise arc in the upper-right)
    ax.add_patch(FancyArrowPatch((0.66, 0.16), (0.16, 0.66),
                                 connectionstyle="arc3,rad=-0.55",
                                 arrowstyle="-|>", mutation_scale=11,
                                 color="#2c6fbb", lw=1.1))
    ax.text(0.46, 0.46, r"$T$", fontsize=9.5, color="#2c6fbb")
    for q, (x, y) in {"QI": (0.62, 1.02), "QII": (-0.72, 1.02),
                      "QIII": (-0.78, -1.12), "QIV": (0.6, -1.12)}.items():
        ax.text(x, y, q, fontsize=7.5, color="#444444")
    ax.text(0, -1.32, r"hatched: $\sigma\neq\sigma_T$, $P_Z=\frac{1}{2}$",
            ha="center", fontsize=8.5, color=C_DIS)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig5_witness.{ext}"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: DELVE pipeline
# --------------------------------------------------------------------------
def pipeline_figure():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef3fa", ec="#3d6da8", bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.08,rounding_size=0.12",
                                    facecolor=fc, edgecolor=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=8.3, fontweight="bold" if bold else "normal")

    def arrow(x, y1, y2):
        ax.add_patch(FancyArrowPatch((x, y1), (x, y2),
                                     arrowstyle="-|>", mutation_scale=10,
                                     color="#555555", lw=1.0))

    cx, w = 1.4, 4.2
    chain = [
        ("Pooled unlabeled EEG recordings", "#f4f4f4", "#777777", False),
        ("Stage 0: homogenize\nshared channels, common-average,\nband-pass + notch, resample, 4 s windows",
         "#eef3fa", "#3d6da8", False),
        ("Stage 1: window covariance\nLedoit-Wolf shrinkage, $x_w=\\mathrm{vech}(\\log\\Sigma_w)$",
         "#eef3fa", "#3d6da8", False),
        ("Stage 2: recording feature\nwindow average, StandardScaler\n(recording-level estimand)",
         "#fdeedd", "#c97a2b", True),
        ("Stage 3: fixed-$K$ K-means\nnearest-centroid assignment",
         "#eef3fa", "#3d6da8", False),
        ("Recovered covariance environments", "#e9f5ec", "#3a8a52", True),
    ]
    top, h, gap = 8.45, 1.05, 0.42
    ys = []
    for i, (text, fc, ec, bold) in enumerate(chain):
        y = top - i * (h + gap)
        ys.append(y)
        box(cx, y, w, h, text, fc, ec, bold)
        if i:
            arrow(cx + w / 2, ys[i - 1], y + h)

    # side branch: sample-split / inductive guarantee
    sx, sw = 6.4, 3.2
    box(sx, ys[3], sw, h,
        "Sample-split variant\nfreeze scaler and centers,\nheld-out assignment",
        "#f3eef8", "#7a4faa", False)
    ax.add_patch(FancyArrowPatch((cx + w, ys[3] + h / 2),
                                 (sx, ys[3] + h / 2),
                                 arrowstyle="-|>", mutation_scale=10,
                                 color="#7a4faa", lw=1.0))
    box(sx, ys[3] - (h + gap), sw, h,
        "Stage 4: conditional misclassification\nguarantee (Corollary), not a\ncomputed numeric bound",
        "#f3eef8", "#7a4faa", False)
    arrow(sx + sw / 2, ys[3], ys[3] - gap + 0.02)

    ax.text(5, 0.45,
            "Stages 0-1, 3, 5-6 are standard components; the estimand (Stage 2) "
            "and conditional guarantee (Stage 4) are this paper's contributions.",
            ha="center", fontsize=7.6, color="#555555")

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig6_pipeline.{ext}"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    witness_figure()
    pipeline_figure()
    print("done")
