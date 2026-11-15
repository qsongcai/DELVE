# Recovery Theory (Chapter 5, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery*
Date: 2026-11-14. Status: formal manuscript section, conditional framing. Symbols follow the conservative bridge.

---

## 5.1 A recording-level model

The unit of analysis is the recording, not the window. Write the transformed recording feature as

$$X_r = A x_r^{(0)} + b \in \mathbb R^p,\qquad Z_r\in\{1,\dots,K\},$$

and define the environment-specific mean, the mixing weight, and the smallest center separation by

$$\mu_e = E[X\mid Z=e],\qquad \pi_e=P(Z=e),\qquad
\Delta=\min_{e\ne f}\|\mu_e-\mu_f\|.$$

The population K-means risk and its optimum are

\begin{equation}\label{eq:risk}
R(c)=E\!\left[\min_k\|X-c_k\|^2\right],\qquad R^\star=\inf_c R(c).
\end{equation}

\begin{definition}[center space, tie-breaking, and the misclassification rate]\label{def:err}
A center configuration is an ordered $K$-tuple $c=(c_1,\dots,c_K)$ in $(\mathbb R^p)^K$. The symmetric group $S_K$ acts on it by relabeling, $\tau\cdot c=(c_{\tau^{-1}(1)},\dots,c_{\tau^{-1}(K)})$, and center configurations that differ only by such a permutation are identified in the quotient space $(\mathbb R^p)^K/S_K$. The bounded center domain used below is $\mathcal C_B=(\overline{\mathcal B_p(B)})^K/S_K$.

For a configuration $c$, the nearest-center rule is $g_c(x)=\arg\min_k\|x-c_k\|^2$. Where two or more centers tie, the tie is broken by a fixed measurable rule, the smallest index among the tied centers, so $g_c$ is defined at every point. The misclassification rate is then
$$\mathrm{Err}(c,Z)=\min_{\tau\in S_K}P\{g_c(X)\ne\tau(Z)\}.$$
Taking the minimum over permutations makes $\mathrm{Err}$ invariant to label permutation and well defined on the quotient for every configuration, with values in $[0,1]$.
\end{definition}

This model is conditional on the feature the pipeline actually builds. In the implementation,

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

This is a direct condition on the geometry of the population objective, not a consequence of any split/merge calculation. A nearby formulation in the K-means literature is the cost or $\varepsilon$-separation condition, under which the optimal $(K-1)$-center cost sits a strict and stable margin above the $K$-center cost and binds the $K$ centers to the $K$ natural groups. The exact statement and its constants must be checked against the source before a specific constant is quoted; we assume none here.

The split/merge quantities used in the diagnostics call for caution. With

$$V_e(m)=\inf_{c_1,\dots,c_m}E[\min_j\|X-c_j\|^2\mid Z=e],\quad
S_e(m)=V_e(1)-V_e(m),$$

$$M_{ef}=\frac{\pi_e\pi_f}{\pi_e+\pi_f}\|\mu_e-\mu_f\|^2,$$

the comparison between the smallest merge cost $M_{\min}$ and the largest weighted split gain $S_{\max}^{\rm tot}=\max_e\pi_e\sup_m S_e(m)$ carries useful intuition. It does not establish population optimality. A hard ball keeps points inside their own ball; it does not stop a center from landing between two balls and serving both at once. The loss from removing a center is bounded by the conditional optimum only when the current centers already realize that optimum, and the merge term $M_{ef}$ describes two whole environments re-centered together, not the gain a new center produces inside a running multi-center configuration. The local exchange argument built on these quantities has been withdrawn. We report them as descriptive diagnostics only.

\begin{assumption}[closed level sets]\label{a:closed}
The misclassification function $\mathrm{Err}(c,Z)$ is upper semicontinuous on the center domain; equivalently, every level set $\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\}$ is closed. On a non-degenerate center domain this follows from Lemma~\ref{lem:closed}; on the full domain, including coincident centers, it is retained as an explicit assumption.
\end{assumption}

