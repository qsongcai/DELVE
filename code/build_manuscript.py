#!/usr/bin/env python3
"""Assemble the eight chapters into a compilable elsarticle manuscript."""
import os
import re
import shutil
import subprocess

ROOT = "/home/user/Doubao/chats/38451878760457474"
SRC = ROOT
BUILD = os.path.join(ROOT, "manuscript")
ELS = os.path.join(ROOT, "elsevier_template", "elsarticle")

CHAPTERS = [
    ("CRL_Introduction_Chapter1_EN_20261114.md", "Introduction"),
    ("CRL_RelatedWork_Chapter2_EN_20261114.md", "Related Work"),
    ("CRL_ProblemFormulation_Chapter3_EN_20261114.md", "Problem Formulation"),
    ("CRL_Identifiability_Chapter4_EN_20261114.md", "Identifiability Boundary"),
    ("CRL_RecoveryTheory_Chapter5_EN_20261114.md", "Recovery Theory"),
    ("CRL_Synthetic_Chapter6_EN_20261114.md", "Synthetic and Semi-synthetic Experiments"),
    ("CRL_RealEEG_Chapter7_EN_20261114.md", "Recording-level Covariance Clustering Across EEG Sources"),
    ("CRL_LimitationsConclusion_Chapter8_EN_20261114.md", "Limitations and Conclusion"),
]
ABSTRACT = "CRL_Abstract_FINAL_20261114.md"
APPENDIX = "CRL_Appendix_A_20261115.md"


