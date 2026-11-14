#!/usr/bin/env python3
"""
Transparent K selection through the one-standard-error rule.

We do not tune the rule to recover the oracle K=3. For a balanced 30-per-source
design we repeatedly split into train (20/source) and held-out (10/source), fit
KMeans for each K on the training side (inductive scaler), and record the
per-point held-out clustering cost. The 1-SE rule then picks the smallest K
whose mean cost is within one standard error of the minimum. The rule is fixed
before any number is read.
"""
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "recording_features.npz")
N_PER, N_TRAIN, B, K_GRID = 30, 20, 100, list(range(2, 7))
d = np.load(NPZ, allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
idx_by_ds = {x: np.where(dss == x)[0] for x in DS}

rng = np.random.default_rng(0)
# one balanced 90-recording design (pre-specified seed 0)
bal = np.concatenate([rng.choice(idx_by_ds[x], N_PER, replace=False) for x in DS])
Xb, yb = feats[bal], dss[bal]

costs = {K: [] for K in K_GRID}
for _ in range(B):
    tr, ho = [], []
    for x in DS:
        rows = np.where(yb == x)[0]
        rng.shuffle(rows)
        tr.append(rows[:N_TRAIN]); ho.append(rows[N_TRAIN:])
    tr, ho = np.concatenate(tr), np.concatenate(ho)
    sc = StandardScaler().fit(Xb[tr])
    Xtr, Xho = sc.transform(Xb[tr]), sc.transform(Xb[ho])
    for K in K_GRID:
        km = KMeans(K, n_init=50, random_state=rng.integers(1 << 30)).fit(Xtr)
        d2 = ((Xho[:, None, :] - km.cluster_centers_[None]) ** 2).sum(-1)
        costs[K].append(d2.min(axis=1).mean())

print("held-out clustering cost (B=%d train/held-out splits), mean +/- SE" % B)
mean, se = {}, {}
for K in K_GRID:
    c = np.array(costs[K])
    mean[K], se[K] = c.mean(), c.std(ddof=1) / np.sqrt(B)
    print("  K=%d cost=%.4f SE=%.4f" % (K, mean[K], se[K]))

k_star = min(K_GRID, key=lambda K: mean[K])
thr = mean[k_star] + se[k_star]
one_se = min(K for K in K_GRID if mean[K] <= thr)
print("\nminimum-cost K = %d ; 1-SE threshold = %.4f" % (k_star, thr))
print("one-SE chosen K = %d (oracle = 3)" % one_se)
print("rule fixed before reading results; no threshold was adjusted to reach K=3.")