\begin{lemma}[boundary-tube vanishing on a non-degenerate center domain]\label{lem:closed}
Work in the bounded frame $\|X\|\le B$ almost surely, and let the law of $X$ be absolutely continuous with a density bounded by $f_{\max}$, either globally or in a neighborhood of every Voronoi boundary. Fix $d_{\min}>0$ and define the non-degenerate center domain
$$\mathcal C_{B,d_{\min}}=\{c\in\mathcal C_B:\|c_i-c_j\|\ge d_{\min}\ \text{for all }i\ne j\}.$$
On $\mathcal C_{B,d_{\min}}$, $\mathrm{Err}(c,Z)$ is continuous, hence upper semicontinuous, and every level set $\mathcal C_q$ intersected with $\mathcal C_{B,d_{\min}}$ is closed.
\end{lemma}

\begin{proof}
For a fixed permutation $\tau$, write $e_\tau(c)=P\{g_c(X)\ne\tau(Z)\}$. The Voronoi boundary between centers $i$ and $j$ is the affine hyperplane
$$H_{ij}(c)=\{x:2x^\top(c_j-c_i)=\|c_j\|^2-\|c_i\|^2\}.$$
Because $\|c_j-c_i\|\ge d_{\min}>0$, its normal is non-degenerate and $H_{ij}$ is a genuine hyperplane; the full Voronoi boundary is a finite union of at most $K(K-1)/2$ such hyperplanes. Let $V_{p-1}$ denote the volume of the unit $(p-1)$-ball, and write $\mathrm{tube}_w$ for the set of points within distance $w$ of that boundary. Inside $\mathcal B_p(B)$, a width-$w$ tube around one hyperplane has volume at most $2w\,V_{p-1}B^{p-1}$, so
\begin{equation}\label{eq:tube-mass}
\begin{aligned}
P\{X\in\mathrm{tube}_w(\partial V(c))\}
&\le f_{\max}\,\frac{K(K-1)}2\,2V_{p-1}B^{p-1}\,w\\
&= C_{\mathrm{geom}}(K,p,B)\,f_{\max}\,w\;\longrightarrow\;0.
\end{aligned}
\end{equation}
If the density is bounded only in a neighborhood, the same expression holds with the local supremum after restricting to that neighborhood.

Now let $c_n\to c$ with both configurations in $\mathcal C_{B,d_{\min}}$. Away from the Voronoi boundary of $c$, the winning center has a strictly positive margin, and on this fixed non-degenerate domain the margin geometry is uniform with constants depending only on $d_{\min}$ and $B$. A point on which $g_{c_n}(x)\ne g_c(x)$ therefore lies inside a tube of width $O(\|c_n-c\|)$ around the boundary. Applying~\eqref{eq:tube-mass},
$$P\{g_{c_n}(X)\ne g_c(X)\}\le C_{\mathrm{geom}}f_{\max}\,O(\|c_n-c\|)\to0.$$
Hence $|e_\tau(c_n)-e_\tau(c)|\le P\{g_{c_n}\ne g_c\}\to0$, so $e_\tau$ is continuous. Since $\mathrm{Err}(c)=\min_\tau e_\tau(c)$ is the minimum of finitely many continuous functions, it is continuous, hence upper semicontinuous, and the preimage $\mathcal C_q=\mathrm{Err}^{-1}([q,1])$ is closed. Tie points carry zero probability under absolute continuity, so the tie-breaking rule does not enter the argument, and a center exchange is only a relabeling already quotiented out.
\end{proof}

\begin{remark}[the lemma does not cover coincident centers]\label{rem:coincident}
The full center domain $\mathcal C_B$ allows $c_i=c_j$. At such a configuration the equidistant set $\{x:\|x-c_i\|=\|x-c_j\|\}$ is the whole space rather than a Lebesgue-null hyperplane, and an arbitrarily small perturbation can place the new bisector through a region of positive probability. In one dimension, take $X$ uniform on $[-1,1]$, $c_1=c_2=0$ with ties assigned to the first center, and perturb to $c_n=(-a,a)$; the two rules then disagree on a half-space of mass $1/2$ for every $a>0$, so the change does not vanish. Quotienting by the center permutation does not remove this, because the coincident point can split in distinct directions. The lemma therefore makes no claim at coincident centers, and the closed level-set condition there is assumed directly through Assumption~\ref{a:closed} rather than derived.
\end{remark}

