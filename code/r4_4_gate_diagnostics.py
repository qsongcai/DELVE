import numpy as np
from sklearn.preprocessing import StandardScaler
import delve_core as dc

d = np.load("figures/recording_features.npz", allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))
GRID = list(range(2, 7))


def balanced(seed):
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, 30, replace=False)
        Xf.append(feats[idx])
        y.append(np.full(30, ds))
    return StandardScaler().fit_transform(np.vstack(Xf)), np.concatenate(y)


rows = []
for s in range(6):
    X, y = balanced(s)
    chosen, metrics = dc.select_K(X, GRID, np.random.default_rng(2026))
    stab = np.array([metrics[K]["stability"] for K in GRID])
    stab_thr = min(0.85, 0.9 * stab.max())
    eligible = [K for K in GRID
                if metrics[K]["stability"] >= stab_thr and metrics[K]["silhouette"] > 0]
    # BIC rank within eligible (lower BIC = rank 1)
    bic_elig = sorted(eligible, key=lambda K: metrics[K]["bic"])
    print(f"=== seed {s} | chosen K={chosen} | stability threshold={stab_thr:.3f} ===")
    print(" K | silhouette | stability | eligible | BIC | BIC rank among eligible")
    for K in GRID:
        elig = K in eligible
        rank = bic_elig.index(K) + 1 if elig else "-"
        print(f" {K} | {metrics[K]['silhouette']:.3f} | {metrics[K]['stability']:.3f} | "
              f"{'yes' if elig else 'no'} | {metrics[K]['bic']:.1f} | {rank}")
    rows.append((s, chosen, stab_thr, metrics, eligible))
    print()

np.save("figures/r4_gate_diagnostics.npy",
        np.array([(s, ch, th) for s, ch, th, _, _ in rows], dtype=object),
        allow_pickle=True)
print("saved figures/r4_gate_diagnostics.npy")
