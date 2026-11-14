#!/usr/bin/env python3
"""
Anti-splitting diagnostic for the population KMeans bridge (oracle).

On the balanced 30/30/30 recording design, in the StandardScaler-transformed
space (the space the theory calls X), estimate for each environment:
  pi_e, mu_e, V_e(1), V_e(2), S_e(2)
and for each pair:
  M_ef.
Check the anti-splitting condition  min M_ef > max S_e(2), and report the
separation-to-noise ratio  Delta / max sigma_e.
"""
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
NPZ = os.path.join(DATA_DIR, "recording_features.npz")
N_PER = 30
SEEDS = 20

d = np.load(NPZ, allow_pickle=True)
feats, dss, subs = d["features"], d["datasets"], d["subjects"]
DS = sorted(set(dss))


def balanced(seed):
    r = np.random.default_rng(seed)
    Xf, y = [], []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, N_PER, replace=False)
        Xf.append(feats[idx]); y.append(np.full(N_PER, ds))
    return StandardScaler().fit_transform(np.vstack(Xf)), np.concatenate(y)


def one_design(X, y):
    pi = {e: (y == e).mean() for e in DS}
    mu, V1, V2, S2, sigma = {}, {}, {}, {}, {}
    for e in DS:
        Xe = X[y == e]
        mu[e] = Xe.mean(axis=0)
        V1[e] = ((Xe - mu[e]) ** 2).sum(axis=1).mean()
        km = KMeans(2, n_init=20, random_state=0).fit(Xe)
        V2[e] = -km.score(Xe) / len(Xe)
        S2[e] = V1[e] - V2[e]
        sigma[e] = np.sqrt(V1[e])
    M = {}
    for i, e in enumerate(DS):
        for f in DS[i + 1:]:
            M[(e, f)] = (pi[e] * pi[f] / (pi[e] + pi[f])) * ((mu[e] - mu[f]) ** 2).sum()
    # weighted split gain in TOTAL-RISK units (M_ef is already total-risk)
    wS = {e: pi[e] * S2[e] for e in DS}
    Delta = min(np.linalg.norm(mu[e] - mu[f]) for e, f in M)
    return dict(pi=pi, S2=S2, wS=wS, M=M, m_min=min(M.values()),
                s_max_cond=max(S2.values()), s_max_tot=max(wS.values()),
                Delta=Delta, snr=Delta / max(sigma.values()))


rows = [one_design(*balanced(s)) for s in range(SEEDS)]
m_min = np.array([r["m_min"] for r in rows])
s_cond = np.array([r["s_max_cond"] for r in rows])
s_tot = np.array([r["s_max_tot"] for r in rows])
snr = np.array([r["snr"] for r in rows])

print("anti-splitting diagnostic (balanced 30/30/30, %d seeds, scaled space)" % SEEDS)
print("  min M_ef (total-risk)            : mean=%.3f range=[%.3f, %.3f]"
      % (m_min.mean(), m_min.min(), m_min.max()))
print("  max S_e(2) conditional (doc literal, mismatched units): mean=%.3f"
      % s_cond.mean())
print("  max pi_e S_e(2) total-risk (correct comparison)       : mean=%.3f range=[%.3f, %.3f]"
      % (s_tot.mean(), s_tot.min(), s_tot.max()))
print("  literal doc comparison  min M_ef > max S_e(cond): holds in %d/%d"
      % ((m_min > s_cond).sum(), SEEDS))
print("  correct total-risk comparison min M_ef > max pi S : holds in %d/%d"
      % ((m_min > s_tot).sum(), SEEDS))
print("  separation/noise ratio Delta/max sigma: mean=%.3f range=[%.3f, %.3f]"
      % (snr.mean(), snr.min(), snr.max()))

# detail for seed 0
r0 = rows[0]
print("\nseed-0 detail")
for e in DS:
    print("  %-9s pi=%.3f S_e(2)=%.3f pi*S=%.3f"
          % (e, r0["pi"][e], r0["S2"][e], r0["wS"][e]))
for (e, f), v in r0["M"].items():
    print("  M(%s,%s)=%.3f" % (e, f, v))
