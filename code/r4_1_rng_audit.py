import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import delve_core as dc

d = np.load("figures/recording_features.npz", allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
saved = np.load("figures/blind_perseed.npz")


def balanced(seed):
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, 30, replace=False)
        Xf.append(feats[idx])
        y.append(np.full(30, ds))
    return StandardScaler().fit_transform(np.vstack(Xf)), np.concatenate(y)


first_rs = np.random.default_rng(2026).integers(1 << 30)
print("fresh default_rng(2026) first KMeans random_state integer =", int(first_rs))
print()
print("seed | oracle rs=seed ARI | blind selectedK | blind ARI@sel(npz) | blind fit_partition ARI")
for s in range(6):
    X, y = balanced(s)
    oracle = KMeans(3, n_init=50, random_state=s).fit_predict(X)
    a_oracle = adjusted_rand_score(y, oracle)
    chosen = int(saved["selK"][s])
    lab, _, _ = dc.fit_partition(X, chosen, np.random.default_rng(2026))
    a_blind = adjusted_rand_score(y, lab)
    print(f"{s} | {a_oracle:.3f} | {chosen} | {saved['ariSel'][s]:.3f} | {a_blind:.3f}")
