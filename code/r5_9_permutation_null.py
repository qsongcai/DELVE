#!/usr/bin/env python3
"""R5 problem 9: permutation null for the balanced ARI."""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

d = np.load("figures/recording_features.npz")
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
N_PERM = 2000


def balanced(seed):
    rng = np.random.default_rng(seed); xf, y = [], []
    for src in DS:
        idx = rng.choice(np.where(dss == src)[0], 30, replace=False)
        xf.append(feats[idx]); y.append(np.full(30, src))
    X = StandardScaler().fit_transform(np.vstack(xf))
    return X, np.concatenate(y)


obs_ari = []
null_max = []
for seed in range(6):
    X, y = balanced(seed)
    lab = KMeans(3, n_init=50, random_state=seed).fit_predict(X)
    obs = adjusted_rand_score(y, lab)
    rng = np.random.default_rng(5000 + seed)
    null = np.array([adjusted_rand_score(rng.permutation(y), lab)
                     for _ in range(N_PERM)])
    obs_ari.append(obs)
    null_max.append(np.quantile(null, .99))
    print("seed %d: observed ARI %.3f | perm null mean %.3f q95 %.3f q99 %.3f"
          % (seed, obs, null.mean(), np.quantile(null, .95),
             np.quantile(null, .99)))

print("\nall observed ARI above the 99th permutation quantile:",
      all(o > q for o, q in zip(obs_ari, null_max)))
np.savez("figures/r5_9_permutation_null.npz",
         obs=np.array(obs_ari), null_q99=np.array(null_max))
