#!/usr/bin/env python3
"""Cache recording-level features + dataset/subject mapping under the unified protocol."""
import os
import numpy as np
import delve_third_dataset as d3

recs = d3.collect()
feats = np.array([r["feature"] for r in recs])
datasets = np.array([r["dataset"] for r in recs])
subjects = np.array([r["subject"] for r in recs])
nwin = np.array([r["nwin"] for r in recs])
DATA_DIR = os.environ.get("DELVE_DATA_DIR", "/mnt/sdd1/datasets_qsong")
out = os.path.join(DATA_DIR, "recording_features.npz")
np.savez(out, features=feats, datasets=datasets, subjects=subjects, nwin=nwin)
print("saved", out, feats.shape)
for ds in sorted(set(datasets)):
    m = datasets == ds
    print("  %s: %d recordings, %d unique subjects"
          % (ds, m.sum(), len(set(subjects[m]))))