\begin{assumption}[quadratic growth]\label{a:growth}
$R(c)-R^\star\ge\kappa\,d(c,\mathcal C^\star)^2$.
\end{assumption}

This is an independent strong assumption. The margin condition does not imply it, and the quantitative bound it supports is local.

## 5.3 The conditional compatibility theorem

\begin{theorem}[population identification under alignment]\label{thm:A}
Suppose Assumptions~\ref{a:weights}--\ref{a:sep} and Assumption~\ref{a:align} hold. Then for some permutation $\pi$,
$$P\{g_{c^\star}(X)\ne\pi(Z)\}=0.$$
\end{theorem}

\begin{proof}
Assumption~\ref{a:align} identifies the optimal centers as a permutation of the environment means. Lemma~\ref{lem:truecenter} makes that configuration error-free.
\end{proof}

The identification comes from the alignment that is assumed, not from a lower-level generative argument. The theorem name keeps this visible: the *Conditional Compatibility Theorem* states that K-means compatibility implies risk-gap recovery, and it is not a generative bridge from recording separation to partition recovery.

For a target misclassification level $q$, set

\begin{equation}\label{eq:margin}
\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\},\qquad
\psi(q)=\inf_{c\in\mathcal C_q}\{R(c)-R^\star\}.
\end{equation}

The absence of a positive-probability tie region at the optimum is not, by itself, enough to close $\mathcal C_q$ or to make $\mathrm{Err}$ continuous. The compactness and continuity the gap argument uses need to be stated rather than left implicit.

\begin{lemma}[compact center domain and continuity of the risk]\label{lem:compact}
Work in the bounded-feature frame, $\|X\|\le B$ almost surely. Let the center space be the product of closed balls $\mathcal C_B=(\overline{\mathcal B_p(B)})^K$, with the label permutation quotient out. Then $\mathcal C_B$ is compact, the population risk $R$ is continuous on it, and an optimizer of $R$ can be taken inside $\mathcal C_B$.
\end{lemma}

\begin{proof}
The space $\mathcal C_B$ is a closed and bounded subset of the finite-dimensional space $\mathbb R^{Kp}$, so it is compact by the Heine–Borel theorem. If a center $c_k$ lies outside the ball, project it to $\bar c_k=Bc_k/\|c_k\|$. The ball is convex, and for every $x$ with $\|x\|\le B$ the projection does not increase the distance, $\|x-\bar c_k\|\le\|x-c_k\|$; replacing every out-of-ball center therefore cannot raise the risk, which places an optimizer inside $\mathcal C_B$. For continuity, write $\ell(c,x)=\min_k\|x-c_k\|^2$. Each map $c\mapsto\|x-c_k\|^2$ is continuous, and the minimum of finitely many continuous functions is continuous. Since $\ell$ is bounded on $\mathcal C_B$, taking the expectation preserves continuity, so $R(c)=E[\ell(c,X)]$ is continuous. The misclassification used in $\mathrm{Err}(c,Z)$ is computed after matching the fitted labels to the true labels by the optimal permutation, so the label permutation is quotient out and does not create extra points.
\end{proof}

Under Assumption~\ref{a:closed}, $\mathrm{Err}$ is upper semicontinuous, so the level set $\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\}$ is closed. Intersected with the compact domain $\mathcal C_B$, it is compact, and the continuous function $R-R^\star$ attains its infimum on it.

\begin{theorem}[positive risk gap]\label{thm:B}
Under the assumptions of Theorem~\ref{thm:A} together with Assumption~\ref{a:closed}, for every $q>0$ with $\mathcal C_q\ne\varnothing$,
\begin{equation}\label{eq:compatibility}
\psi(q)>0.
\end{equation}
\end{theorem}

\begin{proof}
Under Theorem~\ref{thm:A} the optimal set has error zero, so $\mathcal C_q\cap\mathcal C^\star=\varnothing$. Lemma~\ref{lem:compact} supplies the compact center domain and the continuity of $R$, and Assumption~\ref{a:closed} closes $\mathcal C_q$. The infimum of the continuous function $R-R^\star$ over that compact set is attained, and it is strictly positive because the set excludes every point where the risk difference is zero.
\end{proof}

