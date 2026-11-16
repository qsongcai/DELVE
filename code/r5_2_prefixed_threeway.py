import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

d = np.load("figures/recording_features.npz", allow_pickle=True)
feats, dss = d["features"], d["datasets"]
DS = sorted(set(dss))


def balanced(seed):
    r = np.random.default_rng(seed)
    Xf, y, idx_all = [], [], []
    for ds in DS:
        pool = np.where(dss == ds)[0]
        idx = r.choice(pool, 30, replace=False)
        Xf.append(feats[idx]); y.append(np.full(30, ds)); idx_all.append(idx)
    return np.vstack(Xf), np.concatenate(y), idx_all


# ---- Part 1: pre-fixed identity vs fitted StandardScaler ----
print("=== Part 1: balanced 90, K=3, six seeds ===")
print(" seed | identity ARI | StandardScaler ARI | identity NMI")
ari_id, ari_sc = [], []
for s in range(6):
    Xraw, y, _ = balanced(s)
    lab_id = KMeans(3, n_init=50, random_state=s).fit_predict(Xraw)
    Xsc = StandardScaler().fit_transform(Xraw)
    lab_sc = KMeans(3, n_init=50, random_state=s).fit_predict(Xsc)
    a_id, a_sc = adjusted_rand_score(y, lab_id), adjusted_rand_score(y, lab_sc)
    nmi_id = normalized_mutual_info_score(y, lab_id)
    ari_id.append(a_id); ari_sc.append(a_sc)
    print("  %d   |    %.3f     |      %.3f        |   %.3f" % (s, a_id, a_sc, nmi_id))
print("mean +/- std identity ARI = %.3f +/- %.3f" % (np.mean(ari_id), np.std(ari_id)))
print("mean +/- std scaler  ARI = %.3f +/- %.3f" % (np.mean(ari_sc), np.std(ari_sc)))

# ---- Part 2: strict three-way split ----
print("\n=== Part 2: three-way split (10 scaler / 10 center / 10 eval per source) ===")
print(" seed | center-fit ARI | held-out eval ARI | eval NMI | eval counts per source")
ari_eval, ari_center = [], []
for s in range(6):
    Xraw, y, idx_all = balanced(s)
    rs = np.random.default_rng(100 + s)
    sc_idx, ce_idx, ev_idx = [], [], []
    for k in range(3):
        perm = rs.permutation(30)
        base = 30 * k
        sc_idx += list(base + perm[:10])
        ce_idx += list(base + perm[10:20])
        ev_idx += list(base + perm[20:30])
    sc_idx, ce_idx, ev_idx = map(np.array, (sc_idx, ce_idx, ev_idx))
    scaler = StandardScaler().fit(Xraw[sc_idx])
    Xc = scaler.transform(Xraw[ce_idx])
    km = KMeans(3, n_init=50, random_state=s).fit(Xc)
    a_ce = adjusted_rand_score(y[ce_idx], km.labels_)
    Xe = scaler.transform(Xraw[ev_idx])
    lab_e = km.predict(Xe)
    a_ev = adjusted_rand_score(y[ev_idx], lab_e)
    n_ev = normalized_mutual_info_score(y[ev_idx], lab_e)
    ari_center.append(a_ce); ari_eval.append(a_ev)
    # per-source cluster purity on eval
    pur = []
    for k in range(3):
        m = y[ev_idx] == DS[k]
        vals, cnt = np.unique(lab_e[m], return_counts=True)
        pur.append(int(cnt.max()))
    print("  %d   |     %.3f      |       %.3f       |  %.3f  | %s" % (s, a_ce, a_ev, n_ev, pur))
print("mean +/- std held-out eval ARI = %.3f +/- %.3f" % (np.mean(ari_eval), np.std(ari_eval)))
print("mean +/- std center-fit ARI    = %.3f +/- %.3f" % (np.mean(ari_center), np.std(ari_center)))

np.savez("figures/r5_2_prefixed_threeway.npz",
         ari_identity=np.array(ari_id), ari_scaler=np.array(ari_sc),
         ari_eval=np.array(ari_eval), ari_center=np.array(ari_center))
