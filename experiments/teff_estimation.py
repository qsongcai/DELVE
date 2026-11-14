#!/usr/bin/env python3
"""
Numerical estimate of the effective sample size T_eff.

The O(1/T_w) mixing extension replaces the window count by an effective count.
For each recording we re-derive the ordered window-level log-cov features and
estimate the integrated autocorrelation time per dimension with the initial
positive sequence estimator; T_eff = T_w / tau_int. Non-overlapping windows
should already weaken autocorrelation, and short sequences make the estimate
noisy; both caveats are reported rather than hidden.
"""
import os
import numpy as np
from pathlib import Path
import delve_third_dataset as d3

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
DATA = Path(DATA_DIR, "eegdash_data")


def integrated_tau(x):
    T = len(x)
    x = x - x.mean()
    var = np.dot(x, x) / T
    if var <= 0 or T < 4:
        return 1.0
    f = np.fft.fft(x, n=2 * T)
    acf = np.fft.ifft(f * np.conj(f))[:T].real / np.dot(x, x)
    tau = 1.0
    for h in range(1, T // 2):
        g = acf[2 * h - 1] + acf[2 * h]
        if g <= 0:
            break
        tau += 2 * g
    return min(tau, float(T))


def main():
    specs = [
        ("ds007541",
         sorted((DATA / "ds007541").glob("sub-*/ses-*/eeg/*task-verification_run-01_eeg.vhdr")),
         lambda v: __import__("mne").io.read_raw_brainvision(v, verbose=False)),
        ("ds008099",
         sorted((DATA / "ds008099").glob("sub-*/eeg/*_eeg.edf")),
         lambda v: __import__("mne").io.read_raw_edf(v, verbose=False, preload=False)),
        ("on004362",
         sorted((DATA / "on004362").glob("*R01.edf")),
         d3.read_4362),
    ]
    rows = []
    for ds, files, reader in specs:
        for p in files:
            try:
                W = d3.windows_of(p, reader)
            except Exception:
                continue
            if len(W) < 3:
                continue
            T = len(W)
            taus = np.array([integrated_tau(W[:, j]) for j in range(W.shape[1])])
            tau_med = np.median(taus)
            rows.append((ds, T, T / tau_med, tau_med))
        print("processed", ds, "cumulative recordings:", len(rows))

    dsarr = np.array([r[0] for r in rows])
    num = np.array([(r[1], r[2], r[3]) for r in rows], dtype=float)
    Tw, Teff, tau = num[:, 0], num[:, 1], num[:, 2]
    print("\nall recordings: n=%d" % len(rows))
    print("  T_w median [min,max] = %.1f [%d,%d]" % (np.median(Tw), Tw.min(), Tw.max()))
    print("  T_eff median [min,max] = %.2f [%.2f,%.2f]"
          % (np.median(Teff), Teff.min(), Teff.max()))
    ratio = Teff / Tw
    print("  T_eff/T_w median [min,max] = %.3f [%.3f,%.3f]"
          % (np.median(ratio), ratio.min(), ratio.max()))
    print("  tau_int median = %.3f" % np.median(tau))
    for ds in sorted(set(dsarr)):
        m = dsarr == ds
        print("  %-9s n=%d median T_w=%.1f T_eff=%.2f ratio=%.3f"
              % (ds, m.sum(), np.median(Tw[m]), np.median(Teff[m]),
                 np.median(ratio[m])))
    print("\ncaveat: short window sequences (median T_w ~ %.0f) make tau noisy;"
          " non-overlapping windows already reduce autocorrelation." % np.median(Tw))


if __name__ == "__main__":
    main()
