# Synthetic and Semi-synthetic Experiments (Chapter 6, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-14. Status: formal manuscript section. The bounded-noise experiment satisfies the hard-ball and margin premises by construction and gives a finite-sample numerical diagnosis of the recovery chain; the Gaussian arm is an empirical robustness study under unbounded noise. Neither upgrades the compatibility assumption to a consequence of a generative model.

---

## 6.1 What the experiments are for

The theory states an implication. Under the population alignment condition and the closed level-set condition, a positive risk gap separates the global empirical solution from configurations that misclassify, and an empirical solution whose excess risk stays below the gap inherits the misclassification bound. Controlled experiments can check that the implication holds when the premises are independently verified, and they can show what happens when the premises fail. They cannot turn the alignment premise into a generated conclusion. The simulations below use known truth, controlled margins, and a fixed feature transformation, the exact regime the theorem addresses.

## 6.2 Population reference

The main design is a Gaussian location model with three environments, ten feature dimensions, equal weights, and unit noise. Three centers sit on an equilateral geometry in the first two coordinates, and the signal-to-noise ratio sets the center spacing. A reference sample of $10^5$ draws serves two purposes. It independently checks the population alignment, by comparing the optimal three-center and two-center empirical risks rather than assuming the former, and it estimates the risk-gap curve $\psi(q)$ through center perturbation across a wide radius.

Two arms are run, one at signal-to-noise ratio six and one at nine tenths. The second matches the order of the separation measured on the real EEG, which makes it the relevant negative control rather than a straw case.

## 6.3 The well-separated arm

At signal-to-noise ratio six the alignment and the closed level-set conditions are checked on the reference sample rather than assumed. The true centers misclassify about three points in a thousand, and the two-center optimum runs roughly six units above the three-center optimum, a clear gap. The estimated gap curve is positive at every target level, rising from about $6.7$ at $q=0.05$ to about $15.7$ at $q=0.20$.

One premise is not met by this design. Gaussian noise has unbounded support, so no finite $\rho$ makes the almost-sure hard-ball condition $\|\xi_e\|\le\rho$ hold; what the reference shows is an empirical truncation, the fraction of draws inside any chosen ball, not the probability-one condition. On the Gaussian arm the alignment and level-set premises are checked empirically and the risk-gap implication is observed without violation, but the theorem as a whole does not apply because the hard-ball premise fails; that premise is met by the bounded-noise design in the next section. We read this arm as an empirical robustness study under model misspecification, not as a validation of the theorem, and we do not write that every premise holds.

Across the finite-sample sweep, sixty independent repetitions are drawn at each sample size. The global empirical solution is fit with a fixed number of centers and scored on the held-out reference, so its excess risk and its misclassification are measured against the same population target. Excess risk falls from about $2.35$ at the smallest size to under one tenth at the largest, and misclassification falls with it, from about nine per thousand to three. The implication is then tested directly: whenever the excess sits below the gap for a level, the error stays below that level. No violation occurs in any repetition at any sample size or target level, zero across the full sweep. The misclassification shows the phase transition the theorem predicts, sharp rather than gradual.

## 6.4 Bounded-noise design and the hard-ball premise

The hard-ball premise deserves a design that satisfies it rather than approximating it. A second synthetic keeps the same three-environment, ten-dimensional geometry but replaces the Gaussian noise with isotropic noise uniform on a ball of radius $\rho$. The hard-ball condition $\|\xi_e\|\le\rho$ then holds almost surely by construction, and the equilateral center spacing is set to $\Delta=6\rho$, which strictly exceeds the $4\rho$ the margin requires.

