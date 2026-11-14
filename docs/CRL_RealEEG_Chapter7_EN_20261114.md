# Real EEG: Blind Environment Recovery without Labels (Chapter 7, formal English)

Working title: *Identifiability and Recovery of Covariance-Based Environment Structure under Pooled Observations*
Date: 2026-11-14. Status: formal manuscript section. Every real-data conclusion is limited to dataset-level, source-associated technical structure. The environment here is not a biological or causal environment.

---

## 7.1 Three independent sources and one protocol

The empirical study uses three independently collected EEG sources. They deliberately span a wide range of acquisition and protocol differences, so the recovered label is interpreted only as a source-associated technical mixture rather than a latent environment, and no claim is made that a single device or task can be isolated as the cause.

The first source is a research-grade BrainVision study with eight channels sampled at a thousand hertz, thirty-two subjects, and sixty-four recordings spread across sessions, roughly two recordings per subject. The second is a consumer-grade Emotiv headset with fourteen channels at a hundred and twenty-eight hertz, thirty subjects and thirty long recordings, with a median of eighty-seven windows each. The third is the PhysioNet eyes-open baseline, a hundred and nine subjects and sixty-four channels, with about fifteen windows per recording, obtained through the public PhysioNet bucket.

All three are reduced to one pre-specified pipeline before any clustering. Four shared channels are retained, F3, F4, O1, and O2; the data are resampled to a hundred and twenty-eight hertz, common-average referenced, band-passed from one to forty hertz with a fifty-hertz notch, and cut into four-second windows. Window covariances use shrinkage and are linearized through the matrix logarithm, and the recording feature is the within-recording average. The protocol is fixed before analysis, not chosen after seeing the clusters. Recordings carry different window counts, and each recording receives one equal vote rather than being weighted by its precision.

The source-level facts and the preprocessing choices needed for reproduction are stated explicitly.

\begin{center}
\small
\begin{tabular}{lllll}
\hline
source (accession) & device & channels & rate & subjects/recordings\\
\hline
ds007541 & BrainVision & 8 & 1000 Hz & 32 / 64\\
ds008099 & Emotiv EPOC & 14 & 128 Hz & 30 / 30\\
on004362 & PhysioNet R01 & 64 & 160 Hz & 109 / 109\\
\hline
\end{tabular}
\end{center}

The harmonization keeps the four shared channels, resamples to $128$ hertz, applies the common-average reference, a one-to-forty-hertz band-pass with a fifty-hertz notch, and non-overlapping four-second windows. Window covariances use the Ledoit–Wolf shrinkage, the matrix logarithm is taken on the shrunk positive-definite matrices with no eigenvalue clipping, and the recording feature is the unweighted mean across windows. The scaler is fitted only on the analysis subset, and the fixed-$K$ K-means uses fifty initializations with the default Lloyd stopping rule. No recording is excluded after download, missing channels are not interpolated, and the PhysioNet source is read through its public bucket. The exact accession numbers, download locations, and the data references are listed in the bibliography.

## 7.2 Units and the permutation rule

The recording is the unit of feature construction and of the primary clustering. Windows estimate a recording's feature and never carry their own p-values. Because a subject can contribute several recordings, a separate analysis treats the subject as the independent unit, and the two are reported apart.

All permutation tests use the same rule, a one-sided upper tail with the plus-one correction,

$$p=\frac{1+\#\{b:T_b\ge T_{\mathrm{obs}}\}}{B+1}.$$

The smallest reportable value is one over $B+1$, and a statistic at that floor is reported as the exact value rather than as strictly smaller. Each p-value is labeled with its resampling count and its unit. Descriptive window-level figures, including the window ARI near $.26$, stay descriptive and carry no independent p-value.

## 7.3 Recovery under a known number of sources

The clearest positive evidence comes from the balanced cross-source design. With only two sources pooled, every paired combination is recovered, with ARI between $.48$ and $.64$. Pooling all three sources and fixing the number at the oracle value of three strengthens the result. On the balanced ninety-recording design, recording-level ARI reaches $.608$, with a recording permutation at the smallest reportable value, and the result holds across six balanced seeds at a mean of $.582$.

This is read for exactly what it is: recording-level, oracle-$K$ evidence that the source label can be reconstructed from the covariance features, a repeatability result across independent sources. It is not an external validation of the fully blind pipeline, and it is not a subject-level claim.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.72\columnwidth]{fig2_pca_scatter.pdf}
\caption{The balanced ninety recording features projected onto their first two principal components and colored by the true source. One source separates along the first component, while the other two occupy closer but still structured regions; the geometry is consistent with an oracle-$K$ recovery rather than three fully disjoint clouds.}
\label{fig:pca}
\end{figure}

