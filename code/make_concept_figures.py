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
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef3fa", ec="#3d6da8", bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.08,rounding_size=0.12",
                                    facecolor=fc, edgecolor=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=8.0, fontweight="bold" if bold else "normal")

    def arrow(x, y1, y2):
        ax.add_patch(FancyArrowPatch((x, y1), (x, y2),
                                     arrowstyle="-|>", mutation_scale=10,
                                     color="#555555", lw=1.0))

    cx, w = 3.1, 3.5
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

    # ---- evaluation-design path (dashed), kept separate from the solid analysis path ----
    # Source labels node (top)
    src_x, src_y, src_w, src_h = 0.2, ys[0] + 0.15, 2.15, 0.75
    ax.add_patch(FancyBboxPatch((src_x, src_y), src_w, src_h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor="#f6f6f6", edgecolor="#888888",
                                lw=1.0, linestyle="--"))
    ax.text(src_x + src_w / 2, src_y + src_h / 2, "Source labels",
            ha="center", va="center", fontsize=8.0, color="#555555")

    # Balanced subset: a distinct dashed node on the evaluation-design path
    bs_x, bs_y, bs_w, bs_h = 0.2, 7.35, 2.15, 0.85
    ax.add_patch(FancyBboxPatch((bs_x, bs_y), bs_w, bs_h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor="#f6f6f6", edgecolor="#888888",
                                lw=1.0, linestyle="--"))
    ax.text(bs_x + bs_w / 2, bs_y + bs_h / 2,
            "Balanced subset\n(30 per source)\nevaluation design",
            ha="center", va="center", fontsize=7.0, color="#555555")

    # Source labels -> balanced subset (dashed down)
    ax.add_patch(FancyArrowPatch((src_x + src_w / 2, src_y),
                                 (bs_x + bs_w / 2, bs_y + bs_h),
                                 arrowstyle="-|>", mutation_scale=9,
                                 linestyle="--", color="#888888", lw=0.9))

    # Balanced subset -> solid main-chain input (right-up-right dashed, through the gap)
    y_top = ys[0] + h / 2
    gap_x = 2.75
    y_bs = bs_y + bs_h / 2
    ax.add_patch(FancyArrowPatch((bs_x + bs_w, y_bs), (gap_x, y_bs),
                                 arrowstyle="-", linestyle="--",
                                 color="#888888", lw=0.9))
    ax.add_patch(FancyArrowPatch((gap_x, y_bs), (gap_x, y_top),
                                 arrowstyle="-", linestyle="--",
                                 color="#888888", lw=0.9))
    ax.add_patch(FancyArrowPatch((gap_x, y_top), (cx, y_top),
                                 arrowstyle="-|>", mutation_scale=9,
                                 linestyle="--", color="#888888", lw=0.9))

    # Source labels re-enter only at post-hoc scoring
    y_bot = ys[5] + h / 2
    ax.add_patch(FancyArrowPatch((src_x, y_bot), (cx, y_bot),
                                 arrowstyle="-|>", mutation_scale=9,
                                 linestyle="--", color="#888888", lw=0.9))
    ax.text(src_x, y_bot + 0.32, "post-hoc scoring",
            ha="left", va="center", fontsize=6.7, color="#666666")
    ax.text(0.2, 0.42,
            "evaluation-only; not used in\nfeatures, scaling, center fitting,\nor assignment",
            ha="left", va="bottom", fontsize=6.6, color="#666666")

    # side branch: sample-split / inductive guarantee
    sx, sw = 7.35, 2.8
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

    # guarantee condition box: all six premises must hold
    cbx, cby, cbw, cbh = 7.35, 5.90, 2.8, 3.6
    ax.add_patch(FancyBboxPatch((cbx, cby), cbw, cbh,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor="#fff7ec", edgecolor="#c97a2b", lw=1.0))
    ax.text(cbx + cbw / 2, cby + cbh - 0.35, "Guarantee applies only if:",
            ha="center", va="center", fontsize=7.4, fontweight="bold",
            color="#8a5a1e")
    conds = ["fixed $K$", "frozen transformation", "global empirical K-means",
             "bounded features", "population alignment", "level-set condition"]
    for j, ctext in enumerate(conds):
        ax.text(cbx + 0.16, cby + cbh - 0.95 - j * 0.46, "- " + ctext,
                ha="left", va="center", fontsize=7.0, color="#333333")
    s4_y = ys[3] - (h + gap) + h / 2
    # guarantee box -> Stage 4: right-down-left dashed route, arrowhead at Stage 4
    route_x, y_out = 10.5, 6.4
    ax.add_patch(FancyArrowPatch((cbx + cbw, y_out), (route_x, y_out),
                                 arrowstyle="-", linestyle="--",
                                 color="#c97a2b", lw=0.9))
    ax.add_patch(FancyArrowPatch((route_x, y_out), (route_x, s4_y),
                                 arrowstyle="-", linestyle="--",
                                 color="#c97a2b", lw=0.9))
    ax.add_patch(FancyArrowPatch((route_x, s4_y), (sx + sw, s4_y),
                                 arrowstyle="-|>", mutation_scale=9,
                                 linestyle="--", color="#c97a2b", lw=0.9))

    # DELVE-B: blind K / full-pool scaler, outside the unconditional guarantee
    dbx, dby, dbw, dbh = 7.35, 0.85, 5.8, 1.0
    ax.add_patch(FancyBboxPatch((dbx, dby), dbw, dbh,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor="#f2f2f2", edgecolor="#888888",
                                lw=1.0, linestyle="--"))
    ax.text(dbx + dbw / 2, dby + dbh / 2,
            "DELVE-B: blind $K$ selection and full-pool scaler\n"
            "empirical pipeline only, outside the unconditional guarantee",
            ha="center", va="center", fontsize=7.2, color="#555555")

    ax.text(10.3, 0.3,
            "Stages 0-1, 3, 5-6 are standard; Stages 2 and 4 are this paper's contributions.",
            ha="center", fontsize=7.1, color="#555555")

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig6_pipeline.{ext}"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    witness_figure()
    pipeline_figure()
    print("done")