On a reference of $10^5$ draws the empirical maximum noise norm is exactly $\rho$, the margin reads $\Delta=6\rho>4\rho$, and the nearest-center classifier at the true centers makes no error at all, zero rather than three per thousand. That exact correctness is the hard-ball argument made direct: a point sits within $\rho$ of its own center and no closer than $\Delta-\rho=5\rho$ to any other, so the own center always wins. The finite-sample sweep repeats the global empirical fit across the same sample sizes and sixty repetitions. Excess risk falls from about $0.19$ at the smallest size to under one hundredth at the largest, misclassification stays at zero throughout, and the gap implication has no violation in any repetition at any level. The bounded design meets the hard-ball premise in full, and the Gaussian arm is read as a separate, unbounded-support robustness study rather than a witness to that premise.

The premises do not all have the same logical status, and the experiment is reported accordingly. Two pieces hold analytically and with probability one: the hard-ball support $\|\xi_e\|\le\rho$, because the noise is uniform on that ball by construction, and the margin $\Delta=6\rho>4\rho$, which is a fixed design choice; the nearest-center correctness at the true centers then follows from the hard-ball argument rather than from a count. The remaining pieces are finite-sample checks, not analytic proofs. The population K-means alignment is assessed by comparing the three-center and two-center risks on the finite reference, and the gap curve $\psi(q)$ is estimated from the same finite draws; the absence of violations across the sixty repetitions is a finite-repetition observation. The reference therefore gives a numerical diagnosis of the theorem's chain. It does not prove the population alignment, and a larger reference would only sharpen the estimate rather than turn it into a probability-one conclusion.

## 6.5 The negative control

At signal-to-noise ratio nine tenths the picture changes. The true centers misclassify close to half the reference, and the two-versus-three-center gap shrinks to about half a unit, with the estimated gap curve near zero. The empirical excess still declines as the sample grows, from about $1.48$ to under one fifth, yet misclassification does not follow. It stays on a plateau near sixty percent with no phase transition across the whole sweep.

That plateau is the informative result. When the population optimum is not aligned with the true labels, adding data cannot restore them, because the object being estimated is itself misaligned. A mechanical count of gap violations on this arm is not meaningful: the gap is near zero, and the reference estimate of a near-zero quantity carries finite-sample noise. We therefore read the arm through its one stable fact—the error plateau—rather than reporting noisy threshold crossings as counterexamples. The arm parallels the real EEG, whose separation is of the same order and whose recovery numbers are diagnostic rather than validation.

## 6.6 Secondary robustness checks

Three secondary designs probe the boundary without standalone systematic tables, so they are summarized as qualitative checks rather than numbered results, with no cross-design comparison.

- **Non-Gaussian shapes.** With the shape left free, the pooled fourth moment stays non-identified, as each higher moment introduces a new unknown shape parameter; fixing the shape restores a parametric rate, but this is a substitution on the same footing as the Gaussian rather than a relaxation. Jointly estimating the shape does not converge in the tested Student-$t$ design.
- **Heavy tails and contamination.** A median-of-means robust variant is more stable than the non-robust fit in the specified Huber and heavy-tailed configurations, but the comparison is confined to those designs and is not asserted across distributions. The non-asymptotic bound weakens as the environments approach each other and becomes unusable once the propagated error exceeds the margin.
- **Number of environments.** A pre-specified grid sweep shows that underestimating $K$ merges the same pair of environments across seeds, while overestimating adds nested refinement with no elbow that identifies the true value. This supports keeping automatic selection outside the guarantees.

These checks sharpen the boundary rather than add a contribution, and no claim is made beyond the specific designs.

## 6.9 Summary

The experiments establish four facts. On the Gaussian arm, where the hard-ball support condition fails, the risk-gap implication is nevertheless observed with no violations and a clear phase transition, an empirical robustness result rather than a theorem check. The bounded-noise design meets the hard-ball premise and the margin analytically by construction, while its population alignment and gap curve are finite-reference checks; the experiment therefore numerically diagnoses the theorem's chain rather than validating it, classifying with zero error and zero violations across the observed repetitions. When the population optimum is misaligned, more data leave a stable error plateau, and the same is true under unknown non-Gaussian shapes. Robust and misspecification results are stated with their conditions attached, and the compatibility premise stays an assumption throughout.
