# Related Work (Chapter 2, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. Citations use author-year; preprints are marked as such.

---

## 2.1 Causal representation learning and the identifiability program

The framing of representation learning as a causal problem is laid out by Schölkopf et al.~\cite{scholkopf2021}, who organize the field around the gap between independent and identically distributed representations and representations tied to an underlying causal model. The identifiability question sits at the center of that program: without some structural anchor, a representation is determined only up to a broad class of transformations, and downstream causal claims inherit the ambiguity.

A substantial line of work supplies the anchor through interventions and then asks how many are needed. Ahuja et al.~\cite{ahuja2023} show that interventional data identify the latent variables up to componentwise nonlinearities, with a degree-counting argument rather than a distributional assumption. Squires et al.~\cite{squires2023} work the linear case and pin down the number of interventions required when the mixing matrix is unknown, where a global rotation adds a degree of freedom beyond the fully observed setting. The score-based treatment of Varıcı et al.~\cite{varici2025} reaches identification under sparsity and faithfulness conditions using score matching, without recovering the mixing itself. These results establish what interventions buy. They presuppose that the environment or intervention index is available, which is precisely the object this paper treats as missing.

## 2.2 Mixture identifiability and the moment-order threshold

A second line asks what a single pooled distribution reveals about its components. The classical answer is that a finite mixture of normal distributions is identifiable up to permutation from the full distribution~\cite{teicher1963}. The picture changes when only a finite collection of moments is in hand. The pooled covariance, a single second moment, is underdetermined. At fourth order the generic map for centered Gaussian mixtures is non-injective, a consequence of the parallelogram identity, and generic injectivity is reached only at sixth order, within explicit rank bounds on the number of components~\cite{blomenhofer2023}. The identified object is the unordered collection of component quadratic forms, modulo permutation and a third-root-of-unity symmetry, not a partition and not a finite-sample statement.

These propositions define a boundary rather than support an algorithm. We quote the rank bounds only after checking them against the source for the relevant dimensions, and we keep them separate from our own constrained fourth-order result, where whitening and a symmetric two-component frame remove the generic fourth-order freedom. The moment-order line does not imply recording-level recovery, and no claim here treats it as doing so.

## 2.3 Environment discovery and partition learning

The closest line in spirit studies environments without treating them as fully given. Yao et al.~\cite{yao2025} formulate multi-environment learning under a known index and an explicit uniqueness condition, the assumption our impossibility witness interrogates. Clustered objectives approach the same problem from the estimation side: Murata~\cite{murata2025} extends invariant-risk objectives to a clustered setting and characterizes the environmental complexity needed for recovery, while Ng~\cite{ng2025} treats nonparametric mixtures across general environments and states the conditions under which components separate. These methods share our concern that the environment is latent, yet they differ on the unit of analysis and on the signal used. They operate on predictive or distributional objectives rather than on recording-level covariance features, and their guarantees are conditioned on the same fixed-separation premises we adopt.

## 2.4 Unlabeled recovery and the partial-identification vocabulary

Recent work continues the unlabeled-mixture line along signals we do not use. Kanamori et al.~\cite{kanamori2026} recover latent components and the mixing matrix from marginal independence, a component-level result that leaves the partition of pooled observations untouched; their estimator is a kernel-moment-matching criterion, with $k$-means serving only as a weak baseline. Chen et al.~\cite{chen2026} develop sharp partial-identification bounds for a latent prevalence from large-model panels. Our three-tier analysis targets a different object, the covariance-based environment partition, and the two should be read as complementary rather than competing.

The term partial identification carries more than one meaning and the uses are kept apart. In the econometric usage it denotes sharp bounds on a scalar parameter from a fixed set of moment or calibration constraints. In this paper it denotes the set of covariance environment parameters consistent with the relaxed assumptions, a descriptive mechanism-A framing rather than a claim of priority or a proved sharp set. We do not present partial identification as a first, and the resampling intervals that accompany it are finite-sample diagnostics, not confidence sets with an unconditional coverage theorem.

## 2.5 Position of this paper

The standard components are not where the novelty lies. Shrinkage covariance estimation, the log-Euclidean feature, nearest-centroid clustering, and the resampling diagnostics are established tools, and Ledoit and Wolf~\cite{ledoit2004} is cited for the exact shrinkage construction rather than repackaged as an invention. What this paper adds is the explicit boundary between observation mechanisms, a recording-level estimand defined apart from its window-level counterpart, a conditional risk-gap guarantee for the global empirical solution, and a pre-specified empirical protocol over three independent EEG datasets that reports where blind recovery fails. The cited work identifies components under interventions, full distributions, or marginal independence; none of it constructs the same pooled-marginal two-partition witness, and none addresses recording-level covariance recovery under the conditions stated here.
