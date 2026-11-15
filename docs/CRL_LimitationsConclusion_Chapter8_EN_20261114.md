# Limitations and Conclusion (Chapter 8, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-15. Status: shortened manuscript section. The limitations state the boundaries of the claims; the conclusion restates only what the evidence supports.

---

## 8.1 Limitations

The compatibility premise is assumed, not derived. The central bridge is a recording-level compatibility condition between the latent assignment and the population K-means objective, and the closed level-set and quadratic-growth conditions are hypotheses as well. Nothing in the generative model forces them to hold, and the earlier exchange argument that sought to derive them is withdrawn. Proving alignment on a structured class of distributions is the natural next step, and the quantitative growth bound is local, with no global version claimed.

The number of environments is not identified. Every theoretical statement conditions on $K$, and there is no proof that $K$ is identifiable or consistently estimable; the blind selector under-counts on the pooled real data, a stable finding rather than an isolated miss. Automatic selection, full-pool standardization, and finite-initialization Lloyd stay outside the unconditional guarantees, and the window-level and recording-level estimands coincide only under extra conditions.

Several technical pieces remain open. An algorithm-independent bound on the training-side center error is not established, and the projection cross-terms are treated through an all-direction control rather than a closed form. The exact correspondence between estimated and population objects, the unification of the scaler coordinates, and the fitted center term are each stated as conditions, and the K-means basin of attraction and a local-to-global proof are not provided. On the data side, bad-channel interpolation and an absolute quality threshold are absent, and the channel-sensitivity result rules out only a single-channel explanation, not distributed artifacts or a shared device fingerprint.

The empirical and identification claims are bounded. The real-data label is a technical mixture of device, task, population, duration, reference, and preprocessing whose driver cannot be separated, and no biological or causal reading is available. The three-source design gives repeatability evidence rather than a generality proof, and full cross-domain generalization is not established. The partial-identification framing is descriptive rather than a proved sharp set, the resampling intervals carry no coverage guarantee, and the general non-Gaussian, fully blind problem remains open.

## 8.2 Conclusion

The paper asked whether a covariance-based environment structure stays identifiable once the labels disappear and the observations are pooled. The answer is deliberately several answers rather than one.

A two-dimensional witness shows that two genuinely different partitions can induce the same pooled distribution, enough to rule out treating identifiability as automatic without making a universal claim. In a constrained, whitened two-component frame the component covariance pair is point-identified, plainly a special case, while the moment-order threshold beyond it is reported as cited work. Relax the assumptions and the target can only be described as a set of consistent structures, a descriptive partial-identification framing rather than a proved sharp set.

The practical contribution is a recording-level framework that keeps the observation mechanism, the estimand, and the algorithm version distinct. Under fixed $K$ and a fixed transformation, the global empirical K-means solution carries a finite-sample risk-gap guarantee, and a sample-split variant gives a held-out decomposition whose training-side term stays explicit. The standard components are not presented as novel; the contribution lies in the estimand, the conditional guarantee, and the repeatable failure boundary. On three independent EEG sources, source-associated structure is recoverable under a known $K$ and a balanced design and survives subject-level resampling, while blind under-counting, the weak unbalanced plug-in, and absent within-source recovery are all reported as findings.

Deriving the compatibility condition from a structured distribution class, establishing the identifiability of $K$, closing the training-side bound, and extending the framework to non-Gaussian and unseen settings would each move the boundary outward. Until then, the claims are offered with their conditions attached. The complete implementation and the scripts that reproduce every table and figure are released in a public repository, and the data sources and access details are stated in the Data Availability section.
