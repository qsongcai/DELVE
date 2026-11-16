#!/usr/bin/env python3
"""Four-panel main EEG result figure (reviewer R3-14).

(a) PCA projection of the balanced 90 recording features.
(b) Normalized source x cluster contingency at oracle K=3.
(c) ARI across the four primary designs, with error bars where multi-seed.
(d) Selected K and bootstrap stability across six balanced seeds.
All multi-seed values match figures/blind_perseed.npz and tab:designs.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "figures")

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "axes.titlesize": 9,
    "xtick.labelsize": 7.8,
    "ytick.labelsize": 7.8,
    "legend.fontsize": 7.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

C = {"blue": "#3b6fb6", "orange": "#e08a3c", "green": "#4f9d69",
     "red": "#c0504d", "grey": "#8a8a8a", "purple": "#7d6bb0"}
DSCOLOR = {"ds007541": C["blue"], "ds008099": C["orange"],
           "on004362": C["green"]}
DSMARKER = {"ds007541": "X", "ds008099": "*", "on004362": "P"}

d = np.load(os.path.join(OUT, "recording_features.npz"), allow_pickle=True)
F, DS = d["features"], d["datasets"]
SRC = sorted(set(DS))


def balanced_idx(seed):
    rng = np.random.default_rng(seed)
    keep = []
    for ds in SRC:
        pool = np.where(DS == ds)[0]
        keep += list(pool[rng.choice(len(pool), 30, replace=False)])
    return np.array(keep)


keep = balanced_idx(0)
X = StandardScaler().fit_transform(F[keep])
y = DS[keep]
km3 = KMeans(3, n_init=50, random_state=0).fit(X)
lab3 = km3.labels_

fig, axes = plt.subplots(2, 2, figsize=(9.6, 7.0))

# (a) PCA projection
ax = axes[0, 0]
pcs = PCA(n_components=2).fit_transform(X)
for ds in SRC:
    m = y == ds
    ax.scatter(pcs[m, 0], pcs[m, 1], s=26, marker=DSMARKER[ds],
               color=DSCOLOR[ds], edgecolor="white", linewidth=0.4, label=ds)
ax.set_xlabel("PC 1")
ax.set_ylabel("PC 2")
ax.legend(frameon=False, loc="best")
ax.set_title("(a) Feature projection (balanced 90)")

# (b) normalized source x cluster contingency
ax = axes[0, 1]
cont = np.zeros((3, 3))
for i, ds in enumerate(SRC):
    m = ds == y
    for k in range(3):
        cont[i, k] = np.sum(lab3[m] == k)
norm = cont / cont.sum(axis=1, keepdims=True)
im = ax.imshow(norm, cmap="Blues", vmin=0, vmax=1, aspect="auto")
for i in range(3):
    for k in range(3):
        ax.text(k, i, f"{norm[i, k]:.2f}", ha="center", va="center",
                fontsize=8, color="black" if norm[i, k] < 0.6 else "white")
ax.set_xticks(range(3)); ax.set_xticklabels([f"cluster {k}" for k in range(3)])
ax.set_yticks(range(3)); ax.set_yticklabels(SRC)
ax.set_title("(b) Source x cluster contingency (seed 0)")
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.ax.tick_params(labelsize=7.4)

# (c) ARI across four primary designs
ax = axes[1, 0]
designs = ["oracle\nbalanced", "blind\nselected K", "unbalanced\nK=3", "subject\nplug-in"]
means = [0.582, 0.419, 0.371, 0.241]
stds = [0.068, 0.140, 0.0, 0.0]
single = [False, False, True, True]
xpos = np.arange(4)
for i in range(4):
    if single[i]:
        ax.scatter(xpos[i], means[i], s=46, marker="D", color=C["red"],
                   edgecolor="white", zorder=3)
    else:
        ax.errorbar(xpos[i], means[i], yerr=stds[i], fmt="o", color=C["blue"],
                    capsize=4, ms=7, lw=1.3, zorder=3)
ax.set_xticks(xpos); ax.set_xticklabels(designs)
ax.set_ylabel("recording-level ARI")
ax.set_ylim(0, 0.75)
ax.set_title("(c) ARI across primary designs")
ax.text(0.99, 0.04, "diamonds: single run", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=7, color=C["red"])

# (d) selected K and stability across seeds
ax = axes[1, 1]
b = np.load(os.path.join(OUT, "blind_perseed.npz"))
selK, stab = b["selK"], b["stabSel"]
seeds = np.arange(6)
bars = ax.bar(seeds, selK, width=0.6, color=C["grey"], alpha=0.75,
              label="selected K")
ax.set_xlabel("seed")
ax.set_ylabel("selected K")
ax.set_xticks(seeds)
ax.set_ylim(0, 3.6)
ax.set_yticks([2, 3])
ax2 = ax.twinx()
ax2.plot(seeds, stab, "-o", color=C["orange"], ms=5, lw=1.4,
         label="stability")
ax2.set_ylabel("stability")
ax2.set_ylim(0.7, 0.95)
ax2.spines["top"].set_visible(False)
ax.set_title("(d) Selected K and stability")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, loc="lower right", fontsize=7)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig8_main_results.pdf"))
fig.savefig(os.path.join(OUT, "fig8_main_results.png"))
plt.close(fig)

print("oracle seed-0 ARI check:", round(adjusted_rand_score(y, lab3), 3))
print("contingency counts:\n", cont.astype(int))
print("saved fig8_main_results")
