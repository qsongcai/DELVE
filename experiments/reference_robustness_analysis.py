#!/usr/bin/env python3
"""
Analysis of the reference / bad-channel robustness cache.

Balanced 30-per-source, oracle K=3, six seeds. We report recording-level and
subject-aggregated ARI for the common-average (baseline), bipolar, and CSD
schemes, the four leave-one-channel-out variants, the bipolar multiband PLV
dataset ARI, and the bad-channel statistics. No metadata enters any fit.
"""
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "reference_robustness.npz")
N_PER, N_SEEDS, K = 30, 6, 3
d = np.load(NPZ, allow_pickle=True)
dss, subs = d["datasets"], d["subjects"]
DS = sorted(set(dss))


def balanced_idx(seed, n_per=N_PER):
    r = np.random.default_rng(seed)
    out = []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        out.append(r.choice(pool, min(n_per, len(pool)), replace=False))
    return np.concatenate(out)


def ari_for(feat, seed, k=K, idx=None):
    if idx is None:
        idx = balanced_idx(seed)
    X = StandardScaler().fit_transform(feat[idx])
    lab = KMeans(k, n_init=50, random_state=seed).fit_predict(X)
    return adjusted_rand_score(dss[idx], lab)


def scheme_summary(name, feat):
    rec = np.array([ari_for(feat, s) for s in range(N_SEEDS)])
    print("  %-14s recording ARI = %.3f [%.3f, %.3f]"
          % (name, rec.mean(), rec.min(), rec.max()))
    return rec


# subject-aggregated rows for each scheme
def subject_rows(feat):
    xf, yf = [], []
    for s in sorted(set(subs)):
        m = subs == s
        xf.append(feat[m].mean(axis=0)); yf.append(dss[m][0])
    return np.array(xf), np.array(yf)


def subject_ari(name, feat):
    sf, sy = subject_rows(feat)
    vals = []
    for seed in range(N_SEEDS):
        r = np.random.default_rng(seed)
        idx = []
        for ds in DS:
            pool = np.where(sy == ds)[0]
            idx.append(r.choice(pool, min(N_PER, len(pool)), replace=False))
        idx = np.concatenate(idx)
        X = StandardScaler().fit_transform(sf[idx])
        lab = KMeans(K, n_init=50, random_state=seed).fit_predict(X)
        vals.append(adjusted_rand_score(sy[idx], lab))
    vals = np.array(vals)
    print("  %-14s subject   ARI = %.3f [%.3f, %.3f]"
          % (name, vals.mean(), vals.min(), vals.max()))


print("=" * 64)
print("REFERENCE ROBUSTNESS, balanced 30/source, oracle K=3, %d seeds" % N_SEEDS)
print("=" * 64)
print("\n[1] recording-level ARI by reference scheme")
for name, key in [("common-average", "common"), ("bipolar", "bipolar"), ("CSD", "csd")]:
    scheme_summary(name, d[key])

print("\n[2] subject-aggregated ARI by reference scheme (independent unit)")
for name, key in [("common-average", "common"), ("bipolar", "bipolar"), ("CSD", "csd")]:
    subject_ari(name, d[key])

print("\n[3] leave-one-channel-out (3-channel features, recording level)")
loo = d["loo"]
for drop in range(4):
    vals = np.array([ari_for(loo[:, drop, :], s) for s in range(N_SEEDS)])
    print("  drop %d  ARI = %.3f [%.3f, %.3f]"
          % (drop, vals.mean(), vals.min(), vals.max()))

print("\n[4] bipolar multiband PLV: dataset ARI (reference-free)")
plv = d["plv_bp"]
for k in (2, 3):
    vals = np.array([ari_for(plv, s, k=k) for s in range(N_SEEDS)])
    print("  K=%d PLV-bipolar ARI = %.3f [%.3f, %.3f]"
          % (k, vals.mean(), vals.min(), vals.max()))

print("\n[5] bad-channel flags (robust within-recording variance z + flatline)")
bad = d["bad"]
shared = ["F3", "F4", "O1", "O2"]
for j, c in enumerate(shared):
    print("  %s flagged in %d recordings" % (c, int(bad[:, j].sum())))
for ds in DS:
    m = dss == ds
    print("  %s: %d/%d recordings with >=1 flagged shared channel"
          % (ds, int(np.any(bad[m], axis=1).sum()), int(m.sum())))
print("\ndone.")
