#!/usr/bin/env python3
"""R5 problem 8: sensitivity of the gated selector to cap, multiplier,
silhouette gate, and candidate range."""
import numpy as np
from sklearn.preprocessing import StandardScaler
import delve_core as dc

d = np.load("figures/recording_features.npz", allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss)); FULL = list(range(2, 7))


def balanced(seed):
    r = np.random.default_rng(seed); Xf, y = [], []
    for ds in DS:
        idx = r.choice(np.where(dss == ds)[0], 30, replace=False)
        Xf.append(feats[idx]); y.append(np.full(30, ds))
    return StandardScaler().fit_transform(np.vstack(Xf)), np.concatenate(y)


def gate(metrics, kgrid, cap, mult, use_sil):
    stab = np.array([metrics[K]["stability"] for K in kgrid])
    thr = min(cap, mult * stab.max())
    elig = [K for K in kgrid
            if metrics[K]["stability"] >= thr
            and (metrics[K]["silhouette"] > 0 or not use_sil)]
    if elig:
        return min(elig, key=lambda K: metrics[K]["bic"])
    sils = np.array([metrics[K]["silhouette"] for K in kgrid])
    bics = np.array([metrics[K]["bic"] for K in kgrid])
    return kgrid[int(np.argmax(sils))] if sils.max() > 0 else kgrid[int(np.argmin(bics))]


caps = [0.80, 0.85, 0.90]; mults = [0.8, 0.9, 1.0]
ranges = {"2-4": [2, 3, 4], "2-5": [2, 3, 4, 5], "2-6": FULL}
all_metrics = []
for s in range(6):
    X, _ = balanced(s)
    _, metrics = dc.select_K(X, FULL, np.random.default_rng(2026))
    all_metrics.append(metrics)

print("=== gate parameter sensitivity (chosen K per seed), true K=3 ===")
results = []
for cap in caps:
    for mult in mults:
        for use_sil in [True, False]:
            row = [gate(m, FULL, cap, mult, use_sil) for m in all_metrics]
            f3 = row.count(3)
            results.append((cap, mult, use_sil, row, f3))
            print("cap %.2f mult %.1f sil-gate %s: %s  K3=%d/6"
                  % (cap, mult, use_sil, row, f3))

print("\n=== candidate range sensitivity (cap .85 mult .9 sil on) ===")
for rname, grid in ranges.items():
    row = [gate(m, grid, 0.85, 0.9, True) for m in all_metrics]
    print("range %s: %s  K3=%d/6" % (rname, row, row.count(3)))

n3 = np.mean([r[4] for r in results])
print("\nmean K=3 frequency across %d gate variants: %.2f/6"
      % (len(results), n3))
