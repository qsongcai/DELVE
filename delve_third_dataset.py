#!/usr/bin/env python3
"""
DELVE third independent EEG source validation (self-contained, GPU).
Adds PhysioNet eegmmidb (on004362; R01 eyes-open baseline) alongside ds007541
and ds008099, under the SAME blind protocol:
  4 shared channels F3/F4/O1/O2, 128 Hz, common-average reference, 4s windows,
  LedoitWolf + logm covariance, recording-level equal-weight aggregation, StandardScaler.
Reports:
  (A) three-dataset balanced recovery (oracle K=3 + estimated K), K sensitivity,
      recording-level permutation, balance across seeds;
  (B) all three pairwise cross-dataset recoveries (repeatability, not one pair);
  (C) within-dataset check for the new source;
  (D) unbalanced all-available robustness run.
Blind: metadata never used in estimation; dataset/subject used only post-hoc.
"""
import os
import warnings
from pathlib import Path
import numpy as np
from scipy.linalg import logm
from sklearn.covariance import LedoitWolf
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
import mne
import delve_core as bc

warnings.filterwarnings("ignore")
DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
DATA = Path(DATA_DIR, "eegdash_data")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0
ti0 = np.triu_indices(len(SHARED), k=0)


def read_4362(p):
    raw = mne.io.read_raw_edf(p, preload=False, verbose=False)
    raw.rename_channels({c: c.rstrip(".") for c in raw.ch_names})
    return raw


def windows_of(path, reader):
    raw = reader(path)
    raw.pick(SHARED).load_data()
    raw.set_eeg_reference("average", verbose=False)
    raw.filter(1.0, 40.0, verbose=False)
    raw.notch_filter(50.0, verbose=False)
    raw.resample(RESAMPLE, verbose=False)
    data, fs = raw.get_data(), raw.info["sfreq"]
    wl = int(WIN_S * fs)
    feats = []
    for stt in range(0, data.shape[1] - wl + 1, wl):
        seg = data[:, stt:stt + wl]
        C = LedoitWolf().fit(seg.T).covariance_
        feats.append(logm(C).real[ti0])
    return np.array(feats)


def collect():
    specs = [
        ("ds007541",
         sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr")),
         lambda v: mne.io.read_raw_brainvision(v, verbose=False)),
        ("ds008099",
         sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf")),
         lambda v: mne.io.read_raw_edf(v, verbose=False, preload=False)),
        ("on004362",
         sorted((DATA / "on004362").glob("*R01.edf")),
         read_4362),
    ]
    recs = []
    for ds, files, reader in specs:
        ok = 0
        for p in files:
            try:
                f = windows_of(p, reader)
            except Exception as e:
                print("  FAIL", ds, p.name, e)
                continue
            if len(f) < 3:
                continue
            subj = p.name.split("R01")[0] if ds == "on004362" else (
                next(x for x in p.parts if x.startswith("sub-")))
            recs.append(dict(dataset=ds, subject=f"{ds}:{subj}",
                             feature=f.mean(axis=0), nwin=len(f)))
            ok += 1
        print(f"loaded {ds}: {ok} recordings")
    return recs


def matrix(recs_subset):
    X = StandardScaler().fit_transform(np.array([r["feature"] for r in recs_subset]))
    y = np.array([r["dataset"] for r in recs_subset])
    return X, y


def km(X, K, seed):
    return KMeans(K, n_init=50, random_state=seed).fit_predict(X)


def balanced(recs, n_per, seed):
    rng = np.random.default_rng(seed)
    out = []
    for ds in sorted(set(r["dataset"] for r in recs)):
        pool = [r for r in recs if r["dataset"] == ds]
        idx = rng.choice(len(pool), min(n_per, len(pool)), replace=False)
        out += [pool[i] for i in idx]
    return out


