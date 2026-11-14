#!/usr/bin/env python3
"""R1 M7: device/metadata simple baselines, same-device and same-task controls.

Runs entirely from recording_features.npz (no mne / GPU needed).
Mirrors the pipeline preprocessing (StandardScaler on the 10-d covariance features).
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import adjusted_rand_score, silhouette_score

FEAT_NPZ = "figures/recording_features.npz"


def load():
    d = np.load(FEAT_NPZ, allow_pickle=True)
    return d["features"], d["datasets"], d["subjects"], d["nwin"]


def balanced_idx(y, n_per, seed):
    rng = np.random.default_rng(seed)
    idx = []
    for s in sorted(set(y)):
        pool = np.where(y == s)[0]
        idx += list(rng.choice(pool, min(n_per, len(pool)), replace=False))
    return np.array(idx)


def metadata_table(y, nwin):
    """Real per-source device metadata (constant within source) + nwin."""
    sfreq = {"ds007541": 1000, "ds008099": 128, "on004362": 160}
    nchan = {"ds007541": 8, "ds008099": 14, "on004362": 64}
    fmt = {"ds007541": 0, "ds008099": 1, "on004362": 1}  # BrainVision=0, EDF=1
    M = np.array([[sfreq[s], nchan[s], fmt[s], float(n)] for s, n in zip(y, nwin)])
    return M


def main():
    X, y, sub, nwin = load()
    sources = sorted(set(y))

    print("=== B1: metadata-only baselines ===")
    # nwin alone: simple range rule is exact; report via a decision tree CV
    nw = nwin.reshape(-1, 1).astype(float)
    tree = DecisionTreeClassifier(random_state=0)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    acc_nw = cross_val_score(tree, nw, y, cv=cv)
    print("nwin-only decision-tree CV accuracy = %.3f (folds %s)"
          % (acc_nw.mean(), np.round(acc_nw, 3)))
    # ranges
    for s in sources:
        v = nwin[y == s]
        print("  %-9s nwin range=[%d,%d]" % (s, v.min(), v.max()))
    # full device metadata + nwin
    M = metadata_table(y, nwin)
    for name, clf in [("logistic", LogisticRegression(max_iter=2000)),
                      ("decision-tree", DecisionTreeClassifier(random_state=0))]:
        acc = cross_val_score(clf, M, y, cv=cv)
        print("metadata+%s CV accuracy = %.3f" % (name, acc.mean()))

    print("\n=== B2: same-device control (within-source clustering) ===")
    for s in sources:
        m = y == s
        Xs = StandardScaler().fit_transform(X[m])
        row = "  %-9s n=%d" % (s, m.sum())
        for K in (2, 3):
            lab = KMeans(K, n_init=50, random_state=0).fit_predict(Xs)
            row += " | K=%d silhouette=%.3f" % (K, silhouette_score(Xs, lab))
        print(row)
    # ds007541: only source with repeated recordings per subject -> ARI vs subject
    m = y == "ds007541"
    Xs = StandardScaler().fit_transform(X[m])
    for K in (2, 3):
        lab = KMeans(K, n_init=50, random_state=0).fit_predict(Xs)
        print("  ds007541 within-source K=%d ARI vs subject = %.3f"
              % (K, adjusted_rand_score(sub[m], lab)))

    print("\n=== B3: same-task control (two resting/eyes-open sources, K=2) ===")
    pair = np.array([i for i in range(len(y)) if y[i] in ("ds007541", "on004362")])
    bi = balanced_idx(y[pair], 30, 0)
    Xp = StandardScaler().fit_transform(X[pair][bi])
    yp = y[pair][bi]
    lab = KMeans(2, n_init=50, random_state=0).fit_predict(Xp)
    print("  ds007541+on004362 balanced n=%d ARI=%.3f silhouette=%.3f"
          % (len(yp), adjusted_rand_score(yp, lab), silhouette_score(Xp, lab)))
    # across 3 seeds
    ars = []
    for seed in range(3):
        bi = balanced_idx(y[pair], 30, seed)
        Xp = StandardScaler().fit_transform(X[pair][bi])
        lab = KMeans(2, n_init=50, random_state=seed).fit_predict(Xp)
        ars.append(adjusted_rand_score(y[pair][bi], lab))
    print("  3-seed ARI mean=%.3f range=[%.3f,%.3f]" % (np.mean(ars), min(ars), max(ars)))


if __name__ == "__main__":
    main()
