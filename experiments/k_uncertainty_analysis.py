#!/usr/bin/env python3
"""
Formal experiment: How does uncertainty in K affect environment recovery?
Reuses the exact blind balanced protocol from delve_third_dataset (same features,
n_per=30, StandardScaler). Independent unit = recording.
Outputs:
  (1) K=2..6 ARI/NMI/silhouette curves;
  (2) K=2 contingency: which two real sources are merged;
  (3) whether the same pair is systematically merged across balanced seeds;
  (4) K=2 vs K=3 reassignment (merged sources split at K=3);
  (5) oracle-K=3 vs estimated-K=2 performance gap and select_K rationale.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
import delve_third_dataset as d3
import delve_core as bc


def km(X, K, seed):
    return KMeans(K, n_init=50, random_state=seed).fit_predict(X)


def crosstab(y, lab, datasets):
    k = int(lab.max()) + 1
    tab = np.zeros((len(datasets), k), dtype=int)
    for i, ds in enumerate(datasets):
        for c in range(k):
            tab[i, c] = int(np.sum((y == ds) & (lab == c)))
    return tab


def merged_pair(tab, datasets):
    # dominant dataset of each cluster; the cluster whose two largest rows are both
    # sizable is the one absorbing two sources
    dom = tab.argmax(axis=0)
    pairs = []
    for c in range(tab.shape[1]):
        order = np.argsort(-tab[:, c])
        top = [datasets[i] for i in order[:2]]
        share = tab[order[1], c] / max(tab[:, c].sum(), 1)
        pairs.append((c, top[0], top[1], round(share, 2)))
    return pairs


def main():
    recs = d3.collect()
    datasets = sorted(set(r["dataset"] for r in recs))

    print("=== (1) K=2..6 curves on balanced 90 (seed 0) ===")
    sub = d3.balanced(recs, 30, 0)
    X, y = d3.matrix(sub)
    for K in range(2, 7):
        lab = km(X, K, 0)
        print("  K=%d ARI=%.3f NMI=%.3f sil=%.3f"
              % (K, adjusted_rand_score(y, lab), normalized_mutual_info_score(y, lab),
                 silhouette_score(X, lab)))

    print("\n=== (2) K=2 contingency (rows=true dataset, cols=cluster) ===")
    lab2 = km(X, 2, 0)
    tab = crosstab(y, lab2, datasets)
    print("           " + "".join("cluster%d  " % c for c in range(2)))
    for i, ds in enumerate(datasets):
        print("  %-9s " % ds + "".join("%6d    " % v for v in tab[i]))
    print("  merge diagnosis (cluster, dominant, second source, second share):",
          merged_pair(tab, datasets))

    print("\n=== (3) is the same pair systematically merged across 6 balanced seeds? ===")
    seen = []
    for s in range(6):
        Xs, ys = d3.matrix(d3.balanced(recs, 30, s))
        l2 = km(Xs, 2, s)
        tb = crosstab(ys, l2, datasets)
        # record the second-source (the absorbed one) per merged cluster
        pairs = [tuple(sorted([a, b])) for _, a, b, sh in merged_pair(tb, datasets) if sh > .15]
        seen.append(tuple(sorted(set(pairs))))
    for s, p in enumerate(seen):
        print("  seed %d merged pairs=%s" % (s, p))

    print("\n=== (4) K=2 -> K=3 reassignment (do merged sources split?) ===")
    lab3 = km(X, 3, 0)
    for c in range(2):
        m = lab2 == c
        print("  K=2 cluster %d (n=%d): distribution at K=3 = %s"
              % (c, m.sum(), {int(k): int(np.sum(m & (lab3 == k))) for k in range(3)}))

    print("\n=== (5) oracle vs estimated gap + select_K rationale ===")
    chosen, metrics = bc.select_K(X, list(range(2, 7)), np.random.default_rng(2026))
    for K in range(2, 7):
        m = metrics[K]
        print("  K=%d bic=%.1f sil=%.3f stability=%.3f"
              % (K, m["bic"], m["silhouette"], m["stability"]))
    print("  estimated K=%d (oracle=3)" % chosen)
    print("  ARI gap: estimated K=2 %.3f vs oracle K=3 %.3f"
          % (adjusted_rand_score(y, lab2), adjusted_rand_score(y, lab3)))
    print("  NMI gap: %.3f vs %.3f"
          % (normalized_mutual_info_score(y, lab2), normalized_mutual_info_score(y, lab3)))


if __name__ == "__main__":
    main()
