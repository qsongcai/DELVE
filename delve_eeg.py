#!/usr/bin/env python3
"""
DELVE on real unlabeled EEG (GPU driver, Stage 0 + core Stages 1-7).
Pools ds007541 (BrainVision) + ds008099 (EDF), hides dataset ID.
Harmonization: 4 shared channels F3/F4/O1/O2, 128 Hz, common-average, 4s windows.
Outputs: K_hat, labels/posterior, co-assignment stability, random-merge p,
         bootstrap membership + K uncertainty, perturbation sensitivity,
         and post-hoc ARI/NMI vs dataset (validation only; technical-env interpretation).
"""
import os
import warnings
from pathlib import Path
import numpy as np
from scipy.signal import welch
from sklearn.covariance import LedoitWolf
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import mne

import delve_core as bc

warnings.filterwarnings("ignore")
DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
DATA = Path(DATA_DIR, "eegdash_data")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0
BANDS = [(1, 4), (4, 8), (8, 13), (13, 30)]


def sub_of(v):
    return next(p for p in v.parts if p.startswith("sub-"))


def process(vhdr, ds_label, reader):
    rows = []
    for ri, v in enumerate(vhdr):
        raw = reader(v)
        raw.pick(SHARED).load_data()
        raw.set_eeg_reference("average", verbose=False)
        raw.filter(1.0, 40.0, verbose=False)
        raw.notch_filter(50.0, verbose=False)
        raw.resample(RESAMPLE, verbose=False)
        data, fs = raw.get_data(), raw.info["sfreq"]
        wl = int(WIN_S * fs)
        s_id = f"{ds_label}:{sub_of(v)}"
        for stt in range(0, data.shape[1] - wl + 1, wl):
            seg = data[:, stt:stt + wl]
            cov = LedoitWolf().fit(seg.T).covariance_
            xw = bc.vech_log_cov(cov)
            # optional band log-power features
            freqs, pxx = welch(seg, fs=fs, nperseg=min(256, wl), axis=1)
            ps = []
            for lo, hi in BANDS:
                m = (freqs >= lo) & (freqs <= hi)
                ps.extend(np.log(np.clip(np.trapz(pxx[:, m], freqs[m], axis=1), 1e-12, None)))
            rows.append((xw, np.array(ps), ds_label, s_id, f"{ds_label}:{ri}"))
    return rows


f7541 = sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr"))
f8099 = sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf"))
rows = (process(f7541, "ds007541", lambda v: mne.io.read_raw_brainvision(v, verbose=False))
        + process(f8099, "ds008099", lambda v: mne.io.read_raw_edf(v, verbose=False, preload=False)))

Xw = np.array([r[0] for r in rows])
dset = np.array([r[2] for r in rows])
subj = np.array([r[3] for r in rows])
rec = np.array([r[4] for r in rows])

rids, Xr = bc.aggregate(Xw, rec)
rec_dset = np.array([dset[rec == r][0] for r in rids])
print("DELVE real-data: windows=%d recordings=%d subjects=%d feature_dim=%d"
      % (len(rows), len(rids), len(set(subj)), Xr.shape[1]))

rng = np.random.default_rng(0)
k_grid = list(range(2, 7))
chosen, metrics = bc.select_K(Xr, k_grid, rng, n_boot=50)
print("\n=== Stage 3: K selection ===")
for K in k_grid:
    m = metrics[K]
    print(" K=%d bic=%.1f sil=%.3f stability=%.3f"
          % (K, m['bic'], m['silhouette'], m['stability']))
print(" -> K_hat=%d" % chosen)

labels, posterior = bc.fit_partition(Xr, chosen, rng)[:2]
print("\n=== Stage 4: partition ===")
print(" cluster sizes=%s" % np.bincount(labels, minlength=chosen))
ari = adjusted_rand_score(rec_dset, labels)
nmi = normalized_mutual_info_score(rec_dset, labels)
print(" post-hoc ARI(dataset)=%.3f NMI=%.3f (validation only)" % (ari, nmi))

lab_s, co, sil, p_merge = bc.stability_analysis(Xr, chosen, rng, n_boot=60)
print("\n=== Stage 5: stability ===")
print(" silhouette=%.3f random-merge p=%.3f" % (sil, p_merge))
print(" co-assignment: diagonal mean=%.3f" % np.mean(np.diag(co)))

_, _, member, k_dist = bc.uncertainty(Xr, chosen, rng, n_boot=60,
                                      reselect=True, k_grid=k_grid)
print("\n=== Stage 6: uncertainty ===")
print(" mean max membership=%.3f" % np.mean(member.max(1)))
print(" bootstrap K distribution=%s" % {k: round(v, 2) for k, v in k_dist.items() if v > 0})
print(" perturbation sensitivity (noise, ARI, agreement):")
for s, a, ag in bc.sensitivity(Xr, chosen, rng):
    print("  noise=%.2f ARI=%.3f agreement=%.3f" % (s, a, ag))

print("\n=== Stage 7: interpretation ===")
print(" Recovered clusters are TECHNICAL/state environments (device/task/cohort/state),")
print(" NOT biological or causal environments. ARI vs dataset used only for validation.")
