# Manuscripts

**Covariance-Based Latent Environments: Identifiability Limits and Conditional Recording-Level Recovery**

This directory holds the self-contained LaTeX manuscripts. Each subfolder compiles
on its own and includes its compiled PDF.

## Layout

- `main/` — the main manuscript (47 pages). Contains `main.tex`, the abstract, the
  eight chapter fragments, Appendix A, the Elsevier class and bibliography styles,
  all figure PDFs, the bibliography, and `main.pdf`.
- `supplementary/` — the standalone Supplementary Material (13 pages). Contains its
  own `main.tex`, the supplementary fragment, figures, bibliography, and `main.pdf`.

## Build

Both projects use the standard Elsevier `elsarticle` class and compile with
`pdflatex`. The bibliography is shipped as a `.bbl`, so a single run is sufficient;
running `bibtex` is only needed if the references change.

```
cd main && pdflatex main.tex
cd supplementary && pdflatex main.tex
```

Both build with zero errors, zero overfull boxes, and no undefined references, and
they contain no Type 3 fonts.
