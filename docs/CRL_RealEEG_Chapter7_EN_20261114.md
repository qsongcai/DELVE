# Real EEG: Blind Environment Recovery without Labels (Chapter 7, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. Every real-data conclusion is limited to dataset-level, source-associated technical structure. The environment here is not a biological or causal environment.

---

## 7.1 Three independent sources and one protocol

The empirical study uses three independently collected EEG sources, chosen so that no single device, lab, or task can account for the whole result.

The first source is a research-grade BrainVision study with eight channels sampled at a thousand hertz, thirty-two subjects, and sixty-four recordings spread across sessions, roughly two recordings per subject. The second is a consumer-grade Emotiv headset with fourteen channels at a hundred and twenty-eight hertz, thirty subjects and thirty long recordings, with a median of eighty-seven windows each. The third is the PhysioNet eyes-open baseline, a hundred and nine subjects and sixty-four channels, with about fifteen windows per recording, obtained through the public PhysioNet bucket.

All three are reduced to one pre-specified pipeline before any clustering. Four shared channels are retained, F3, F4, O1, and O2; the data are resampled to a hundred and twenty-eight hertz, common-average referenced, band-passed from one to forty hertz with a fifty-hertz notch, and cut into four-second windows. Window covariances use shrinkage and are linearized through the matrix logarithm, and the recording feature is the within-recording average. The protocol is fixed before analysis, not chosen after seeing the clusters. Recordings carry different window counts, and each recording receives one equal vote rather than being weighted by its precision.

## 7.2 Units and the permutation rule

The recording is the unit of feature construction and of the primary clustering. Windows estimate a recording's feature and never carry their own p-values. Because a subject can contribute several recordings, a separate analysis treats the subject as the independent unit, and the two are reported apart.

All permutation tests use the same rule, a one-sided upper tail with the plus-one correction,

