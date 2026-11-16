"""
Step 4 semi-synthetic: real-data mixing structure + controlled two-env intervention.
Design 1: Gaussian latent + real mixing (within theorem scope; test robustness to
          realistic ill-conditioned mixing and the N^{-1/2} rate).
Design 2: real non-Gaussian PCA scores + intervention (honest non-Gaussian stress test).
Self-contained, no /tmp deps.
"""
import numpy as np
from scipy.linalg import sqrtm
from sklearn import datasets as ds

d = 5
active = [0, 1, 2]
DELTA = 1.0
D = np.eye(d)
for a in active:
    D[a, a] = 1.0 + DELTA

def real_structure(name):
    X = ds.load_wine().data if name == 'wine' else ds.load_digits().data
    X = X[:, X.var(0) > 1e-8]
    Xs = (X - X.mean(0)) / X.std(0)          # standardize
    # pick d highest-variance (standardized -> highest mean abs) features
    order = np.argsort(-np.abs(Xs).mean(0))[:d]
    Xr = Xs[:, order]                         # n x d real correlated features
    C = np.cov(Xr, rowvar=False)              # real correlation matrix
    G = np.real(sqrtm(C))                     # d x d symmetric invertible mixing
    Zw = Xr @ np.linalg.inv(G)                # real whitened (generally non-Gaussian)
    return G, Zw, np.linalg.cond(C)

def sym_basis(d):
    Bs = []
    for a in range(d):
        B = np.zeros((d, d)); B[a, a] = 1; Bs.append(B)
    for a in range(d):
        for b in range(a + 1, d):
            B = np.zeros((d, d)); B[a, b] = B[b, a] = 1 / np.sqrt(2); Bs.append(B)
    return Bs

def cumulant4(w):
    N = len(w)
    m4 = np.einsum('ni,nj,nk,nl->ijkl', w, w, w, w) / N
    c = w.T @ w / N
    return m4 - (np.einsum('ij,kl->ijkl', c, c)
                 + np.einsum('ik,jl->ijkl', c, c)
                 + np.einsum('il,jk->ijkl', c, c))

def T_operator(k4, Bs):
    m = len(Bs); T = np.zeros((m, m))
    for p, Bp in enumerate(Bs):
        TB = np.einsum('ijkl,kl->ij', k4, Bp)
        for q, Bq in enumerate(Bs):
            T[q, p] = (TB * Bq).sum()
    return (T + T.T) / 2

Bs = sym_basis(d)
# whitened-frame true magnitude for the active components
k_active = np.repeat(DELTA / (2 + DELTA), len(active))

def blind_estimate(X):
    Xc = X - X.mean(0)
    L = np.linalg.cholesky(np.cov(Xc, rowvar=False))
    w = Xc @ np.linalg.inv(L).T
    T = T_operator(cumulant4(w), Bs)
    ev = np.linalg.eigvalsh(T)               # ascending
    # D eigenvalues 3k^2 are the largest; take top len(active)
    k = np.sqrt(np.maximum(ev[-len(active):], 0) / 3)
    return k[::-1]

def design1(N, G, rng):
    n1 = N // 2
    z0 = rng.normal(size=(N - n1, d))
    z1 = rng.normal(size=(n1, d)) @ np.sqrt(D)
    z = np.vstack([z0, z1])
    return z @ G.T

def design2(N, Zw, G, rng):
    idx = rng.integers(0, len(Zw), size=N)
    z0 = Zw[idx]
    z1 = Zw[idx] @ np.sqrt(D)
    n1 = N // 2
    z = np.vstack([z0[:N - n1], z1[:n1]])
    rng.shuffle(z)
    return z @ G.T

for name in ['wine', 'digits']:
    G, Zw, cond = real_structure(name)
    print("=== %s : retained-subspace cond = %.1f ===" % (name, cond))
    rng = np.random.default_rng(0)
    print(" Design 1 (Gaussian latent + real mixing): sqrt(N)*RMSE")
    for N in [1000, 2000, 4000, 8000]:
        errs = []
        for _ in range(80):
            k = blind_estimate(design1(N, G, rng))
            errs.append(np.abs(k - k_active).mean())
        rmse = np.sqrt(np.mean(np.array(errs) ** 2))
        print("  N=%5d RMSE=%.4f sqrt(N)*RMSE=%.2f" % (N, rmse, np.sqrt(N) * rmse))
    print(" Design 2 (real non-Gaussian scores + intervention): magnitude RMSE")
    for N in [1000, 2000, 4000]:
        errs = []
        for _ in range(60):
            k = blind_estimate(design2(N, Zw, G, rng))
            errs.append(np.abs(k - k_active).mean())
        rmse = np.sqrt(np.mean(np.array(errs) ** 2))
        print("  N=%5d RMSE=%.4f sqrt(N)*RMSE=%.2f" % (N, rmse, np.sqrt(N) * rmse))
