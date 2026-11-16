# DELVE reproduction code

This directory contains the independently runnable Python scripts that reproduce the
analyses reported in *Covariance-Based Latent Environments: Identifiability Limits and
Conditional Recording-Level Recovery*. The scripts are kept in one flat folder so that
`import delve_core` and the relative `figures/` data paths resolve when run from this
directory.

## Setup

```
pip install -r requirements.txt
```

The local scripts need only NumPy, SciPy, and scikit-learn. The raw-data pipeline
additionally needs MNE and access to the original EEG recordings.

## Core algorithm

- `delve_core.py` — the DELVE core (Stages 1–6), pure numerical code with no MNE
  dependency. Running it directly executes a synthetic self-test.

## Local reproduction (no raw EEG, no MNE)

Run each from this directory; the data are the `.npz` files in `figures/`.

| Script | Reproduces |
|---|---|
| `r4_1_rng_audit.py` | RNG/seed derivation audit and oracle/blind comparability |
| `r4_4_gate_diagnostics.py` | eligibility-gate diagnostics (Supplementary S6) |
| `r5_2_prefixed_threeway.py` | pre-fixed, frozen, and three-way split; held-out ARI 0.470 |
| `r5_7_balanced_montecarlo.py` | balanced Monte Carlo over 100 draws; ARI 0.606 (Table 5) |
| `r5_8_selector_baselines.py` | cluster-number selector baselines (Table 4) |
| `r5_8_gate_sensitivity.py` | gate-parameter sensitivity (Supplementary S10) |
| `r5_9_permutation_null.py` | permutation null, 99th percentile near 0.05 |
| `bounded_noise_validation.py` | bounded-noise theorem-compatible arm (Section 6.2) |
| `semi_synth.py` | semi-synthetic checks |
| `leave_one_source_inductive.py` | leave-one-source-out induction and novelty; cross-fitted ARI 0.610 |
| `plugin_subject_ari.py` | subject-level plug-in ARI 0.241 |
| `subject_cluster_bootstrap.py` | subject-cluster bootstrap and subject permutation |

## Raw-data pipeline (MNE and original EEG required)

These scripts run on the GPU server where the raw EEG are stored; the data root is
set to `/mnt/sdd1/datasets_qsong/eegdash_data`.

- `delve_eeg.py` — Stage 0 raw-EEG processing and feature extraction.
- `delve_third_dataset.py` — third-dataset processing.
- `delve_strong_baselines.py` — strong baselines: three estimators and three mappings,
  six clusterers, non-covariance features, K sensitivity, hierarchy, deconfounding.
- `delve_airm_hdbscan.py` — affine-invariant Riemannian and HDBSCAN checks.
- `plv_audit.py` — phase-locking audit.
- `r5_6_fixed_window.py` — fixed-window control (imports `delve_third_dataset`);
  balanced ARI 0.577.

## Manuscript and figure builds

- `build_manuscript.py`, `build_compressed.py`, `build_supplementary.py`,
  `build_packages.py` — assemble the LaTeX sources and packages.
- `make_figures.py`, `make_concept_figures.py`, `make_ch6_figure.py`,
  `make_main_figure.py` — regenerate the figures.

## Bundled data (`figures/`)

`recording_features.npz` holds the 203 recording-level features with dataset and
subject identifiers. The remaining `.npz` files are the outputs of the listed scripts,
shipped for inspection and for cross-checking reruns.
