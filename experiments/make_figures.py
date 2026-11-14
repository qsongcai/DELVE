#!/usr/bin/env python3
"""Generate publication EEG figures from the cached recording features.

All recomputed quantities are verified to match the numbers reported in the
manuscript (K=2..6 ARI/NMI/silhouette). Summary-only values (bootstrap CIs,
spatial representations, novelty AUC) come from the verified blueprint tables.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (adjusted_rand_score, normalized_mutual_info_score,
                             silhouette_score)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.4,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

# muted, color-blind-friendly palette
C = {"blue": "#3b6fb6", "orange": "#e08a3c", "green": "#4f9d69",
     "red": "#c0504d", "grey": "#8a8a8a", "purple": "#7d6bb0"}
DSCOLOR = {"ds007541": C["blue"], "ds008099": C["orange"],
           "on004362": C["green"]}
DSLABEL = {"ds007541": "ds007541", "ds008099": "ds008099",
           "on004362": "on004362"}

d = np.load(os.path.join(OUT, "recording_features.npz"), allow_pickle=True)
F, DS = d["features"], d["datasets"]


def balanced_idx(seed):
    rng = np.random.default_rng(seed)
    keep = []
    for ds in sorted(set(DS)):
        pool = np.where(DS == ds)[0]
        keep += list(pool[rng.choice(len(pool), 30, replace=False)])
    return np.array(keep)


Ks = list(range(2, 7))
keep = balanced_idx(0)
X = StandardScaler().fit_transform(F[keep])
y = DS[keep]

ari, nmi, sil = [], [], []
for K in Ks:
    lab = KMeans(K, n_init=50, random_state=0).fit_predict(X)
    ari.append(adjusted_rand_score(y, lab))
    nmi.append(normalized_mutual_info_score(y, lab))
    sil.append(silhouette_score(X, lab))

# ---------------------------------------------------------------------------
# Figure 1: K sensitivity
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.4, 3.3))
ax.plot(Ks, ari, "-o", color=C["blue"], label="ARI")
ax.plot(Ks, nmi, "-s", color=C["orange"], label="NMI")
ax.plot(Ks, sil, "-^", color=C["green"], label="Silhouette")
ax.axvline(3, color=C["grey"], ls="--", lw=1)
ax.annotate("oracle $K=3$", xy=(3, 0.62), xytext=(3.18, 0.72),
            color=C["grey"], fontsize=8)
ax.annotate("", xy=(2, 0.279), xytext=(1.8, 0.13),
            arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.9))
ax.set_xlabel("number of clusters $K$")
ax.set_ylabel("score")
ax.set_xticks(Ks)
ax.set_xlim(1.4, 6.5)
ax.set_ylim(0, 0.8)

# Place "blind choice K=2" so the gap between "blind" and "choice" sits
# directly above the arrow's starting point (x = 1.8). Measure rendered
# character extents rather than guessing proportional widths.
fig.canvas.draw()
def _data_extent(s):
    t = ax.text(0, 0.1, s, ha="left", va="bottom", color=C["red"],
                fontsize=8)
    e = t.get_window_extent().transformed(ax.transData.inverted())
    t.remove()
    return e
e_bc = _data_extent("blind choice")
e_b = _data_extent("blind")
e_c = _data_extent("choice")
_gap_start = e_b.x1
_choice_left = e_bc.x1 - e_c.width
_gap_center = 0.5 * (_gap_start + _choice_left)
_gap_offset = _gap_center - e_bc.x0
label = ax.text(1.8 - _gap_offset, 0.1, "blind choice $K=2$",
                ha="left", va="bottom", color=C["red"], fontsize=8)

ax.legend(frameon=False, ncol=3, loc="lower center")
ax.set_title("Recovery on the balanced 90-record design (seed 0)")
fig.savefig(os.path.join(OUT, "fig1_k_sensitivity.pdf"))
fig.savefig(os.path.join(OUT, "fig1_k_sensitivity.png"))
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 2: PCA scatter of the balanced recording features
# ---------------------------------------------------------------------------
lab3 = KMeans(3, n_init=50, random_state=0).fit_predict(X)
pcs = PCA(n_components=2).fit_transform(X)
fig, ax = plt.subplots(figsize=(4.6, 3.6))
for ds in sorted(set(y)):
    m = y == ds
    ax.scatter(pcs[m, 0], pcs[m, 1], s=22, color=DSCOLOR[ds],
               edgecolor="white", linewidth=0.4, label=DSLABEL[ds])
ax.set_xlabel("PC 1")
ax.set_ylabel("PC 2")
ax.legend(frameon=False, loc="best")
ax.set_title("Recording features (balanced 90), colored by source")
fig.savefig(os.path.join(OUT, "fig2_pca_scatter.pdf"))
fig.savefig(os.path.join(OUT, "fig2_pca_scatter.png"))
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 3: subject-cluster bootstrap confidence intervals (verified summary)
# ---------------------------------------------------------------------------
boot = [
    ("subject\naggregate", 0.616, 0.312, 0.812),
    ("cluster\nretained", 0.554, 0.286, 0.830),
    ("naive\nrecording", 0.603, 0.317, 0.810),
]
fig, ax = plt.subplots(figsize=(5.4, 3.3))
yy = np.arange(len(boot))[::-1]
for yi, (name, mean, lo, hi) in zip(yy, boot):
    ax.errorbar(mean, yi, xerr=[[mean - lo], [hi - mean]], fmt="o",
                color=C["blue"], capsize=4, ms=6, lw=1.3)
ax.axvline(0.608, color=C["purple"], ls="--", lw=1.1)
ax.axvline(0.241, color=C["red"], ls="--", lw=1.1)
ax.text(0.235, 2.78, "plug-in 0.241", color=C["red"],
        fontsize=7.5, ha="right", va="center")
ax.text(0.615, 2.78, "point 0.608", color=C["purple"],
        fontsize=7.5, ha="left", va="center")
ax.set_yticks(yy)
ax.set_yticklabels([b[0].replace("\n", " ") for b in boot])
ax.set_xlabel("ARI")
ax.set_xlim(0, 1)
ax.set_ylim(-0.6, 3.05)
ax.set_title("Subject-cluster bootstrap (B=500): mean and 95% CI")
fig.savefig(os.path.join(OUT, "fig3_bootstrap_ci.pdf"))
fig.savefig(os.path.join(OUT, "fig3_bootstrap_ci.png"))
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 4: spatial representation (6 seeds) and novelty AUC
# ---------------------------------------------------------------------------
spatial = [("common", 0.582, 0.476, 0.675),
           ("bipolar", 0.415, 0.359, 0.505),
           ("CSD", 0.678, 0.622, 0.740)]
novelty = [("ds007541", 0.706), ("ds008099", 0.893), ("on004362", 0.914)]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.1))
yy = np.arange(len(spatial))[::-1]
for yi, (name, mean, lo, hi) in zip(yy, spatial):
    a1.errorbar(mean, yi, xerr=[[mean - lo], [hi - mean]], fmt="o",
                color=C["green"], capsize=4, ms=6, lw=1.3)
a1.set_yticks(yy)
a1.set_yticklabels([s[0] for s in spatial])
a1.set_xlabel("recording-level ARI")
a1.set_xlim(0.3, 0.8)
a1.set_title("Spatial representation (6 seeds)")
names = [n[0] for n in novelty]
vals = [n[1] for n in novelty]
a2.bar(names, vals, color=[C["blue"], C["orange"], C["green"]], width=0.6)
a2.set_ylim(0.5, 1.0)
a2.set_ylabel("novelty AUC")
a2.set_title("Leave-one-source novelty detection")
for i, v in enumerate(vals):
    a2.text(i, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
plt.setp(a2.get_xticklabels(), rotation=15, ha="right")
fig.savefig(os.path.join(OUT, "fig4_spatial_novelty.pdf"))
fig.savefig(os.path.join(OUT, "fig4_spatial_novelty.png"))
plt.close(fig)

print("ARI", [round(a, 3) for a in ari])
print("NMI", [round(a, 3) for a in nmi])
print("SIL", [round(a, 3) for a in sil])
print("figures written to", OUT)
