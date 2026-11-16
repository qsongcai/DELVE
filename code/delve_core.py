"""
DELVE core (Stages 1-6), pure numerical, self-contained (no mne, no /tmp).
Provides:
  log-euclidean covariance features, recording aggregation,
  automatic K selection (BIC + silhouette + bootstrap stability),
  partition (hard labels + GMM posterior),
  co-assignment stability + random-merge test,
  bootstrap membership uncertainty + K uncertainty + perturbation sensitivity.
Run directly for a synthetic-data self-test.
"""
import numpy as np
from scipy.linalg import logm
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler


# ---------- Stage 1: covariance representation ----------
def vech_log_cov(cov):
    """cov: (d,d) SPD -> upper-triangular vech of matrix log."""
    lc = logm(cov).real
    d = cov.shape[0]
    return lc[np.triu_indices(d, k=0)]


# ---------- Stage 2: recording aggregation ----------
def aggregate(Xw, rec_id):
    """Mean of window features per recording (equal weight)."""
    rids = sorted(set(rec_id))
    Xr = np.array([Xw[rec_id == r].mean(axis=0) for r in rids])
    return np.array(rids), StandardScaler().fit_transform(Xr)


# ---------- Stage 4: partition ----------
def fit_partition(Xr, K, rng):
    km = KMeans(K, n_init=50, random_state=rng.integers(1 << 30))
    labels = km.fit_predict(Xr)
    gm = GaussianMixture(K, covariance_type='diag', n_init=5,
                         reg_covar=1e-4, random_state=rng.integers(1 << 30))
    gm.fit(Xr)
    posterior = gm.predict_proba(Xr)
    return labels, posterior, km.inertia_


def _align_labels(ref_labels, new_labels, K):
    """Hungarian alignment of new labels to reference based on confusion."""
    conf = np.zeros((K, K))
    for a, b in zip(ref_labels, new_labels):
        conf[a, b] += 1
    row, col = linear_sum_assignment(-conf)
    mapping = {b: a for a, b in zip(row, col)}
    return np.array([mapping[j] for j in new_labels])


# ---------- Stage 3: automatic K selection ----------
def select_K(Xr, k_grid, rng, n_boot=60):
    M = len(Xr)
    metrics = {}
    base_labels = {}
    for K in k_grid:
        labels, _, inertia = fit_partition(Xr, K, rng)
        base_labels[K] = labels
        gm = GaussianMixture(K, covariance_type='diag', n_init=5,
                             reg_covar=1e-4, random_state=rng.integers(1 << 30)).fit(Xr)
        bic = gm.bic(Xr)
        sil = silhouette_score(Xr, labels) if 1 < K < M else -1.0
        # bootstrap stability: cluster resample, predict original via nearest centroid, ARI
        agree = []
        for _ in range(n_boot):
            bidx = rng.integers(0, M, M)
            if len(set(bidx)) < K:
                continue
            lab_b = KMeans(K, n_init=15, random_state=rng.integers(1 << 30)).fit_predict(Xr[bidx])
            cent = np.array([Xr[bidx][lab_b == j].mean(axis=0) for j in range(K)])
            pred = np.argmin(((Xr[:, None, :] - cent[None]) ** 2).sum(-1), axis=1)
            agree.append(adjusted_rand_score(labels, pred))
        metrics[K] = {'bic': bic, 'silhouette': sil,
                      'stability': np.mean(agree), 'inertia': inertia}

    stab = np.array([metrics[K]['stability'] for K in k_grid])
    stab_thr = min(0.85, 0.9 * stab.max())
    eligible = [K for K in k_grid
                if metrics[K]['stability'] >= stab_thr and metrics[K]['silhouette'] > 0]
    bic = np.array([metrics[K]['bic'] for K in k_grid])
    if eligible:
        chosen = min(eligible, key=lambda K: metrics[K]['bic'])
    else:
        sils = np.array([metrics[K]['silhouette'] for K in k_grid])
        chosen = k_grid[int(np.argmax(sils))] if sils.max() > 0 else k_grid[int(np.argmin(bic))]
    return chosen, metrics


