# Identifiability Boundary (Chapter 4, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery*
Date: 2026-11-14. Status: formal manuscript section. This is mechanism A: a single pooled distribution, with no environment labels. The results below do not imply the DELVE recovery guarantees in Chapter 5.

---

## 4.1 What identifiability means

Let $P_X$ be the pooled marginal, and write a mixture as a measure over component laws,

$$\mu=\sum_e a_e\delta_{G_e},\qquad a_e>0,\qquad \sum_e a_e G_e=P_X.$$

The decomposition set is

\begin{equation}\label{eq:identified-set}
\mathcal D(P_X)=\left\{\mu=\sum_e a_e\delta_{G_e}:\ a_e>0,\ \sum_e a_e G_e=P_X\right\}.
\end{equation}

The structure is identified up to label permutation when $\mathcal D(P_X)$ is a singleton. With the labels gone and only $P_X$ in hand, the joint law of $(X,E)$ is not fixed. Any Markov kernel $\kappa(e\mid x)$ whose integral against $P_X$ matches the label marginal is a valid assignment, and outside degenerate cases the set of such kernels contains more than one point. The first result makes this concrete with an explicit witness.

## 4.2 Partition non-identification

\begin{theorem}[the pooled marginal does not determine the partition]\label{thm:d2}
There exist two environment assignments $\sigma$ and $\sigma'$, not related by a global label permutation, that hold simultaneously under one and the same observation distribution. A measure-preserving bijection $T$ on the latent space satisfies
\begin{equation}\label{eq:witness}
T_\#P_Z=P_Z,\qquad \sigma'=\sigma\circ T,\qquad \sigma'\notin\{\sigma,\ 1-\sigma\}.
\end{equation}
\end{theorem}

\begin{proof}
\emph{Construction.} Work in two dimensions. Let the latent variable $z=(Z_1,Z_2)$ be uniform on the unit disk $\mathcal D=\{z:\|z\|\le 1\}$, and take the mixing map to be the identity so that $x=z$. There are two environments of equal weight.

The first assignment splits the disk by the sign of the first coordinate,

$$\sigma(z)=\mathbb 1[z_1\ge 0].$$

Each half carries half the disk. Now rotate by a quarter turn,

$$T(z_1,z_2)=(-z_2,z_1),\qquad \det J_T=1.$$

The rotation preserves the disk and its uniform measure, so $T_\#P_Z=P_Z$ and the pooled distribution is unchanged. The second assignment is

$$\sigma'(z)=\sigma(Tz)=\mathbb 1[z_2\le 0],$$

which splits the disk by the sign of the second coordinate. The two partitions disagree on the second and fourth quadrants, where the coordinates have opposite signs:

