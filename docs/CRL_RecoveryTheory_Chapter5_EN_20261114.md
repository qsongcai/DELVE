# Recovery Theory (Chapter 5, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section, conditional framing. Symbols follow the conservative bridge.

---

## 5.1 A recording-level model

The unit of analysis is the recording, not the window. Write the transformed recording feature as

$$X_r = A x_r^{(0)} + b \in \mathbb R^p,\qquad Z_r\in\{1,\dots,K\},$$

and define the environment-specific mean, the mixing weight, and the smallest center separation by

$$\mu_e = E[X\mid Z=e],\qquad \pi_e=P(Z=e),\qquad
\Delta=\min_{e\ne f}\|\mu_e-\mu_f\|.$$

The population K-means risk and its optimum are

$$R(c)=E\!\left[\min_k\|X-c_k\|^2\right],\qquad R^\star=\inf_c R(c).$$

This model is a conditional model for the feature the pipeline actually builds. In the implementation,

$$X_r=A\!\left[\frac1{W_r}\sum_{w=1}^{W_r}\operatorname{vech}\{\log(\widehat\Sigma_{rw})\}\right]+b,$$

so window-level dependence and non-stationarity enter the residual, and the recording variance is governed by the effective window count $T_{\rm eff}$ rather than the nominal $W_r$. The systematic Ledoit–Wolf~\cite{ledoit2004} and matrix-log bias shifts the center; the random fluctuation is noise, with $E[\mu_{e,T}]-\mu_e=O(T_w^{-1})$. Within-environment subject and session heterogeneity is allowed and absorbed into the residual. The pair $(A,b)$ is fixed or frozen on the training side. A scaler estimated on the full pool belongs to the transductive variant and does not enter the fixed-transformation theorem.

## 5.2 Assumptions

We work with a location model $X=\mu_Z+\xi_Z$, where $E[\xi_e\mid Z=e]=0$.

\begin{assumption}[weights]\label{a:weights}
$\pi_e\ge\pi_{\min}>0$ for every $e$.
\end{assumption}

\begin{assumption}[concentration, hard ball]\label{a:conc}
$\|\xi_e\|\le\rho$ almost surely.
\end{assumption}

\begin{assumption}[separation]\label{a:sep}
$\Delta>4\rho$.
\end{assumption}

The first three assumptions support one result on their own. Take a point drawn from environment $e$. Its distance to its own center is at most $\rho$, while for $f\ne e$,

$$\|X-\mu_f\|\ge\Delta-\rho>3\rho>\|X-\mu_e\|.$$

\begin{lemma}[the true-center classifier is correct]\label{lem:truecenter}
Under Assumptions~\ref{a:weights}--\ref{a:sep}, the nearest-center classifier at the true centers satisfies
$$g_\mu(X)=\arg\min_f\|X-\mu_f\|^2=Z\quad\text{almost surely.}$$
\end{lemma}

The lemma says only that the true centers classify correctly. It does not say those centers solve the population K-means problem. That stronger statement is the compatibility condition below.

\begin{assumption}[population K-means alignment]\label{a:align}
For fixed $K$ and a fixed transformation, every global minimizer of the population K-means risk assigns exactly one center to each environment:
$$\mathcal C^\star=\{c:R(c)=R^\star\}
=\{(\mu_1,\dots,\mu_K)\text{ up to label permutation}\}.$$
\end{assumption}

This is a direct condition on the geometry of the population objective, not a consequence of any split/merge calculation. A nearby formulation in the K-means literature is the cost or $\varepsilon$-separation condition, under which the optimal $(K-1)$-center cost sits a strict and stable margin above the $K$-center cost and binds the $K$ centers to the $K$ natural groups. The exact statement and its constants must be checked against the source before a specific constant is quoted; we do not assume one here.

The split/merge quantities used in the diagnostics call for a word of caution. With

$$V_e(m)=\inf_{c_1,\dots,c_m}E[\min_j\|X-c_j\|^2\mid Z=e],\quad
S_e(m)=V_e(1)-V_e(m),$$

$$M_{ef}=\frac{\pi_e\pi_f}{\pi_e+\pi_f}\|\mu_e-\mu_f\|^2,$$

the comparison between the smallest merge cost $M_{\min}$ and the largest weighted split gain $S_{\max}^{\rm tot}=\max_e\pi_e\sup_m S_e(m)$ carries useful intuition. It does not establish population optimality. A hard ball keeps points inside their own ball; it does not stop a center from landing between two balls and serving both at once. The loss from removing a center is bounded by the conditional optimum only when the current centers already realize that optimum, and the merge term $M_{ef}$ describes two whole environments re-centered together, not the gain a new center produces inside a running multi-center configuration. The local exchange argument built on these quantities has been withdrawn. We report them as descriptive diagnostics only.

\begin{assumption}[closed level sets]\label{a:closed}
The misclassification function $\mathrm{Err}(c,Z)$ is upper semicontinuous on the center domain; equivalently, every level set $\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\}$ is closed.
\end{assumption}

The condition holds for an absolutely continuous distribution whose density stays bounded near the Voronoi boundary, since the mass of the boundary tube vanishes with its width. It still has to be stated rather than inferred.

\begin{assumption}[quadratic growth]\label{a:growth}
$R(c)-R^\star\ge\kappa\,d(c,\mathcal C^\star)^2$.
\end{assumption}

This is an independent strong assumption. It is not implied by the margin condition, and the quantitative bound it supports is local.

## 5.3 The conditional compatibility theorem