A quantitative form is available only locally. Let the margin obey $P(X\in\mathcal M_t)\le C_{\rm margin}t^\beta$, with $\beta=1$ in the ordinary case. Inside the local stability region, where a label flip is caused only by the boundary tube,

$$\mathrm{Err}(c)\le C_{\rm margin}\,d(c,\mathcal C^\star)^\beta.$$

Combining this with Assumption~\ref{a:growth} and restricting to $0<q\le q_0$,

$$\psi(q)\ge\kappa\Big(\frac{q}{C_{\rm margin}}\Big)^{2/\beta}.$$

For $\beta=1$, $\psi(q)\ge(\kappa/C_{\rm margin}^2)q^2$. The cutoff $q_0$ is the largest misclassification level at which the local linearization holds; it is back-solved from the radius of the boundary stability region through the margin relation. Three limits stay in force. The perturbation has to lie in the local stability region, the margin condition has to hold for the transformed feature $X$ rather than the raw covariance or a window feature, and Assumption~\ref{a:growth} remains independent of the margin. We claim no global quantitative bound, and neither $\kappa$ nor $C_{\rm margin}$ is self-certified.

## 5.4 Finite-sample transfer

Let $\widehat R_M$ be the empirical risk on $M$ independent recordings, let $\varepsilon_M$ be the uniform deviation $\sup_{c\in\mathcal C}|\widehat R_M(c)-R(c)|$, and let $\delta_{\rm opt}=\widehat R_M(\widehat c)-\widehat R_M^\star$ be the optimization error. The standard excess-risk decomposition is

\begin{equation}\label{eq:risk-gap}
R(\widehat c)-R^\star\le 2\varepsilon_M+\delta_{\rm opt}.
\end{equation}

\begin{lemma}[risk transfer]\label{lem:transfer}
Fix $q>0$, and suppose the level set $\mathcal C_q$ is closed so that $\psi(q)$ is well defined; this is Assumption~\ref{a:closed} on the compact center domain. For any center configuration $\widehat c$,
$$R(\widehat c)-R^\star<\psi(q)\quad\Longrightarrow\quad \mathrm{Err}(\widehat c,Z)<q.$$
Combined with the excess-risk decomposition~\eqref{eq:risk-gap}, the condition $2\varepsilon_M+\delta_{\rm opt}<\psi(q)$ therefore implies $\mathrm{Err}(\widehat c,Z)<q$.
\end{lemma}

\begin{proof}
If $\mathrm{Err}(\widehat c,Z)\ge q$, then $\widehat c\in\mathcal C_q$, which by the definition of $\psi(q)$ forces $R(\widehat c)-R^\star\ge\psi(q)$, a contradiction. The argument is a conditional implication only; it does not assume alignment and does not assert that $\psi(q)$ is positive.
\end{proof}

For bounded features with $\|X\|\le B$ and centers in $\mathcal C=(\mathcal B_p(B))^K$, the uniform deviation admits an explicit grid bound. Stacking the centers into a $Kp$-vector with the product Frobenius norm gives a domain of radius $\sqrt K B$, and an $\eta$-net of size

$$N_\eta\le\Big(1+\frac{2\sqrt K B}{\eta}\Big)^{Kp}.$$

The cell function $f_c(x)=\min_k\|x-c_k\|^2$ ranges in $[0,4B^2]$. Its Lipschitz constant in the stacked centers is computed, not assumed. For fixed $x$, write $\phi_k(c_k)=\|x-c_k\|^2$, whose gradient is $\nabla_{c_k}\phi_k=2(c_k-x)$ with norm at most $2(\|c_k\|+\|x\|)\le 4B$. Taking a minimum is $1$-Lipschitz in its arguments, and away from Voronoi ties the gradient of the minimum is the gradient of the single active cell, with every other center block contributing zero. The stacked gradient therefore has Frobenius norm at most $4B$, so $f_c$ is $4B$-Lipschitz in the product center norm. The $\sqrt K$ factor enters the covering radius but not this constant.

