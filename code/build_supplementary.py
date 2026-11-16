#!/usr/bin/env python3
"""Build the standalone Supplementary Material for the CRL manuscript."""
import os
import shutil
import subprocess

from build_manuscript import move_table_captions, fix_nbsp

SRC = os.path.dirname(os.path.abspath(__file__))
SUPP = "CRL_Supplementary_20261115.md"
BUILD = os.path.join(SRC, "supplementary")
BIB = "references.bib"

FIGURES = ["fig2_pca_scatter.pdf", "fig3_bootstrap_ci.pdf", "fig4_spatial_novelty.pdf"]


def strip_header(text):
    marker = "---\n"
    idx = text.find(marker)
    if idx >= 0:
        return text[idx + len(marker):]
    return text


def main():
    os.makedirs(BUILD, exist_ok=True)

    with open(os.path.join(SRC, SUPP), encoding="utf-8") as fh:
        body = strip_header(fh.read())
    # drop the top-level title; main.tex supplies the title block
    body_lines = body.splitlines()
    for j, line in enumerate(body_lines):
        if line.startswith("# "):
            body = "\n".join(body_lines[j + 1:]).strip() + "\n"
            break

    frag_md = os.path.join(BUILD, "supp.md")
    frag_tex = os.path.join(BUILD, "supp.tex")
    with open(frag_md, "w", encoding="utf-8") as fh:
        fh.write(body)
    subprocess.run(["pandoc", frag_md, "-o", frag_tex], check=True)
    with open(frag_tex, encoding="utf-8") as fh:
        frag = fix_nbsp(move_table_captions(fh.read()))
    # force every table to stay at its declared position so consecutive
    # tables are not deferred and stacked away from their headings
    frag = frag.replace("\\begin{table}[htbp]", "\\begin{table}[H]")
    with open(frag_tex, "w", encoding="utf-8") as fh:
        fh.write(frag)
    os.remove(frag_md)

    shutil.copy(os.path.join(SRC, BIB), os.path.join(BUILD, BIB))
    for fig in FIGURES:
        shutil.copy(os.path.join(SRC, "figures", fig), os.path.join(BUILD, fig))

    main_tex = r"""\documentclass[preprint,12pt]{elsarticle}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{float}
\usepackage{url}
\usepackage[colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue]{hyperref}
\usepackage{lineno}

\bibliographystyle{elsarticle-num}

\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\emergencystretch}{3em}
\hbadness=10000

\begin{document}

\begin{frontmatter}
\title{Supplementary Material for \\
\emph{Covariance-Based Latent Environments: Identifiability Limits and Conditional Recording-Level Recovery}}
\end{frontmatter}
\linenumbers

\input{supp.tex}

\bibliography{references}

\end{document}
"""
    with open(os.path.join(BUILD, "main.tex"), "w", encoding="utf-8") as fh:
        fh.write(main_tex)

    for cls in ["elsarticle.cls", "elsarticle-num.bst"]:
        src_cls = os.path.join(SRC, "manuscript", cls)
        if os.path.exists(src_cls):
            shutil.copy(src_cls, os.path.join(BUILD, cls))

    def run(cmd):
        subprocess.run(cmd, cwd=BUILD, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    run(["bibtex", "main"])
    run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    print("built supplementary in", BUILD)


if __name__ == "__main__":
    main()