\begin{theorem}[population identification under alignment]\label{thm:A}
Suppose Assumptions~\ref{a:weights}--\ref{a:sep} and Assumption~\ref{a:align} hold. Then for some permutation $\pi$,
$$P\{g_{c^\star}(X)\ne\pi(Z)\}=0.$$
\end{theorem}

\begin{proof}
Assumption~\ref{a:align} identifies the optimal centers as a permutation of the environment means. Lemma~\ref{lem:truecenter} makes that configuration error-free.
\end{proof}

The identification comes from the alignment that is assumed, not from a lower-level generative argument. The theorem name in the paper keeps this visible: the *Conditional Compatibility Theorem* states that K-means compatibility implies risk-gap recovery, and it is not a generative bridge from recording separation to partition recovery.

For a target misclassification level $q$, set

$$\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\},\qquad
\psi(q)=\inf_{c\in\mathcal C_q}\{R(c)-R^\star\}.$$

The absence of a positive-probability tie region at the optimum is not, by itself, enough to close $\mathcal C_q$ or to make $\mathrm{Err}$ continuous.

\begin{theorem}[positive risk gap]\label{thm:B}
Under the assumptions of Theorem~\ref{thm:A} together with Assumption~\ref{a:closed}, for every $q>0$ with $\mathcal C_q\ne\varnothing$,
$$\psi(q)>0.$$
\end{theorem}

\begin{proof}
Under Theorem~\ref{thm:A} the optimal set has error zero, so $\mathcal C_q\cap\mathcal C^\star=\varnothing$. Assumption~\ref{a:closed} closes $\mathcal C_q$. On a compact domain the infimum of $R-R^\star$ over that closed set is attained and is strictly positive.
\end{proof}

A quantitative form is available only locally. Let the margin obey $P(X\in\mathcal M_t)\le C_{\rm margin}t^\beta$, with $\beta=1$ in the ordinary case. Inside the local stability region, where a label flip is caused only by the boundary tube,

$$\mathrm{Err}(c)\le C_{\rm margin}\,d(c,\mathcal C^\star)^\beta.$$

Combining this with Assumption~\ref{a:growth} and restricting to $0<q\le q_0$,

$$\psi(q)\ge\kappa\Big(\frac{q}{C_{\rm margin}}\Big)^{2/\beta}.$$

For $\beta=1$, $\psi(q)\ge(\kappa/C_{\rm margin}^2)q^2$. The cutoff $q_0$ is the largest misclassification level at which the local linearization holds; it is back-solved from the radius of the boundary stability region through the margin relation. Three limits stay in force. The perturbation has to lie in the local stability region, the margin condition has to hold for the transformed feature $X$ rather than the raw covariance or a window feature, and Assumption~\ref{a:growth} remains independent of the margin. We do not claim a global quantitative bound, and neither $\kappa$ nor $C_{\rm margin}$ is self-certified.

## 5.4 Finite-sample transfer

Let $\widehat R_M$ be the empirical risk on $M$ independent recordings, let $\varepsilon_M$ be the uniform deviation $\sup_{c\in\mathcal C}|\widehat R_M(c)-R(c)|$, and let $\delta_{\rm opt}=\widehat R_M(\widehat c)-\widehat R_M^\star$ be the optimization error. The standard excess-risk decomposition is

$$R(\widehat c)-R^\star\le 2\varepsilon_M+\delta_{\rm opt}.$$

\begin{theorem}[finite-sample recovery]\label{thm:C}
Suppose Assumption~\ref{a:align} and Assumption~\ref{a:closed} hold, so that $\psi(q)$ is well defined. If
$$2\varepsilon_M+\delta_{\rm opt}<\psi(q),$$
then
$$\mathrm{Err}(\widehat c,Z)<q.$$
\end{theorem}

\begin{proof}
If $\mathrm{Err}(\widehat c,Z)\ge q$, then $\widehat c\in\mathcal C_q$, which forces $R(\widehat c)-R^\star\ge\psi(q)$, contradicting the excess-risk bound.
\end{proof}

For bounded features with $\|X\|\le B$ and centers in $\mathcal C=(\mathcal B_p(B))^K$, the uniform deviation admits an explicit grid bound. Stacking the centers into a $Kp$-vector with the product Frobenius norm gives a domain of radius $\sqrt K B$, and an $\eta$-net of size

$$N_\eta\le\Big(1+\frac{2\sqrt K B}{\eta}\Big)^{Kp}.$$

The cell function $f_c(x)=\min_k\|x-c_k\|^2$ ranges in $[0,4B^2]$ and is $4B$-Lipschitz in the product center norm; the $\sqrt K$ factor enters the covering radius but not the Lipschitz constant. Hoeffding on the net and the two-sided discretization error give

$$\varepsilon_M\le\sqrt{\frac{8B^4\log(2N_\eta/\alpha)}{M}}+8B\eta.$$

A global empirical minimizer has $\delta_{\rm opt}=0$. Lloyd's algorithm only approximates it, and a center outside the ball can be projected back without increasing risk; the Lloyd result is therefore stated with an explicit $\delta_{\rm opt}$ and kept separate.

## 5.5 Scope

The guarantee covers the global empirical K-means solution under a fixed K, a fixed or frozen feature transformation, bounded features, and the alignment and level-set assumptions. It does not cover automatic K selection, full-pool standardization, or finite-initialization Lloyd, and it does not establish that the unlabeled EEG satisfies the conditions. Those components are reported as empirical or transductive procedures, outside the unconditional claims. The stronger route—proving alignment on a structured distribution class through a capture or exchange argument—is left as future work.
