#!/usr/bin/env python3
"""
Bounded-noise validation of the hard-ball premise (Assumption 5.2).

Unlike the Gaussian location model, whose noise has unbounded support, this
design draws isotropic uniform-in-ball noise of radius rho, so the hard-ball
condition ||xi|| <= rho holds almost surely by construction. The equilateral
center spacing is set to Delta = 6 rho, which strictly exceeds 4 rho.

Checks:
  (1) hard ball: empirical maximum noise norm equals rho (up to numerics);
  (2) margin: Delta = 6 rho > 4 rho;
  (3) true-center classifier is exactly correct on a large reference (zero error);
  (4) finite-M global empirical KMeans: excess and error decline, and the
      implication excess < psi(q) => Err < q has zero violations.
"""
import numpy as np
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment

K, P = 3, 10
RHO = 1.0
DELTA = 6.0 * RHO
N_REF = 100_000
M_GRID = [15, 30, 45, 60, 90, 120, 180, 300]
REPS = 60
Q_TARGETS = [0.05, 0.10, 0.20]


def make_centers(delta):
    mu = np.zeros((K, P))
    mu[0, 0] = -delta / 2
    mu[1, 0] = delta / 2
    mu[2, 1] = delta * np.sqrt(3) / 2
    return mu


def ball_noise(n, rng):
    g = rng.normal(0, 1, (n, P))
    g /= np.linalg.norm(g, axis=1, keepdims=True)
    r = RHO * rng.random(n) ** (1.0 / P)
    return g * r[:, None]


def sample(mu, n, rng):
    z = rng.integers(0, K, n)
    return mu[z] + ball_noise(n, rng), z


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


rng = np.random.default_rng(0)
mu = make_centers(DELTA)
Xref, zref = sample(mu, N_REF, rng)

# (1) hard ball and (2) margin
noise = Xref - mu[zref]
print("hard ball: max||xi||=%.4f (rho=%.4f)" % (np.linalg.norm(noise, axis=1).max(), RHO))
print("margin: Delta=%.4f vs 4rho=%.4f, Delta>4rho: %s" % (DELTA, 4 * RHO, DELTA > 4 * RHO))

# (3) true-center classifier
true_err = err_hungarian(mu, Xref, zref)
r_star = risk(mu, Xref)
print("true-center error=%.4f, risk(mu)=%.4f" % (true_err, r_star))

# psi(q) via perturbation
pts = []
for t in np.linspace(0.0, 5.0 * RHO, 20):
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
print("estimated psi: " + ", ".join("q=%g:%.3f" % (q, v) for q, v in psi.items()))

# (4) finite-M sweep
print("%5s | %10s %10s | %s" % ("M", "excess", "Err", "violations"))
for M in M_GRID:
    exc, er, viol = [], [], {q: 0 for q in Q_TARGETS}
    for b in range(REPS):
        X, z = sample(mu, M, rng)
        c = KMeans(K, n_init=20, random_state=b).fit(X).cluster_centers_
        e = max(0.0, risk(c, Xref) - r_star)
        ehat = err_hungarian(c, Xref, zref)
        exc.append(e)
        er.append(ehat)
        for q in Q_TARGETS:
            if np.isfinite(psi[q]) and e < psi[q] and ehat >= q:
                viol[q] += 1
    vtxt = ", ".join("q=%g:%d/%d" % (q, viol[q], REPS) for q in Q_TARGETS)
    print("%5d | %10.4f %10.4f | %s" % (M, np.mean(exc), np.mean(er), vtxt))