Let $\{c^{(1)},\dots,c^{(N_\eta)}\}$ be the net. For any $c$, choose $c^{(j)}$ with $\|c-c^{(j)}\|\le\eta$, which gives $|f_c(x)-f_{c^{(j)}}(x)|\le 4B\eta$ for every $x$. Splitting the uniform deviation at that net point,

$$|\widehat R_M(c)-R(c)|\le
\underbrace{|\widehat R_M(c)-\widehat R_M(c^{(j)})|}_{\le 4B\eta}
+|\widehat R_M(c^{(j)})-R(c^{(j)})|
+\underbrace{|R(c^{(j)})-R(c)|}_{\le 4B\eta},$$

so the two-sided discretization contributes $8B\eta$. On the net, each summand lies in $[0,4B^2]$, and Hoeffding applied to the average of $M$ independent recordings gives

$$P\!\left\{|\widehat R_M(c^{(j)})-R(c^{(j)})|\ge t\right\}
\le 2\exp\!\left(-\frac{M t^2}{8B^4}\right).$$

A union bound over the $N_\eta$ net points and the discretization above yield, with probability at least $1-\alpha$,

$$\varepsilon_M\le\sqrt{\frac{8B^4\log(2N_\eta/\alpha)}{M}}+8B\eta.$$

A global empirical minimizer has $\delta_{\rm opt}=0$. Lloyd's algorithm only approximates it, and a center outside the ball can be projected back without increasing risk; the Lloyd result is therefore stated with an explicit $\delta_{\rm opt}$ and kept separate.

Write the high-probability bound as a function of the net resolution,
$$h(M,\eta)=\sqrt{\frac{8B^4\log(2N_\eta/\alpha)}{M}}+8B\eta.$$
The preceding Hoeffding and union-bound argument states that $\mathbb P\{\varepsilon_M\le h(M,\eta)\}\ge1-\alpha$. This converts the conditional transfer into a checkable finite-sample statement.

\begin{corollary}[nontrivial finite-sample recovery]\label{cor:finite}
Suppose every assumption of Theorem~\ref{thm:B} holds, namely Assumptions~\ref{a:weights}--\ref{a:sep}, Assumption~\ref{a:align}, and Assumption~\ref{a:closed}, and choose $q$ with $\psi(q)>0$. For a global empirical minimizer, $\delta_{\rm opt}=0$, and if
$$2h(M,\eta)<\psi(q),$$
then with probability at least $1-\alpha$,
$$\mathrm{Err}(\widehat c,Z)<q.$$
For a finite-initialization Lloyd solution the same conclusion holds with probability at least $1-\alpha$ under $2h(M,\eta)+\delta_{\rm opt}<\psi(q)$.
\end{corollary}

\begin{proof}
On the event $\varepsilon_M\le h(M,\eta)$, which has probability at least $1-\alpha$, the excess-risk decomposition gives $R(\widehat c)-R^\star\le2h(M,\eta)+\delta_{\rm opt}<\psi(q)$. Applying the risk-transfer lemma~\ref{lem:transfer} yields $\mathrm{Err}(\widehat c,Z)<q$. The positivity $\psi(q)>0$ is the content of Theorem~\ref{thm:B} and is what makes the condition attainable; without it the bound is the empty conditional of the lemma.
\end{proof}

## 5.5 The DELVE procedure

The estimand and the guarantee above are operationalized by one procedure. Algorithm~\ref{alg:delve} lists the complete staged sequence from the raw recordings to the assignment and its diagnostics. The bracketed tags separate standard components from this paper's estimand and guarantee.

