#!/usr/bin/env python3
"""R5 problem 8: standard K-selection baselines on the balanced design.

Compares internal indices, GMM BIC/AIC, hierarchical, stability-only,
and gap statistic over the six prespecified balanced seeds.
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (silhouette_score, calinski_harabasz_score,
                             davies_bouldin_score)

d = np.load("figures/recording_features.npz")
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss)); KGRID = [2, 3, 4, 5, 6]
SEEDS = [0, 1, 2, 3, 4, 5]


def balanced(seed):
    rng = np.random.default_rng(seed); xf, y = [], []
    for src in DS:
        pool = np.where(dss == src)[0]
        idx = rng.choice(pool, 30, replace=False)
        xf.append(feats[idx]); y.append(np.full(30, src))
    X = StandardScaler().fit_transform(np.vstack(xf))
    return X, np.concatenate(y)


def gap_statistic(X, B=30, rng=None):
    rng = rng or np.random.default_rng(0)
    lo, hi = X.min(0), X.max(0)

    def logw(data, lab):
        w = 0.0
        for k in np.unique(lab):
            pts = data[lab == k]
            c = pts.mean(0)
            w += ((pts - c) ** 2).sum()
        return np.log(w) if w > 0 else -np.inf

    gaps, sk = [], []
    ref = []
    for _ in range(B):
        null = rng.uniform(lo, hi, size=X.shape)
        ref.append(null)
    for k in KGRID:
        obs = logw(X, KMeans(k, n_init=20, random_state=0).fit_predict(X))
        nulls = [logw(z, KMeans(k, n_init=10, random_state=0).fit_predict(z))
                 for z in ref]
        g = np.mean(nulls) - obs
        gaps.append(g)
        sk.append(np.std(nulls) * np.sqrt(1 + 1 / B))
    # smallest K with gap(k) >= gap(k+1) - s(k+1)
    for i in range(len(KGRID) - 1):
        if gaps[i] >= gaps[i + 1] - sk[i + 1]:
            return KGRID[i]
    return KGRID[-1]


picks = {m: [] for m in ["silhouette", "CH", "DB", "GMM-diag BIC",
                         "GMM-diag AIC", "GMM-full BIC", "GMM-full AIC",
                         "hierarchical silhouette", "gap"]}
for seed in SEEDS:
    X, y = balanced(seed)
    vals = {m: {} for m in picks}
    for k in KGRID:
        km = KMeans(k, n_init=50, random_state=seed).fit(X)
        lab = km.labels_
        vals["silhouette"][k] = silhouette_score(X, lab)
        vals["CH"][k] = calinski_harabasz_score(X, lab)
        vals["DB"][k] = davies_bouldin_score(X, lab)
        for ct, tag in [("diag", "GMM-diag"), ("full", "GMM-full")]:
            gm = GaussianMixture(k, covariance_type=ct, n_init=10,
                                 random_state=seed).fit(X)
            vals[tag + " BIC"][k] = gm.bic(X)
            vals[tag + " AIC"][k] = gm.aic(X)
        hc = AgglomerativeClustering(k).fit_predict(X)
        vals["hierarchical silhouette"][k] = silhouette_score(X, hc)
    picks["silhouette"].append(max(vals["silhouette"], key=vals["silhouette"].get))
    picks["CH"].append(max(vals["CH"], key=vals["CH"].get))
    picks["DB"].append(min(vals["DB"], key=vals["DB"].get))
    picks["GMM-diag BIC"].append(min(vals["GMM-diag BIC"], key=vals["GMM-diag BIC"].get))
    picks["GMM-diag AIC"].append(min(vals["GMM-diag AIC"], key=vals["GMM-diag AIC"].get))
    picks["GMM-full BIC"].append(min(vals["GMM-full BIC"], key=vals["GMM-full BIC"].get))
    picks["GMM-full AIC"].append(min(vals["GMM-full AIC"], key=vals["GMM-full AIC"].get))
    picks["hierarchical silhouette"].append(max(vals["hierarchical silhouette"], key=vals["hierarchical silhouette"].get))
    picks["gap"].append(gap_statistic(X, rng=np.random.default_rng(seed)))

print("method            selected K across six seeds (true K=3)")
for m, v in picks.items():
    freq = {k: v.count(k) for k in KGRID}
    print("%-22s %s   freq3=%d/6" % (m, v, v.count(3)))
np.savez("figures/r5_8_selector_baselines.npz",
         **{m.replace(" ", "_").replace("-", "_"): np.array(v) for m, v in picks.items()})