def strip_header(text):
    """Drop everything through the first line that is exactly '---'."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:]).strip() + "\n"
    raise ValueError("no header separator found")


HEAD_NUM = re.compile(r"^(#{1,6})[ \t]+\d+(?:\.\d+)*\.?[ \t]+(.*)$")


def strip_heading_numbers(text):
    """Remove manual numbers (e.g. '5.1') baked into headings; LaTeX numbers them."""
    out = []
    for line in text.splitlines():
        m = HEAD_NUM.match(line)
        out.append(f"{m.group(1)} {m.group(2)}" if m else line)
    return "\n".join(out) + "\n"


def pandoc(md_path, tex_path):
    cmd = ["pandoc", md_path, "-f", "markdown+tex_math_dollars+raw_tex",
           "-t", "latex", "-o", tex_path]
    subprocess.run(cmd, check=True)


def _find_cmd(text, cmd, start=0):
    """Return (start, end) of '\\cmd{...}' with brace matching, or None."""
    i = text.find(cmd + "{", start)
    if i == -1:
        return None
    depth, k = 0, i + len(cmd)
    while k < len(text):
        ch = text[k]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return (i, k + 1)
        k += 1
    return None


def _reorder_table_block(block):
    """Move the table caption/label (pandoc puts them below) above the tabular."""
    cap = _find_cmd(block, r"\caption")
    if cap is None:
        return block
    cstart, cend = cap
    lab = _find_cmd(block, r"\label", cend)
    spans = sorted([cap] + ([lab] if lab is not None else []))
    captext = block[cstart:cend].strip()
    labtext = block[lab[0]:lab[1]].strip() if lab is not None else ""
    remainder, cursor = "", 0
    for a, b in spans:
        remainder += block[cursor:a]
        cursor = b
    remainder += block[cursor:]
    remainder = re.sub(r"\n[ \t]*\n[ \t]*\n", "\n\n", remainder)
    bt = remainder.find(r"\begin{tabular}")
    if bt == -1:
        return block
    moved = captext + "\n" + (labtext + "\n" if labtext else "")
    return remainder[:bt] + moved + remainder[bt:]


def fix_nbsp(text):
    """Pandoc turns the LaTeX non-breaking '~' into a visible '\\textasciitilde{}';
    restore the intended tie before \\cite/\\ref/\\eqref. Pandoc sometimes emits
    the command without braces (followed by a space), so cover both forms."""
    return re.sub(r"\\textasciitilde(?:\{\})?", "~", text)


def move_table_captions(text):
    """Reorder every 'table' float; algorithm floats are left untouched."""
    out, pos = [], 0
    for m in re.finditer(r"\\begin\{table\}", text):
        start = m.start()
        end = text.find(r"\end{table}", start)
        if end == -1:
            continue
        end += len(r"\end{table}")
        out.append(text[pos:start])
        out.append(_reorder_table_block(text[start:end]))
        pos = end
    out.append(text[pos:])
    return "".join(out)


def main():
    os.makedirs(BUILD, exist_ok=True)
    # class and bibliography styles
    for name in ["elsarticle.cls", "elsarticle-num.bst", "elsarticle-harv.bst",
                 "elsarticle-num-names.bst"]:
        shutil.copy(os.path.join(ELS, name), os.path.join(BUILD, name))
    shutil.copy(os.path.join(ROOT, "references.bib"), os.path.join(BUILD, "references.bib"))
    for fig in ("fig1_k_sensitivity", "fig2_pca_scatter", "fig3_bootstrap_ci",
                "fig4_spatial_novelty", "fig5_witness", "fig6_pipeline",
                "fig7_ch6_sweep", "fig8_main_results"):
        shutil.copy(os.path.join(ROOT, "figures", fig + ".pdf"),
                    os.path.join(BUILD, fig + ".pdf"))

    fragment_inputs = []
    for idx, (fname, clean_title) in enumerate(CHAPTERS, start=1):
        with open(os.path.join(SRC, fname), encoding="utf-8") as fh:
            body = strip_heading_numbers(strip_header(fh.read()))
        md_clean = os.path.join(BUILD, f"ch{idx}.md")
        tex_frag = os.path.join(BUILD, f"ch{idx}.tex")
        with open(md_clean, "w", encoding="utf-8") as fh:
            fh.write(body)
        pandoc(md_clean, tex_frag)
        # pandoc emits bare auto labels for repeated subsection titles; make them
        # unique per chapter (these labels are not referenced in the prose)
        with open(tex_frag, encoding="utf-8") as fh:
            frag = fh.read()
        frag = fix_nbsp(frag)
        for bare in ("scope", "summary"):
            frag = frag.replace(f"\\label{{{bare}}}", f"\\label{{{bare}-{idx}}}")
        # Elsevier house style: table caption/title sits above the tabular
        frag = move_table_captions(frag)
        with open(tex_frag, "w", encoding="utf-8") as fh:
            fh.write(frag)
        fragment_inputs.append((idx, clean_title))
        os.remove(md_clean)

    # abstract fragment
    with open(os.path.join(SRC, ABSTRACT), encoding="utf-8") as fh:
        abs_body = strip_header(fh.read())
    abs_md = os.path.join(BUILD, "abs.md")
    abs_tex = os.path.join(BUILD, "abs.tex")
    with open(abs_md, "w", encoding="utf-8") as fh:
        fh.write(abs_body)
    pandoc(abs_md, abs_tex)
    with open(abs_tex, encoding="utf-8") as fh:
        abs_frag = fix_nbsp(fh.read())
    with open(abs_tex, "w", encoding="utf-8") as fh:
        fh.write(abs_frag)
    os.remove(abs_md)

    # appendix fragment: drop the top-level title; main.tex emits \appendix + \section
    with open(os.path.join(SRC, APPENDIX), encoding="utf-8") as fh:
        app_body = strip_header(fh.read())
    app_lines = app_body.splitlines()
    for j, line in enumerate(app_lines):
        if line.startswith("# "):
            app_body = "\n".join(app_lines[j + 1:]).strip() + "\n"
            break
    app_md = os.path.join(BUILD, "appA.md")
    app_tex = os.path.join(BUILD, "appA.tex")
    with open(app_md, "w", encoding="utf-8") as fh:
        fh.write(app_body)
    pandoc(app_md, app_tex)
    with open(app_tex, encoding="utf-8") as fh:
        app_frag = fix_nbsp(move_table_captions(fh.read()))
    with open(app_tex, "w", encoding="utf-8") as fh:
        fh.write(app_frag)
    os.remove(app_md)

    # main document
    sections = "\n".join(
        "\\section{%s}\n\\input{ch%d.tex}\n" % (title, i) for i, title in fragment_inputs
    )
    sections += "\n\\appendix\n\\section{Proofs and detailed derivations}\n\\input{appA.tex}\n"
    main_tex = r"""\documentclass[preprint,12pt]{elsarticle}