## 7.4 Blind selection fails, and the failure is a headline

The pre-specified blind selector does not reproduce the oracle result. It returns two clusters rather than three, with ARI $.279$, and the merge is systematic. Across every balanced seed the same two sources are joined, while the third stays apart. The contingency table shows the merged cluster absorbing nearly equal numbers from the two joined sources, and that cluster separates cleanly into the two true components once the correct number is restored.

The stability gate is what drives the under-selection, not the BIC term, which on its own prefers the larger values. No pre-specified automatic rule recovers the oracle number, and the one-standard-error rule instead runs to the grid boundary. We present this as a primary finding rather than a caveat: covariance structure can be recoverable at a fixed $K$ while the number of sources is itself not identifiable by the blind procedure. The framing stays neutral on whether a reviewer reads it as a method failure, and both readings are left open.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{fig1_k_sensitivity.pdf}
\caption{Adjusted Rand index, normalized mutual information, and silhouette across $K=2,\dots,6$ on the balanced ninety-recording design. The blind selector stops at two clusters with ARI $.279$, whereas the oracle value of three gives $.608$, and the scores plateau before declining as extra clusters split the sources.}
\label{fig:ksens}
\end{figure}

## 7.5 Balance is a necessary condition

The balanced design is doing real work, and removing it lowers the point estimate. On the full unbalanced pool the recording-level ARI falls to $.371$. The most direct plug-in, which runs the procedure once over all subjects without resampling or rebalancing, is weaker still. With a hundred and seventy-one subjects in unequal group sizes, the subject-level ARI is only $.241$. The large source is split across several clusters and the small sources merge, the same mechanism seen in the unbalanced recording result. Balance is therefore a condition for recovery, not a cosmetic detail, and the weak plug-in is reported alongside the balanced figure rather than hidden.

The four primary designs are consolidated in one table, so the point estimate is never read apart from the design that produced it.

\begin{center}
\begin{tabular}{lllll}
\hline
design & $K$ & balance & unit & ARI\\
\hline
oracle-$K$ (DELVE-G) & 3 & balanced & recording & .608\\
blind selector (DELVE-B) & 2 & balanced & recording & .279\\
fixed $K=3$ & 3 & unbalanced & recording & .371\\
full plug-in & selected & unbalanced & subject & .241\\
\hline
\end{tabular}
\end{center}

The $.608$ is a balanced oracle-$K$ diagnostic, not a general performance number for the blind pipeline. The balanced oracle-$K$ result holds across six seeds at a mean of $.582$, and the cross-fitted fold gives $.610$; the other three rows report the blind and unbalanced regimes as primary results rather than footnotes.

## 7.6 Subject-level uncertainty

Treating the subject as the independent unit, a subject-cluster bootstrap with five hundred resamples confirms the balanced recovery does not rest on treating repeated recordings as independent. Three designs are compared. The subject-aggregated bootstrap gives a mean of $.616$ with a ninety-five percent interval from $.31$ to $.81$, the cluster-preserving design gives $.554$ with a slightly wider interval, and the naive recording bootstrap gives $.603$. All three intervals exclude zero. A subject-level permutation reaches the smallest reportable value, with the null distribution centered near zero.

