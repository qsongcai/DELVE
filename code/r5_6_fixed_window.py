#!/usr/bin/env python3
"""R5 problem 6: fixed window-count (k=9) recording-level recovery.

Re-extracts window features, subsamples the same number of windows per
recording, then runs the balanced 30/source K=3 protocol over six clustering
seeds. Full-window baseline is recomputed for direct comparison.
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import delve_third_dataset as d3

K_FIX = 9
N_RESAMPLE = 10
CLUSTER_SEEDS = [0, 1, 2, 3, 4, 5]


def collect_with_windows():
    recs = []
    specs = [
        ("ds007541",
         sorted((d3.DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr")),
         lambda v: d3.mne.io.read_raw_brainvision(v, verbose=False)),
        ("ds008099",
         sorted((d3.DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf")),
         lambda v: d3.mne.io.read_raw_edf(v, verbose=False, preload=False)),
        ("on004362",
         sorted((d3.DATA / "on004362").glob("*R01.edf")),
         d3.read_4362),
    ]
    for ds, files, reader in specs:
        for p in files:
            try:
                f = d3.windows_of(p, reader)
            except Exception as e:
                print("  FAIL", ds, p.name, e)
                continue
            if len(f) < 3:
                continue
            subj = p.name.split("R01")[0] if ds == "on004362" else (
                next(x for x in p.parts if x.startswith("sub-")))
            recs.append(dict(dataset=ds, subject=f"{ds}:{subj}",
                             wfeats=f, nwin=len(f)))
        print("done", ds, sum(r["dataset"] == ds for r in recs))
    return recs


def balanced_idx(dss, seed):
    r = np.random.default_rng(seed)
    idx_all, y = [], []
    for ds in sorted(set(dss)):
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, 30, replace=False)
        idx_all.append(idx)
        y.append(np.full(30, ds))
    return np.concatenate(idx_all), np.concatenate(y)


def ari_for_features(feats, dss, seed):
    idx, y = balanced_idx(dss, seed)
    X = StandardScaler().fit_transform(feats[idx])
    lab = KMeans(3, n_init=50, random_state=seed).fit_predict(X)
    return adjusted_rand_score(y, lab)


def main():
    recs = collect_with_windows()
    dss = np.array([r["dataset"] for r in recs])
    n = len(recs)
    print("total recordings:", n)

    # full-window baseline
    full = np.array([r["wfeats"].mean(axis=0) for r in recs])
    base = [ari_for_features(full, dss, s) for s in CLUSTER_SEEDS]
    print("full-window ARI per seed:", np.round(base, 3))
    print("full-window mean +/- std: %.3f +/- %.3f" % (np.mean(base), np.std(base)))

    # fixed window count
    grid = np.zeros((N_RESAMPLE, len(CLUSTER_SEEDS)))
    for rr in range(N_RESAMPLE):
        rng = np.random.default_rng(9000 + rr)
        fe = np.zeros((n, full.shape[1]))
        for i, r in enumerate(recs):
            w = r["wfeats"]
            pick = rng.choice(len(w), K_FIX, replace=(len(w) < K_FIX))
            fe[i] = w[pick].mean(axis=0)
        for j, s in enumerate(CLUSTER_SEEDS):
            grid[rr, j] = ari_for_features(fe, dss, s)
        print("resample %d ARI: %s" % (rr, np.round(grid[rr], 3)))

    flat = grid.reshape(-1)
    print("fixed-k=%d pooled mean +/- std: %.3f +/- %.3f"
          % (K_FIX, flat.mean(), flat.std()))
    print("fixed-k per-cluster-seed mean:", np.round(grid.mean(0), 3))
    np.savez("/mnt/sdd1/datasets_qsong/r5_6_fixed_window.npz",
             full=np.array(base), fixed=grid, k=K_FIX)


if __name__ == "__main__":
    main()