\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{url}
\mathchardef\UrlBreakPenalty=10000
\mathchardef\UrlBigBreakPenalty=10000
\usepackage{graphicx}
\usepackage{float}
\newfloat{algorithm}{htbp}{loa}
\floatname{algorithm}{Algorithm}
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.8}
\setcounter{topnumber}{2}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{3}

\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{proposition}[theorem]{Proposition}
\theoremstyle{definition}
\newtheorem{assumption}[theorem]{Assumption}
\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

\tolerance=2000
\emergencystretch=2em
\hbadness=2000

\journal{Neurocomputing}

\usepackage{lineno}

\begin{document}

\begin{frontmatter}

\title{Covariance-Based Latent Environments: Identifiability Limits and Conditional Recording-Level Recovery}

\author[inst1]{Qingsong Cai\corref{cor1}}
\ead{caiqs@btbu.edu.cn}
\author[inst1]{Jieping Lu}
\ead{2531062236@st.btbu.edu.cn}
\author[inst1]{Tianze Hao}
\ead{2531062234@st.btbu.edu.cn}
\cortext[cor1]{Corresponding author}
\affiliation[inst1]{organization={Beijing Technology and Business University, School of Computer and Artificial Intelligence},
            city={Beijing},
            country={China}}

\begin{abstract}
\input{abs.tex}
\end{abstract}

\begin{keyword}
Causal representation learning \sep Identifiability \sep Latent environment discovery \sep K-means clustering \sep Electroencephalography
\end{keyword}

\end{frontmatter}
\linenumbers

%s

\section*{Declaration of Competing Interest}
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

\section*{Funding}
This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

\section*{Data Availability}
The EEG data analyzed in this study are publicly available without access restrictions. The OpenNeuro datasets ds007541 and ds008099 are available at \url{https://openneuro.org/datasets/ds007541} and \url{https://openneuro.org/datasets/ds008099}, and the EEG Motor Movement/Imagery Dataset (eegmmidb) is available on PhysioNet at \url{https://physionet.org/content/eegmmidb/1.0.0/}. The processed recording-level features and the code to reproduce all analyses are available in the public DELVE repository at \url{https://github.com/qsongcai/DELVE}.

\section*{CRediT Authorship Contribution Statement}
\textbf{Qingsong Cai:} Conceptualization, Methodology, Formal analysis, Software, Writing -- original draft, Writing -- review \& editing, Supervision, Project administration. \textbf{Jieping Lu:} Software, Validation, Data curation, Visualization, Writing -- review \& editing. \textbf{Tianze Hao:} Software, Investigation, Data curation, Writing -- review \& editing.

\bibliographystyle{elsarticle-num}
\begingroup
\sloppy
\setlength{\emergencystretch}{3em}
\mathchardef\UrlBreakPenalty=10000
\mathchardef\UrlBigBreakPenalty=10000
\let\newline\relax
\def\urlprefix{\unskip\hskip 0.5em plus 0.2em}
\bibliography{references}
\endgroup

\end{document}
""" % sections
    with open(os.path.join(BUILD, "main.tex"), "w", encoding="utf-8") as fh:
        fh.write(main_tex)
    print("built manuscript in", BUILD)


if __name__ == "__main__":
    main()
