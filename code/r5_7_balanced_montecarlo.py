#!/usr/bin/env python3
"""R5 problem 7: expanded balanced Monte Carlo and unbalanced macro metrics.

Keeps the six prespecified seeds untouched; adds a larger independent
Monte Carlo distribution plus Hungarian-aligned precision/recall/purity.
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (adjusted_rand_score, normalized_mutual_info_score,
                             precision_recall_fscore_support)
from scipy.optimize import linear_sum_assignment

d = np.load("figures/recording_features.npz")
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
N_BAL = 100


def balanced_draw(rng):
    xf, y = [], []
    for src in DS:
        pool = np.where(dss == src)[0]
        idx = rng.choice(pool, 30, replace=False)
        xf.append(feats[idx]); y.append(np.full(30, src))
    return np.vstack(xf), np.concatenate(y)


def hungarian_map(y, lab):
    classes = np.unique(y); clusters = np.unique(lab)
    cm = np.zeros((len(classes), len(clusters)))
    for i, c in enumerate(classes):
        for j, k in enumerate(clusters):
            cm[i, j] = np.sum((y == c) & (lab == k))
    ri, ci = linear_sum_assignment(-cm)
    return {clusters[j]: classes[i] for i, j in zip(ri, ci)}


def metrics(y, lab):
    ari = adjusted_rand_score(y, lab)
    nmi = normalized_mutual_info_score(y, lab)
    mp = hungarian_map(y, lab)
    aligned = np.array([mp[v] for v in lab])
    p, r, f, _ = precision_recall_fscore_support(
        y, aligned, labels=DS, zero_division=0)
    purity = np.mean(aligned == y)
    return dict(ari=ari, nmi=nmi, purity=purity,
                macro_p=p.mean(), macro_r=r.mean(), macro_f=f.mean(),
                per_source_p=p, per_source_r=r)


rows = []
for t in range(N_BAL):
    rng = np.random.default_rng(7000 + t)
    Xr, y = balanced_draw(rng)
    X = StandardScaler().fit_transform(Xr)
    lab = KMeans(3, n_init=50, random_state=7000 + t).fit_predict(X)
    rows.append(metrics(y, lab))

keys = ["ari", "nmi", "purity", "macro_p", "macro_r", "macro_f"]
print("=== expanded balanced Monte Carlo (n=%d) ===" % N_BAL)
for k in keys:
    v = np.array([r[k] for r in rows])
    print("%-8s mean %.3f std %.3f q05 %.3f q95 %.3f"
          % (k, v.mean(), v.std(), np.quantile(v, .05), np.quantile(v, .95)))
ps_p = np.array([r["per_source_p"] for r in rows]).mean(0)
ps_r = np.array([r["per_source_r"] for r in rows]).mean(0)
print("per-source precision:", np.round(ps_p, 3))
print("per-source recall:   ", np.round(ps_r, 3))

# unbalanced full pool
X = StandardScaler().fit_transform(feats)
lab = KMeans(3, n_init=50, random_state=0).fit_predict(X)
um = metrics(dss, lab)
print("\n=== unbalanced full pool (n=%d) ===" % len(dss))
for k in keys:
    print("%-8s %.3f" % (k, um[k]))

np.savez("figures/r5_7_montecarlo.npz",
         ari=np.array([r["ari"] for r in rows]),
         nmi=np.array([r["nmi"] for r in rows]),
         purity=np.array([r["purity"] for r in rows]),
         macro_p=np.array([r["macro_p"] for r in rows]),
         macro_r=np.array([r["macro_r"] for r in rows]),
         macro_f=np.array([r["macro_f"] for r in rows]),
         per_source_p=ps_p, per_source_r=ps_r,
         unbalanced=np.array([um[k] for k in keys]))
