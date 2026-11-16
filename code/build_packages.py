#!/usr/bin/env python3
"""Rebuild the flat manuscript package and the full project archive."""
import os
import shutil
import tempfile
import zipfile

SRC = os.path.dirname(os.path.abspath(__file__))
STAMP = "20261115"

SKIP_EXT = {".aux", ".log", ".out", ".toc", ".lof", ".lot", ".blg"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}

CANON_MD = [
    "CRL_Abstract_FINAL_20261114.md",
    "CRL_Introduction_Chapter1_EN_20261114.md",
    "CRL_RelatedWork_Chapter2_EN_20261114.md",
    "CRL_ProblemFormulation_Chapter3_EN_20261114.md",
    "CRL_Identifiability_Chapter4_EN_20261114.md",
    "CRL_RecoveryTheory_Chapter5_EN_20261114.md",
    "CRL_Synthetic_Chapter6_EN_20261114.md",
    "CRL_RealEEG_Chapter7_EN_20261114.md",
    "CRL_LimitationsConclusion_Chapter8_EN_20261114.md",
    "CRL_Appendix_A_20261115.md",
    "CRL_Supplementary_20261115.md",
]


def ignore_factory(skip_extra=()):
    def _ignore(directory, names):
        blocked = set()
        for name in names:
            full = os.path.join(directory, name)
            if name in SKIP_DIRS or name in skip_extra:
                blocked.add(name)
            elif os.path.isfile(full) and os.path.splitext(name)[1] in SKIP_EXT:
                blocked.add(name)
        return blocked
    return _ignore


def zip_dir(src_root, zip_path, prefix=None):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if os.path.splitext(name)[1] in SKIP_EXT:
                    continue
                full = os.path.join(root, name)
                arc = os.path.relpath(full, src_root)
                if prefix:
                    arc = prefix + "/" + arc
                zf.write(full, arc)
    return zip_path


def build_manuscript_package(work):
    stage = os.path.join(work, "manuscript_stage")
    os.makedirs(stage)
    src = os.path.join(SRC, "manuscript")
    flat = [
        "abs.tex", "main.tex", "references.bib",
        "elsarticle.cls", "elsarticle-harv.bst",
        "elsarticle-num.bst", "elsarticle-num-names.bst",
        "fig1_k_sensitivity.pdf", "fig2_pca_scatter.pdf",
        "fig3_bootstrap_ci.pdf", "fig4_spatial_novelty.pdf",
        "fig5_witness.pdf", "fig6_pipeline.pdf", "fig7_ch6_sweep.pdf",
        "fig8_main_results.pdf",
        "main.pdf", "main.bbl", "main.blg", "main.spl",
    ]
    flat += ["ch%d.tex" % i for i in range(1, 9)] + ["appA.tex"]
    for name in flat:
        shutil.copy(os.path.join(src, name), os.path.join(stage, name))
    out = os.path.join(SRC, "manuscript_elsarticle_%s.zip" % STAMP)
    zip_dir(stage, out)
    return out


README = """# CRL Project Archive

Manuscript: *Covariance-Based Latent Environments: Identifiability Limits and Conditional Recording-Level Recovery*.

This archive is the full working snapshot for the 2026-11-15 submission build.

## Contents

- Root: authoritative Markdown sources for the abstract, eight chapters, Appendix A, and the standalone Supplementary.
- `build_manuscript.py`, `build_supplementary.py`, `make_figures.py`, `make_concept_figures.py`, `make_ch6_figure.py`, `make_main_figure.py`: reproducible build and figure scripts.
- `manuscript/`: clean Elsevier main manuscript (sources plus compiled PDF; no auxiliary files).
- `supplementary/`: clean standalone Supplementary (sources plus compiled PDF).
- `DELVE/`: public code repository (core, EEG pipeline, experiments, docs), with no Git history.
- `figures/`: figure PDFs and PNGs and the local feature archives.
- `elsevier_template/`: the upstream Elsevier template.
- `references.bib`: the 25 verified bibliography entries.

The main manuscript is 44 pages and the Supplementary is 9 pages. Both build with
zero errors, overfull boxes, or undefined references, and contain no Type 3 fonts.
"""


def build_full_archive(work):
    top = "CRL_Project_Archive_%s" % STAMP
    stage = os.path.join(work, top)
    os.makedirs(stage)

    for name in CANON_MD:
        shutil.copy(os.path.join(SRC, name), os.path.join(stage, name))
    for name in ["build_manuscript.py", "build_supplementary.py",
                 "build_packages.py", "make_figures.py",
                 "make_concept_figures.py", "make_ch6_figure.py",
                 "make_main_figure.py", "verify_blind_pairs.py"]:
        shutil.copy(os.path.join(SRC, name), os.path.join(stage, name))
    shutil.copy(os.path.join(SRC, "references.bib"), os.path.join(stage, "references.bib"))

    shutil.copytree(os.path.join(SRC, "manuscript"),
                    os.path.join(stage, "manuscript"),
                    ignore=ignore_factory())
    shutil.copytree(os.path.join(SRC, "supplementary"),
                    os.path.join(stage, "supplementary"),
                    ignore=ignore_factory())
    shutil.copytree(os.path.join(SRC, "DELVE"),
                    os.path.join(stage, "DELVE"),
                    ignore=ignore_factory())
    shutil.copytree(os.path.join(SRC, "figures"),
                    os.path.join(stage, "figures"),
                    ignore=ignore_factory())
    shutil.copytree(os.path.join(SRC, "elsevier_template"),
                    os.path.join(stage, "elsevier_template"),
                    ignore=ignore_factory())

    with open(os.path.join(stage, "README_archive.md"), "w", encoding="utf-8") as fh:
        fh.write(README)

    out = os.path.join(SRC, "CRL_Project_Archive_%s.zip" % STAMP)
    zip_dir(stage, out, prefix=top)
    return out


def main():
    with tempfile.TemporaryDirectory() as work:
        mzip = build_manuscript_package(work)
        azip = build_full_archive(work)
    for path in (mzip, azip):
        print(path, os.path.getsize(path))


if __name__ == "__main__":
    main()
