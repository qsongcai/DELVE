#!/usr/bin/env python3
"""
Oracle-Q / support diagnostic.

With the true labels we build the three oracle centers and ask how separable
the recordings really are. For each point we measure its margin (distance to
the nearest other center minus distance to its own center) and the error of
the nearest-oracle-center rule. No fitted (unsupervised) partition enters this
diagnostic; it is a best-case, label-aware characterization.
"""
import os
import numpy as np
from sklearn.preprocessing import StandardScaler

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "recording_features.npz")
N_PER = 30
d = np.load(NPZ, allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
rng = np.random.default_rng(0)
idx = np.concatenate([rng.choice(np.where(dss == x)[0], N_PER, replace=False)
                      for x in DS])
X = StandardScaler().fit_transform(feats[idx])
y = dss[idx]

# oracle centers in the scaled space
centers = np.array([X[y == x].mean(axis=0) for x in DS])
d2 = ((X[:, None, :] - centers[None]) ** 2).sum(-1)
own = np.array([DS.index(v) for v in y])
d_own = d2[np.arange(len(X)), own]
d2_mask = d2.copy()
d2_mask[np.arange(len(X)), own] = np.inf
nearest_other = d2_mask.argmin(axis=1)
d_other = d2_mask.min(axis=1)
margin = d_other - d_own

assign = d2.argmin(axis=1)
err = (assign != own)
print("oracle nearest-center assignment: error = %.3f (%d/%d)"
      % (err.mean(), err.sum(), len(X)))
for j, x in enumerate(DS):
    m = y == x
    print("  %-9s n=%d  correct=%.3f" % (x, m.sum(), (assign[m] == own[m]).mean()))

print("\nmargin distribution (positive = supported, negative = misclassified)")
print("  min/median/max = %.3f / %.3f / %.3f" % (margin.min(), np.median(margin), margin.max()))
print("  fraction margin > 0 (supported): %.3f" % (margin > 0).mean())
for band in (0.0, 0.25, 0.5, 1.0):
    print("  fraction |margin| <= %.2f (near boundary): %.3f"
          % (band, (np.abs(margin) <= band).mean()))

# oracle-Q: cumulative error when points are ordered by margin (worst first)
order = np.argsort(margin)
sorted_m = margin[order]
print("\noracle-Q: error fraction vs margin threshold")
for t in (-0.5, 0.0, 0.25, 0.5, 1.0):
    print("  threshold %.2f -> points below = %.3f, cumulative error among them = %.3f"
          % (t, (margin < t).mean(), (sorted_m < t).sum() / max(1, (margin < t).sum())))
print("\ndone.")
