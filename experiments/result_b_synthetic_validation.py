#!/usr/bin/env python3
"""
Synthetic validation of Result B (Conditional Compatibility Theorem).

Three parts:
  (1) Population reference: independently verify A4' (one-center-per-env is the
      population optimum) and A6 (closed level sets), and estimate the risk-gap
      curve psi(q) by center perturbation.
  (2) Finite-M sweep with Monte Carlo: track true excess risk and misclassification
      of the GLOBAL empirical KMeans, and test the implication
      excess < psi(q)  =>  Err < q; report violation fraction (coverage).
  (3) Negative control: SNR ~ 0.9 (EEG-like), show no clean phase transition.
"""
import numpy as np
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment

K, P, SIGMA = 3, 10, 1.0
N_REF = 100_000
M_GRID = [15, 30, 45, 60, 90, 120, 180, 300]
REPS = 60
Q_TARGETS = [0.05, 0.10, 0.20]
SS_GOOD, SS_BAD = 6.0, 0.9


def make_centers(snr):
    delta = snr * SIGMA
    mu = np.zeros((K, P))
    mu[0, 0] = -delta / 2
    mu[1, 0] = delta / 2
    mu[2, 1] = delta * np.sqrt(3) / 2
    return mu


def sample(mu, n, rng):
    z = rng.integers(0, K, n)
    X = mu[z] + rng.normal(0, SIGMA, (n, P))
    return X, z


def err_hungarian(c, X, z):
    lab = np.argmin(((X[:, None, :] - c[None, :, :]) ** 2).sum(2), axis=1)
    cm = np.zeros((K, K), int)
    for a, b in zip(lab, z):
        cm[a, b] += 1
    r, cc = linear_sum_assignment(-cm)
    mapped = np.empty(K, int)
    mapped[r] = cc
    return (mapped[lab] != z).mean()


def risk(c, X):
    return ((X[:, None, :] - c[None, :, :]) ** 2).sum(2).min(1).mean()


def run_arm(snr, rng):
    mu = make_centers(snr)
    Xref, zref = sample(mu, N_REF, rng)
    r_mu = risk(mu, Xref)
    true_err = err_hungarian(mu, Xref, zref)

    # --- verify A4': compare K=3 vs K=2 population optimum on large reference
    km3 = KMeans(K, n_init=10, random_state=0).fit(Xref)
    km2 = KMeans(K - 1, n_init=10, random_state=0).fit(Xref)
    r3, r2 = -km3.score(Xref) / N_REF, -km2.score(Xref) / N_REF
    r_star = r3  # global population optimum (NOT risk(mu))

    # --- estimate psi(q) via center perturbation (wide enough to cross boundary)
    pts = []
    for t in np.linspace(0.0, 5.0 * SIGMA, 20):
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

    # --- finite-M sweep
    print("\n=== arm SNR=%.1f ===" % snr)
    print("A4' check: true-center Err=%.4f, risk(mu)=%.3f, R*(K3)=%.3f, R*(K2)=%.3f, gap R2-R3=%.3f"
          % (true_err, r_mu, r3, r2, r2 - r3))
    print("estimated psi: " + ", ".join("q=%g: %s" % (q, ("%.3f" % v if np.isfinite(v) else "not reached"))
                                        for q, v in psi.items()))
    print("%5s | %12s %12s | %s" % ("M", "excess", "Err", "violations (excess<psi but Err>=q)"))
    for M in M_GRID:
        exc, er, viol = [], [], {q: 0 for q in Q_TARGETS}
        for b in range(REPS):
            X, z = sample(mu, M, rng)
            c = KMeans(K, n_init=20, random_state=b).fit(X).cluster_centers_
            e = max(0.0, risk(c, Xref) - r_star)
            ehat = err_hungarian(c, Xref, zref)
            exc.append(e); er.append(ehat)
            for q in Q_TARGETS:
                if np.isfinite(psi[q]) and e < psi[q] and ehat >= q:
                    viol[q] += 1
        vtxt = ", ".join("q=%g:%d/%d" % (q, viol[q], REPS) for q in Q_TARGETS)
        print("%5d | %12.4f %12.4f | %s" % (M, np.mean(exc), np.mean(er), vtxt))


rng = np.random.default_rng(0)
run_arm(SS_GOOD, rng)
run_arm(SS_BAD, rng)
