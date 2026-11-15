# Problem Formulation (Chapter 3, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-15. Status: shortened manuscript section. Notation set here is used throughout Chapters 4 and 5.

---

## 3.1 Environments and the pooled marginal

A latent environment $E$ takes values in $\{1,\dots,K\}$ with probabilities $\pi_e>0$. The observed vector follows a fixed deterministic mixing,

\begin{equation}\label{eq:obs-model}
X=A\,x^{(0)}+b,
\end{equation}

where $A$ has full column rank and $b$ is a fixed offset; conditional on $E$, $X$ has law $G_e$. Without labels the analyst receives only

\begin{equation}\label{eq:pool-mixture}
P_X=\sum_{e=1}^K \pi_e G_e,
\end{equation}

with no mark of the component behind a draw. Its second moment,

\begin{equation}\label{eq:pool-cov}
\bar\Sigma=E[XX^\top]=\sum_e\pi_e\Sigma_e,
\end{equation}

is one fixed positive-definite matrix, not a random per-sample covariance. A hierarchical model with random $C$ is a different object we do not treat.

## 3.2 Observation mechanisms and the recording hierarchy

Two mechanisms are kept separate, with no implication between them. **Mechanism A (one pooled distribution).** The analyst observes draws from $P_X$ or its moments and asks whether a mixture decomposition is recoverable. **Mechanism B (repeated recordings).** The analyst observes $M$ recordings, each with several windows and a covariance, and asks whether recordings can be assigned to their environment.

Under mechanism B, a recording $R_r$ holds $W_r$ windows and carries one environment label $Z_r$ shared by every window. Recordings are the independent units, windows the repeated measurements. Each window covariance is estimated by shrinkage and linearized as $x_w=\operatorname{vech}(\log\widehat\Sigma_w)$; the recording feature is the within-recording average,

\begin{equation}\label{eq:rec-estimand}
x_r=\frac1{W_r}\sum_{w=1}^{W_r}x_w,
\end{equation}

followed by one standardization across recordings, which makes differing window counts and durations comparable.

## 3.3 The two-layer estimand

The window-level mean $\mu_{e,w}=E[x_w^{(0)}\mid Z_r=e]$ and the recording-level mean $\mu_{e,\mathrm{rec}}=E[x_r^{(0)}\mid Z_r=e]$ must not be conflated. DELVE targets the recording-level object. The two coincide only under extra conditions on the within-recording averaging. The finite-window target $\mu_{e,T}$ approaches the window-level target as the effective window count grows.

The back-transformed summary $\widetilde\Sigma_e=\operatorname{expm}(\mu_{e,w})$ is a log-Euclidean summary, not the component covariance $\Sigma_e$. An $O(1/T_w)$ conditional bias, including the shrinkage contribution, relates the two. The log-Euclidean mean is also distinct from the affine-invariant Karcher mean. We never treat a cluster center as a component covariance.

## 3.4 Identification objects, environments, and separation quantities

Three objects carry distinct conclusion forms. **L1 (component parameters).** Under mechanism A, the unordered component parameters are identified up to permutation. Finite moments reach generic injectivity only at a higher order. **L2 (recording assignment).** Under mechanism B, the assignment is stated as a misclassification-rate or posterior-consistency result rather than a mixture theorem. It needs a constant within-recording environment, consistent features, and a positive margin. **L3 (single-window classification).** The window label carries a Bayes error from distributional overlap that recording-level consistency does not remove. A benign label permutation is distinguished from genuine non-identification, where components merge, the margin vanishes, or distributions overlap.

All statements condition on $K$. The theory does not prove $K$ identifiable or consistently estimable. Automatic selection is an engineering rule over $\mathcal K=\{2,\dots,6\}$ that combines BIC, silhouette, and bootstrap stability terms. Oracle-$K$ is reported separately from estimated-$K$. Selection is a data-driven choice within a candidate range, never fully blind discovery.

Three separation quantities are not interchangeable: $\sigma_J$, the smallest singular value of the Jacobian or symmetric-basis operator; $\Delta_{\mathrm{cov}}=\min_{e\ne f}\|\mu_e-\mu_f\|$, the assignment margin; and $\Delta_{\mathrm{dist}}$, a KL or total-variation distance governing posterior rates and the Bayes error. Component-parameter identification is necessary but not sufficient for assignment. Assignment also needs enough recordings per environment and a positive $\Delta_{\mathrm{cov}}$. These requirements are stated as premises, not derived from one another.
