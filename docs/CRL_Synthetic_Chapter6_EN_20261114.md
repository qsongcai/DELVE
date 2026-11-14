# Synthetic and Semi-synthetic Experiments (Chapter 6, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. The experiments validate the implication in the recovery theorem; they do not upgrade the compatibility assumption to a consequence of a generative model.

---

## 6.1 What the experiments are for

The theory states an implication. Under the population alignment condition and the closed level-set condition, a positive risk gap separates the global empirical solution from configurations that misclassify, and an empirical solution whose excess risk stays below the gap inherits the misclassification bound. Controlled experiments can check that the implication holds when the premises are independently verified, and they can show what happens when the premises fail. They cannot turn the alignment premise into a generated conclusion. The simulations below use known truth, controlled margins, and a fixed feature transformation, the exact regime the theorem addresses.

## 6.2 Population reference

The main design is a Gaussian location model with three environments, ten feature dimensions, equal weights, and unit noise. Three centers sit on an equilateral geometry in the first two coordinates, and the signal-to-noise ratio sets the center spacing. A reference sample of $10^5$ draws serves two purposes. It independently checks the population alignment, by comparing the optimal three-center and two-center empirical risks rather than assuming the former, and it estimates the risk-gap curve $\psi(q)$ through center perturbation across a wide radius.

Two arms are run, one at signal-to-noise ratio six and one at nine tenths. The second matches the order of the separation measured on the real EEG, which makes it the relevant negative control rather than a straw case.

## 6.3 The well-separated arm

At signal-to-noise ratio six the alignment and the closed level-set conditions are checked on the reference sample rather than assumed. The true centers misclassify about three points in a thousand, and the two-center optimum runs roughly six units above the three-center optimum, a clear gap. The estimated gap curve is positive at every target level, rising from about $6.7$ at $q=0.05$ to about $15.7$ at $q=0.20$.

One premise is not met by this design. Gaussian noise has unbounded support, so no finite $\rho$ makes the almost-sure hard-ball condition $\|\xi_e\|\le\rho$ hold; what the reference shows is an empirical truncation, the fraction of draws inside any chosen ball, not the probability-one condition. The Gaussian arm therefore validates the alignment and level-set premises and the risk-gap implication, while the hard-ball premise is left to the bounded-noise design in the next section. We do not write that every premise holds on the Gaussian sample.

Across the finite-sample sweep, sixty independent repetitions are drawn at each sample size. The global empirical solution is fit with a fixed number of centers and scored on the held-out reference, so its excess risk and its misclassification are measured against the same population target. Excess risk falls from about $2.35$ at the smallest size to under one tenth at the largest, and misclassification falls with it, from about nine per thousand to three. The implication is then tested directly: whenever the excess sits below the gap for a level, the error stays below that level. No violation occurs in any repetition at any sample size or target level, zero across the full sweep. The misclassification shows the phase transition the theorem predicts, sharp rather than gradual.

## 6.4 Bounded-noise design and the hard-ball premise

The hard-ball premise deserves a design that satisfies it rather than approximating it. A second synthetic keeps the same three-environment, ten-dimensional geometry but replaces the Gaussian noise with isotropic noise uniform on a ball of radius $\rho$. The hard-ball condition $\|\xi_e\|\le\rho$ then holds almost surely by construction, and the equilateral center spacing is set to $\Delta=6\rho$, which strictly exceeds the $4\rho$ the margin requires.

On a reference of $10^5$ draws the empirical maximum noise norm is exactly $\rho$, the margin reads $\Delta=6\rho>4\rho$, and the nearest-center classifier at the true centers makes no error at all, zero rather than three per thousand. That exact correctness is the hard-ball argument made direct: a point sits within $\rho$ of its own center and no closer than $\Delta-\rho=5\rho$ to any other, so the own center always wins. The finite-sample sweep repeats the global empirical fit across the same sample sizes and sixty repetitions. Excess risk falls from about $0.19$ at the smallest size to under one hundredth at the largest, misclassification stays at zero throughout, and the gap implication has no violation in any repetition at any level. The bounded design meets the hard-ball premise in full, and the Gaussian arm is read as a separate, unbounded-support robustness study rather than a witness to that premise.

