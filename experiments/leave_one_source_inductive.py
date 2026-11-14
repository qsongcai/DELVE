#!/usr/bin/env python3
"""
Leave-one-source inductive (novelty) test for the EEG environment recovery.

This is the genuine generalization test that the pooled label-recovery experiments
do not provide. For each source held out in turn:

  * fit StandardScaler and a K=2 KMeans on the other two (balanced) sources only;
  * freeze the scaler and the two centers;
  * map the unseen source through the frozen objects and measure its nearest-center
    distance. A pre-specified novelty rule (threshold = 95th percentile of training
    nearest-center distances, fixed before looking at the held-out source) flags
    unseen recordings. We report the flag fraction, an ROC AUC separating unseen
    from seen, the standardized mean distance difference (Cohen's d), and the
    nearest-center assignment (descriptive geometry only).

A cross-fitted K=3 block (all three environments present in training, held-out
fold assigned by frozen centers) exercises the DELVE-IS inductive guarantee on
real EEG and reports held-out ARI and per-source assignment accuracy.

Both a recording-level and a subject-aggregated (one row per subject) version are
run. No metadata enters any fit; source labels are used only for post-hoc scoring.
Nothing is tuned to force a positive result.
"""
import os
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, roc_auc_score

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "recording_features.npz")
N_PER = 30          # balanced rows per source
N_SEEDS = 6
Q = 0.95            # novelty threshold quantile, fixed on training only
K_TRAIN = 2         # two seen sources
K_ALL = 3

d = np.load(NPZ, allow_pickle=True)
feats, dss, subs = d["features"], d["datasets"], d["subjects"]
DS = sorted(set(dss))

# ---- subject-aggregated rows (one row per subject) ----
sf, sd = [], []
for ds in DS:
    for s in sorted(set(subs[dss == ds])):
        sf.append(feats[(dss == ds) & (subs == s)].mean(axis=0))
        sd.append(ds)
sub_feat, sub_ds = np.array(sf), np.array(sd)


def balanced_rows(Xf, y, seed, n_per=N_PER):
    """Draw n_per rows per source without replacement."""
    r = np.random.default_rng(seed)
    xi, yi = [], []
    for ds in DS:
        pool = np.where(y == ds)[0]
        n = min(n_per, len(pool))
        idx = r.choice(pool, n, replace=False)
        xi.append(Xf[idx]); yi.append(y[idx])
    return np.vstack(xi), np.concatenate(yi)


def nearest_center_dist(X, centers):
    return np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2).min(axis=1)


def cohen_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (a.mean() - b.mean()) / sp if sp > 0 else np.nan


def novelty_fold(held, Xf, y, seed):
    """Train on the two sources != held; score the held-out source."""
    seen = [s for s in DS if s != held]
    tr_mask = np.isin(y, seen)
    Xtr0, ytr = balanced_rows(Xf[tr_mask], y[tr_mask], seed)
    sc = StandardScaler().fit(Xtr0)
    Xtr = sc.transform(Xtr0)
    km = KMeans(K_TRAIN, n_init=50, random_state=seed).fit(Xtr)
    d_tr = nearest_center_dist(Xtr, km.cluster_centers_)
    thr = np.quantile(d_tr, Q)

    Xte = sc.transform(Xf[y == held])
    d_te = nearest_center_dist(Xte, km.cluster_centers_)
    assign = np.linalg.norm(Xte[:, None, :] - km.cluster_centers_[None, :, :], axis=2).argmin(axis=1)

    ytrue = np.concatenate([np.zeros(len(d_tr)), np.ones(len(d_te))])
    auc = roc_auc_score(ytrue, np.concatenate([d_tr, d_te]))
    flag = np.mean(d_te > thr)
    fa = np.mean(d_tr > thr)
    frac = [np.mean(assign == k) for k in range(K_TRAIN)]
    return dict(auc=auc, flag=flag, fa=fa, d=cohen_d(d_te, d_tr),
                tr=d_tr.mean(), te=d_te.mean(), frac=frac)