Two honest qualifications attach. The single balanced subject realization at seed zero is $.523$, a single draw from the same resampling mechanism whose bootstrap mean is $.616$, and it is not a point estimate on its own. The intervals are not widened by clustering in the way one might expect, because only one source carries repeated recordings and subject aggregation lowers the per-row noise, which offsets the loss of independent units. With roughly thirty subjects per source the intervals remain wide, and the bootstrap is a finite-sample approximation rather than a proof.

The resampling protocol is stated in full so the intervals are read for what they are.

\begin{center}
\small
\begin{tabular}{lllll}
\hline
design & resampling unit & scaler \& centers & $B$ & interval\\
\hline
subject aggregate & subject & refit & 500 & 2.5/97.5\\
cluster, keep recordings & subject & refit & 500 & 2.5/97.5\\
naive recording & recording & refit & 500 & 2.5/97.5\\
\hline
\end{tabular}
\end{center}

The target parameter is the recording-level ARI, an external metric that needs the true labels rather than a sample mean. Thirty units are drawn per source, the scaler and the fixed-$K$ K-means centers are refitted on every draw, and the number of environments stays at the oracle value rather than being reselected. The cached covariance and log features are not recomputed. The intervals are percentile intervals, not BCa, and they are finite-sample resampling diagnostics, not confidence guarantees with a coverage theorem. The subject-level permutation uses the subject as its unit, with the same plus-one correction and a minimum reportable value of $1/(B+1)$.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{fig3_bootstrap_ci.pdf}
\caption{Subject-cluster bootstrap means and ninety-five percent intervals for three resampling designs. All three intervals exclude zero and sit near the recording point estimate of $.608$, while the all-subject plug-in of $.241$ marks the weaker unbalanced regime.}
\label{fig:bootstrap}
\end{figure}

## 7.7 Where recovery stops

The same data trace the boundary. In the single-source repeated-session setting, recording-level ARI is $.009$, with a nonparametric recording bootstrap interval from $-.018$ to $.114$ that contains zero, and free and paired permutations give $.291$ and $.136$, both non-significant. This is consistent with the non-identifiability regime rather than a proof of it, and the negative result is stable across the control conditions. The contrast with the cross-source figure is the point: the signal appears across sources and fades within a single source, where no latent environment varies.

## 7.8 De-confounding and the technical label

A set of checks asks whether the separation is carried by subject structure rather than by source. Within-source clustering against subject labels is near zero, and the balanced recording permutation on the de-confounded design remains at the smallest reportable value. The result is consistent with dataset-level acquisition and protocol differences, yet the specific driver is not separated. The source label bundles amplifier, task or resting state, population, duration, reference, and preprocessing into one mixed tag, and these cannot be pulled apart from the pooled data. Original preprocessing artifacts, including hardware anti-aliasing and the amplifier noise floor, are fixed before Stage zero and cannot be removed downstream. No biological or causal interpretation is offered.

## 7.9 Alternative spatial representations

A predictable concern is that the recovery is an artifact of the common-average reference or of one bad channel. Recording features are re-derived under two alternative spatial representations. A reference-free bipolar montage lowers the balanced ARI to $.415$, and a surface Laplacian raises it to $.678$, with both clearly positive. The Laplacian is not a pure re-reference, since it uses a different montage and a spatial transform, and the figures are read with that boundary. Dropping any one of the four shared channels leaves ARI between $.34$ and $.42$, so no single channel drives the result, though distributed bad channels or a shared device fingerprint are not excluded. Recovery persists across representations while its magnitude is representation-dependent, and strict reference invariance is not claimed. Bad-channel marking is a relative heuristic with no interpolation, and an absolute quality threshold remains unbuilt.

## 7.10 Novelty detection and inductive assignment

