# Real EEG: Diagnosing Cross-Source Technical Separability without Labels (Chapter 7, formal English)

Working title: *Identifiability Boundaries and Conditional Recovery of Covariance-Based Environments*
Date: 2026-11-14. Status: formal manuscript section. Every real-data conclusion is limited to dataset-level, source-associated technical structure. The environment here is not a biological or causal environment.

---

## 7.1 Three independent sources and one protocol

The empirical study uses three independently collected EEG sources. They span a wide spread of acquisition and protocol differences, so the recovered label is interpreted only as a source-associated technical mixture rather than a latent environment, and no claim is made that a single device or task can be isolated as the cause.

The first source is a research-grade BrainVision study with eight channels sampled at a thousand hertz, thirty-two subjects, and sixty-four recordings spread across sessions, roughly two recordings per subject. The second is a consumer-grade Emotiv headset with fourteen channels at a hundred and twenty-eight hertz, thirty subjects and thirty long recordings, with a median of eighty-seven windows each. The third is the eyes-open baseline run R01, the first of the two one-minute baseline runs, of the PhysioNet *EEG Motor Movement/Imagery Dataset* (eegmmidb), a hundred and nine subjects and sixty-four channels, with about fifteen windows per recording, obtained through the public PhysioNet bucket.

All three are reduced to one pre-specified pipeline before any clustering. Four shared channels are retained, F3, F4, O1, and O2; the data are resampled to a hundred and twenty-eight hertz, common-average referenced, band-passed from one to forty hertz with a fifty-hertz notch, and cut into four-second windows. Window covariances use shrinkage and are linearized through the matrix logarithm, and the recording feature is the within-recording average. The protocol is fixed before analysis, not chosen after seeing the clusters. Recordings carry different window counts, and each recording receives one equal vote rather than being weighted by its precision.

The source-level facts and the preprocessing choices needed for reproduction are stated explicitly in Table~\ref{tab:sources}.

\begin{table}[htbp]
\centering
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
\caption{The three independently collected EEG sources and their acquisition characteristics. The harmonized pipeline reduces these heterogeneous sources to a common feature space.}
\label{tab:sources}
\end{table}

The harmonization keeps the four shared channels, resamples to $128$ hertz, applies the common-average reference, a one-to-forty-hertz band-pass with a fifty-hertz notch, and non-overlapping four-second windows. Window covariances use the Ledoit–Wolf shrinkage, the matrix logarithm is taken on the shrunk positive-definite matrices with no eigenvalue clipping, and the recording feature is the unweighted mean across windows. The scaler is fitted only on the analysis subset, and the fixed-$K$ K-means uses fifty initializations with the default Lloyd stopping rule. No recording is excluded after download, missing channels are not interpolated, and the PhysioNet source is read through its public bucket. The exact accession numbers, download locations, and the data references are listed in the bibliography.

## 7.2 Units and the permutation rule

The recording is the unit of feature construction and of the primary clustering. Windows estimate a recording's feature and never carry their own p-values. Because a subject can contribute several recordings, a separate analysis treats the subject as the independent unit, and the two are reported apart.

All permutation tests use the same rule, a one-sided upper tail with the plus-one correction,

