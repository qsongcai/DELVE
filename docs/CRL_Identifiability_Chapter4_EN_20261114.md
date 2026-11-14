# Identifiability Boundary (Chapter 4, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. This is mechanism A: a single pooled distribution, with no environment labels. The results below do not imply the DELVE recovery guarantees in Chapter 5.

---

## 4.1 What identifiability means

Let $P_X$ be the pooled marginal, and write a mixture as a measure over component laws,

$$\mu=\sum_e a_e\delta_{G_e},\qquad a_e>0,\qquad \sum_e a_e G_e=P_X.$$

The decomposition set is

$$\mathcal D(P_X)=\left\{\mu=\sum_e a_e\delta_{G_e}:\ a_e>0,\ \sum_e a_e G_e=P_X\right\}.$$

The structure is identified up to label permutation when $\mathcal D(P_X)$ is a singleton. With the labels gone and only $P_X$ in hand, the joint law of $(X,E)$ is not fixed. Any Markov kernel $\kappa(e\mid x)$ whose integral against $P_X$ matches the label marginal is a valid assignment, and the set of such kernels is, outside degenerate cases, more than one point. The first result makes this concrete with an explicit witness.

## 4.2 Partition non-identification

**Theorem 1 (the pooled marginal does not determine the partition).** *There exist two environment assignments $\sigma$ and $\sigma'$, not related by a global label permutation, that hold simultaneously under one and the same observation distribution. A measure-preserving bijection $T$ on the latent space satisfies*

$$T_\#P_Z=P_Z,\qquad \sigma'=\sigma\circ T,\qquad \sigma'\notin\{\sigma,\ 1-\sigma\}.$$

**Construction.** Work in two dimensions. Let the latent variable $z=(Z_1,Z_2)$ be uniform on the unit disk $\mathcal D=\{z:\|z\|\le 1\}$, and take the mixing map to be the identity so that $x=z$. There are two environments of equal weight.

The first assignment splits the disk by the sign of the first coordinate,

$$\sigma(z)=\mathbb 1[z_1\ge 0].$$

Each half carries half the disk. Now rotate by a quarter turn,

$$T(z_1,z_2)=(-z_2,z_1),\qquad \det J_T=1.$$

The rotation preserves the disk and its uniform measure, so $T_\#P_Z=P_Z$ and the pooled distribution is unchanged. The second assignment is

$$\sigma'(z)=\sigma(Tz)=\mathbb 1[z_2\le 0],$$

which splits the disk by the sign of the second coordinate. The two partitions disagree on the second and fourth quadrants, where the coordinates have opposite signs:

$$P_Z(\sigma\ne\sigma')=\tfrac12.$$

A global label permutation flips either every point or none, measured by the assignment, so it cannot produce a half-set disagreement. Hence $\sigma'$ is not a relabeling of $\sigma$. $\square$

The same fact reads as a coupling argument. The label $E$ is an unobserved categorical variable, and $P_X$ fixes only the marginal of $X$. The joint law of $X$ and $E$ is a coupling of $P_X$ with the label marginal, and the set of such couplings is convex and is a singleton only in degenerate cases. Every coupling in that set gives a different assignment while sharing $P_X$. The rotation is an explicit, smooth, measure-preserving witness to the general statement rather than the general statement itself.

The construction is not tied to the identity map. For any diffeomorphism $g$ onto its image, the transported partitions $\sigma\circ g^{-1}$ and $\sigma'\circ g^{-1}$ remain distinct under the same $P_X$ and are not related by a permutation. A full-column-rank linear mixing $x=Gz$ is the special case where the rotation becomes the linear conjugate $GTG^{-1}$. A local variant, a compactly supported volume-preserving involution that swaps the assignment on two small equal-area regions, shows the non-uniqueness is not an artifact of a global rotation.

On a sample of $2\times10^5$ draws the disagreement fraction is $0.5000$, the two assignments stay near equal weight, and the empirical squared maximum-mean-discrepancy between $Z$ and $T(Z)$ is $0.00058$, finite-sample noise around a population value of zero. The environment-specific means under the two partitions point along orthogonal axes, so the conditional distributions genuinely differ even though the pooled law cannot tell them apart.

A scoping note belongs here. The theorem is a single $d=2$ witness, not a claim that every pooled distribution is non-identifiable. It establishes that identifiability cannot be assumed and that the uniqueness clause in the known-index formulations of the problem fails at the population level; finite samples then add estimation error on top of a non-uniqueness that is already present.

## 4.3 Point identification in a constrained Gaussian frame

Tighten the setting and the decomposition set collapses to a point. The frame is a linear, invertible mixing, whitened after the fact, with a symmetric two-component structure.

**Theorem 2 (point identification under the constrained frame).** *Under a linear invertible mixing, after whitening and within the symmetric two-component frame, the fourth-order cumulant tensor determines the component parameter up to label permutation. In $d=2$ the moment inversion is unique under a fixed separation.*

The cumulant identity behind the inversion is

$$\kappa_{ijkl}=K_{ij}K_{kl}+K_{ik}K_{jl}+K_{il}K_{jk},$$

where $K$ is the symmetric component parameter in the whitened frame, written $I\pm K$ for the two components. Contracting the tensor against a symmetric basis and inverting the resulting moment equations recovers $K$; the whitening step removes the second-order freedom, and the symmetry constraint removes the remaining rotational freedom. The recovered object is the unordered component parameter, up to permutation. $\square$

This is exactly what it looks like: a constrained special case. The whitening, the two-component restriction, and the symmetry are doing the work, and the result is not a generic fourth-order theorem. Outside that frame the generic fourth-order map is non-injective, and the generic injectivity threshold for centered Gaussian mixtures sits at sixth order, within explicit rank bounds on the number of components. With the full distribution rather than a finite collection of moments, a finite Gaussian mixture is identifiable up to permutation by the classical mixture result. We report the fourth-versus-sixth order threshold and the full-distribution result as cited propositions, checking the exact rank bounds against the source for each $(m,n)$ before quoting them; they are not proofs this paper claims as its own.

## 4.4 Scope

The identifiability results operate on one pooled marginal and identify either the partition witness or the unordered component parameter. They do not identify recording assignments, they do not establish finite-sample recovery, and they do not support the DELVE algorithm in Chapter 5. The two mechanisms are kept separate on purpose: mechanism A states what a single pooled distribution can and cannot pin down, and mechanism B asks what repeated recording-level features recover. No implication runs from one to the other. The generic non-Gaussian, fully blind identification problem remains open and is stated in the limitations.