Pooled label recovery does not establish generalization to unseen data. Each source is held out in turn, the scaler and two centers are fitted on the other two and frozen, and the held-out recordings are mapped without a refit. Two held-out sources are clearly detectable as novel, with ROC AUC between $.89$ and $.93$, while the third is only weakly separated at $.70$, near the training false-alarm rate. The ranking is stable across seeds even though the absolute threshold is not, and held-out recordings split about evenly between the two seen centers rather than collapsing into one, which places them outside the training clusters. When all three sources enter training, a cross-fitted fold assigns held-out recordings with ARI $.610$, essentially matching the transductive $.608$, and this corresponds directly to the sample-split mechanism in the theory. Novelty detection is not the same as correctly labeling a new environment, and full cross-domain generalization remains unproved.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{fig4_spatial_novelty.pdf}
\caption{Left: recording-level ARI under common-average, bipolar, and surface-Laplacian (CSD) spatial representations across six seeds, with the magnitude varying but staying positive. Right: leave-one-source novelty ROC AUC, high for two sources and weak for the third.}
\label{fig:spatial}
\end{figure}

## 7.11 Auxiliary diagnostics

Phase locking is a non-covariance diagnostic and is kept in that role. The pooled multiband phase-locking value gives a high dataset ARI of $.915$, yet the weighted version collapses to $.016$ and single bands run only $.17$ to $.38$. The fingerprint is robust to the reference, since a bipolar montage on the same two sources gives the same $.915$, which removes the hypothesis that the average reference drives it. The contrast is consistent with sensitivity to zero-lag or common-source structure, and it does not establish that such structure is the causal source of the separation. It is not used to support DELVE.

On the Riemannian geometry, the between-source distance exceeds the within-source distance, yet clustering gives near-zero agreement, and the density-based clusterer produces only noise across the tested configurations, with one marginal exception carrying sixty percent noise. The honest conclusion is confined to the tested configurations: no stable dataset-consistent clusters form there, and no claim is made about low-density gaps in general.

## 7.12 Baselines and component ablations

The DELVE components are standard pieces, and the design choices need to be justified against measured alternatives rather than asserted. The baseline matrix was run on the two-source design, ninety-four recordings and sixty-two subjects, with the same harmonization and a blind fit; metadata entered only in the post-hoc scoring. The numbers are therefore two-source, $K=2$ evidence and are read with that scope.

The covariance representation varies the estimator and the matrix mapping, with recording-level ARI against the source label.

\begin{center}
\begin{tabular}{llll}
\hline
estimator \textbackslash\ mapping & logm & raw & sqrtm\\
\hline
Empirical & .232 & .049 & .163\\
Ledoit–Wolf & .581 & .049 & .163\\
OAS & .457 & .049 & .163\\
\hline
\end{tabular}
\end{center}

The logarithm is the decisive mapping, with raw and square-root features near zero, and shrinkage is indispensable at the available sample size: empirical shrinkage with the log reaches only $.232$, against $.581$ for Ledoit–Wolf. The clusterer and the non-covariance features are compared on the same fixed design.

\begin{center}
\begin{tabular}{llll}
\hline
clusterer & ARI & non-covariance feature & ARI\\
\hline
GMM & .795 & phase locking (PLV) & .915\\
agg-complete & .649 & correlation & .393\\
spectral & .582 & band power & .108\\
K-means & .581 & phase lag index & .100\\
agg-ward & .317 & &\\
agg-average & .024 & &\\
\hline
\end{tabular}
\end{center}

The soft GMM and the non-covariance phase-locking feature outperform the hard K-means on this two-source design, which is reported rather than hidden; phase locking is an acquisition-sensitive fingerprint and is not used as evidence for the covariance framework. The Riemannian and density-based clusterers do not form stable source-consistent clusters across the tested configurations, as stated in the previous section. The table covers the estimator, mapping, clusterer, and feature choices; the earlier recording-averaging and standardization steps are not separately ablated here, and that gap is stated rather than filled with an unmeasured number.

## 7.13 Summary

The real-data evidence supports one narrow statement and marks its limits. Under a known $K$ and a balanced design, source-associated covariance structure is recoverable across three independent sources, and the conclusion survives subject-level resampling. The blind selector under-counts, the unbalanced plug-in is weak, and within-source recovery is absent, all reported as boundary checks rather than hidden failures. The recovered object is a technical, dataset-level structure tied to acquisition and protocol, never a causal environment, and the ARI figures are not presented as validation of the theorem.