\begin{equation}\label{eq:disagreement}
P_Z(\sigma\ne\sigma')=\tfrac12.
\end{equation}

A global label permutation flips either every point or none, measured by the assignment, so it cannot produce a half-set disagreement. Hence $\sigma'$ is not a relabeling of $\sigma$.
\end{proof}

The same fact can be read as a coupling argument. The label $E$ is an unobserved categorical variable, and $P_X$ fixes only the marginal of $X$. The joint law of $X$ and $E$ is a coupling of $P_X$ with the label marginal, and the set of such couplings is convex and shrinks to a singleton only in degenerate cases. Every coupling gives a different assignment while sharing $P_X$. The rotation is an explicit, smooth, measure-preserving witness to the general statement, not the general statement itself.

The construction transports under a reparameterization. For a full-column-rank linear mixing $x=Gz$, the rotation becomes the linear conjugate $GTG^{-1}$ and the same witness applies, and a smooth change of coordinates carries it over in the same way. No separate theorem is built from this; the $d=2$ rotation is the explicit result, and the transported versions are the same witness in new coordinates rather than a broader non-identifiability claim.

On a sample of $2\times10^5$ draws the disagreement fraction is $0.5000$, the two assignments stay near equal weight, and the empirical squared maximum-mean-discrepancy between $Z$ and $T(Z)$ is $0.00058$, finite-sample noise around a population value of zero. The environment-specific means under the two partitions point along orthogonal axes, so the conditional distributions genuinely differ even though the pooled law cannot tell them apart.

The model class has to be stated precisely. The result operates on the class of arbitrary measurable environment assignments with no parametric restriction on the component laws; only the pooled marginal is constrained. Within that class the theorem is a single $d=2$ witness, not a claim that every pooled distribution is non-identifiable. If the component laws are restricted to a structured family, fixed Gaussian covariances for example, the construction need not remain inside that smaller class, and the witness says nothing about it. What it establishes is that, with only $P_X$ fixed, identifiability cannot be assumed and the uniqueness clause in the known-index formulations fails at the population level; finite samples then add estimation error on top of a non-uniqueness already present.

## 4.3 Point identification in a symmetric two-component covariance-mixture model

Tighten the setting and the decomposition set collapses to a point. The model is a two-component Gaussian mixture with a symmetric, whitened structure. Let $E\in\{+1,-1\}$ carry equal weight, $P(E=+1)=P(E=-1)=1/2$, and write the two component laws as zero-mean Gaussians,

$$X\mid E=+1\sim N(0,I+K),\qquad X\mid E=-1\sim N(0,I-K),$$

where $K$ is symmetric and $I\pm K\succ0$, equivalently every eigenvalue of $K$ lies strictly inside $(-1,1)$. The pooled mean is zero and the pooled covariance is

$$E[XX^\top]=\tfrac12(I+K)+\tfrac12(I-K)=I,$$

so the frame is whitened by construction. The object the theorem identifies is the unordered component covariance pair $\{I+K,I-K\}$, not the pooled covariance fixed at $I$, and not any recording assignment.

\begin{theorem}[point identification of the component covariance pair]\label{thm:pointid}
In the symmetric two-component model above, with $K$ symmetric and every eigenvalue of $K$ lying strictly inside $(-1,1)$, the fourth-order cumulant tensor determines $K$ up to the global sign $K\leftrightarrow-K$ in $d=2$, and hence determines the unordered component covariance pair uniquely. Write $K=Q\operatorname{diag}(\lambda_1,\lambda_2)Q^\top$. The following cases are exhaustive.

\textbf{Case (i): $\lambda_1^2\ne\lambda_2^2$.} The contraction $T$ has two distinct eigenvalues, and diagonalizing it recovers the eigenbasis; the eigenvalue magnitudes and their relative sign follow from the diagonal cumulants.

\textbf{Case (ii): $\lambda_1=-\lambda_2\ne0$, so $\operatorname{tr}K=0$ and $T$ is scalar.} The entries of $K$ are recovered directly from the full tensor by the algebraic identities~\eqref{eq:direct-recover}, with no ratio and no singular direction; the swap configuration $K_{11}=0$ is included.

\textbf{Case (iii): $\lambda_1=\lambda_2\ne0$, so $K=\lambda_1 I$ is isotropic.} There is no basis to recover, and the single value follows from $\kappa_{1111}/3$.

\textbf{Case (iv): $\lambda_1=\lambda_2=0$, so $K=0$.} The zero cumulant tensor forces $K=0$ uniquely, but the two component covariances coincide at $I$; two distinct components and an eigenbasis are not identified.

The only genuine observational freedom is the global sign $K\leftrightarrow-K$, which is exactly the label permutation exchanging $I+K$ with $I-K$. Replacing an eigenvector by its negative leaves $Q\Lambda Q^\top$ and the rank-one projector unchanged and is not a separate freedom, and permuting the eigenvalues together with the eigenvectors leaves the same matrix on the label-permutation quotient.
\end{theorem}

\begin{proof}
Use the fourth cumulant, defined as

\begin{align*}
\kappa_{ijkl}={}&E[X_iX_jX_kX_l]-E[X_iX_j]E[X_kX_l]\\
&-E[X_iX_k]E[X_jX_l]-E[X_iX_l]E[X_jX_k].
\end{align*}

For a zero-mean Gaussian component, Isserlis' theorem gives the fourth moment as the sum over the three pairings, $(\Sigma_\pm)_{ij}(\Sigma_\pm)_{kl}+(\Sigma_\pm)_{ik}(\Sigma_\pm)_{jl}+(\Sigma_\pm)_{il}(\Sigma_\pm)_{jk}$. Averaging the two components and using $\Sigma_\pm=I\pm K$,

$$\tfrac12\sum_{\pm}(\Sigma_\pm)_{ij}(\Sigma_\pm)_{kl}=\delta_{ij}\delta_{kl}+K_{ij}K_{kl},$$

with the same identity for the other two pairings. Since $E[X_iX_j]=\delta_{ij}$, subtracting the three second-order terms leaves

$$\kappa_{ijkl}=K_{ij}K_{kl}+K_{ik}K_{jl}+K_{il}K_{jk}.$$

Now specialize to $d=2$ and orthogonally diagonalize $K=Q\operatorname{diag}(\lambda_1,\lambda_2)Q^\top$, with $\lambda_1,\lambda_2\in(-1,1)$. The cumulant transforms under the same orthogonal matrix, so in the eigenbasis of $K$ it takes the diagonal form

$$\kappa'_{1111}=3\lambda_1^2,\qquad \kappa'_{2222}=3\lambda_2^2,\qquad
\kappa'_{1122}=\lambda_1\lambda_2,\qquad
\kappa'_{1112}=\kappa'_{1222}=0.$$

The eigenbasis still has to be located from the observed tensor. Contract over the two middle indices to form the matrix

$$T_{ij}=\sum_m\kappa_{i m m j}=2(K^2)_{ij}+\operatorname{tr}(K)\,K_{ij},$$

a polynomial in $K$, so it commutes with $K$ and shares its eigenvectors. In the eigenbasis its eigenvalues are $\tau_i=3\lambda_i^2+\lambda_1\lambda_2$, with $\tau_1-\tau_2=3(\lambda_1^2-\lambda_2^2)$.

When $\lambda_1^2\ne\lambda_2^2$, the two $\tau_i$ are distinct, and diagonalizing $T$ recovers the eigenbasis $Q$ uniquely. In that basis the eigenvalues follow as

\begin{equation}\label{eq:point-id}
|\lambda_i|=\sqrt{\kappa'_{iiii}/3},\qquad
\operatorname{sign}(\lambda_1\lambda_2)=\operatorname{sign}(\kappa'_{1122}),
\end{equation}

fixing both magnitudes and their relative sign.

The remaining cases have $\lambda_1^2=\lambda_2^2$, so $T$ is scalar and cannot locate a basis.

If $\lambda_1=-\lambda_2\ne0$, write $\lambda=\lambda_1$ and parametrize $K=\lambda(2qq^\top-I)$ with $q=(\cos\phi,\sin\phi)$. In the fixed whitened coordinates the entries obey $K_{22}=-K_{11}$, with $K_{11}=\lambda\cos2\phi$ and $K_{12}=\lambda\sin2\phi$. Recover the entries directly from the tensor, with no division and hence no singular direction,
\begin{equation}\label{eq:direct-recover}
K_{11}^2=\frac{\kappa_{1111}}3,\qquad
K_{12}^2=\frac{\kappa_{1122}+K_{11}^2}{2}
=\frac{\kappa_{1122}+\kappa_{1111}/3}{2}.
\end{equation}
The second identity uses $\kappa_{1122}=-K_{11}^2+2K_{12}^2$. Fix the relative sign through $\kappa_{1112}=3K_{11}K_{12}$. When $K_{11}\ne0$, choose $K_{11}=+\sqrt{\kappa_{1111}/3}$ and set $\operatorname{sign}K_{12}=\operatorname{sign}\kappa_{1112}$; the opposite choice reproduces $-K$. When $K_{11}=0$, which is exactly the swap configuration $K=\lambda[[0,1],[1,0]]$ at $\phi=\pi/4$, one has $\kappa_{1111}=\kappa_{1112}=0$ and $K_{12}^2=\kappa_{1122}/2=\lambda^2$, so the entry is still recovered and its sign is the global sign. The magnitude closes as $|\lambda|=\sqrt{K_{11}^2+K_{12}^2}$.

If $\lambda_1=\lambda_2\ne0$, then $K=\lambda_1 I$ is isotropic and no basis exists; the single value follows from $\kappa_{1111}/3$. If $\lambda_1=\lambda_2=0$, every cumulant vanishes and the identities force $K=0$; the matrix is unique, but $I+K=I-K=I$ are coincident and no two distinct components, eigenbasis, or direction are identified.

The one freedom that remains is the global sign $K\mapsto-K$. Every component of $\kappa$ is quadratic or a product and is unchanged by it, and it sends $K$ to $-K$, which exchanges $I+K$ with $I-K$. That is the component label permutation, not a distinct parameter. The unordered pair $\{I+K,I-K\}$ is therefore unique, and the positivity condition $I\pm K\succ0$ is checked on the recovered eigenvalues.
\end{proof}

The dimension deserves a precise boundary. The same calculation extends formally: after orthogonally diagonalizing $K=Q\Lambda Q^\top$, one has $\kappa_{iiii}=3\lambda_i^2$ and $\kappa_{iijj}=\lambda_i\lambda_j$, so the eigenvalues and their relative signs follow as in $d=2$, and locating the eigenbasis in $\kappa$ is a symmetric tensor decomposition. Under distinct $|\lambda_i|$ that decomposition is finite and unique up to the global sign, but we state the general-dimension uniqueness as a tensor-decomposition result rather than prove it here; the formal theorem is claimed for $d=2$ under the eigenvalue conditions above.

This is a constrained special case, plainly. The whitening, the two-component restriction, the equal weights, and the symmetry do the work, and the result is not a generic fourth-order theorem. Outside that frame the generic fourth-order map is non-injective, and the generic injectivity threshold for centered Gaussian mixtures sits at sixth order, within explicit rank bounds on the number of components. Given the full distribution rather than a finite collection of moments, a finite Gaussian mixture is identifiable up to permutation by the classical mixture result. We report the fourth-versus-sixth order threshold and the full-distribution result as cited propositions, checking the exact rank bounds against the source for each $(m,n)$ before quoting them; they are not proofs this paper claims as its own.

## 4.4 Scope

The identifiability results operate on one pooled marginal and identify either the partition witness or the unordered component parameter. They do not identify recording assignments, they do not establish finite-sample recovery, and they do not support the DELVE algorithm in Chapter 5. The two mechanisms are kept separate on purpose: mechanism A states what a single pooled distribution can and cannot pin down, and mechanism B asks what repeated recording-level features recover. No implication runs from one to the other. The generic non-Gaussian, fully blind identification problem remains open and is stated in the limitations.
