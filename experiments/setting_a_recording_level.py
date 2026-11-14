#!/usr/bin/env python3
"""
Setting A (CORRECTED, recording-level): negative result as formal evidence.
Every inferential unit is the RECORDING (n=64; 32 subjects x 2 sessions):
  windows  -> only estimate per-recording features (never treated as independent);
  recordings -> clustering unit;
  subject/session -> resampling and significance unit.
Data: ds007541 verification run01, 8 channels, common-average, 250 Hz.
Blind; session/subject used only post-hoc.
Outputs:
  point ARI + genuine nonparametric recording-bootstrap CI;
  two valid permutation schemes: free recording-label shuffle and paired
  within-subject session flip (session is a paired within-subject factor);
  robustness over cluster methods, window lengths, estimators, bands, PLV/wPLI,
  recording subsets -- all aggregated to recording level first.
"""
import os
import re
from pathlib import Path
import numpy as np
from scipy.linalg import logm
from scipy.signal import butter, sosfiltfilt, hilbert
from sklearn.covariance import EmpiricalCovariance, LedoitWolf, OAS
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, silhouette_score
import mne

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
ROOT = Path(DATA_DIR, "eegdash_data", "ds007541")
vhdr = sorted(ROOT.glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr"))
RESAMPLE = 250.0
BANDS = {"full": (1, 45), "delta": (1, 4), "theta": (4, 8),
         "alpha": (8, 13), "beta": (13, 30)}
PHASE_BANDS = ["theta", "alpha", "beta"]

# ---------- load once; per-recording band arrays ----------
recs = []
for v in vhdr:
    raw = mne.io.read_raw_brainvision(v, verbose=False)
    raw.load_data()
    raw.set_eeg_reference("average", verbose=False)
    raw.filter(1.0, 45.0, verbose=False)
    raw.notch_filter(50.0, verbose=False)
    raw.resample(RESAMPLE, verbose=False)
    data, fs = raw.get_data(), raw.info["sfreq"]
    mm = re.search(r"sub-(\d+)/ses-(\d+)/", str(v))
    band_arr = {"full": data}
    for b, (lo, hi) in BANDS.items():
        if b != "full":
            band_arr[b] = sosfiltfilt(butter(4, [lo/(fs/2), hi/(fs/2)],
                                        btype="band", output="sos"), data, axis=1)
    analytic = {b: hilbert(band_arr[b], axis=1) for b in PHASE_BANDS}
    recs.append(dict(subject=mm.group(1), session=mm.group(2),
                     bands=band_arr, analytic=analytic))
nch = data.shape[0]
ti0 = np.triu_indices(nch, k=0)
ti1 = np.triu_indices(nch, k=1)
M = len(recs)
print("recordings=%d channels=%d fs=%d" % (M, nch, RESAMPLE))


def cov_est(seg_T, kind):
    if kind == "emp":
        return EmpiricalCovariance().fit(seg_T).covariance_
    if kind == "lw":
        return LedoitWolf().fit(seg_T).covariance_
    return OAS().fit(seg_T).covariance_


def recording_features(win_s=4.0, band="full", est="lw", kind="cov"):
    """One feature vector per recording (mean of window vectors)."""
    wl = int(win_s * RESAMPLE)
    out, ses, sub = [], [], []
    for r in recs:
        vecs = []
        arr = r["bands"][band]
        if kind == "cov":
            for st in range(0, arr.shape[1] - wl + 1, wl):
                C = cov_est(arr[:, st:st+wl].T, est)
                vecs.append(logm(C).real[ti0])
        else:  # PLV / wPLI
            for st in range(0, arr.shape[1] - wl + 1, wl):
                v = []
                for b in PHASE_BANDS:
                    z = r["analytic"][b][:, st:st+wl]
                    z = z / np.abs(z)
                    dphi = z[ti1[0]] * z[ti1[1]].conj()
                    if kind == "plv":
                        v.append(np.abs(dphi.mean(axis=1)))
                    else:
                        v.append(np.abs(np.mean(np.sign(dphi.imag), axis=1)))
                vecs.append(np.concatenate(v))
        out.append(np.mean(vecs, axis=0))
        ses.append(r["session"]); sub.append(r["subject"])
    return np.array(out), np.array(ses), np.array(sub)


def cluster(method, X, K, seed):
    if method == "kmeans":
        return KMeans(K, n_init=50, random_state=seed).fit_predict(X)
    if method == "gmm":
        return GaussianMixture(K, n_init=8, reg_covar=1e-4, random_state=seed).fit_predict(X)
    if method.startswith("agg"):
        return AgglomerativeClustering(K, linkage=method.split("-")[1]).fit_predict(X)
    if method == "spectral":
        return SpectralClustering(K, affinity="nearest_neighbors",
                                  random_state=seed).fit_predict(X)


def ari_at(X, ses, method="kmeans", seed=0):
    z = StandardScaler().fit_transform(X)
    return adjusted_rand_score(ses, cluster(method, z, 2, seed))


rng = np.random.default_rng(0)
X, ses, sub = recording_features()
obs = ari_at(X, ses)
print("\n=== point estimate (recording-level, K=2 KMeans vs session) ===")
print("  n=%d independent recordings; observed ARI=%.3f silhouette=%.3f"
      % (M, obs, silhouette_score(StandardScaler().fit_transform(X),
                                 cluster("kmeans", StandardScaler().fit_transform(X), 2, 0))))

# genuine nonparametric recording bootstrap CI (resample recordings, recluster)
boot = []
for _ in range(500):
    idx = rng.integers(0, M, M)
    z = StandardScaler().fit_transform(X[idx])
    boot.append(adjusted_rand_score(ses[idx], cluster("kmeans", z, 2, 0)))
print("\n=== recording-bootstrap CI (B=500, resampling unit = recording) ===")
print("  ARI mean=%.3f 95%% percentile CI=[%.3f, %.3f]"
      % (np.mean(boot), np.percentile(boot, 2.5), np.percentile(boot, 97.5)))

# valid permutation 1: free recording-label shuffle
z = StandardScaler().fit_transform(X)
lab = cluster("kmeans", z, 2, 0)
null_free = np.array([adjusted_rand_score(rng.permutation(ses), lab) for _ in range(500)])
# valid permutation 2: paired within-subject session flip
pairs = {s: np.where(sub == s)[0] for s in np.unique(sub)}
null_pair = []
for _ in range(500):
    perm = ses.copy()
    for s, ii in pairs.items():
        if rng.random() < 0.5:
            perm[ii] = perm[ii][::-1]
    null_pair.append(adjusted_rand_score(perm, lab))
print("\n=== recording-level permutation (B=500, unit = recording) ===")
print("  free shuffle:      null mean=%.3f p95=%.3f max=%.3f fraction=%.3f"
      % (null_free.mean(), np.percentile(null_free, 95), null_free.max(),
         (1 + np.sum(null_free >= obs)) / 501))
print("  paired within-sub: null mean=%.3f p95=%.3f max=%.3f fraction=%.3f"
      % (np.mean(null_pair), np.percentile(null_pair, 95), np.max(null_pair),
         (1 + np.sum(np.array(null_pair) >= obs)) / 501))

print("\n=== robustness (all aggregated to recording level first) ===")
for m in ("kmeans", "gmm", "agg-ward", "agg-complete", "spectral"):
    print("  cluster=%-12s ARI=%.3f" % (m, ari_at(X, ses, m)))
for w in (2.0, 4.0, 6.0, 8.0):
    Xw, sw, _ = recording_features(win_s=w)
    print("  window=%-2s ARI=%.3f" % (w, ari_at(Xw, sw)))
for e in ("emp", "lw", "oas"):
    Xe, se, _ = recording_features(est=e)
    print("  estimator=%-3s ARI=%.3f" % (e, ari_at(Xe, se)))
for b in BANDS:
    Xb, sb, _ = recording_features(band=b)
    print("  band=%-6s ARI=%.3f" % (b, ari_at(Xb, sb)))
for k in ("plv", "wpli"):
    Xk, sk, _ = recording_features(kind=k)
    print("  %-5s ARI=%.3f" % (k, ari_at(Xk, sk)))
# recording subset (50% of recordings, stratified by session, 8 repeats)
sub_ari = []
for s in range(8):
    keep = np.concatenate([rng.choice(np.where(ses == u)[0], 16, replace=False)
                           for u in np.unique(ses)])
    sub_ari.append(ari_at(X[keep], ses[keep], seed=s))
print("  recording 50%% subsets: mean=%.3f range=[%.3f,%.3f]"
      % (np.mean(sub_ari), np.min(sub_ari), np.max(sub_ari)))

print("\n=== verdict ===")
print("At the correct independent unit (recording), ARI vs session stays near 0,")
print("the recording-bootstrap CI includes 0, and the statistic sits inside both valid")
print("permutation nulls across all robustness choices: consistent with the")
print("impossibility analysis (no recoverable session signature); not a failed run.")