## 6.5 The negative control

At signal-to-noise ratio nine tenths the picture changes. The true centers misclassify close to half the reference, and the two-versus-three-center gap shrinks to about half a unit, with the estimated gap curve near zero. The empirical excess still declines as the sample grows, from about $1.48$ to under one fifth, yet misclassification does not follow. It stays on a plateau near sixty percent with no phase transition across the whole sweep.

That plateau is the informative result. When the population optimum is not aligned with the true labels, adding data cannot restore them, because the object being estimated is itself misaligned. A mechanical count of gap violations on this arm is not meaningful: the gap is near zero, and the reference estimate of a near-zero quantity carries finite-sample noise. We therefore read the arm through the stable fact, the error plateau, instead of reporting noisy threshold crossings as counterexamples. The arm parallels the real EEG, whose separation is of the same order and whose recovery numbers are diagnostic rather than validation.

## 6.6 Non-Gaussian shapes

A separate set of experiments asks whether dropping the Gaussian shape while keeping the blind, minimal-data setting helps. With the shape unknown, the pooled fourth moment is non-identified: the same moment matches several pairs of component and kurtosis parameters, and each higher moment introduces a new unknown shape parameter, so finite moments never catch up. Pinning the shape restores identification. A light-tailed fixed family reaches a parametric rate, with blind recovery error falling from about $0.17$ to $0.02$ as the sample grows, while a heavy-tailed fixed family stays consistent but inefficient, with error around $0.14$ even at the largest sample. Letting the shape be estimated jointly fails on a Student-$t$ design: the degrees-of-freedom estimate is badly biased and the component error does not decline, because the higher moment the estimator needs has infinite sampling variance.

The honest reading is that fixing the shape is a parametric assumption on the same footing as the Gaussian, a substitution rather than a relaxation, and it is not packaged as a separate contribution. The general-shape non-identification and the fixed-shape recovery sharpen the boundary rather than widen the claim.

## 6.7 Heavy tails and contamination

Under Huber contamination and heavy-tailed designs, the robust, median-of-means variant is compared with the non-robust fit on equal footing. In the specified contamination and heavy-tail experiments the robust version carries smaller error or recovers more stably, with a breakdown point at one half. The statement is confined to those experiments and is not asserted across distributions or sample sizes. The non-asymptotic bound degrades as the environments approach each other, since the strong-convexity constant controlling parameter propagation tends to zero with the separation, and it becomes unusable once the propagated error exceeds the margin. Small-separation cases are dominated by this floor, and the high-quantile error falls with sample size in the simulations, consistent with the bound.

## 6.8 Misspecifying the number of environments

The number of environments is fixed in the theory, and a pre-specified sweep over the candidate grid shows how a wrong value acts on the assignment. Underestimating by one merges two environments into a single cluster, and the merge is systematic rather than random: across six balanced seeds the same pair is joined every time, driven by the relative proximity of their log-covariance centers. The merged cluster separates cleanly into the two true components once the correct number is restored. Overestimating adds nested refinement and lowers the nearest-centroid cost monotonically, with no elbow that would identify the true value, which is why the one-standard-error rule runs to the grid boundary. Neither pre-specified rule recovers the oracle number. The experiment supports keeping automatic selection outside the guarantees and reports the underestimation as a primary finding.

## 6.9 Summary

The experiments establish four facts. When the alignment and closed-set premises hold independently, the risk-gap implication is borne out on the Gaussian arm with no violations and a clear phase transition, even though that arm does not satisfy the hard-ball support condition. The bounded-noise design meets the hard-ball premise in full and classifies with zero error and zero violations. When the population optimum is misaligned, more data leave a stable error plateau, and the same is true under unknown non-Gaussian shapes. Robust and misspecification results are stated with their conditions attached. Nothing here upgrades the compatibility premise, and the synthetic evidence is not used to claim that the real EEG satisfies the theorem.
