#!/usr/bin/env python3
"""
Genuine plug-in subject-level ARI on the FULL observed subject set.

The earlier .523 was one balanced resampling draw (seed 0), not a plug-in
statistic. Here we keep every subject exactly once, aggregate their recordings,
and compute a single K-means ARI with no resampling, on the unbalanced counts.
"""
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "recording_features.npz")
d = np.load(NPZ, allow_pickle=True)
feats, dss, subs = d["features"], d["datasets"], d["subjects"]
DS = sorted(set(dss))

rows_feat, rows_ds = [], []
for ds in DS:
    for s in sorted(set(subs[dss == ds])):
        rows_feat.append(feats[(dss == ds) & (subs == s)].mean(axis=0))
        rows_ds.append(ds)
Xf = np.array(rows_feat)
y = np.array(rows_ds)

X = StandardScaler().fit_transform(Xf)
lab = KMeans(3, n_init=50, random_state=0).fit_predict(X)
ari = adjusted_rand_score(y, lab)

print("plug-in subject-level ARI (full set, no resampling): %.3f" % ari)
print("total subjects:", len(y))
for ds in DS:
    print("  %-9s subjects=%d" % (ds, (y == ds).sum()))