def main():
    recs = collect()
    for ds in sorted(set(r["dataset"] for r in recs)):
        nw = [r["nwin"] for r in recs if r["dataset"] == ds]
        print(f"  {ds}: n={len(nw)} windows/rec min/med={min(nw)}/{int(np.median(nw))}")
    rng = np.random.default_rng(0)

    print("\n=== (A) three-dataset balanced recovery, n_per=30 ===")
    sub = balanced(recs, 30, 0)
    X, y = matrix(sub)
    print("  M=%d per-dataset counts=%s" % (len(X), {d: int((y == d).sum())
          for d in sorted(set(y))}))
    for K in range(2, 7):
        lab = km(X, K, 0)
        print("  K=%d ARI=%.3f NMI=%.3f silhouette=%.3f"
              % (K, adjusted_rand_score(y, lab), normalized_mutual_info_score(y, lab),
                 silhouette_score(X, lab)))
    # oracle K=3 with both KMeans and GMM
    lab3 = km(X, 3, 0)
    g3 = GaussianMixture(3, n_init=8, reg_covar=1e-4, random_state=0).fit_predict(X)
    print("  oracle K=3: KMeans ARI=%.3f NMI=%.3f | GMM ARI=%.3f NMI=%.3f"
          % (adjusted_rand_score(y, lab3), normalized_mutual_info_score(y, lab3),
             adjusted_rand_score(y, g3), normalized_mutual_info_score(y, g3)))
    # estimated K (blind, data-driven within candidate grid)
    chosen, metrics = bc.select_K(X, list(range(2, 7)), np.random.default_rng(2026))
    for K in range(2, 7):
        m = metrics[K]
        print("  selectK K=%d bic=%.1f sil=%.3f stability=%.3f"
              % (K, m["bic"], m["silhouette"], m["stability"]))
    print("  -> estimated K=%d (oracle=3)" % chosen)
    # recording-level permutation at oracle K=3
    obs = adjusted_rand_score(y, km(X, 3, 0))
    B = 200
    null = [adjusted_rand_score(rng.permutation(y), km(X, 3, 0)) for _ in range(B)]
    frac = (1 + np.sum(np.array(null) >= obs)) / (B + 1)
    print("  permutation B=%d obs=%.3f null mean=%.3f p95=%.3f perm-p<%.4f"
          % (B, obs, np.mean(null), np.percentile(null, 95), 1 / (B + 1)))
    print("  exact permutation fraction=%.4f" % frac)
    # balance across seeds
    ars = []
    for s in range(6):
        Xs, ys = matrix(balanced(recs, 30, s))
        ars.append(adjusted_rand_score(ys, km(Xs, 3, s)))
    print("  balanced across 6 seeds: ARI mean=%.3f range=[%.3f,%.3f]"
          % (np.mean(ars), np.min(ars), np.max(ars)))

    print("\n=== (B) pairwise cross-dataset recovery (K=2, n_per=30, 3 seeds) ===")
    dss = sorted(set(r["dataset"] for r in recs))
    for i in range(len(dss)):
        for j in range(i + 1, len(dss)):
            a, b = dss[i], dss[j]
            pair = [r for r in balanced(recs, 30, 0) if r["dataset"] in (a, b)]
            ar = []
            for s in range(3):
                Xp, yp = matrix([r for r in balanced(recs, 30, s)
                                 if r["dataset"] in (a, b)])
                ar.append(adjusted_rand_score(yp, km(Xp, 2, s)))
            Xp, yp = matrix(pair)
            print("  %-9s + %-9s ARI mean=%.3f range=[%.3f,%.3f] NMI=%.3f"
                  % (a, b, np.mean(ar), np.min(ar), np.max(ar),
                     normalized_mutual_info_score(yp, km(Xp, 2, 0))))

    print("\n=== (C) within-dataset check: on004362 alone (no dataset boundary) ===")
    pool = [r for r in recs if r["dataset"] == "on004362"]
    Xw, _ = matrix(pool)
    for K in (2, 3):
        lab = km(Xw, K, 0)
        print("  K=%d silhouette=%.3f (subject labels unique/recording)"
              % (K, silhouette_score(Xw, lab)))

    print("\n=== (D) all-available unbalanced robustness run ===")
    Xa, ya = matrix(recs)
    print("  M=%d counts=%s" % (len(recs), {d: int((ya == d).sum())
          for d in sorted(set(ya))}))
    for K in (2, 3):
        lab = km(Xa, K, 0)
        print("  K=%d ARI=%.3f NMI=%.3f silhouette=%.3f"
              % (K, adjusted_rand_score(ya, lab), normalized_mutual_info_score(ya, lab),
                 silhouette_score(Xa, lab)))


if __name__ == "__main__":
    main()
