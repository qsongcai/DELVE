#!/usr/bin/env python3
"""
Cache reference / bad-channel robustness features for the EEG recovery.

Each recording is read once on its FULL montage; the reference-independent steps
(filter 1-40, notch 50, resample 128) are applied once, then we derive:

  feat_common : 4 shared channels, common-average (baseline; reproduces the protocol)
  feat_bipolar: four reference-free bipolar differences (F3-F4, O1-O2, F3-O1, F4-O2)
  feat_csd    : surface Laplacian (CSD) on the full montage, then keep 4 shared ch.
  feat_loo    : leave-one-shared-channel-out, four 3-channel variants
  bad_flag    : robust per-channel variance z-score + flatline, on the 4 shared ch.
  plv_bipolar : multiband PLV on the bipolar channels (does the .915 fingerprint fade?)

All covariance features are LedoitWolf + logm recording means of window features.
No metadata enters any fit. Sparse-montage CSD is reported with explicit caveats.
"""
import os
import warnings
from pathlib import Path
import numpy as np
from scipy.linalg import logm
from scipy.signal import butter, sosfiltfilt, hilbert
from sklearn.covariance import LedoitWolf
import mne

warnings.filterwarnings("ignore")
DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
DATA = Path(DATA_DIR, "eegdash_data")
OUT = os.path.join(DATA_DIR, "reference_robustness.npz")
SHARED = ["F3", "F4", "O1", "O2"]
WIN_S, RESAMPLE = 4.0, 128.0
NBANDS = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}


def read_4362(p):
    raw = mne.io.read_raw_edf(p, preload=False, verbose=False)
    raw.rename_channels({c: c.rstrip(".") for c in raw.ch_names})
    return raw


def ci_index(names, target):
    """Case-insensitive channel-name lookup."""
    up = [n.upper() for n in names]
    return up.index(target.upper())


def rec_logcov(data, fs):
    """Windowed LW+logm; return recording mean of upper-triangle vech and nwin."""
    wl = int(WIN_S * fs)
    ti = np.triu_indices(data.shape[0])
    feats = []
    for stt in range(0, data.shape[1] - wl + 1, wl):
        seg = data[:, stt:stt + wl]
        C = LedoitWolf().fit(seg.T).covariance_
        feats.append(logm(C).real[ti])
    F = np.array(feats)
    return F.mean(axis=0), len(F)


def bipolar_plv(data, fs):
    """Multiband PLV on 4 channels: 6 pairs x 3 bands = 18."""
    wl = int(WIN_S * fs)
    pairs = np.triu_indices(4, k=1)
    out = []
    for lo, hi in NBANDS.values():
        nb = sosfiltfilt(butter(4, [lo / (fs / 2), hi / (fs / 2)],
                                btype="band", output="sos"), data, axis=1)
        vals = []
        for stt in range(0, data.shape[1] - wl + 1, wl):
            z = hilbert(nb[:, stt:stt + wl], axis=1)
            z = z / np.abs(z)
            dphi = z[pairs[0]] * z[pairs[1]].conj()
            vals.append(np.abs(dphi.mean(axis=1)))
        out.append(np.mean(vals, axis=0))
    return np.concatenate(out)


def bad_flags(data):
    """Robust per-channel log-variance z (MAD) plus flatline; 4 shared channels."""
    lv = np.log(np.clip(data.var(axis=1), 1e-12, None))
    med = np.median(lv)
    mad = np.median(np.abs(lv - med)) + 1e-12
    z = (lv - med) / (1.4826 * mad)
    flat = data.var(axis=1) < 1e-10
    return ((np.abs(z) > 3) | flat).astype(bool)


def process(ds, p, reader):
    raw = reader(p)
    mont = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(mont, match_case=False, match_alias=True,
                    on_missing="ignore", verbose=False)
    raw.load_data()
    raw.filter(1.0, 40.0, verbose=False)
    raw.notch_filter(50.0, verbose=False)
    raw.resample(RESAMPLE, verbose=False)
    fs = raw.info["sfreq"]
    full = raw.get_data()
    names = list(raw.ch_names)
    idx = np.array([ci_index(names, c) for c in SHARED])
    d4 = full[idx]

    # common-average on the 4 shared channels
    ca = d4 - d4.mean(axis=0, keepdims=True)
    f_common, nwin = rec_logcov(ca, fs)

    # bipolar reference-free differences
    # F3-F4, O1-O2, F3-O1, F4-O2  (indices into d4: F3=0,F4=1,O1=2,O2=3)
    bp = np.array([d4[0] - d4[1], d4[2] - d4[3],
                   d4[0] - d4[2], d4[1] - d4[3]])
    f_bipolar, _ = rec_logcov(bp, fs)
    plv_bp = bipolar_plv(bp, fs)

    # surface Laplacian on the full montage, then keep the 4 shared channels
    csd_ok = True
    try:
        csd_raw = mne.preprocessing.compute_current_source_density(raw, verbose=False)
        cfull = csd_raw.get_data()
        cnames = list(csd_raw.ch_names)
        cidx = np.array([ci_index(cnames, c) for c in SHARED])
        f_csd, _ = rec_logcov(cfull[cidx], fs)
    except Exception as e:
        csd_ok = False
        f_csd = np.full_like(f_common, np.nan)
        print("  CSD failed", ds, p.name, e)

    # leave-one-channel-out on the common-average 4 channels
    loo = []
    for drop in range(4):
        keep = [k for k in range(4) if k != drop]
        f_loo, _ = rec_logcov(ca[keep], fs)
        loo.append(f_loo)
    loo = np.array(loo)

    flags = bad_flags(d4)

    subj = p.name.split("R01")[0] if ds == "on004362" else \
        next(x for x in p.parts if x.startswith("sub-"))
    return dict(dataset=ds, subject=f"{ds}:{subj}", nwin=nwin,
                common=f_common, bipolar=f_bipolar, csd=f_csd, csd_ok=csd_ok,
                loo=loo, bad=flags, plv_bp=plv_bp)


def main():
    specs = [
        ("ds007541",
         sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr")),
         mne.io.read_raw_brainvision),
        ("ds008099",
         sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf")),
         lambda p: mne.io.read_raw_edf(p, preload=False)),
        ("on004362",
         sorted((DATA / "on004362").glob("*R01.edf")),
         read_4362),
    ]
    recs = []
    for ds, files, reader in specs:
        ok = 0
        for p in files:
            try:
                r = process(ds, p, reader)
            except Exception as e:
                print("  FAIL", ds, p.name, e)
                continue
            if r["nwin"] < 3:
                continue
            recs.append(r); ok += 1
        print("processed %s: %d recordings" % (ds, ok))

    np.savez(OUT,
             datasets=np.array([r["dataset"] for r in recs]),
             subjects=np.array([r["subject"] for r in recs]),
             nwin=np.array([r["nwin"] for r in recs]),
             common=np.array([r["common"] for r in recs]),
             bipolar=np.array([r["bipolar"] for r in recs]),
             csd=np.array([r["csd"] for r in recs]),
             csd_ok=np.array([r["csd_ok"] for r in recs]),
             loo=np.array([r["loo"] for r in recs]),
             bad=np.array([r["bad"] for r in recs]),
             plv_bp=np.array([r["plv_bp"] for r in recs]))
    print("saved", OUT, "N=", len(recs))


if __name__ == "__main__":
    main()
