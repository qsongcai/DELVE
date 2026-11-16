#!/usr/bin/env python3
"""
DELVE strong baselines & cross-dataset controls (self-contained, GPU).
Harmonization: 4 shared channels F3/F4/O1/O2, 128 Hz, common-average, 4s windows.
Covers:
  (1) two independent sources ds007541 + ds008099;
  (2) covariance representations: Empirical/LedoitWolf/OAS x logm/raw/sqrtm;
  (3) clusterers: KMeans/GMM/Agglomerative(ward,complete,average)/Spectral;
  (4) non-covariance features: band power, correlation, PLV, PLI;
  (5) K sensitivity K=2..6;
  (6) recording- vs subject-level statistics;
  (7) de-confounding controls: within-dataset clustering, dataset-label permutation,
      balanced windows.
Blind protocol: estimation never uses metadata; dataset/subject/session used only post-hoc.
"""
import warnings
from pathlib import Path
import numpy as np
from scipy.linalg import logm, sqrtm
from scipy.signal import welch, butter, sosfiltfilt, hilbert
from sklearn.covariance import EmpiricalCovariance, LedoitWolf, OAS
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import (KMeans, AgglomerativeClustering, SpectralClustering)
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
import mne

warnings.filterwarnings("ignore")
DATA = Path("/mnt/sdd1/datasets_qsong/eegdash_data")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0
PBANDS = [(1, 4), (4, 8), (8, 13), (13, 30)]            # power
NBANDS = [(4, 8), (8, 13), (13, 30)]                    # connectivity
ti0 = np.triu_indices(len(SHARED), k=0)
ti1 = np.triu_indices(len(SHARED), k=1)


def sub_of(v):
    return next(p for p in v.parts if p.startswith("sub-"))


def vech(A):
    return A[ti0]


def cov_estimate(seg_T, kind):
    if kind == "emp":
        return EmpiricalCovariance().fit(seg_T).covariance_
    if kind == "lw":
        return LedoitWolf().fit(seg_T).covariance_
    return OAS().fit(seg_T).covariance_


def map_cov(C, mapping):
    if mapping == "logm":
        return vech(logm(C).real)
    if mapping == "raw":
        return vech(C)
    return vech(sqrtm(C).real)


def process(vhdr, ds_label, reader):
    out = []
    for ri, v in enumerate(vhdr):
        raw = reader(v)
        raw.pick(SHARED).load_data()
        raw.set_eeg_reference("average", verbose=False)
        raw.filter(1.0, 40.0, verbose=False)
        raw.notch_filter(50.0, verbose=False)
        raw.resample(RESAMPLE, verbose=False)
        data, fs = raw.get_data(), raw.info["sfreq"]
        wl = int(WIN_S * fs)
        narrow = {(lo, hi): sosfiltfilt(butter(4, [lo/(fs/2), hi/(fs/2)],
                          btype="band", output="sos"), data, axis=1)
                  for (lo, hi) in NBANDS}
        sid = f"{ds_label}:{sub_of(v)}"
        for stt in range(0, data.shape[1] - wl + 1, wl):
            seg = data[:, stt:stt + wl]
            # covariance (all 3 estimators)
            covs = {k: cov_estimate(seg.T, k) for k in ("emp", "lw", "oas")}
            # power
            fr, px = welch(seg, fs=fs, nperseg=min(256, wl), axis=1)
            pw = []
            for lo, hi in PBANDS:
                m = (fr >= lo) & (fr <= hi)
                pw.extend(np.log(np.clip(np.trapz(px[:, m], fr[m], axis=1), 1e-12, None)))
            # correlation
            corr = np.corrcoef(seg)[ti1]
            # PLV / PLI per narrow band
            plv, pli = [], []
            for bd in NBANDS:
                nb = narrow[bd][:, stt:stt + wl]
                ph = hilbert(nb, axis=1)
                z = ph / np.abs(ph)
                dphi = z[ti1[0]] * z[ti1[1]].conj()
                plv.append(np.abs(dphi.mean(axis=1)))
                pli.append(np.abs(np.mean(np.sign(dphi.imag), axis=1)))
            out.append(dict(covs=covs, power=np.array(pw), corr=corr,
                            plv=np.concatenate(plv), pli=np.concatenate(pli),
                            dataset=ds_label, subject=sid, rec=f"{ds_label}:{ri}"))
    return out


f7541 = sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr"))
f8099 = sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf"))
rows = (process(f7541, "ds007541", lambda v: mne.io.read_raw_brainvision(v, verbose=False))
        + process(f8099, "ds008099", lambda v: mne.io.read_raw_edf(v, verbose=False, preload=False)))
print("windows=%d recordings=%d subjects=%d"
      % (len(rows), len(set(r["rec"] for r in rows)), len(set(r["subject"] for r in rows))))


def build(rec_ids, feat, K, method="kmeans", seed=0):
    """Aggregate window rows to requested units and return standardized X + labels."""
    X, units = [], sorted(rec_ids)
    for u in units:
        sel = [r for r in rows if r[unit_key] == u]
        if feat.startswith("cov:"):
            _, est, mp = feat.split(":")
            X.append(np.mean([map_cov(r["covs"][est], mp) for r in sel], axis=0))
        else:
            X.append(np.mean([r[feat] for r in sel], axis=0))
    X = StandardScaler().fit_transform(np.array(X))
    return X, units


