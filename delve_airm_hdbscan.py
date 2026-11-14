#!/usr/bin/env python3
"""
DELVE additional baselines: AIRM (covariance-manifold specialized) and HDBSCAN
(density-based, unknown K). Same harmonization as setting C:
4 shared channels, 128 Hz, common-average, 4s windows; LedoitWolf per window.
Recording representative covariance = log-Euclidean mean of window covariances.
Blind protocol; dataset used only post-hoc.
"""
import os
import warnings
from pathlib import Path
import numpy as np
from scipy.linalg import logm, expm, fractional_matrix_power
from sklearn.covariance import LedoitWolf
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering, HDBSCAN
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import mne

warnings.filterwarnings("ignore")
DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
DATA = Path(DATA_DIR, "eegdash_data")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0


def sub_of(v):
    return next(p for p in v.parts if p.startswith("sub-"))


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
        logs = []
        for st in range(0, data.shape[1] - wl + 1, wl):
            C = LedoitWolf().fit(data[:, st:st+wl].T).covariance_
            logs.append(logm(C).real)
        # log-Euclidean mean covariance (SPD barycenter)
        C_rec = expm(np.mean(logs, axis=0)).real
        out.append(dict(rec=f"{ds_label}:{ri}", dataset=ds_label,
                        subject=f"{ds_label}:{sub_of(v)}", C=C_rec,
                        tvec=logm(C_rec).real[np.triu_indices(len(SHARED), k=0)]))
    return out


f7541 = sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr"))
f8099 = sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf"))
recs = (process(f7541, "ds007541", lambda v: mne.io.read_raw_brainvision(v, verbose=False))
        + process(f8099, "ds008099", lambda v: mne.io.read_raw_edf(v, verbose=False, preload=False)))
M = len(recs)
print("recordings=%d" % M)
truth = np.array([r["dataset"] for r in recs])

# ---------- AIRM pairwise distance ----------
def airm(C1, C2):
    h = fractional_matrix_power(C1, -0.5)
    return np.linalg.norm(logm(h @ C2 @ h).real, ord="fro")

D = np.zeros((M, M))
for i in range(M):
    for j in range(i+1, M):
        d = airm(recs[i]["C"], recs[j]["C"])
        D[i, j] = D[j, i] = d
print("AIRM distance: within/between dataset mean = %.3f / %.3f"
      % (np.mean([D[i, j] for i in range(M) for j in range(i+1, M)
                  if truth[i] == truth[j]]),
         np.mean([D[i, j] for i in range(M) for j in range(i+1, M)
                  if truth[i] != truth[j]])))

print("\n=== AIRM agglomerative (precomputed, K=2) vs dataset ===")
for link in ("average", "complete"):
    lab = AgglomerativeClustering(2, metric="precomputed", linkage=link).fit_predict(D)
    print("  AIRM %-8s ARI=%.3f NMI=%.3f"
          % (link, adjusted_rand_score(truth, lab),
             normalized_mutual_info_score(truth, lab)))

# ---------- HDBSCAN on tangent features ----------
X = StandardScaler().fit_transform(np.array([r["tvec"] for r in recs]))
print("\n=== HDBSCAN (unknown K) on log-Euclidean tangent features ===")
for mcs in (5, 10, 15):
    hdb = HDBSCAN(min_cluster_size=mcs).fit(X)
    lab = hdb.labels_
    nclu = len(set(lab) - {-1})
    noise = np.mean(lab == -1)
    ari = adjusted_rand_score(truth, lab)
    print("  tangent mcs=%2d clusters=%d noise=%.2f ARI=%.3f"
          % (mcs, nclu, noise, ari))

# HDBSCAN on the AIRM precomputed distance matrix (different metric) to check
# whether the all-noise result is metric-specific.
print("\n=== HDBSCAN (unknown K) on AIRM precomputed distance ===")
for mcs in (5, 10, 15):
    hdb = HDBSCAN(min_cluster_size=mcs, metric="precomputed").fit(D)
    lab = hdb.labels_
    nclu = len(set(lab) - {-1})
    noise = np.mean(lab == -1)
    ari = adjusted_rand_score(truth, lab)
    print("  AIRM mcs=%2d clusters=%d noise=%.2f ARI=%.3f"
          % (mcs, nclu, noise, ari))
print("\ndone")
