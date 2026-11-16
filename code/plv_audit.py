#!/usr/bin/env python3
"""
Dedicated PLV audit (risk point 4), same blind harmonization:
4 shared channels F3/F4/O1/O2, 128 Hz, common-average, 4s windows.
Independent unit = recording (windows only estimate features).
Runs the same rigor as covariance:
  (1) pooled vs dataset, per band and combined: PLV and wPLI (volume-conduction robust);
  (2) within-dataset vs subject (both datasets);
  (3) recording-level permutation (B=200);
  (4) balanced recording subsample (30/set, 6 repeats);
  (5) band sensitivity; wPLI as the volume-conduction diagnostic.
Blind; metadata only post-hoc.
"""
import warnings
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import mne

warnings.filterwarnings("ignore")
DATA = Path("/mnt/sdd1/datasets_qsong/eegdash_data")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0
NBANDS = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
ti1 = np.triu_indices(len(SHARED), k=1)


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
        narrow = {b: sosfiltfilt(butter(4, [lo/(fs/2), hi/(fs/2)], btype="band",
                          output="sos"), data, axis=1)
                  for b, (lo, hi) in NBANDS.items()}
        win_plv, win_wpli = {b: [] for b in NBANDS}, {b: [] for b in NBANDS}
        for stt in range(0, data.shape[1] - wl + 1, wl):
            for b in NBANDS:
                z = hilbert(narrow[b][:, stt:stt+wl], axis=1)
                z = z / np.abs(z)
                dphi = z[ti1[0]] * z[ti1[1]].conj()          # pairs x time
                plv = np.abs(dphi.mean(axis=1))
                im = dphi.imag
                wpli = np.abs(im.mean(axis=1)) / np.maximum(np.abs(im).mean(axis=1), 1e-12)
                win_plv[b].append(plv); win_wpli[b].append(wpli)
        rec = dict(rec=f"{ds_label}:{ri}", dataset=ds_label, subject=f"{ds_label}:{sub_of(v)}")
        for b in NBANDS:
            rec["plv_"+b] = np.mean(win_plv[b], axis=0)
            rec["wpli_"+b] = np.mean(win_wpli[b], axis=0)
        out.append(rec)
    return out


f7541 = sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr"))
f8099 = sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf"))
rows = (process(f7541, "ds007541", lambda v: mne.io.read_raw_brainvision(v, verbose=False))
        + process(f8099, "ds008099", lambda v: mne.io.read_raw_edf(v, verbose=False, preload=False)))
print("recordings=%d" % len(rows))
rng = np.random.default_rng(0)


def matrix(feat, subset=None):
    sel = rows if subset is None else [r for r in rows if r["dataset"] == subset]
    return StandardScaler().fit_transform(np.array([r[feat] for r in sel])), sel


def ari(feat, subset, truth_key):
    X, sel = matrix(feat, subset)
    lab = KMeans(2, n_init=30, random_state=0).fit_predict(X)
    t = np.array([r[truth_key] for r in sel])
    return adjusted_rand_score(t, lab), normalized_mutual_info_score(t, lab)


print("\n=== (1) pooled vs dataset: PLV / wPLI, per band + combined ===")
for r in rows:
    r["plv_all"] = np.concatenate([r["plv_"+b] for b in NBANDS])
    r["wpli_all"] = np.concatenate([r["wpli_"+b] for b in NBANDS])
for b in ("theta", "alpha", "beta", "all"):
    a, n = ari("plv_"+b, None, "dataset")
    print("  PLV %-5s ARI=%.3f NMI=%.3f" % (b, a, n))
for b in ("theta", "alpha", "beta", "all"):
    a, n = ari("wpli_"+b, None, "dataset")
    print("  wPLI %-5s ARI=%.3f NMI=%.3f" % (b, a, n))

print("\n=== (2) within-dataset vs subject (combined) ===")
for ds in ("ds007541", "ds008099"):
    for feat in ("plv_all", "wpli_all"):
        a, n = ari(feat, ds, "subject")
        print("  %s %-8s n=%d ARI(vs subject)=%.3f"
              % (ds, feat, len([r for r in rows if r["dataset"] == ds]), a))

print("\n=== (3) recording-level permutation (PLV combined, B=200) ===")
X, sel = matrix("plv_all")
lab = KMeans(2, n_init=30, random_state=0).fit_predict(X)
t = np.array([r["dataset"] for r in sel])
obs = adjusted_rand_score(t, lab)
null = np.array([adjusted_rand_score(rng.permutation(t), lab) for _ in range(200)])
print("  obs=%.3f null mean=%.3f p95=%.3f p<1/201 fraction=%.3f"
      % (obs, null.mean(), np.percentile(null, 95), (1 + np.sum(null >= obs))/201))

print("\n=== (4) balanced recording subsample (30/set, 6 repeats) ===")
r75 = [r for r in rows if r["dataset"] == "ds007541"]
r80 = [r for r in rows if r["dataset"] == "ds008099"]
for feat in ("plv_all", "wpli_all"):
    vals = []
    for s in range(6):
        pick = list(rng.choice(r75, 30, replace=False)) + r80
        Xp = StandardScaler().fit_transform(np.array([r[feat] for r in pick]))
        lp = KMeans(2, n_init=30, random_state=s).fit_predict(Xp)
        vals.append(adjusted_rand_score(np.array([r["dataset"] for r in pick]), lp))
    print("  %-8s ARI mean=%.3f range=[%.3f,%.3f]"
          % (feat, np.mean(vals), np.min(vals), np.max(vals)))

print("\n=== (5) volume-conduction diagnostic ===")
print("PLV is sensitive to zero-lag coupling; wPLI suppresses zero-lag. If PLV is high")
print("but wPLI collapses, the dataset signal is dominated by zero-lag/reference/volume-")
print("conduction-like phase structure rather than genuine inter-regional synchronization.")