# ---------- Stage 5: co-assignment stability ----------
def stability_analysis(Xr, K, rng, n_boot=80):
    M = len(Xr)
    labels, _, inertia = fit_partition(Xr, K, rng)
    co = np.zeros((M, M))
    count = np.zeros((M, M))
    for _ in range(n_boot):
        bidx = rng.integers(0, M, M)
        lab_b = KMeans(K, n_init=15, random_state=rng.integers(1 << 30)).fit_predict(Xr[bidx])
        lab_aligned = _align_labels(labels[bidx], lab_b, K)
        same = (lab_aligned[:, None] == lab_aligned[None, :])
        for ii, a in enumerate(bidx):
            for jj, b in enumerate(bidx):
                count[a, b] += 1
                co[a, b] += same[ii, jj]
    co = np.divide(co, np.maximum(count, 1))
    sil = silhouette_score(Xr, labels) if 1 < K < M else -1.0
    # random-merge baseline on inertia
    rng0 = np.random.default_rng(0)
    rnd = []
    for _ in range(300):
        lab = rng0.integers(0, K, M)
        cent = np.array([Xr[lab == j].mean(axis=0) if np.any(lab == j)
                         else Xr.mean(0) for j in range(K)])
        rnd.append(((Xr - cent[lab]) ** 2).sum())
    p_merge = np.mean(np.array(rnd) <= inertia)
    return labels, co, sil, p_merge


# ---------- Stage 6: uncertainty + sensitivity ----------
def uncertainty(Xr, K, rng, n_boot=80, reselect=False, k_grid=None):
    M = len(Xr)
    labels, posterior, _ = fit_partition(Xr, K, rng)
    member = np.zeros((M, K))
    k_choices = []
    for _ in range(n_boot):
        bidx = rng.integers(0, M, M)
        if len(set(bidx)) < K:
            continue
        lab_b = KMeans(K, n_init=15, random_state=rng.integers(1 << 30)).fit_predict(Xr[bidx])
        lab_aligned = _align_labels(labels[bidx], lab_b, K)
        for ii, a in enumerate(bidx):
            member[a, lab_aligned[ii]] += 1
        if reselect and k_grid is not None:
            k_hat, _ = select_K(Xr[bidx], k_grid, rng, n_boot=25)
            k_choices.append(k_hat)
    member = np.divide(member, np.maximum(member.sum(1, keepdims=True), 1))
    k_dist = {K: float(np.mean(np.array(k_choices) == K)) for K in (k_grid or [])}
    return labels, posterior, member, k_dist


def sensitivity(Xr, K, rng, noise_levels=(0.0, 0.1, 0.25, 0.5, 1.0)):
    """Partition sensitivity to feature-space perturbation (representation robustness)."""
    base_labels, _, _ = fit_partition(Xr, K, rng)
    scale = Xr.std(0, keepdims=True)
    out = []
    for s in noise_levels:
        Xp = Xr + rng.normal(scale=s, size=Xr.shape) * scale
        lab, _, _ = fit_partition(Xp, K, rng)
        lab = _align_labels(base_labels, lab, K)
        out.append((s, adjusted_rand_score(base_labels, lab),
                    np.mean(lab == base_labels)))
    return out


# ---------- self-test on synthetic data ----------
if __name__ == '__main__':
    rng = np.random.default_rng(2026)
    M, d, K_true = 90, 6, 3
    centers = rng.normal(scale=3.0, size=(K_true, d))
    sizes = [M // K_true] * K_true
    Xr = np.vstack([rng.normal(centers[g], size=(n, d)) for g, n in enumerate(sizes)])
    truth = np.repeat(np.arange(K_true), sizes)
    Xr = StandardScaler().fit_transform(Xr)

    k_grid = list(range(2, 7))
    chosen, metrics = select_K(Xr, k_grid, rng)
    print("=== synthetic K selection (true K=%d) ===" % K_true)
    for K in k_grid:
        m = metrics[K]
        print(" K=%d bic=%.1f sil=%.3f stability=%.3f"
              % (K, m['bic'], m['silhouette'], m['stability']))
    print(" -> chosen K=%d" % chosen)

    labels, co, sil, p_merge = stability_analysis(Xr, chosen, rng)
    print("\nstability: silhouette=%.3f random-merge p=%.3f" % (sil, p_merge))
    block = np.mean([co[truth == a][:, truth == a].mean() for a in range(K_true)])
    print(" within-true-group co-assignment mean=%.3f (ideal 1)" % block)

    _, _, member, k_dist = uncertainty(Xr, chosen, rng, reselect=True, k_grid=k_grid)
    print(" mean max membership prob=%.3f" % np.mean(member.max(1)))
    print(" bootstrap K distribution=%s" % {k: round(v, 2) for k, v in k_dist.items()})

    print("\nsensitivity to perturbation:")
    for s, ari, agree in sensitivity(Xr, chosen, rng):
        print(" noise=%.2f ARI=%.3f label-agreement=%.3f" % (s, ari, agree))
