# Appendix A: Proofs and detailed derivations

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-15. This appendix contains the full proofs and derivations whose statements and sketches appear in the main text. Mathematical content is preserved verbatim.

---

## Proof of Theorem pointid (point identification of the component covariance pair)

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

## Proof of Theorem d2 (partition non-identification)

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

The construction transports under a reparameterization. For a full-column-rank linear mixing $x=Gz$, the rotation becomes the linear conjugate $GTG^{-1}$ and the same witness applies, and a smooth change of coordinates carries it over in the same way. No separate theorem is built from this; the $d=2$ rotation is the explicit result, and the transported versions are the same witness in new coordinates rather than a broader non-identifiability claim.

## Proofs of the Conditional Compatibility Theorem and the positive risk gap

\begin{proof}
Assumption~\ref{a:align} identifies the optimal centers as a permutation of the environment means. Lemma~\ref{lem:truecenter} makes that configuration error-free.
\end{proof}

\begin{proof}
Under Theorem~\ref{thm:A} the optimal set has error zero, so $\mathcal C_q\cap\mathcal C^\star=\varnothing$. Lemma~\ref{lem:compact} supplies the compact center domain and the continuity of $R$, and Assumption~\ref{a:closed} closes $\mathcal C_q$. The infimum of the continuous function $R-R^\star$ over that compact set is attained, and it is strictly positive because the set excludes every point where the risk difference is zero.
\end{proof}

A quantitative form is available only locally. Let the margin obey $P(X\in\mathcal M_t)\le C_{\rm margin}t^\beta$, with $\beta=1$ in the ordinary case. Inside the local stability region, where a label flip is caused only by the boundary tube,

$$\mathrm{Err}(c)\le C_{\rm margin}\,d(c,\mathcal C^\star)^\beta.$$

Combining this with Assumption~\ref{a:growth} and restricting to $0<q\le q_0$,

$$\psi(q)\ge\kappa\Big(\frac{q}{C_{\rm margin}}\Big)^{2/\beta}.$$

For $\beta=1$, $\psi(q)\ge(\kappa/C_{\rm margin}^2)q^2$. The cutoff $q_0$ is the largest misclassification level at which the local linearization holds; it is back-solved from the radius of the boundary stability region through the margin relation. Three limits stay in force. The perturbation has to lie in the local stability region, the margin condition has to hold for the transformed feature $X$ rather than the raw covariance or a window feature, and Assumption~\ref{a:growth} remains independent of the margin. We claim no global quantitative bound, and neither $\kappa$ nor $C_{\rm margin}$ is self-certified.

## Net and Hoeffding derivation for the finite-sample bound

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

\begin{proof}
On the event $\varepsilon_M\le h(M,\eta)$, which has probability at least $1-\alpha$, the excess-risk decomposition gives $R(\widehat c)-R^\star\le2h(M,\eta)+\delta_{\rm opt}<\psi(q)$. Applying the risk-transfer lemma~\ref{lem:transfer} yields $\mathrm{Err}(\widehat c,Z)<q$. The positivity $\psi(q)>0$ is the content of Theorem~\ref{thm:B} and is what makes the condition attainable; without it the bound is the empty conditional of the lemma.
\end{proof}

## Closed-set lemma, boundary-tube mass, and compactness

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

\begin{proof}
The space $\mathcal C_B$ is a closed and bounded subset of the finite-dimensional space $\mathbb R^{Kp}$, so it is compact by the Heine–Borel theorem. If a center $c_k$ lies outside the ball, project it to $\bar c_k=Bc_k/\|c_k\|$. The ball is convex, and for every $x$ with $\|x\|\le B$ the projection does not increase the distance, $\|x-\bar c_k\|\le\|x-c_k\|$; replacing every out-of-ball center therefore cannot raise the risk, which places an optimizer inside $\mathcal C_B$. For continuity, write $\ell(c,x)=\min_k\|x-c_k\|^2$. Each map $c\mapsto\|x-c_k\|^2$ is continuous, and the minimum of finitely many continuous functions is continuous. Since $\ell$ is bounded on $\mathcal C_B$, taking the expectation preserves continuity, so $R(c)=E[\ell(c,X)]$ is continuous. The misclassification used in $\mathrm{Err}(c,Z)$ is computed after matching the fitted labels to the true labels by the optimal permutation, so the label permutation is quotient out and does not create extra points.
\end{proof}