$$p=\frac{1+\#\{b:T_b\ge T_{\mathrm{obs}}\}}{B+1}.$$

The smallest reportable value is one over $B+1$, and a statistic at that floor is reported as the exact value rather than as strictly smaller. Each p-value is labeled with its resampling count and its unit. Descriptive window-level figures, including the window ARI near $.26$, stay descriptive and carry no independent p-value.

## 7.3 Recovery under a known number of environments

The clearest positive evidence comes from the balanced cross-source design. With only two environments pooled, every paired combination is recovered, with ARI between $.48$ and $.64$. Pooling all three sources and fixing the number at the oracle value of three strengthens the result. On the balanced ninety-recording design, recording-level ARI reaches $.608$, with a recording permutation at the smallest reportable value, and the result holds across six balanced seeds at a mean of $.582$.

This is read for exactly what it is: recording-level, oracle-$K$ evidence that the source label can be reconstructed from the covariance features, a repeatability result across independent sources. It is not an external validation of the fully blind pipeline, and it is not a subject-level claim.

## 7.4 Blind selection fails, and the failure is a headline

The pre-specified blind selector does not reproduce the oracle result. It returns two clusters rather than three, with ARI $.279$, and the merge is systematic. Across every balanced seed the same two sources are joined, while the third stays apart. The contingency table shows the merged cluster absorbing nearly equal numbers from the two joined sources, and that cluster separates cleanly into the two true components once the correct number is restored.

The stability gate is what drives the under-selection, not the BIC term, which on its own prefers the larger values. No pre-specified automatic rule recovers the oracle number, and the one-standard-error rule instead runs to the grid boundary. We present this as a primary finding rather than a caveat: covariance structure can be recoverable at a fixed $K$ while the number of environments is itself not identifiable by the blind procedure. The framing stays neutral on whether a reviewer reads it as a method failure, and both readings are left open.

## 7.5 Balance is a necessary condition

The balanced design is doing real work, and removing it lowers the point estimate. On the full unbalanced pool the recording-level ARI falls to $.371$. The most direct plug-in, which runs the procedure once over all subjects without resampling or rebalancing, is weaker still. With a hundred and seventy-one subjects in unequal group sizes, the subject-level ARI is only $.241$. The large source is split across several clusters and the small sources merge, the same mechanism seen in the unbalanced recording result. Balance is therefore a condition for recovery, not a cosmetic detail, and the weak plug-in is reported alongside the balanced figure rather than hidden.

## 7.6 Subject-level uncertainty

Treating the subject as the independent unit, a subject-cluster bootstrap with five hundred resamples confirms the balanced recovery does not rest on treating repeated recordings as independent. Three designs are compared. The subject-aggregated bootstrap gives a mean of $.616$ with a ninety-five percent interval from $.31$ to $.81$, the cluster-preserving design gives $.554$ with a slightly wider interval, and the naive recording bootstrap gives $.603$. All three intervals exclude zero. A subject-level permutation reaches the smallest reportable value, with the null distribution centered near zero.

Two honest qualifications attach. The single balanced subject realization at seed zero is $.523$, a single draw from the same resampling mechanism whose bootstrap mean is $.616$, and it is not a point estimate on its own. The intervals are not widened by clustering in the way one might expect, because only one source carries repeated recordings and subject aggregation lowers the per-row noise, which offsets the loss of independent units. With roughly thirty subjects per source the intervals remain wide, and the bootstrap is a finite-sample approximation rather than a proof.

## 7.7 Where recovery stops

The same data trace the boundary. In the single-source repeated-session setting, recording-level ARI is $.009$, with a nonparametric recording bootstrap interval from $-.018$ to $.114$ that contains zero, and free and paired permutations give $.291$ and $.136$, both non-significant. This is consistent with the non-identifiability regime rather than a proof of it, and the negative result is stable across the control conditions. The contrast with the cross-source figure is the point: the signal appears across sources and fades within a single source, where no latent environment varies.

## 7.8 De-confounding and the technical label

A set of checks asks whether the separation is carried by subject structure rather than by source. Within-source clustering against subject labels is near zero, and the balanced recording permutation on the de-confounded design remains at the smallest reportable value. The result is consistent with dataset-level acquisition and protocol differences, yet the specific driver is not separated. The source label bundles amplifier, task or resting state, population, duration, reference, and preprocessing into one mixed tag, and these cannot be pulled apart from the pooled data. Original preprocessing artifacts, including hardware anti-aliasing and the amplifier noise floor, are fixed before Stage zero and cannot be removed downstream. No biological or causal interpretation is offered.

## 7.9 Alternative spatial representations

A predictable concern is that the recovery is an artifact of the common-average reference or of one bad channel. Recording features are re-derived under two alternative spatial representations. A reference-free bipolar montage lowers the balanced ARI to $.415$, and a surface Laplacian raises it to $.678$, with both clearly positive. The Laplacian is not a pure re-reference, since it uses a different montage and a spatial transform, and the figures are read with that boundary. Dropping any one of the four shared channels leaves ARI between $.34$ and $.42$, so no single channel drives the result, though distributed bad channels or a shared device fingerprint are not excluded. Recovery persists across representations while its magnitude is representation-dependent, and strict reference invariance is not claimed. Bad-channel marking is a relative heuristic with no interpolation, and an absolute quality threshold remains unbuilt.

## 7.10 Novelty detection and inductive assignment

Pooled label recovery does not establish generalization to unseen data. Each source is held out in turn, the scaler and two centers are fitted on the other two and frozen, and the held-out recordings are mapped without a refit. Two held-out sources are clearly detectable as novel, with ROC AUC between $.89$ and $.93$, while the third is only weakly separated at $.70$, near the training false-alarm rate. The ranking is stable across seeds even though the absolute threshold is not, and held-out recordings split about evenly between the two seen centers rather than collapsing into one, which places them outside the training clusters. When all three sources enter training, a cross-fitted fold assigns held-out recordings with ARI $.610$, essentially matching the transductive $.608$, and this corresponds directly to the sample-split mechanism in the theory. Novelty detection is not the same as correctly labeling a new environment, and full cross-domain generalization remains unproved.

## 7.11 Auxiliary diagnostics

Phase locking is a non-covariance diagnostic and is kept in that role. The pooled multiband phase-locking value gives a high dataset ARI of $.915$, yet the weighted version collapses to $.016$ and single bands run only $.17$ to $.38$. The fingerprint is robust to the reference, since a bipolar montage on the same two sources gives the same $.915$, which removes the hypothesis that the average reference drives it. The contrast is consistent with sensitivity to zero-lag or common-source structure, and it does not establish that such structure is the causal source of the separation. It is not used to support DELVE.

On the Riemannian geometry, the between-source distance exceeds the within-source distance, yet clustering gives near-zero agreement, and the density-based clusterer produces only noise across the tested configurations, with one marginal exception carrying sixty percent noise. The honest conclusion is confined to the tested configurations: no stable dataset-consistent clusters form there, and no claim is made about low-density gaps in general.

## 7.12 Summary

The real-data evidence supports one narrow statement and marks its limits. Under a known $K$ and a balanced design, source-associated covariance structure is recoverable across three independent sources, and the conclusion survives subject-level resampling. The blind selector under-counts, the unbalanced plug-in is weak, and within-source recovery is absent, all reported as boundary checks rather than hidden failures. The recovered object is a technical, dataset-level structure tied to acquisition and protocol, never a causal environment, and the ARI figures are not presented as validation of the theorem.