def cluster(method, X, K, seed=0):
    if method == "kmeans":
        return KMeans(K, n_init=30, random_state=seed).fit_predict(X)
    if method == "gmm":
        return GaussianMixture(K, n_init=8, reg_covar=1e-4, random_state=seed).fit_predict(X)
    linkage = method.split("-")[1] if "-" in method else "ward"
    if method.startswith("agg"):
        return AgglomerativeClustering(K, linkage=linkage).fit_predict(X)
    if method == "spectral":
        return SpectralClustering(K, affinity="nearest_neighbors",
                                  random_state=seed).fit_predict(X)


def truth_for(units, key):
    return np.array([next(r[key] for r in rows if r[unit_key] == u) for u in units])


unit_key = "rec"
rec_ids = set(r["rec"] for r in rows)
sub_ids = set(r["subject"] for r in rows)

print("\n=== (2) covariance representations: KMeans K=2, recording, vs dataset ===")
for est in ("emp", "lw", "oas"):
    for mp in ("logm", "raw", "sqrtm"):
        unit_key = "rec"
        X, units = build(rec_ids, f"cov:{est}:{mp}", 2)
        lab = cluster("kmeans", X, 2)
        t = truth_for(units, "dataset")
        print("  %-4s/%-5s ARI=%.3f NMI=%.3f"
              % (est, mp, adjusted_rand_score(t, lab), normalized_mutual_info_score(t, lab)))

print("\n=== (3) clusterers: LW+logm, K=2, recording, vs dataset ===")
unit_key = "rec"
X, units = build(rec_ids, "cov:lw:logm", 2)
t = truth_for(units, "dataset")
for meth in ("kmeans", "gmm", "agg-ward", "agg-complete", "agg-average", "spectral"):
    lab = cluster(meth, X, 2)
    print("  %-12s ARI=%.3f NMI=%.3f"
          % (meth, adjusted_rand_score(t, lab), normalized_mutual_info_score(t, lab)))

print("\n=== (4) non-covariance features: KMeans K=2, recording, vs dataset ===")
for feat in ("power", "corr", "plv", "pli"):
    unit_key = "rec"
    X, units = build(rec_ids, feat, 2)
    lab = cluster("kmeans", X, 2)
    t = truth_for(units, "dataset")
    print("  %-6s ARI=%.3f NMI=%.3f"
          % (feat, adjusted_rand_score(t, lab), normalized_mutual_info_score(t, lab)))

print("\n=== (5) K sensitivity: LW+logm, KMeans, recording, vs dataset ===")
unit_key = "rec"
X, units = build(rec_ids, "cov:lw:logm", 2)
t = truth_for(units, "dataset")
for K in range(2, 7):
    lab = cluster("kmeans", X, K)
    sil = silhouette_score(X, lab)
    print("  K=%d ARI=%.3f NMI=%.3f silhouette=%.3f"
          % (K, adjusted_rand_score(t, lab), normalized_mutual_info_score(t, lab), sil))

print("\n=== (6) levels: LW+logm, KMeans K=2, vs dataset ===")
for lvl, ids in (("recording", rec_ids), ("subject", sub_ids)):
    unit_key = "rec" if lvl == "recording" else "subject"
    X, units = build(ids, "cov:lw:logm", 2)
    lab = cluster("kmeans", X, 2)
    t = truth_for(units, "dataset")
    print("  %-9s units=%d ARI=%.3f NMI=%.3f"
          % (lvl, len(units), adjusted_rand_score(t, lab),
             normalized_mutual_info_score(t, lab)))

print("\n=== (7) de-confounding controls ===")
# 7a within-dataset clustering (no dataset label to separate); truth=subject/session
for ds in ("ds007541", "ds008099"):
    ids = set(r["rec"] for r in rows if r["dataset"] == ds)
    unit_key = "rec"
    X, units = build(ids, "cov:lw:logm", 2)
    tsub = truth_for(units, "subject")
    lab = cluster("kmeans", X, 2)
    print("  within %s: n=%d ARI(vs subject)=%.3f"
          % (ds, len(units), adjusted_rand_score(tsub, lab)))
# 7b dataset-label permutation on pooled data
unit_key = "rec"
X, units = build(rec_ids, "cov:lw:logm", 2)
obs = adjusted_rand_score(truth_for(units, "dataset"), cluster("kmeans", X, 2))
rng = np.random.default_rng(0)
null = [adjusted_rand_score(rng.permutation(truth_for(units, "dataset")),
                            cluster("kmeans", X, 2)) for _ in range(200)]
print("  pooled ARI=%.3f | permutation null mean=%.3f p95=%.3f perm-p=%.3f"
      % (obs, np.mean(null), np.percentile(null, 95), np.mean(np.array(null) >= obs)))
# 7c balanced windows: equal recordings per dataset, repeated subsamples
unit_key = "rec"
rids75 = sorted(set(r["rec"] for r in rows if r["dataset"] == "ds007541"))
rids80 = sorted(set(r["rec"] for r in rows if r["dataset"] == "ds008099"))
ars = []
for s in range(6):
    pick = set(rng.choice(rids75, min(len(rids80), len(rids75)), replace=False)) | set(rids80)
    X, units = build(pick, "cov:lw:logm", 2)
    ars.append(adjusted_rand_score(truth_for(units, "dataset"), cluster("kmeans", X, 2, seed=s)))
print("  balanced (n=%d/set) ARI mean=%.3f range=[%.3f,%.3f]"
      % (len(rids80), np.mean(ars), np.min(ars), np.max(ars)))