\begin{algorithm}[htbp]
\centering
\small
\renewcommand{\arraystretch}{1.15}
\begin{tabular}{@{}r >{\raggedright\arraybackslash}p{0.78\columnwidth}@{}}
\textbf{Input} & recordings $\{R_1,\dots,R_M\}$, grid $\mathcal K=\{2,\dots,6\}$, level $\alpha$\\
\textbf{Output} & $\hat K$, hard labels $\hat\ell_r$, soft posteriors $\eta_{rk}$, stability, bootstrap, sensitivity\\
\textbf{Stage 0} & [standard] homogenize: shared channels, common-average reference, band-pass with notch, resample, four-second windows\\
\textbf{Stage 1} & [standard] per window $\widehat\Sigma_w=\mathrm{LedoitWolf}$; $x_w=\operatorname{vech}(\log\widehat\Sigma_w)$\\
\textbf{Stage 2} & [this paper's estimand] $x_r=\frac1{W_r}\sum_w x_w$; $X=\mathrm{StandardScaler}$ across recordings\\
\textbf{Stage 3} & [standard] nearest-centroid labels, with K-means as the realization; BIC, silhouette, and stability score; $\hat K$\\
\textbf{Stage 4} & [theoretical guarantee, not a computed output] the conditional misclassification statement of Corollary~\ref{cor:finite}; its terms are population quantities (uniform deviation and center error), and the procedure evaluates no numeric bound\\
\textbf{Stage 5} & [standard] co-assignment and resampling stability\\
\textbf{Stage 6} & [standard] assignment bootstrap and perturbation sensitivity\\
\textbf{Stage 7} & post-hoc interpretation using metadata, not an algorithm output\\
\end{tabular}
\caption{The DELVE procedure for recording-level environment recovery. The standard components (Stages 0--1, 3, 5--6) are not claimed as novel; the contribution lies in the unified recording-level estimand (Stage 2) and the conditional misclassification guarantee (Stage 4), which is a population-level statement attached to the procedure rather than a number it computes. Automatic $K$ selection and the full-pool scaler stay outside the unconditional guarantees.}
\label{alg:delve}
\end{algorithm}

The sample-split variant of Section~5.4 fits the scaler and centers on one half and freezes them for the held-out half, so it is an inductive use of the same staged core rather than a separate procedure. Stages 0 and 7 mark the boundaries of the claim: preprocessing is a design choice rather than a theorem, and the device or protocol reading is admitted only after the assignment is produced.

## 5.6 Three operational variants and the guarantee boundary

The name DELVE covers more than one object, and the guarantee attaches to exactly one of them. The distinction is stated here in the method rather than deferred to the limitations. The population alignment the theorems use is a compatibility condition, assumed on the population objective; this paper does not derive it from the covariance generative model. Table~\ref{tab:variants} lists the three variants and their guarantees.

\begin{table}[htbp]
\centering
\small
\begin{tabular}{lllll}
\hline
Variant & $K$ & scaler & optimizer & guarantee\\
\hline
DELVE-G & fixed & frozen & global K-means & risk-gap\\
DELVE-L & fixed & frozen & finite Lloyd & explicit $\delta_{\rm opt}$\\
DELVE-B & blind & full-pool & Lloyd + selector & none\\
\hline
\end{tabular}
\caption{The three operational variants of DELVE and the guarantee attached to each. Only DELVE-G, with fixed $K$, a frozen scaler, and a global K-means optimizer, is covered in full by the risk-gap guarantee.}
\label{tab:variants}
\end{table}

DELVE-G is the only object the theorem covers in full. It fixes the number of environments and the feature transformation, and a global empirical minimizer has zero optimization error. DELVE-L keeps the same fixed-$K$ setting but obtains its centers from finite-initialization Lloyd, so the finite-sample statement carries the explicit $\delta_{\rm opt}$ of the finite-sample decomposition rather than setting it to zero. DELVE-B is the blind pipeline run in the real-data chapter: a scaler fitted on the full pool and a pre-specified selector over $K$, with no oracle number, and it stays outside the unconditional guarantees. The sample-split construction that gives the held-out decomposition in Section~5.4 is an inductive use of the fixed-$K$ core, not a fourth clusterer. The main results label which variant each number comes from, so the guaranteed sub-procedure and the empirical pipeline are never read as one algorithm.

## 5.7 Scope

The guarantee covers the global empirical K-means solution under a fixed K, a fixed or frozen feature transformation, bounded features, and the alignment and level-set assumptions. It does not cover automatic K selection, full-pool standardization, or finite-initialization Lloyd, and it does not establish that the unlabeled EEG satisfies the conditions. Those components are reported as empirical or transductive procedures, outside the unconditional claims. The stronger route—proving alignment on a structured distribution class through a capture or exchange argument—is left as future work.
