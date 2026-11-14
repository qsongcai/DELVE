# Problem Formulation (Chapter 3, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. Notation set here is used throughout Chapters 4 and 5.

---

## 3.1 Environments and the pooled marginal

A latent environment $E$ takes values in $\{1,\dots,K\}$ with probabilities $\pi_e=P(E=e)>0$. The observed vector comes from a fixed, deterministic mixing of a latent variable,

\begin{equation}\label{eq:obs-model}
X=A\,x^{(0)}+b,
\end{equation}

where $A$ is a fixed full-column-rank transformation and $b$ a fixed offset. Conditional on the environment, $X$ has law $G_e$. Once the environment labels are removed, the analyst receives only the pooled marginal,

\begin{equation}\label{eq:pool-mixture}
P_X=\sum_{e=1}^K \pi_e G_e,
\end{equation}

a single distribution with no mark of the component behind a given draw.

The pooled covariance is the second moment of this marginal,

\begin{equation}\label{eq:pool-cov}
\bar\Sigma=E[XX^\top]=\sum_e\pi_e\Sigma_e.
\end{equation}

It is one fixed positive-definite matrix, not a random per-sample covariance. The distinction matters: the single-pool model here has no random covariance layer, and a hierarchical model where $X\mid C\sim N(0,C)$ with $C$ itself random is a different object we do not treat.

## 3.2 Two observation mechanisms

The data can be observed in two structurally different ways, and the identifiability questions they raise diverge.

**Mechanism A — one pooled distribution.** The analyst observes draws from $P_X$, or a finite collection of its moments, and asks whether a mixture decomposition is recoverable. This is the classical mixture-identification setting.

**Mechanism B — repeated recordings.** The analyst observes $M$ recordings, each containing several windows and each yielding a covariance, and asks whether recordings can be assigned to their latent environment. This is the DELVE setting.

The two mechanisms are separated on purpose. A theorem proved under mechanism A, on a single pooled marginal, does not support the mechanism B algorithm, and no implication runs in either direction.

## 3.3 The recording hierarchy

Under mechanism B the data carry a nested structure. A recording $R_r$ holds $W_r$ windows, and the environment stays constant within a recording. Write $Z_r$ for the environment of recording $r$, so every window in $R_r$ shares the label $Z_r$. Recordings are the independent units; windows are repeated measurements inside a unit.

Each window is mapped to a log-covariance feature. The window covariance is estimated with a shrinkage estimator, $\widehat\Sigma_w$, and linearized on the positive-definite cone through the matrix logarithm,

$$x_w=\operatorname{vech}(\log \widehat\Sigma_w).$$

The recording feature is the within-recording average,

\begin{equation}\label{eq:rec-estimand}
x_r=\frac1{W_r}\sum_{w=1}^{W_r}x_w.
\end{equation}

A single standardization is then applied across recordings. Window counts, sampling rates, and recording durations can differ across recordings; the feature map makes them comparable.

## 3.4 The two-layer estimand

Two conditional means sit at different levels and must not be conflated.

At the window level,

$$\mu_{e,w}=E[x_w^{(0)}\mid Z_r=e],$$

and at the recording level,

$$\mu_{e,\mathrm{rec}}=E[x_r^{(0)}\mid Z_r=e].$$

DELVE estimates the recording-level object. The two coincide only under additional conditions on the within-recording averaging; they are not assumed equal by default. The finite-window target, which the finite-sample theory actually addresses, is written $\mu_{e,T}$ and approaches the window-level target as the effective window count grows.

The back-transformed summary

$$\widetilde\Sigma_e=\operatorname{expm}(\mu_{e,w})$$

is a log-Euclidean summary of the average log-covariance feature. By default it is not the component covariance $\Sigma_e$. A conditional bias result of order $O(1/T_w)$, including the shrinkage contribution, governs their relationship, and the log-Euclidean mean is defined separately from the affine-invariant Karcher mean. We do not state that a cluster center is a component covariance.

## 3.5 Three identification objects

Three distinct objects are asked about, each with its own conclusion form.

**L1 — component parameters.** Under mechanism A, the object is the unordered set of component parameters, identified up to permutation. The full distribution gives the classical mixture result; finite moments reach generic injectivity only at a higher order.

**L2 — recording assignment.** Under mechanism B, the object is the assignment of each recording to its environment. The conclusion takes the form of a misclassification-rate or posterior-consistency statement, not a mixture-decomposition theorem, and it requires a constant within-recording environment, consistent recording features, and a positive covariance margin.

**L3 — single-window classification.** The object is the label of an individual window, which carries a Bayes error set by distributional overlap. Recording-level consistency does not remove that error.

A benign label permutation, which renames environments and leaves the partition unchanged, is distinguished throughout from genuine non-identification, where components merge, the margin vanishes, or distributions overlap.

## 3.6 The number of environments

Both identification and rate statements condition on $K$. The theory does not prove that $K$ is identifiable or consistently estimable. Automatic selection is an engineering component over a finite grid $\mathcal K=\{2,\dots,6\}$, combining a BIC term, a silhouette term, and a bootstrap stability term under a fixed rule. Oracle-$K$, where $K$ is given, and estimated-$K$ are reported separately. An agreement between them on a real dataset is an empirical coincidence supported by stability, not a theorem. Claims about selection are phrased as data-driven choice within a candidate range, never as fully blind discovery.

## 3.7 Separation quantities

Three separation quantities are used, and they are not interchangeable.

- $\sigma_J$: the smallest singular value of the Jacobian or symmetric-basis operator, the condition number for parameter inversion.
- $\Delta_{\mathrm{cov}}$: the minimum distance between environment log-covariance centers, $\min_{e\ne f}\|\mu_e-\mu_f\|$, the margin for recording assignment.
- $\Delta_{\mathrm{dist}}$: a component distribution distance such as KL or total variation, governing posterior rates and the Bayes error.

Component-parameter identification is a necessary but not sufficient precondition for recording assignment; the latter also needs enough recordings per environment and a positive $\Delta_{\mathrm{cov}}$. The formulation in this chapter states those requirements as premises rather than deriving them from one another.
