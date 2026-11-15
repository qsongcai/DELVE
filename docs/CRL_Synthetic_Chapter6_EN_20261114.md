# Synthetic and Semi-synthetic Experiments (Chapter 6, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-15. Status: shortened manuscript section. The bounded-noise experiment satisfies the hard-ball and margin premises by construction; the Gaussian arm is an empirical robustness study under unbounded noise. Neither turns the compatibility assumption into a generated conclusion.

---

## 6.1 Experimental setup and population reference

The theory states an implication. Under alignment and closed level sets, a positive risk gap separates the global empirical solution from configurations that misclassify, and a solution whose excess risk stays below the gap inherits the misclassification bound. Controlled experiments can check that the implication holds when the premises are independently verified, and they can show what happens when the premises fail. They cannot turn the alignment premise into a generated conclusion.

The main design is a Gaussian location model with three environments, ten feature dimensions, equal weights, and unit noise. Three centers sit on an equilateral geometry in the first two coordinates, and the signal-to-noise ratio sets the spacing. A reference sample of $10^5$ draws serves two purposes. It independently checks the population alignment by comparing the optimal three-center and two-center empirical risks rather than assuming the former, and it estimates the risk-gap curve $\psi(q)$ through center perturbation. Two arms are run, one at signal-to-noise ratio six and one at nine tenths. The second matches the order of the separation measured on the real EEG, which makes it the relevant negative control rather than a straw case.

## 6.2 The well-separated and bounded-noise arms

At signal-to-noise ratio six, the alignment and level-set conditions are checked on the reference rather than assumed. The true centers misclassify about three points in a thousand, and the two-center optimum runs roughly six units above the three-center optimum. The estimated gap curve is positive at every target level, rising from about $6.7$ at $q=0.05$ to about $15.7$ at $q=0.20$.

One premise is not met by this design. Gaussian noise has unbounded support, so no finite $\rho$ makes the almost-sure hard-ball condition hold; what the reference shows is an empirical truncation, not the probability-one condition. The alignment and level-set premises are checked empirically and the risk-gap implication is observed without violation, but the theorem as a whole does not apply because the hard-ball premise fails. We read this arm as an empirical robustness study under model misspecification, not as a validation of the theorem.

Across the finite-sample sweep, sixty independent repetitions are drawn at each sample size, and the global empirical solution is scored on the held-out reference. Excess risk falls from about $2.35$ at the smallest size to under one tenth at the largest, and misclassification falls with it, from about nine per thousand to three. Whenever the excess sits below the gap for a level, the error stays below that level, with no violation in any repetition. The misclassification shows the sharp phase transition the theorem predicts. Figure~\ref{fig:sweep} plots the sweep against the theoretical gap thresholds and the target levels.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{fig7_ch6_sweep.pdf}
\caption{Finite-sample sweep over sixty repetitions. Left: excess risk against sample size with the theoretical gap thresholds $\psi(0.05)$ and $\psi(0.20)$; the excess crosses $\psi(0.05)$ near $M=10$. Right (log scale): misclassification falls below the target level $q=0.05$ after the crossing for the aligned arm, while the negative control stays on a plateau near $0.6$.}
\label{fig:sweep}
\end{figure}

The hard-ball premise deserves a design that satisfies it rather than approximating it. A second synthetic keeps the same geometry but replaces the Gaussian noise with isotropic noise uniform on a ball of radius $\rho$. The hard-ball condition then holds almost surely by construction, and the equilateral spacing is set to $\Delta=6\rho$, which strictly exceeds the $4\rho$ the margin requires. On the reference, the empirical maximum noise norm is exactly $\rho$, and the nearest-center classifier at the true centers makes no error at all. The finite-sample sweep repeats the same fit across the same sizes and sixty repetitions: excess risk falls from about $0.19$ to under one hundredth, misclassification stays at zero, and the gap implication has no violation.

The premises do not all have the same logical status. The hard-ball support and the margin hold analytically and with probability one, while the population alignment and the gap curve are finite-reference checks. The reference therefore gives a numerical diagnosis of the theorem's chain rather than proving it, and a larger reference would only sharpen the estimate.

Three secondary robustness checks sharpen the boundary without standalone tables. With the shape left free, the pooled fourth moment stays non-identified as each higher moment introduces a new shape parameter, and jointly estimating the shape does not converge in the tested Student-$t$ design. A median-of-means robust variant is more stable in the specified Huber and heavy-tailed configurations, but the non-asymptotic bound weakens as the environments approach each other. A pre-specified grid sweep shows that underestimating $K$ merges the same pair of environments while overestimating adds nested refinement with no elbow, which supports keeping automatic selection outside the guarantees.

## 6.3 The negative control

At signal-to-noise ratio nine tenths the picture changes. The true centers misclassify close to half the reference, and the two-versus-three-center gap shrinks to about half a unit, with the estimated gap curve near zero. The empirical excess still declines as the sample grows, from about $1.48$ to under one fifth, yet misclassification does not follow. It stays on a plateau near sixty percent with no phase transition across the whole sweep.

That plateau is the informative result. When the population optimum is not aligned with the true labels, adding data cannot restore them, because the object being estimated is itself misaligned. A mechanical count of gap violations is not meaningful here, since the gap is near zero and its reference estimate carries finite-sample noise. We read the arm through its one stable fact, the error plateau, rather than reporting noisy threshold crossings as counterexamples. The arm parallels the real EEG, whose separation is of the same order and whose recovery numbers are diagnostic rather than validation.

## 6.4 Summary

The experiments establish four facts. On the Gaussian arm, where the hard-ball support condition fails, the risk-gap implication is nevertheless observed with no violations and a clear phase transition, an empirical robustness result rather than a theorem check. The bounded-noise design meets the hard-ball premise and the margin analytically by construction, while its alignment and gap curve are finite-reference checks, so it numerically diagnoses the chain rather than validating it, classifying with zero error and zero violations. When the population optimum is misaligned, more data leave a stable error plateau, and the same is true under unknown non-Gaussian shapes. Robust and misspecification results are stated with their conditions attached, and the compatibility premise stays an assumption throughout.
