#!/usr/bin/env python3
"""
Subject-cluster bootstrap for the EEG environment recovery.

The recording is the feature/estimation unit, but the independent statistical unit
is the subject. ds007541 contributes multiple recordings per subject, so a
recording-level bootstrap would overstate effective sample size. We report:

  (1) recording-level point estimate (reproduce .608) and the unique subjects it
      actually uses, alongside the subject-level aggregated point estimate;
  (2) three bootstrap 95% CIs for the oracle K=3 ARI:
        - subject-level aggregate bootstrap (primary, balanced),
        - cluster bootstrap that resamples subjects and keeps all their recordings,
        - naive recording bootstrap (overconfident contrast);
  (3) a subject-level permutation p-value (independent unit = subject);
  (4) subject-level bootstrap CIs for the three paired K=2 recoveries.

No metadata enters the fit; dataset labels are used only for post-hoc evaluation.
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

NPZ = "figures/recording_features.npz"
B = 500
N_PER = 30
K3 = 3

d = np.load(NPZ, allow_pickle=True)
feats, dss, subs = d["features"], d["datasets"], d["subjects"]
DS = sorted(set(dss))


def ari(Xf, y, k, seed):
    X = StandardScaler().fit_transform(Xf)
    lab = KMeans(k, n_init=50, random_state=seed).fit_predict(X)
    return adjusted_rand_score(y, lab)


# ---- subject-level aggregation: one row per subject ----
subj_feat, subj_ds = [], []
for ds in DS:
    for s in sorted(set(subs[dss == ds])):
        subj_feat.append(feats[(dss == ds) & (subs == s)].mean(axis=0))
        subj_ds.append(ds)
subj_feat = np.array(subj_feat)
subj_ds = np.array(subj_ds)


def draw_subject(seed):
    """30 subjects per source, resampled with replacement (balanced subject design)."""
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        pool = np.where(subj_ds == ds)[0]
        idx = r.choice(pool, N_PER, replace=True)
        Xf.append(subj_feat[idx])
        y.append(np.full(N_PER, ds))
    return np.vstack(Xf), np.concatenate(y)


def draw_cluster_rec(seed):
    """Resample 30 subjects per source; keep ALL their recordings (cluster bootstrap)."""
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        names = sorted(set(subs[dss == ds]))
        for s in r.choice(names, N_PER, replace=True):
            idx = np.where((dss == ds) & (subs == s))[0]
            Xf.append(feats[idx])
            y.append(np.full(len(idx), ds))
    return np.vstack(Xf), np.concatenate(y)


def draw_rec_naive(seed):
    """Naive: resample 30 recordings per source independently (ignores subject)."""
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, N_PER, replace=True)
        Xf.append(feats[idx])
        y.append(np.full(N_PER, ds))
    return np.vstack(Xf), np.concatenate(y)


def ci(vals):
    return (np.percentile(vals, 2.5), np.percentile(vals, 97.5))


# ============ (1) point estimates ============
print("=== (1) point estimates, oracle K=3, balanced ===")
# recording-level balanced subset, seed 0 (same rule as delve_third_dataset)
r0 = np.random.default_rng(0)
Xf, y, chosen_idx = [], [], []
for ds in DS:
    pool = np.where(dss == ds)[0]
    idx = r0.choice(pool, N_PER, replace=False)
    Xf.append(feats[idx]); y.append(np.full(N_PER, ds)); chosen_idx.append(idx)
Xf, y, chosen_idx = np.vstack(Xf), np.concatenate(y), np.concatenate(chosen_idx)
obs_rec = ari(Xf, y, K3, 0)
print("  recording-level: ARI=%.3f (M=%d)" % (obs_rec, len(y)))
for ds in DS:
    m = y == ds
    print("    %s: %d recordings from %d unique subjects"
          % (ds, m.sum(), len(set(subs[chosen_idx[m]]))))
obs_subj = ari(*draw_subject(0), K3, 0)
print("  subject-level aggregate: ARI=%.3f" % obs_subj)

# ============ (2) bootstrap CIs ============
print("\n=== (2) bootstrap 95%% CI for ARI (B=%d) ===" % B)
boot_subj = np.array([ari(*draw_subject(100 + b), K3, 100 + b) for b in range(B)])
boot_clust = np.array([ari(*draw_cluster_rec(200 + b), K3, 200 + b) for b in range(B)])
boot_naive = np.array([ari(*draw_rec_naive(300 + b), K3, 300 + b) for b in range(B)])
for name, v in (("subject-level aggregate (primary)", boot_subj),
                ("cluster, keep all recordings", boot_clust),
                ("naive recording (contrast)", boot_naive)):
    lo, hi = ci(v)
    print("  %-34s mean=%.3f CI=[%.3f, %.3f] width=%.3f"
          % (name, v.mean(), lo, hi, hi - lo))

# ============ (3) subject-level permutation ============
print("\n=== (3) subject-level permutation (B=%d, independent unit=subject) ===" % B)
null = []
for b in range(B):
    Xf, yy = draw_subject(500 + b)
    null.append(ari(Xf, np.random.default_rng(900 + b).permutation(yy), K3, 500 + b))
null = np.array(null)
p = (1 + np.sum(null >= obs_subj)) / (B + 1)
print("  obs(subject)=%.3f null mean=%.3f p95=%.3f perm-p=%.4f (min 1/(B+1)=%.4f)"
      % (obs_subj, null.mean(), np.percentile(null, 95), p, 1 / (B + 1)))

# ============ (4) paired K=2 subject-level CIs ============
print("\n=== (4) paired K=2 subject-level bootstrap CI (B=%d) ===" % B)
for i in range(len(DS)):
    for j in range(i + 1, len(DS)):
        a, b = DS[i], DS[j]
        vals = []
        for bb in range(B):
            r = np.random.default_rng(700 + bb)
            Xf, yy = [], []
            for ds in (a, b):
                pool = np.where(subj_ds == ds)[0]
                idx = r.choice(pool, N_PER, replace=True)
                Xf.append(subj_feat[idx]); yy.append(np.full(N_PER, ds))
            vals.append(ari(np.vstack(Xf), np.concatenate(yy), 2, 700 + bb))
        vals = np.array(vals)
        lo, hi = ci(vals)
        print("  %-9s + %-9s mean=%.3f CI=[%.3f, %.3f]" % (a, b, vals.mean(), lo, hi))