$$p=\frac{1+\#\{b:T_b\ge T_{\mathrm{obs}}\}}{B+1}.$$

The smallest reportable value is one over $B+1$, and a statistic at that floor is reported as the exact value rather than as strictly smaller. Each p-value is labeled with its resampling count and its unit. Descriptive window-level figures, including the window ARI near $0.26$, stay descriptive and carry no independent p-value.

## 7.3 Simple metadata and the technical-difference controls

A direct diagnostic asks whether the sources are already separated by information that has nothing to do with latent environments. The most basic per-recording field is the number of windows, fixed by each recording's length and the four-second window rule. It is nine for every recording in the first source, fifteen for every recording in the third, and ranges from eighty to a hundred and fourteen in the second; the three ranges do not overlap. A decision tree given only this field predicts the source with perfect cross-validated accuracy. The cross-validation is also run with subject-grouped folds, which keep every recording of one subject in a single fold across the 171 subject groups; the grouped accuracy stays at one, so the result is not produced by related recordings of the same subject crossing between training and test. Adding the device metadata that is constant within a source, the original sampling rate, channel count, and file format, holds the accuracy at one for both logistic and tree models under both the stratified and grouped folds. The three sources are therefore fully separable from trivial metadata alone; covariance is not needed to tell them apart, and this is the clearest evidence that the recovered label is a technical one.

The association with metadata is quantified rather than asserted. Across the ten covariance features, the absolute correlation with window count reaches $0.663$ and averages $0.210$, so recording length is not a factor that can be set aside. A length-matched or length-stratified rerun would be the natural control, but the data do not permit one. The three window-count ranges are $\{9\}$, $\{15\}$, and $\{80,\dots,114\}$, with no common support, and no recording length occurs in two sources. There is therefore no stratum on which to match, and trimming to an overlap would leave an empty design. We state this as an infeasibility rather than replace it with a different control.

The wording distinction follows. What is recoverable is a source-associated covariance structure under a known number and a stratified design. It is not environment recovery in the sense of discovering latent causal environments from the pooled data: the source label is already determined by trivial metadata, and the covariance analysis describes how that technical difference appears in the feature space, rather than a latent grouping that exists independently of the acquisition. The two phrases are kept separate throughout the rest of the chapter.

\begin{table}[htbp]
\centering
\small
\begin{tabular}{ll}
\hline
diagnostic & result\\
\hline
source prediction from window count only & CV accuracy 1.000\\
source prediction from full device metadata & CV accuracy 1.000\\
within-source silhouette ($K=2,3$) & 0.18--0.22\\
within-source ARI vs subject (ds007541) & 0.02--0.03\\
same-task two-source $K=2$ ARI (resting sources) & 0.53 (0.56 over seeds)\\
\hline
\end{tabular}
\caption{Metadata baselines and the same-device and same-task controls. Trivial metadata already separates the sources, no stable structure appears within a device, and the two resting sources still separate despite sharing a task.}
\label{tab:metactrl}
\end{table}

Two controls check where the structure appears. The same-device control pools recordings within one source and repeats the clustering there. The silhouette stays low, between about $0.18$ and $0.22$, and for the one source with two recordings per subject the clustering agrees with the subject label at an ARI of only $0.02$ to $0.03$, so no stable within-device structure is recovered. The same-task control keeps the two resting, eyes-open sources and drops the third; despite the shared task they still separate at two clusters, with a balanced ARI of $0.53$, $0.56$ over three seeds. This establishes only that a shared task category is not sufficient to remove the source difference. It does not establish that the task plays no role, because the two sources still differ in device, population, recording length, reference, and preprocessing at the same time, and these factors cannot be separated from the pooled data. The controls therefore support a narrower reading: the across-source structure is tied to acquisition and protocol, and no latent environment is recovered that reappears within a device; they cannot name a single driver.

## 7.4 Recovery under a known number of sources

The clearest positive evidence comes from the balanced cross-source design. With only two sources pooled, every paired combination is recovered, with ARI between $0.48$ and $0.64$. Pooling all three sources and fixing the number at the oracle value of three strengthens the result. On the balanced ninety-recording design, recording-level ARI reaches $0.608$, with a recording permutation at the smallest reportable value, and the result holds across six balanced seeds at a mean of $0.582$.

The balanced design is not a blind run. Thirty recordings are drawn from each source, and that draw uses the source label only to select the recordings; the label never enters the covariance features, the scaler, or the clustering. The size of the draw and the rule are fixed in advance, before any cluster is seen, so the design is a pre-specified evaluation rather than a post-hoc adjustment. The only genuinely blind analysis in this chapter is the data-driven number selection of the next section.

This is read for exactly what it is: recording-level, oracle-$K$ evidence that the source label can be reconstructed from the covariance features, a repeatability result across independent sources. It is not an external validation of the fully blind pipeline, and it is not a subject-level claim.

\begin{table}[htbp]
\centering
\small
\begin{tabular}{lcc}
\hline
seed & balanced $K=3$ ARI & cross-fitted $K=3$ ARI\\
\hline
0 & 0.608 & 0.602\\
1 & 0.589 & 0.630\\
2 & 0.476 & 0.602\\
3 & 0.535 & 0.717\\
4 & 0.607 & 0.617\\
5 & 0.675 & 0.493\\
\hline
mean & 0.582 & 0.610\\
std & 0.068 & 0.072\\
\hline
\end{tabular}
\caption{Per-seed recording-level ARI on the ninety-recording balanced design and on the cross-fitted held-out construction, with the sample mean and standard deviation reported rather than a mean alone. The cross-fitted column is defined in Section~7.13.}
\label{tab:perseed}
\end{table}

\begin{figure}[ht]
\centering
\includegraphics[width=0.85\columnwidth]{fig2_pca_scatter.pdf}
\caption{The balanced ninety recording features projected onto their first two principal components and colored by the true source. One source separates along the first component, while the other two occupy closer but still structured regions; the geometry is consistent with an oracle-$K$ recovery rather than three fully disjoint clouds.}
\label{fig:pca}
\end{figure}

## 7.4 Blind selection fails, and the failure is a headline

The pre-specified blind selector does not reproduce the oracle result. It returns two clusters rather than three, with ARI $0.279$, and the merge is systematic. Across every balanced seed the same two sources are joined, while the third stays apart. The contingency table shows the merged cluster absorbing nearly equal numbers from the two joined sources, and that cluster separates cleanly into the two true components once the correct number is restored.

The stability gate drives the under-selection, not the BIC term, which on its own prefers the larger values. No pre-specified automatic rule recovers the oracle number, and the one-standard-error rule instead runs to the grid boundary. We present this as a primary finding rather than a caveat: covariance structure can be recoverable at a fixed $K$ while the number of sources is itself not identifiable by the blind procedure. The framing stays neutral on whether a reviewer reads it as a method failure, and both readings are left open.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{fig1_k_sensitivity.pdf}
\caption{Adjusted Rand index, normalized mutual information, and silhouette across $K=2,\dots,6$ on the balanced ninety-recording design. The blind selector stops at two clusters with ARI $0.279$, whereas the oracle value of three gives $0.608$, and the scores plateau before declining as extra clusters split the sources.}
\label{fig:ksens}
\end{figure}

## 7.5 Balance is a necessary condition

The balanced design does real work, and removing it lowers the point estimate. On the full unbalanced pool the recording-level ARI falls to $0.371$. The most direct plug-in, which runs the procedure once over all subjects without resampling or rebalancing, is weaker still. With a hundred and seventy-one subjects in unequal group sizes, the subject-level ARI is only $0.241$. The large source is split across several clusters and the small sources merge, the same mechanism seen in the unbalanced recording result. Balance is therefore a condition for recovery, not a cosmetic detail, and the weak plug-in is reported alongside the balanced figure.

The four primary designs are consolidated in Table~\ref{tab:designs}, so the point estimate is never read apart from the design that produced it.

\begin{table}[htbp]
\centering
\begin{tabular}{lllll}
\hline
design & $K$ & balance & unit & ARI\\
\hline
oracle-$K$ (DELVE-G) & 3 & balanced & recording & 0.608\\
blind selector (DELVE-B) & 2 & balanced & recording & 0.279\\
fixed $K=3$ & 3 & unbalanced & recording & 0.371\\
full plug-in & selected & unbalanced & subject & 0.241\\
\hline
\end{tabular}
\caption{ARI across the four primary designs. Recovery is strong under the balanced oracle-$K$ design (0.608) and weakens under blind selection, unbalanced pooling, and the full subject plug-in.}
\label{tab:designs}
\end{table}

The $0.608$ is a balanced oracle-$K$ diagnostic, not a general performance number for the blind pipeline. The balanced oracle-$K$ result holds across six seeds at a mean of $0.582$, and the cross-fitted fold gives $0.610$; the other three rows report the blind and unbalanced regimes as primary results rather than footnotes.

## 7.6 Subject-level uncertainty

Treating the subject as the independent unit, a subject-cluster bootstrap with five hundred resamples confirms the balanced recovery does not rest on treating repeated recordings as independent. Three designs are compared. The subject-aggregated bootstrap gives a mean of $0.616$ with a ninety-five percent interval from $0.31$ to $0.81$, the cluster-preserving design gives $0.554$ with a slightly wider interval, and the naive recording bootstrap gives $0.603$. All three intervals exclude zero. A subject-level permutation reaches the smallest reportable value, with the null distribution centered near zero.

Two honest qualifications attach. The single balanced subject realization at seed zero is $0.523$, a single draw from the same resampling mechanism whose bootstrap mean is $0.616$, and it is not a point estimate on its own. The intervals are not widened by clustering in the way one might expect, because only one source carries repeated recordings and subject aggregation lowers the per-row noise, which offsets the loss of independent units. With roughly thirty subjects per source the intervals remain wide, and the bootstrap is a finite-sample approximation rather than a proof.

Table~\ref{tab:resampling} states the resampling protocol in full so the intervals are read for what they are.

\begin{table}[htbp]
\centering
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
\caption{The three resampling designs used to quantify subject-level uncertainty. All three refit the scaler and centers on each draw and report percentile intervals rather than a coverage theorem.}
\label{tab:resampling}
\end{table}

The target parameter is the recording-level ARI, an external metric that needs the true labels rather than a sample mean. Thirty units are drawn per source, the scaler and the fixed-$K$ K-means centers are refitted on every draw, and the number of environments stays at the oracle value rather than being reselected. The cached covariance and log features are not recomputed. The intervals are percentile intervals, not BCa, and they are finite-sample resampling diagnostics, not confidence guarantees with a coverage theorem. The subject-level permutation uses the subject as its unit, with the same plus-one correction and a minimum reportable value of $1/(B+1)$.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{fig3_bootstrap_ci.pdf}
\caption{Subject-cluster bootstrap means and ninety-five percent intervals for three resampling designs. All three intervals exclude zero and sit near the recording point estimate of $0.608$, while the all-subject plug-in of $0.241$ marks the weaker unbalanced regime.}
\label{fig:bootstrap}
\end{figure}

## 7.7 Where recovery stops

The same data trace the boundary. In the single-source repeated-session setting, recording-level ARI is $0.009$, with a nonparametric recording bootstrap interval from $-0.018$ to $0.114$ that contains zero, and free and paired permutations give $0.291$ and $0.136$, both non-significant. This is consistent with the non-identifiability regime rather than a proof of it, and the negative result is stable across the control conditions. The contrast with the cross-source figure is the point: the signal appears across sources and fades within a single source, where no latent environment varies.

## 7.8 De-confounding and the technical label

A set of checks asks whether the separation is carried by subject structure rather than by source. Within-source clustering against subject labels is near zero, and the balanced recording permutation on the de-confounded design remains at the smallest reportable value. The result is consistent with dataset-level acquisition and protocol differences, yet the specific driver is not separated. The source label bundles amplifier, task or resting state, population, duration, reference, and preprocessing into one mixed tag, and these cannot be pulled apart from the pooled data. Original preprocessing artifacts, including hardware anti-aliasing and the amplifier noise floor, are fixed before Stage zero and cannot be removed downstream.

## 7.9 Alternative spatial representations

A predictable concern is that the recovery is an artifact of the common-average reference or of one bad channel. Recording features are re-derived under two alternative spatial representations. A reference-free bipolar montage lowers the balanced ARI to $0.415$, and a surface Laplacian raises it to $0.678$, with both clearly positive. The Laplacian is not a pure re-reference, since it uses a different montage and a spatial transform, and the figures are read with that boundary. Dropping any one of the four shared channels leaves ARI between $0.34$ and $0.42$, so no single channel drives the result, though distributed bad channels or a shared device fingerprint are not excluded. Recovery persists across representations while its magnitude is representation-dependent, and strict reference invariance is not claimed. Bad-channel marking is a relative heuristic with no interpolation, and an absolute quality threshold remains unbuilt.

## 7.10 Novelty detection and inductive assignment

Pooled label recovery does not establish generalization to unseen data. Each source is held out in turn, the scaler and two centers are fitted on the other two and frozen, and the held-out recordings are mapped without a refit. Two held-out sources are clearly detectable as novel, with ROC AUC between $0.89$ and $0.93$, while the third is only weakly separated at $0.70$, near the training false-alarm rate. The ranking is stable across seeds even though the absolute threshold is not, and held-out recordings split about evenly between the two seen centers rather than collapsing into one, which places them outside the training clusters. When all three sources enter training, a cross-fitted fold assigns held-out recordings with ARI $0.610$, essentially matching the transductive $0.608$, and this corresponds directly to the sample-split mechanism in the theory. Novelty detection is not the same as correctly labeling a new environment, and full cross-domain generalization remains unproved.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{fig4_spatial_novelty.pdf}
\caption{Left: recording-level ARI under common-average, bipolar, and surface-Laplacian (CSD) spatial representations across six seeds, with the magnitude varying but staying positive. Right: leave-one-source novelty ROC AUC, high for two sources and weak for the third.}
\label{fig:spatial}
\end{figure}

## 7.11 Auxiliary diagnostics

Phase locking is a non-covariance diagnostic and is kept in that role. The pooled multiband phase-locking value gives a high dataset ARI of $0.915$, yet the weighted version collapses to $0.016$ and single bands run only $0.17$ to $0.38$. The fingerprint is robust to the reference, since a bipolar montage on the same two sources gives the same $0.915$, which removes the hypothesis that the average reference drives it. The contrast is consistent with sensitivity to zero-lag or common-source structure, and it does not establish that such structure is the causal source of the separation. It is not used to support DELVE.

On the Riemannian geometry, the between-source distance exceeds the within-source distance, yet clustering gives near-zero agreement, and the density-based clusterer produces only noise across the tested configurations, with one marginal exception carrying sixty percent noise. The honest conclusion is confined to the tested configurations: no stable dataset-consistent clusters form there, and no claim is made about low-density gaps in general.

## 7.12 Baselines and component ablations

The DELVE components are standard pieces, and the design choices need to be justified against measured alternatives rather than asserted. The baseline matrix was run on the two-source design, ninety-four recordings and sixty-two subjects, with the same harmonization and a blind fit; metadata entered only in the post-hoc scoring. The numbers are therefore two-source, $K=2$ evidence, read with that scope, and they do not establish how the algorithm performs on the three-source main experiment; no figure is carried across the two designs.

The covariance representation varies the estimator and the matrix mapping, with recording-level ARI against the source label in Table~\ref{tab:covrep}.

\begin{table}[htbp]
\centering
\begin{tabular}{llll}
\hline
estimator \textbackslash\ mapping & logm & raw & sqrtm\\
\hline
Empirical & 0.232 & 0.049 & 0.163\\
Ledoit–Wolf & 0.581 & 0.049 & 0.163\\
OAS & 0.457 & 0.049 & 0.163\\
\hline
\end{tabular}
\caption{Recording-level ARI across covariance estimators and matrix mappings on the fixed two-source, $K=2$ design (94 recordings, 62 subjects, blind fit). The matrix logarithm is decisive and Ledoit--Wolf shrinkage is indispensable at the available sample size. These figures do not measure performance on the three-source main experiment and are not compared with it.}
\label{tab:covrep}
\end{table}

The logarithm is the decisive mapping, with raw and square-root features near zero, and shrinkage is indispensable at the available sample size: empirical shrinkage with the log reaches only $0.232$, against $0.581$ for Ledoit–Wolf. The clusterer and the non-covariance features are compared on the same fixed design in Table~\ref{tab:clusterers}.

\begin{table}[htbp]
\centering
\begin{tabular}{llll}
\hline
clusterer & ARI & non-covariance feature & ARI\\
\hline
GMM & 0.795 & phase locking (PLV) & 0.915\\
agg-complete & 0.649 & correlation & 0.393\\
spectral & 0.582 & band power & 0.108\\
K-means & 0.581 & phase lag index & 0.100\\
agg-ward & 0.317 & &\\
agg-average & 0.024 & &\\
\hline
\end{tabular}
\caption{Recording-level ARI across clusterers and non-covariance features on the same fixed two-source, $K=2$ design. GMM and phase locking outperform hard K-means, but phase locking is an acquisition-sensitive diagnostic rather than evidence for the covariance framework, and the results are scoped to this two-source design rather than compared with the three-source experiment.}
\label{tab:clusterers}
\end{table}

The soft GMM and the non-covariance phase-locking feature outperform the hard K-means on this two-source design; phase locking is an acquisition-sensitive fingerprint and is not used as evidence for the covariance framework. The Riemannian and density-based clusterers do not form stable source-consistent clusters across the tested configurations, as stated in the previous section. The table covers the estimator, mapping, clusterer, and feature choices; the earlier recording-averaging and standardization steps are not separately ablated here, and that gap is stated rather than filled with an unmeasured number.

## 7.13 Data and processing details

The implementation is not an object of the theoretical guarantees, so the processing is fixed in code and the choices that determine the output are listed here in full.

1. **Sources, versions, and links.** ds007541 is the *Multi-identity Information Authentication EEG Dataset*, OpenNeuro snapshots v1.0.0--v1.0.2, at \url{https://openneuro.org/datasets/ds007541}. ds008099 is the *Pizza-topping meat/vegetarian word categorization with consumer EEG (EMOTIV EPOC X)*, snapshot v1.0.0, at \url{https://openneuro.org/datasets/ds008099/versions/1.0.0}; both are also indexed on NEMAR under the matching on-prefixed identifiers and released under CC0. on004362 is the PhysioNet *EEG Motor Movement/Imagery Dataset* (eegmmidb), v1.0.0, at \url{https://physionet.org/content/eegmmidb/1.0.0/}, and is cited through Goldberger et al.~\cite{goldberger2000}.
2. **Inclusion and exclusion.** Files are selected by fixed glob patterns, the verification run-01 BrainVision files, the per-subject EDF files, and the R01 PhysioNet EDF files, where R01 is the eyes-open baseline run, the first of the two one-minute baseline runs in the protocol rather than a label inferred from the filename. A recording that fails to load is skipped and named, and a recording with fewer than three windows is excluded. In the realized run, every targeted file loaded successfully and every retained recording passed the three-window rule, so the post-download exclusion count is zero and there is no exclusion list to report; missing channels are not interpolated. The retained counts are 64, 30, and 109 recordings from 32, 30, and 109 subjects, with all 109 PhysioNet subjects retained.
3. **Channel mapping, reference, and order.** The four shared channels F3, F4, O1, and O2 are picked by name, and the trailing dots in the PhysioNet EDF names are stripped. A common-average reference is applied first, then the band-pass and notch, and resampling last, so the filters run at each device's native rate before any downsampling. Resampling uses the default FFT method with automatic padding.
4. **Filter design.** Processing uses MNE 1.12.1 with FIR, zero-phase, windowed-sinc (firwin) filters and a Hamming window. The one-to-forty-hertz band-pass uses automatic transition bandwidths and an automatic length; the fifty-hertz notch uses a one-hertz transition bandwidth with an automatic length. The filter is therefore fully determined by the MNE version and these calls, and the released code reproduces it without custom coefficients.
5. **Covariance level.** Ledoit–Wolf is fitted once per four-second window, never once per recording. The matrix logarithm is taken on each window covariance, and the recording feature is the unweighted mean of the window log-covariances.
6. **Symmetrization and the logarithm.** No explicit symmetrization is applied; the shrinkage covariance is symmetric by construction. The SciPy matrix logarithm is used and its real part is kept to discard negligible numerical imaginary residue, with no eigenvalue clipping. A logarithm failure would surface as a load failure and the recording would be skipped under item 2; none occurs in the retained set.
7. **Scaler.** The scaler is fitted on the analysis subset rather than the full pool for the fixed-transformation theorem, and it is refitted inside every bootstrap, resampling, and held-out draw. A scaler fitted once on the entire pool appears only in the transductive variant and is not part of the theorem.
8. **Blind number selection.** For each candidate $K$, three scores are produced. The BIC comes from a diagonal Gaussian mixture, \texttt{GaussianMixture(K, covariance\_type='diag', n\_init=5, reg\_covar=$10^{-4}$)}, and is a penalized-likelihood score; the hard K-means partition gives the silhouette; and a bootstrap stability score is computed. The BIC model and the final clusterer are deliberately different. BIC is used only as a pre-specified ranking criterion among candidate numbers that already pass the geometry and stability gates, not as a claim that the data are Gaussian and not as the output partition, which stays K-means.
The stability score has an exact definition. On each of sixty bootstrap rounds, $M$ indices are drawn with replacement, K-means is fitted on the resampled recordings, and its centroids are frozen; those centroids assign the original, unresampled recordings through nearest-centroid prediction, and the round score is the ARI between that prediction and the original K-means labels. The reported stability is the mean of the sixty ARIs. It compares each resampled fit against the original clustering, not against the other resampled fits.
The selection threshold is $\min(0.85,0.9\max_K\text{stability})$; candidates with stability above the threshold and a positive silhouette are eligible, and the eligible candidate with the smallest BIC is chosen. If none is eligible, the largest silhouette is used, and if no silhouette is positive the smallest BIC is used.
9. **Balanced randomization.** For a given integer seed, \texttt{numpy.random.default\_rng(seed)} draws thirty recordings from each source without replacement, or all recordings when a source has fewer. The seed fixes the recording composition exactly, so every draw is reproducible.
10. **Baseline parameters.** The K-means used for the reported partition and the risk-gap setting uses fifty initializations with the default Lloyd stopping rule. The full-covariance GMM baseline clusterer uses eight initializations with \texttt{reg\_covar} $10^{-4}$; agglomerative clustering uses ward, complete, and average linkage with Euclidean affinity; spectral clustering uses a nearest-neighbor affinity. Every randomized baseline takes the seed as its random state.
11. **Cross-fitted construction.** The cross-fitted column of Table~\ref{tab:perseed} uses the recording as its unit. Thirty recordings are first balanced per source, then within each source twenty are assigned to training and ten to the held-out fold, giving sixty training and thirty unseen recordings. The scaler and a $K=3$ K-means are fitted on the training recordings only, and the frozen centers assign the unseen recordings by nearest centroid; the fold ARI is computed between those assignments and the true source labels. No held-out recording enters any fitted object.
12. **Seeds, versions, and call parameters.** The six balanced seeds are the integers $0$ through $5$ and fix both the recording composition and every randomized fit. The processing runs on Python 3.10.12 with NumPy, scikit-learn 1.7.2, SciPy, and MNE 1.12.1; the complete call arguments, random states, and the scripts that generate each table and figure are released in the public code repository, so no parameter is left to be inferred.

## 7.14 Summary

The real-data evidence supports one narrow statement and marks its limits. Under a known $K$ and a balanced design, source-associated covariance structure is recoverable across three independent sources, and the conclusion survives subject-level resampling. The blind selector under-counts, the unbalanced plug-in is weak, and within-source recovery is absent, all reported as boundary checks. The recovered object is the dataset-level technical structure defined in Section 7.1, and the ARI figures are not validation of the theorem.
