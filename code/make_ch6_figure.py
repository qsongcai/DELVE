#!/usr/bin/env python3
"""Ch6 figure: finite-M sweep with reference-estimated thresholds.

Reuses the verified functions from experiments/result_b_synthetic_validation.py.
For each arm it (i) estimates the risk-gap threshold psi(q) by center perturbation
on the reference, and (ii) runs the global empirical K-means over an extended
sample-size grid, plotting excess risk and misclassification with the theorem's
thresholds and the crossing point.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.cluster import KMeans

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "DELVE", "experiments",
                   "result_b_synthetic_validation.py")
src = open(SRC).read()
head = src[:src.index("rng = np.random")]
ns = {}
exec(compile(head, SRC, "exec"), ns)

K, P = ns["K"], ns["P"]
N_REF, REPS, Q_TARGETS = ns["N_REF"], ns["REPS"], ns["Q_TARGETS"]
M_GRID = [8, 10, 12, 15, 30, 45, 60, 90, 120, 180, 300]
make_centers, sample = ns["make_centers"], ns["sample"]
err_hungarian, risk = ns["err_hungarian"], ns["risk"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def run_arm(snr, rng):
    mu = make_centers(snr)
    Xref, zref = sample(mu, N_REF, rng)
    r_star = -KMeans(K, n_init=10, random_state=0).fit(Xref).score(Xref) / N_REF

    # estimate psi(q) by center perturbation (same procedure as the experiment)
    pts = []
    for t in np.linspace(0.0, 5.0, 20):
        for _ in range(16):
            u = rng.normal(0, 1, (K, P))
            u /= np.linalg.norm(u, axis=1, keepdims=True)
            c = mu + t * u
            pts.append((err_hungarian(c, Xref, zref), risk(c, Xref) - r_star))
    pts = np.array(pts)
    psi = {}
    for q in Q_TARGETS:
        sel = pts[:, 0] >= q
        psi[q] = max(0.0, pts[sel, 1].min()) if sel.any() else np.inf

    exc_m, exc_s, err_m, err_s = [], [], [], []
    for M in M_GRID:
        exc, er = [], []
        for b in range(REPS):
            X, z = sample(mu, M, rng)
            c = KMeans(K, n_init=20, random_state=b).fit(X).cluster_centers_
            exc.append(max(0.0, risk(c, Xref) - r_star))
            er.append(err_hungarian(c, Xref, zref))
        exc_m.append(np.mean(exc)); exc_s.append(np.std(exc))
        err_m.append(np.mean(er)); err_s.append(np.std(er))
    return psi, (np.array(exc_m), np.array(exc_s),
                 np.array(err_m), np.array(err_s))


rng = np.random.default_rng(1)
psi_good, good = run_arm(6.0, rng)
psi_bad, bad = run_arm(0.9, np.random.default_rng(2))
blue, orange = "#2c6fbb", "#c0762b"
print("good psi:", {q: round(v, 3) for q, v in psi_good.items()})
print("bad psi:", {q: round(v, 3) for q, v in psi_bad.items()})

M = np.array(M_GRID)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 3.4))

# ---- panel (a): excess risk with psi thresholds
for (em, es, _, _), color, label in [
        (good, blue, "Gaussian robustness arm (SNR 6)"),
        (bad, orange, "misalignment arm (SNR 0.9)")]:
    ax1.plot(M, em, "-o", ms=3.4, lw=1.2, color=color, label=label)
    ax1.fill_between(M, em - es, em + es, color=color, alpha=0.14)

# good-arm thresholds psi(0.05) and psi(0.20)
p05, p20 = psi_good[0.05], psi_good[0.20]
ax1.axhline(p05, color=blue, lw=0.9, ls="--", alpha=0.85)
ax1.text(140, p05 + 0.45, r"$\psi_{\rm ref}(0.05)=%.2f$" % p05, fontsize=7.5, color=blue)
ax1.axhline(p20, color=blue, lw=0.9, ls=":", alpha=0.7)
ax1.text(140, p20 + 0.45, r"$\psi_{\rm ref}(0.20)=%.2f$" % p20, fontsize=7.5, color=blue)
# bad-arm threshold (near zero, not useful)
pb = psi_bad[0.05]
ax1.axhline(pb, color=orange, lw=0.9, ls="--", alpha=0.85)
ax1.text(11, pb + 0.35, r"$\psi_{\rm ref,bad}\approx%.2f$" % pb,
         fontsize=7, color=orange)

# crossing point of the good arm and psi(0.05)
cross = next(M[i] for i in range(len(M)) if good[0][i] < p05)
ax1.axvline(cross, color="#777777", lw=0.8, ls=":")
ax1.annotate(r"excess crosses $\psi_{\rm ref}(0.05)$", xy=(cross, p05),
             xytext=(24, 9.6), fontsize=7.5, color=blue,
             arrowprops=dict(arrowstyle="->", lw=0.8, color=blue))
ax1.set_ylabel("excess risk (reference)")
ax1.set_title("(a) excess risk vs reference-estimated gap")
ax1.legend(frameon=False, loc="upper right")

# ---- panel (b): misclassification (log y) with q target levels
for (_, _, rm, rs), color in [(good, blue), (bad, orange)]:
    ax2.plot(M, rm, "-o", ms=3.4, lw=1.2, color=color)
    ax2.fill_between(M, np.maximum(rm - rs, 1e-4), rm + rs,
                     color=color, alpha=0.14)
for q in Q_TARGETS:
    ax2.axhline(q, color="#999999", lw=0.7, ls=":")
    ax2.text(137, q * 1.10, r"$q=%g$" % q, fontsize=6.8, color="#666666")
ax2.axvline(cross, color="#777777", lw=0.8, ls=":")
ax2.annotate(r"phase transition: error below $q=0.05$",
             xy=(cross, 0.05), xytext=(26, 0.012), fontsize=7.5, color=blue,
             arrowprops=dict(arrowstyle="->", lw=0.8, color=blue))
ax2.annotate("error plateau", xy=(115, 0.58), xytext=(50, 0.66),
             fontsize=7.5, color=orange)
ax2.set_yscale("log")
ax2.set_ylabel("misclassification (reference, log scale)")
ax2.set_title("(b) transition vs plateau")
ax2.set_ylim(0.002, 0.8)


def clean_log_x(ax, ticks):
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.xaxis.set_major_formatter(
        mticker.FixedFormatter([str(int(t)) for t in ticks]))
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.set_xlabel("sample size $M$")


clean_log_x(ax1, M)
ticks_b = [8, 10, 12, 15, 30, 45, 60, 90, 120, 150]
clean_log_x(ax2, ticks_b)
ax2.set_xlim(7, 150)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(ROOT, "figures", f"fig7_ch6_sweep.{ext}"), dpi=200)
print("saved fig7_ch6_sweep")