def crossfit_k3(seed):
    """All three sources in training (20/each); held-out 10/each assigned by frozen K=3."""
    Xb, yb = balanced_rows(feats, dss, seed)
    r = np.random.default_rng(1000 + seed)
    tr_idx, te_idx = [], []
    for ds in DS:
        pool = np.where(yb == ds)[0]
        r.shuffle(pool)
        tr_idx.append(pool[:20]); te_idx.append(pool[20:30])
    tr_idx, te_idx = np.concatenate(tr_idx), np.concatenate(te_idx)
    sc = StandardScaler().fit(Xb[tr_idx])
    Xtr = sc.transform(Xb[tr_idx]); Xte = sc.transform(Xb[te_idx])
    km = KMeans(K_ALL, n_init=50, random_state=seed).fit(Xtr)
    pred = nearest_center_dist(Xte, km.cluster_centers_)  # placeholder
    pred = np.linalg.norm(Xte[:, None, :] - km.cluster_centers_[None, :, :], axis=2).argmin(axis=1)
    yte = yb[te_idx]
    ari = adjusted_rand_score(yte, pred)

    # Hungarian alignment for per-source accuracy
    cm = np.zeros((K_ALL, K_ALL), dtype=int)
    for t, p in zip(yte, pred):
        cm[DS.index(t), p] += 1
    ri, ci = linear_sum_assignment(-cm)
    aligned = {DS[ri[i]]: ci[i] for i in range(K_ALL)}
    acc = {ds: np.mean(pred[yte == ds] == aligned[ds]) for ds in DS}
    return ari, acc


def summarize(level, Xf, y):
    print("\n################ %s level ################" % level)
    for held in DS:
        rows = [novelty_fold(held, Xf, y, s) for s in range(N_SEEDS)]
        auc = np.array([r["auc"] for r in rows]); flag = np.array([r["flag"] for r in rows])
        cd = np.array([r["d"] for r in rows]); fa = np.array([r["fa"] for r in rows])
        trm = np.array([r["tr"] for r in rows]); tem = np.array([r["te"] for r in rows])
        fr = np.array([r["frac"] for r in rows])
        print("\nheld-out %s (mean over %d seeds [range]):" % (held, N_SEEDS))
        print("  novelty AUC   = %.3f [%.3f, %.3f]" % (auc.mean(), auc.min(), auc.max()))
        print("  flag fraction = %.3f [%.3f, %.3f]  (training false-alarm %.3f, nominal %.2f)"
              % (flag.mean(), flag.min(), flag.max(), fa.mean(), 1 - Q))
        print("  Cohen's d     = %.3f [%.3f, %.3f]" % (cd.mean(), cd.min(), cd.max()))
        print("  mean dist     seen %.3f  unseen %.3f" % (trm.mean(), tem.mean()))
        print("  assign to seen centers (mean fractions) = [%.3f, %.3f]"
              % (fr[:, 0].mean(), fr[:, 1].mean()))


print("=" * 60)
print("LEAVE-ONE-SOURCE INDUCTIVE (NOVELTY) TEST, %d seeds, threshold Q=%.2f" % (N_SEEDS, Q))
print("=" * 60)
summarize("recording", feats, dss)
summarize("subject", sub_feat, sub_ds)

print("\n################ cross-fitted K=3 inductive assignment ################")
aris, accs = [], []
for s in range(N_SEEDS):
    a, acc = crossfit_k3(s)
    aris.append(a); accs.append(acc)
print("held-out ARI = %.3f [%.3f, %.3f] over %d seeds" %
      (np.mean(aris), np.min(aris), np.max(aris), N_SEEDS))
for ds in DS:
    v = np.array([a[ds] for a in accs])
    print("  %-9s assignment accuracy = %.3f [%.3f, %.3f]" % (ds, v.mean(), v.min(), v.max()))
print("\ndone.")
