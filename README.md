# DELVE

**Recording-level Discovery of Latent Covariance Environments from Pooled Observations.**

DELVE is the companion code for *Identifiability Boundaries and Conditional Recovery*. It studies whether a covariance-based environment structure stays identifiable once environment labels are removed and observations are pooled. The name is descriptive: there is no deep model, and the procedure does not claim fully blind discovery.

## What the theory does and does not cover

The code and the paper keep the estimand, the observation mechanism, and the algorithm version strictly separate. The theoretical guarantee is a **conditional** one:

- the global empirical K-means solution has a finite-sample risk-gap guarantee under a **fixed K**, a **fixed or frozen feature transformation**, bounded features, and a population alignment condition (A4') together with a closed level-set condition (A6);
- a sample-split variant gives a held-out assignment decomposition whose training-side term stays explicit.

The following stay **outside** the unconditional guarantees and are reported as empirical or transductive procedures: automatic K selection, full-pool standardization, finite-initialization Lloyd, and the unlabeled EEG satisfying the conditions. The alignment condition is an assumption, not a consequence of a generative model.

## Repository layout

```
.
├── delve_core.py              # Stages 1-6, pure numerical, no mne
├── delve_eeg.py               # GPU Stage 0 for ds007541 + ds008099 (imports delve_core)
├── delve_third_dataset.py     # adds PhysioNet on004362 under the same blind protocol
├── delve_strong_baselines.py  # 3 estimators x 3 mappings, 6 clusterers, non-covariance features
├── delve_airm_hdbscan.py      # AIRM and HDBSCAN alternatives
├── experiments/               # scripts that produce the reported numbers
│   ├── cache_recording_features.py
│   ├── subject_cluster_bootstrap.py
│   ├── plugin_subject_ari.py
│   ├── anti_splitting_diagnostic.py
│   ├── result_b_synthetic_validation.py
│   ├── setting_a_recording_level.py
│   ├── leave_one_source_inductive.py
│   ├── reference_robustness_cache.py
│   ├── reference_robustness_analysis.py
│   ├── k_one_se_rule.py
│   ├── oracle_q_support.py
│   ├── teff_estimation.py
│   ├── k_uncertainty_analysis.py
│   └── bulk_download.py
└── docs/                      # formal theory statements
```

## Installation

```bash
python3 -m pip install -r requirements.txt
```

The reported runs use Python 3.10 with numpy 2.2, scipy 1.15, scikit-learn 1.7, and mne 1.12. The EEG Stage 0 expects a GPU environment; the recording-level analyses in `experiments/` reuse the cached `recording_features.npz` and run without mne.

## Data

Three independent EEG sources are used. Set the data location once; the default matches the original GPU path and every script reads it from the same environment variable:

```bash
export DELVE_DATA_DIR=/path/to/data
```

The code expects this layout:

```
$DELVE_DATA_DIR/
└── eegdash_data/
    ├── ds007541/   # OpenNeuro ds007541: 8 ch, 1000 Hz, BrainVision, 32 subjects
    ├── ds008099/   # OpenNeuro ds008099: Emotiv EPOC, 14 ch, 128 Hz, EDF, 30 subjects
    └── on004362/   # PhysioNet eegmmidb R01 eyes-open, 64 ch, 160 Hz, EDF, 109 subjects
```

The unified pipeline keeps four shared channels (F3, F4, O1, O2), resamples to 128 Hz, applies common-average reference, 4-second windows, a 1-40 Hz band-pass and a 50 Hz notch. The dataset label mixes device, task/rest, population, duration and preprocessing; it cannot be read as a single biological or causal driver. `experiments/bulk_download.py` shows the OpenNeuro retrieval path; the PhysioNet source is downloaded directly from its public bucket.

## Reproducing the reported results

Run order is top to bottom. All paths resolve through `DELVE_DATA_DIR`.

| Reported result | Script |
|---|---|
| 203 x 10 recording features (`recording_features.npz`) | `experiments/cache_recording_features.py` |
| Known-K ARI 0.608 vs blind K=2 ARI 0.279; K=2..6 curves | `experiments/k_uncertainty_analysis.py` |
| Subject-cluster bootstrap CIs and subject permutation | `experiments/subject_cluster_bootstrap.py` |
| Unbalanced plug-in ARI 0.241 (all 171 subjects) | `experiments/plugin_subject_ari.py` |
| Split/merge descriptive diagnostics | `experiments/anti_splitting_diagnostic.py` |
| Result B synthetic validation (zero violations; negative control) | `experiments/result_b_synthetic_validation.py` |
| Recording-level formal evidence, ARI 0.009, bootstrap CI | `experiments/setting_a_recording_level.py` |
| Leave-one-source novelty, cross-fitted ARI 0.610 | `experiments/leave_one_source_inductive.py` |
| Bipolar / CSD / leave-one-channel robustness | `experiments/reference_robustness_cache.py`, `reference_robustness_analysis.py` |
| One-SE held-out cost rule (K=6 boundary) | `experiments/k_one_se_rule.py` |
| Label-aware oracle reference (11% error) | `experiments/oracle_q_support.py` |
| Effective window count | `experiments/teff_estimation.py` |
| Strong baselines (estimators, mappings, six clusterers) | `delve_strong_baselines.py` |

## Documentation

`docs/` holds the formal English recovery chapter (Conditional Compatibility Theorem, Results A-C), the $O(1/T_w)$ bias proof, and the conservative bridge that records the withdrawn exchange argument and the exact scope of every assumption.

## Citation

A citation entry will be added once the manuscript is assigned. If you use this code, please reference the paper and the three public data sources above.
