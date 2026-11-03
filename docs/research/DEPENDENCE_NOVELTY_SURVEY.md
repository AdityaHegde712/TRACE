# Dependence and Correlated-Failure Novelty Survey

**Date:** 2026-10-27, rewritten 2026-10-28 after eight adversarial review rounds
**Status:** Eight independent adversarial review rounds run; rounds 1-8 closed. Round 4's findings are incorporated below, including one finding this survey rejected with evidence. Round 2 returned NEEDS REVISION on the previous version; its blocking findings are incorporated below and recorded in "What the adversarial reviews caught". Not owner- or advisor-approved. Does not alter AD-001 through AD-004.

## Method

Primary-source retrieval with verbatim quotation. Every quotation was verified against a locally retained plain-text copy of its source using `.agents/skills/research/scripts/validate_quote.py`. **Two exceptions, disclosed:** two Gottschalk quotations fail that validator because the PDF extract collapses whitespace; both were verified by direct inspection of the retained text instead. The validator is a necessary check, not a sufficient one — round 2 found a quotation whose halves each validated while the splice reversed the meaning. Claims directly asserted by a source are separated from inferences derived here. PDF quotations had line-break hyphenation, whitespace and ligatures normalized; no wording was altered. Where a PDF extraction splits a token (the RCP-Bench extract renders CAV as "CA V"), the quotation shows the repair in brackets rather than propagating the artifact.

**A caution the second review established, recorded because it generalizes.** String validation is necessary and not sufficient. The previous version contained a quotation whose two halves each validated individually but which spliced across a semantic boundary, silently changing the subject of the sentence. Quotations spanning an ellipsis must be checked against unbroken source context, not only matched as strings.

Three phases:

1. **Gated (2026-10-27).** Sources restricted to two years. Reviewed adversarially; NEEDS REVISION with five blocking issues; four re-verified and corrected.
2. **Ungated (2026-10-28).** Recency gate removed. It was a search budget, not a novelty boundary, and was concealing the foundational literature.
3. **Round-2 review and rewrite (2026-10-28).** The expanded survey was independently reviewed again. It found a spliced quotation on the single most load-bearing citation, a mislabeled retrieval, an incorrect exclusion ground, and an entire literature the survey had missed. All are corrected here.

## Search protocol

Recorded so a reviewer can reproduce or challenge coverage. This is a documented protocol, **not** a PRISMA systematic review: no second independent screener, no per-database inclusion ledger.

**Databases:** general web index and arXiv, with publisher sites (ACM DL, IEEE Xplore, Springer, ScienceDirect, PMLR, NeurIPS, CVF, VLDB, ISIF) reached directly when a result named a specific work.

**Inclusion:** a work is included if it (a) estimates or models dependence, correlation or copying between information sources, (b) fuses information under unknown or partial inter-source correlation, (c) evaluates multi-agent collaboration on downstream task outcomes rather than per-item accuracy, or (d) names correlated failure in a multi-agent perception setting.

**Exclusion:** single-source estimation; multi-sensor fusion on one platform; collaboration work with no treatment of inter-source relationship; secondary summaries and unattributed aggregators.

**Queries run (33, across five search activities):** the 27 below, plus 2 venue-targeted queries (recorded under the venue sweep) and 4 dependability queries run for L8 - *common cause failure beta factor model redundant channels IEC 61508*; *SOTIF redundancy analysis correlated perception failure autonomous vehicle*; *common cause failure analysis perception redundancy deep learning diverse sensors joint failure probability*; *Marshall-Olkin shock model common cause failure correlated redundant components*. The citation-graph sweep is the fifth activity and is API-driven rather than query-driven. 27 in the three phases below, plus two venue-targeted queries recorded under the venue sweep.

| Phase | Queries |
| --- | --- |
| Gated | data incest distributed data fusion correlated estimates survey; online correlation estimation unknown cross-covariance distributed sensor fusion; subjective logic dependent opinions fusion correlated evidence; multi-agent LLM conflicting evidence resolution task decision benchmark; covariance intersection learning correlation partial knowledge conservatism; multi-robot perception correlated failure modes shared viewpoint redundant detections; KC-Bench knowledge conflicts LLM agents verify evidence before acting; IFNet data-driven multisensor estimate fusion unknown correlation; estimating source dependence from discrete categorical reports truth discovery |
| Constraint-3 and framing A | ROBOSAC Among Us adversarially robust collaborative perception consensus; closed-loop evaluation collaborative perception downstream planning driving outcomes not detection AP; V2X misbehavior detection correlated colluding sources inter-source dependence trust; multi-agent debate LLM correlated errors echo chamber diversity downstream accuracy; Cyber-Resilient V2X Cooperative Perception Dependency-Aware Fusion; benchmark metric collaborative perception worse than single agent negative collaboration; measuring redundancy diversity complementarity metric multi-agent collaborative perception; correlated failures homogeneous agents shared blind spot benchmark evaluation; when does collaboration hurt multi-robot perception negative transfer failure correlation metric |
| Ungated and round-2 follow-up | Dong Berti-Equille Srivastava truth discovery copying detection source dependence VLDB 2009; track-to-track fusion unknown correlation Chong Mori Bar-Shalom common process noise; correlated annotators crowdsourcing label aggregation dependent workers no gold standard; covariance intersection Julier Uhlmann 1997 unknown cross-correlation; TruPercept trust modelling autonomous vehicle cooperative perception; Gamerdinger robust local cooperative perception varying environmental conditions; Kuncheva Whitaker measures of diversity classifier ensembles double-fault; Lyu redundancy mitigation vehicular cooperative perception; Knight Leveson independence multiversion programming |

**Backward citation chasing:** C1's reference [20] (Yao et al. 2018); and the bibliography of General Collaborative Intelligence, which required retrieving its PDF because the HTML omitted the reference list entirely — yielding [96] ROBOSAC, [106] Krum, [107] TruPercept, [108] Gamerdinger, and, after the second review, **[12] Lyu et al.**, a redundancy survey in the target domain that the first pass missed.

**Retrieval outcome:** 50 works screened. **36 retrieved in full and searched directly**, 10 dispositioned from abstract or publisher record, 4 cited from within a retrieved paper. A further 2 works are cited for context only. A further 2 works are cited for context only and are excluded from the screened count (see Bibliography).

**Retrieval failures, recorded not hidden:** one remains — OpenCDA-∞ (OpenReview PDF endpoint). Two earlier failures were recovered on a second attempt: Estornell & Liu via the NeurIPS 2024 proceedings (now [R]), and Knight & Leveson 1986 only partially: the retained artifact is a third-party student critique that reproduces the paper's abstract verbatim. The abstract quotation validates against it, but the artifact is a secondary summary of the kind this protocol's exclusion criteria otherwise bar, and the IEEE record was not obtained. Marked [A, abstract verified via secondary source]. No verdict rests on OpenCDA-∞.

**Venue-targeted sweep (added 2026-10-28, closing a gap this protocol previously named).** Two further queries targeted CoRL, ICRA, IROS and RSS for correlated failure, shared blind spots and agent-disagreement metrics in multi-robot perception. **No venue paper matching the combination was found.** The sweep did surface two works now dispositioned below: CoDS (inter-agent feature variance in collaborative perception) and *Smart Alone, Blind Together* (an effective-redundancy treatment of correlated errors, in LLM theory-of-mind rather than perception). Neither closes the gap; both narrow it, and both are recorded.

**Citation-graph sweep — attempted three times, and it does not close this gap.**

| Version | Screen | Seeds rejected by its own screen | Verdict |
| --- | --- | --- | --- |
| v1 | Title-level, all three axes required | 2 of 6 (Gottschalk; *Smart Alone, Blind Together*) | Invalid for absence |
| v2 | Title-level, two axes + correlation mandatory | **3 of 7** (GCI; GLST; maritime) | Invalid for absence — worse than v1 |
| v3 | Abstract-level, exact screen asserted over every seed | Gate aborted: Semantic Scholar rate-limiting prevented metadata retrieval for 5 of 8 seeds | Could not be calibrated |

v2 was presented in an earlier draft as "gated by an assertion that every seed title survives it". **That was false.** The assertion covered 3 of 7 seed titles and tested a weaker condition (two axes) than the screen actually applied to candidates (two axes **and** mandatory correlation). Round 7 caught it. Under the real screen, v2 rejects General Collaborative Intelligence — which round 2 called the single most load-bearing citation — and the maritime system, called here the closest system-level counterexample.

**The honest position, stated plainly.** Title-level screening cannot do this job: GCI, GLST and the maritime paper are seeds because of their content, not their words. Abstract-level screening would work but could not be calibrated here under API rate limits. **The citation-graph gap is therefore NOT closed**, and no absence claim in this survey rests on any sweep.

**What the sweeps are still good for.** A screen with poor recall can still return true positives; it is only absence claims it cannot support. v1 screened 168 records and returned none. v2 screened 237 records over 7 seeds with 0 call failures and returned 13 candidates: 7 were the V2X *communication*-redundancy cluster carrying the same disposition as Lyu et al.; 3 were retrieved and are dispositioned above (Agent Behavioral Contracts II in L5; A Unified Theory of Diversity and EnsembleBench in L7); 2 were consensus-theory and swarm-Byzantine work outside the inclusion criteria; and 1 — *Deep Neural Network Ensembles Against Deception* (arXiv:1908.11091) — is an ensemble-diversity paper in L7 that an earlier draft miscategorised as consensus work. It has since been **retrieved in full** and is dispositioned in L7 below.

That one real omission, surfaced by a screen too narrow to certify anything, is the best evidence both for the method and against over-reading it.

**Peer-review status is not recorded per entry, and several 2026 arXiv preprints carry heavy weight.** The #2 falsifier, Agent Behavioral Contracts II, is an unrefereed preprint from independent researchers. *Smart Alone, Blind Together*, GLST and the maritime system are likewise preprints. Their claims were verified against their own text, which establishes what they say, not that it has been refereed. An advisor should weight them accordingly.

**Named coverage gaps that remain.** English-language only. No Scopus or Web of Science sweep; the citation-graph pass used Semantic Scholar only. No second screener, so inclusion decisions are single-rater. Backward chasing was applied systematically to **two** reference lists: General Collaborative Intelligence (yielding ROBOSAC, Krum, TruPercept, Gamerdinger, Lyu) and GLST (yielding MADE, LUCIA, and the GCP / CP-Guard / CoDynTrust line). Recall is lower for L1, L3 and L7, which are adjacent rather than central.

**The eighth literature has now been searched.** Dependability and common-cause failure analysis (IEC 61508 beta-factor, shock models, SOTIF redundancy) was named as unsearched in an earlier version and identified as the most likely counterexample location. It was searched after round 5. It produced no counterexample but did produce the closest prior work in perception (Gottschalk et al. 2021), which narrows Claim 2 and is dispositioned in L8. These are limits of a one-person bounded search, stated so a reader can discount accordingly.

## Claims under test

**Claim 1 (framing B — withdrawn).** Online estimation of inter-source dependence from claim streams alone, scored on task-lifecycle correctness rather than estimation error.

**Claim 2 (framing A — active), stated at the strength the evidence supports:**

> No retrieved source computes a between-agent error-correlation statistic over **perceptual detections of a shared physical scene** and regresses it against **task-lifecycle outcomes**. The statistic already exists (Kuncheva & Whitaker 2003). The statistic-to-outcome regression in multi-agent teams already exists (*Smart Alone, Blind Together* 2026; *Harnessing Disagreement* 2026). Inter-agent agreement statistics already exist in the target domain, used for adversary detection (GLST, CoDS, LUCIA, MADE). **Error correlation between redundant perception networks has been measured** (Gottschalk et al. 2021), on same-input classification by networks on one platform, scored against test-data requirements. The contribution is the **perception-domain instantiation with scene-side correlation channels that can be swept with the predictors held fixed**, plus the characterization of where the independence assumption stops paying.

**The domain qualifier does all the work here, and that is stated deliberately.** Two earlier versions overstated this claim: the first asserted correlated failure was "unmeasured" and attributed that to a source that does not say it; the second implied the statistic-to-outcome regression was unoccupied, when it is occupied in non-perception settings. Both were caught by independent review, not by self-check.

## The eight literatures

Dependence between information sources is at least eight fields that developed largely independently and rarely cite one another.

### L1. Distributed estimation and track fusion

| Work | Establishes | Bearing |
| --- | --- | --- |
| Julier & Uhlmann, ACC 1997 **[A]** | Covariance Intersection: consistent fusion without knowing cross-correlation | Founds the field. **Bounds** correlation rather than estimating it. |
| Bar-Shalom & Campo 1986 **[C]**; Chong, Chang, Mori & Barker, FUSION 1999 **[R]** | Correlated estimation errors arise from common process noise. Chong: "This occurs even when fusion is between sensor tracks not sharing common measurements." | Correlated error is **structural**, not only a copying artifact. |
| Revisiting Split Covariance Intersection, arXiv:2501.07915 **[R]** | "In distributed or cooperative systems, the cross-covariance terms cannot be computed, and to avoid underestimating the estimation error, conservative fusions must be performed." "This paper extends SCI to also take advantage of the correlated components." | Active field. Presumes partial *structural knowledge* of correlation. |
| Overlapping CI **[R]**; DIFNet **[R]** | Partial structural knowledge; learned handling of unknown noise correlation | Consulted; same disposition. |

**Disposition: dependence-aware fusion is thoroughly occupied.** Operates on estimators carrying covariance; scores estimation error, never discrete task outcomes.

### L2. Database truth discovery

| Work | Establishes | Bearing |
| --- | --- | --- |
| **Dong, Berti-Équille & Srivastava, PVLDB 2009 (dynamic world) [R]** | "a Hidden Markov Model that decides whether a source is a copier of another source and identifies the specific moments at which it copies"; "We model the quality of sources over time by their coverage, exactness and freshness" | **Decisive against Claim 1.** HMM-based time-varying dependence estimation from categorical claim streams, no ground truth, in 2009. |
| Dong et al., PVLDB 2009 (source dependence) **[A]** | Bayesian dependence analysis; iterative dependence detection and truth discovery | Static-world companion. |
| Dong et al., VLDB 2010 (global detection) **[R]** | A two-step method: "the first step locally decides possibility of copying" and "the second step globally identifies co-copying". It *critiques* the earlier pairwise approach, which "makes pairwise decisions based on common mistakes made by the sources", with the concession that "Such techniques can detect source dependence and improve truth discovery, but may generate inaccurate copying relationships in the presence of complex copying" - a caveat applying to both the 2009 papers, not to entry 8 alone. | **Correction.** An earlier version of this row attributed the "common mistakes" phrasing to this paper. That sentence describes the 2009 static-data method (entry 8) and is this paper's criticism of it. Co-copying from a common source is the structural analogue of a shared blind spot in the database setting. Reinforces Claim 1's withdrawal. |
| Pochampally et al., SIGMOD 2014 **[R]** | "correlation between sources can be much broader than copying" | Generalizes dependence past copying. |
| Yao et al., SIAM ICDM 2018 **[C]** | Online truth discovery over time series | The *online* half is 2018 work. |
| Zhang et al., IEEE TKDE 38(1) 2026 **[R]** | "One of the key challenges centers on measuring the dynamic dependence among sources" | Modern descendant, not origin. Viterbi over a complete sequence. |

**Disposition: Claim 1's estimator is occupied by a seventeen-year lineage.** Scored on truth-discovery accuracy. No actions, costs or lifecycle; not embodied or visual.

### L3. Crowdsourcing and label aggregation

| Work | Establishes | Bearing |
| --- | --- | --- |
| Li, Rubinstein & Cohn, ICML 2019 (EBCC) **[R]** | Models under-model "worker correlations observed in practical settings"; EBCC avoids "intractable marginalisation of missing labels and poor scaling to large worker cohorts" | Inter-worker correlation estimated with no gold standard. |
| Kim & Ghahramani 2012 (dBCC) **[R]** | Prior methods assume "individual classifiers are independent, which is often unrealistic and results in limited performance" | The independence assumption named and relaxed. |
| LKAAR, Neurocomputing 2021 **[A]** | Inter-annotator dependence with input-dependent labeler behaviour | Same disposition. |

**Disposition: occupied.** Scores label accuracy; no actions, costs or lifecycle.

### L4. Collaborative perception — the target domain

| Work | Establishes | Bearing |
| --- | --- | --- |
| **General Collaborative Intelligence, arXiv:2609.22967 [R]** | States that "Systematic study of these failure modes, and of the conditions under which they dominate, remains an open research need" - a sentence covering four failure modes jointly, correlated failure among them. Names correlated failure: "homogeneous agents with identical perception models and similar viewpoints are susceptible to correlated failures, where all agents miss the same occluded entity; collaboration does not help when the collective shares a common blind spot." Also **proposes GCI-Bench**, "a five-pillar scoring protocol with a maturity model", and assigns the correlated-failure case to a named synergy condition. | **Both support and threat.** It names the failure mode and already places it inside an evaluation framework. Defused by its own admissions: its pillars "RS and SC can only be estimated illustratively and TW is unreported for every method", and its badge assignments "remain author judgments and have not been independently re-labeled". GCI-Bench is a proposal, not an executed instrument, and **no pillar measures inter-agent failure correlation**. |
| ROBOSAC, ICCV 2023 **[R]** | RANSAC-style sampling of teammate subsets for a consensus set excluding adversaries | **Zero** occurrences of "correlat"; its single "independent" is arXiv page furniture (verified). Assumes attackers are a minority. Reports detection performance. |
| GLST, arXiv:2607.23059 **[R]** | Computes a **pairwise inter-agent distance matrix** across collaborators, and observes that colluding attackers "may form a pseudo-consensus in the feature space" | **Prior art for inter-agent agreement statistics in this domain.** Excluded only because it measures agreement in *feature space to identify adversaries*, not correlation of *detection errors*, and scores AP rather than lifecycle outcomes. A previous version excluded it for scoring against ego references; that was wrong — only its structural branch is ego-referenced. |
| TruPercept, IEEE IV 2020 **[R]** | The source defines the field - "Trust modelling is a field of study which aims to identify untrustworthy agents by evaluating the consistency of received information" - and reports up to +5% AP for its method | **Per-source** trust, not inter-source correlation. Scored on AP. |
| Decentralized Multi-Robot Obstacle Detection, arXiv:2602.12012v2 **[R]** | Conservative CI fusion "under unknown cross-correlations"; information-driven allocator; EKF track management; assign/reassign with "a stickiness reward ... to reduce assignment chattering"; scored on "perfect identity continuity with low fragmentation" | **Closest system-level counterexample.** Has the visual setting, a lifecycle, *and* lifecycle-correctness scoring. Excluded on one ground only: it **bounds** correlation via CI and never estimates it. |
| **RCP-Bench, CVPR 2025 [R]** | Defines "three interference scenarios: Global, Ego, and CA[V] Interference", and reports that "perception models are particularly vulnerable to Global Interference" - the regime in which ego and collaborating vehicles degrade together | **Closer than the previous version admitted.** It already varies *which* agents degrade, including a joint regime — the mechanism of correlated failure. It does not define a correlation statistic nor relate correlation strength to outcomes; it compares binary regimes and reports AP-family metrics. |
| Gamerdinger et al., Springer 2024 **[R]** |\1| **Correction (round 8).** An earlier draft moved this entry out of the screened ledger on the stated ground of "zero occurrences of ... cooperative perception". That count was **false**: the retained text contains 58 occurrences, and the phrase is in the paper's title. The entry is restored. It is excluded from Claim 2 on a ground that survives checking: **it computes no between-agent statistic of any kind**. This survey twice rejected reviewer findings for exactly this error class; this one was its own. |
| Krum, NeurIPS 2017 *(context citation, not screened)* | Byzantine-tolerant aggregation under adversarial minorities | Robustness to outliers, not measurement of dependence. Carries no verdict. |
| STAMP, arXiv:2501.18616 **[R]** | "a bottleneck effect, where a weaker agent constrains the overall system performance" | Case observation, not a measure. Correctly **not** conflated with correlated failure. |
| **CoDS, arXiv:2608.14085, 2026 [R]** | Computes inter-agent feature variance as a consistency signal: "Higher variance indicates greater feature disagreement among agents, signaling potential spatial misalignment" | Excluded for the same reason as GLST: it detects *spatial misalignment*, contains **zero** occurrences of "correlat", and never relates agreement to error correlation or to lifecycle outcomes. |
| **MADE, arXiv:2310.11901 [R]**; LUCIA (USENIX Security 2025) **[C]**; and the GCP / CP-Guard / CoDynTrust line **[A]** | A whole subfamily of inter-agent consistency methods. MADE pairs "a match loss statistic and a collaborative reconstruction loss statistic ... both based on the consistency between the agent to be inspected and the ego agent", under a double-hypothesis test with Benjamini-Hochberg control. LUCIA "assigns soft trust weights based on pairwise feature distances among agents" (as described by GLST; LUCIA itself was not retrieved). | **Surfaced from GLST's own related work, which this survey held but had not chased.** Together with GLST and CoDS they establish that pairwise inter-agent consistency statistics are **routine** in this domain, not rare. All are adversary-detection methods scored on detection metrics: MADE has **zero** occurrences of "correlat" and **zero** of "lifecycle", against 13 uses of "AP" and 4 of "average precision". None measures correlation of detection *errors*, and none regresses it on task outcomes. |
| **Lyu et al., arXiv:2501.01200, 2025 [R]** | Survey of redundancy mitigation for vehicular collective perception under ETSI TR 103 562 / TS 103 324 | **Checked because it was the most dangerous missed lead.** Its "redundancy" is *communication* redundancy — "redundant information transmission challenges collective perception systems and creates a high traffic load on the vehicular network". 21 mentions of bandwidth, 102 of communication, **zero** of "failure" or "blind spot". A different sense of the word. Claim 2 survives it. |

### L5. Multi-agent language models

| Work | Establishes | Bearing |
| --- | --- | --- |
| Estornell & Liu, NeurIPS 2024 **[R]** | "similar model capabilities, or similar model responses, can result in static debate dynamics where the debate procedure simply converges to the majority opinion" | **Recovered after an initial retrieval failure.** Establishes the downstream claim formally: correlated capability collapses debate onto the majority. |
| *Smart Alone, Blind Together*, arXiv:2610.19051 **[R]** | Defines an effective-redundancy statistic for observers whose errors correlate, measures "the three observers of a teammate" being "all wrong together far more often than independence allows: 4.7 to 18.6 times for the Claude models", and frames its own aim as "we ask what agreement does to a team that acts on its beliefs" | **Surfaced by the venue sweep and the nearest conceptual analogue to Claim 2's instrument.** Excluded from L4 on inspection: zero occurrences of "visual" or "perception", one of "robot", seventeen of "theory of mind". It is LLM coordination, not perception. |
| Harnessing Disagreement, arXiv:2607.19899 **[R]** | 3.53× joint error inflation (BCa CI [3.50, 3.59]); 57.2% of errors under agreement | **Nearest analogue to Claim 2's instrument.** Network intrusion detection and clinical tabular data, Random Forest and k-NN. Indicators, not a released benchmark. |
| KC-Bench, arXiv:2609.03588 **[R]** | Scores whether agents reconcile conflicts before acting | Full paper: **zero** "correlat", **zero** "collud". No dependence axis. |
| **Agent Behavioral Contracts II, arXiv:2608.12895, 2026 [R]** | Tests the conditional-independence assumption underlying compositional reliability bounds for multi-agent systems - "a step licensed by a conditional-independence assumption that is routinely stated and rarely tested" - in "a preregistered confirmatory evaluation of 18,000 missions". Two instances of one model in a two-agent handoff "co-fail on 90.0% of the missions on which either fails (log OR = 6.66, 95% CI[6.38, 7.00]; phi = 0.916)", and substituting a different model significantly reduces the association. | **Found by the calibrated citation sweep; the three-axis screen had missed it.** It is a second instance of Claim 2's full conjunction outside perception, and on the outcome side it is stronger than *Smart Alone, Blind Together*: mission-level success, 18,000 trials, preregistered. **Zero** occurrences of "percept", "visual", "camera" or "lidar". It makes the domain qualifier carry even more weight, and it belongs in the falsifier list. |
| CooperBench **[A]**; MoltBook **[R]** | Agent teams underperform individuals | Collaboration deficits quantified; no dependence axis. |

### L6. Closed-loop evaluation

| Work | Establishes | Bearing |
| --- | --- | --- |
| OpenCDA-∞ **[A]** | Closed-loop evaluation by planning performance | "Score on consequence" is **occupied** in driving. |
| MDrive, arXiv:2605.10904 **[R]** | Open-loop metrics "correlate weakly with closed-loop performance" | Four "correlat" uses, all metric-to-metric; **zero** "redundan". No inter-source dependence. |
| V2XBench / AURORA **[R]** | CARLA-based closed-loop V2X platform | Same disposition. |

### L7. Classifier-ensemble diversity — missed by both earlier passes

The second review identified this literature. It is the most damaging to Claim 2's original framing and the most important addition here.

| Work | Establishes | Bearing |
| --- | --- | --- |
| **Kuncheva & Whitaker, *Machine Learning* 51(2), 2003 [R]** | Ten diversity measures studied against ensemble accuracy, including the **double-fault measure**: "It is defined as the proportion of the cases that have been misclassified by both classifiers" | **Claim 2's statistic already exists and is 23 years old.** The survey can no longer claim to construct a new measurement. |
| Giacinto & Roli 2001 **[C]** | Used double-fault "to form a pairwise diversity matrix for a classifier pool and subsequently to select classifiers that are least related" | Pairwise joint-error matrices over a predictor pool, in 2001. |
| **Wood, Mu & Brown, "A Unified Theory of Diversity in Ensemble Learning", arXiv:2301.03962 [R]** | Proves "a family of exact bias-variance-diversity decompositions", showing "diversity is in fact a hidden dimension in the bias-variance decomposition of the ensemble loss" | The modern successor to the diversity-measure literature Kuncheva & Whitaker surveyed. Confirms the L7 disposition rather than disturbing it: still same-input supervised learning, zero multi-agent and zero perception content. |
| EnsembleBench, arXiv:2010.10623 **[R]** | A benchmark for ensemble diversity metrics | A *benchmark* for diversity measures already exists, in the ensemble setting. Reinforces that Claim 2 cannot rest on building a diversity benchmark as such; only on the perception-domain instantiation. |
| Liu, Wei, Chow et al., "Deep Neural Network Ensembles against Deception: Ensemble Diversity, Accuracy and Robustness", arXiv:1908.11091 **[R]** | Relates diversity to ensemble accuracy directly: "Diversity is greater when the errors of the ensemble prediction is more uniformly distributed. Greater diversity is highly correlated with the increase in ensemble accuracy." | **Surfaced by sweep v2, miscategorised in an earlier draft, now retrieved.** Same disposition as the rest of L7: **zero** occurrences of "multi-agent", "percept", or any of "downstream"/"mission"/"lifecycle" against 29 of "correlat". Single-platform ensembles scored on prediction accuracy. |
| Knight & Leveson 1986 **[A, abstract verified via secondary source]**; Eckhardt & Lee 1985 **[A]** | N-version programming "depends for its reliability improvement on the assumption that programs that have been developed independently will fail independently" — an assumption the experiment rejects | **Ancestor of the whole question**, and the closest historical precedent for this project's framing: an empirical test of an independence assumption that a system's correctness rested on. Abstract verified; full paper not retrieved. |

**Disposition: the measurement is occupied; the domain is not.** Ensemble diversity varies inputs only by varying predictor construction - which features, which training subset - while the item set stays fixed and given. Multi-agent perception agents see **different views of the same scene**, so correlation is mediated by viewpoint overlap, shared occluders and shared weather. The statistic ports; its drivers do not.

### L8. Dependability and common-cause failure — searched after round 5 named it as the likely counterexample location

The previous version listed this field as **unsearched** and as "the most likely place for a counterexample". It has now been searched. It did not produce a counterexample, but it produced the **closest prior work in perception** and narrows Claim 2 a third time.

| Work | Establishes | Bearing |
| --- | --- | --- |
| **Gottschalk, Rottmann & Saltagic, arXiv:2112.04758 [R]** | Measures correlated errors between redundant perception networks, concluding independence "cannot be taken simply for granted, even if different sources of data are employed". 89 occurrences of "correlat", 59 of "independen". Crucially, its 3D-MNIST experiments create "5 rotated variants of the dataset" and each of five networks "obtains one of the 5 rotated variants" - **different input per network, viewpoint as an actuated knob, architectures identical** (the trained predictors differ by training distribution, which makes this the same move as Kuncheva's feature-subset sweep rather than a distinct one) - and it regresses the measured correlation against **k-out-of-5 voter accuracy**. | **The closest prior work in perception, and closer than two earlier versions of this row admitted.** Those versions excluded it for using the same input per network and for not having agents viewing a shared scene from different poses. **Both grounds are false** for the 3D-MNIST half and were withdrawn in round 6. What separates it, and is now the whole separation: **one platform, not distributed agents**; **synthetic rotations of a toy dataset**, not a real scene with separately actuable occlusion, weather and viewpoint; and **voter accuracy**, a perception metric, rather than task-lifecycle outcomes (zero occurrences of "downstream" or "planning"; all seven uses of "task" denote the perception task itself). |
| IEC 61508 beta-factor model; alpha-factor, multiple Greek letter, binomial failure rate **[A]** | The beta factor is the fraction of a channel's failures that are common-cause, and feeds directly into system-level failure probability for redundant channels | **The conjunction exists here in principle**: a between-channel correlation parameter related to system outcome probability. But beta is an *engineering input parameter*, estimated from field data or standards tables, not a quantity measured from the channels' own outputs; and the channels are hardware, not perceptual observers of a scene. |
| Marshall-Olkin and multivariate shock models (Kvam; Mercier & Pham; Kozyrev et al.) **[A]** | Models where one external shock fails two or more components simultaneously, fitted to field data such as emergency diesel generators | The formal model of a shared external cause — the mathematical ancestor of a shared occluder. Hardware reliability, no perception, no task lifecycle. |
| "Safety Integrity Framework for Automated Driving", arXiv:2503.20544 **[R]** | Models a 2-out-of-3 voter over camera, lidar and radar and states: "assume statistical independence of the failures in this first analysis" | **Assumes exactly what this project proposes to measure**, in the target domain, in a safety-integrity calculation. Useful evidence that the assumption is load-bearing and unmeasured in practice. |
| "Towards Identifying and closing Gaps in Assurance of autonomous Road vehicleS", arXiv:2003.00790 **[R]** | Argues that the effectiveness of design diversity turns on "failure correlation between the two channels", illustrated with a stereo-camera / LIDAR pair | Names the quantity and its importance for a perception channel pair; does not measure it. |

**Disposition: the conjunction's components are all present in this field, and the combination still is not.** Common-cause analysis has a between-channel correlation parameter tied to system outcome (beta), and the perception corner of the field measures error correlation between redundant networks. What none of them does is measure correlation between **agents observing a shared scene from different poses**, with the correlation driven by **scene-side channels that can be swept**, regressed against **task-lifecycle outcomes** rather than against test-data volume or a safety-integrity number.

## Why this intersection is not arbitrary

A conjunction of properties is unoccupied for almost any arbitrary triple, so the gap needs a reason to be interesting rather than merely empty.

**An earlier version of this section argued the wrong thing, and was refuted by this survey's own sources.** It claimed that every literature already measuring between-source error correlation assumes sources observe *identical input*. That is false:

- Kuncheva & Whitaker use "different subsets of features for each of L = 3 classifiers", building "14700 teams by enumerating all possible partitions of the 10 features into three subsets", then relate the resulting diversity to accuracy. Different inputs, and a configuration sweep: structurally the same move this section had claimed was unique to perception.
- Pochampally et al. state that "extractors may focus on different types of information" and "may apply common rules in extraction (positive correlation, without copying)". Different inputs, plus a shared-tooling channel that is the direct analogue of a shared detector version.
- In the N-version literature, coincident failure is attributed to inputs differing in difficulty: a property of the item rather than of the predictors, and the formal analogue of a shared occluder. **Routing disclosed:** this characterization is taken from *Smart Alone, Blind Together*, which states that versions "fail together because inputs differ in difficulty [15]", citing Eckhardt & Lee. Eckhardt & Lee was not retrieved.

Only Knight & Leveson, where 27 programs ran the same test cases, fits the identical-input description. One case does not support "every literature".

**The distinction that does survive is narrower, and round 4 had to repair it too.** An intermediate version said correlation in those literatures is *observed* rather than *set*. That is also false: Kuncheva & Whitaker enumerate 14700 team configurations, Giacinto & Roli *select* least-related classifiers, and the N-version literature deliberately forces diversity.

**This argument has now failed four times, and the fourth failure came from the source added to answer the third.** Earlier versions claimed, in turn: that every such literature uses identical input (false — Kuncheva sweeps feature subsets); that correlation there is *observed* rather than *set* (false — Kuncheva enumerates 14700 configurations); and that correlation is reached only by writing it into synthetic outputs or by changing the predictors (false — Gottschalk rotates a shared 3D object and hands each of five networks a different view, with the networks held identical, and RCP-Bench actuates shared weather across chosen agents).

**What survives is embodiment alone. The separability half did not survive either.** Agent Behavioral Contracts II, added in the same draft that made the separability argument, manipulates a sharing condition across three graph topologies inside one preregistered campaign and regresses it against mission outcomes via a co-failure contingency table. The channel it sweeps — shared model — is the direct analogue of this project's own "shared detector model version". So *which channel drives the statistic* is already answerable on the predictor side, not merely askable.

**Embodiment is not itself unoccupied either, and this is the argument's sixth narrowing.** Four retrieved sources have correlation channels with physical referents in a shared scene: RCP-Bench crosses External Weather with Global / Ego / CAV interference across distributed vehicles; the maritime system names its channels outright - "unknown cross-correlations due to shared priors, overlapping observations, common process models, and information relaying"; Gamerdinger simulates adverse weather for cooperative perception; and the assurance-gaps notes name failure correlation between a camera/LIDAR pair on a test vehicle. An earlier draft claimed embodiment as a standalone absence while conceding RCP-Bench's weather actuation four lines above. That was incoherent.

**What no retrieved work does is the conjunction.** Of the works that *measure* between-source error correlation, none has distributed agents in a shared scene. Of the works with distributed agents in a shared scene, none *measures* correlation - they bound it (maritime, via covariance intersection), assume it away (safety-integrity), or vary degradation without quantifying its covariation (RCP-Bench). The gap is a conjunction, not a property, and every attempt to restate it as a property has failed.

**This argument has now failed five times and been narrowed each time.** That record is kept deliberately: it is the best available evidence of how much of the claim is load-bearing and how much was decoration.

That is a materially weaker claim than the three it replaces, and it is stated at that strength deliberately.

The open question is therefore whether a between-agent error-correlation statistic, computed over embodied channels, predicts task-lifecycle error - and which channel drives it. No retrieved work answers it, because none holds both halves at once.

The channel taxonomy is not original to this survey either. The maritime multi-robot paper lists "shared priors, overlapping observations, common process models, and information relaying" as the sources of unknown cross-correlation in exactly this setting. What it does not do is measure them.

That makes the question experimental rather than observational: **which physical configuration drives the statistic, and does the statistic predict task-level error?** Answering it requires a simulator in which those channels are separable knobs, which is what this project already has a prototype for.

This is an argument, not a source claim, and it is weaker than the version it replaces. It should be read as such.

## Verdict

**Claim 1: withdrawn.** Occupied by L2 back to 2009, L1 back to 1997, L6 for its scoring framing, and L5 for its downstream finding.

**Claim 2: survives in its restated form, and only in that form.** Not claimed: that correlated failure is unmeasured (L7 measures it); that a source asserts the gap (it does not); that the metric is new (Kuncheva & Whitaker 2003). Claimed: no retrieved source relates a between-agent error-correlation statistic to task-lifecycle outcomes in collaborative visual perception, where the correlation is driven by controllable physical channels.

**Falsifier.** A source that computes an error-correlation statistic between agents over perceptual detections of a shared scene and relates it to task or track lifecycle outcomes. Nearest misses, ordered by how close they come:

1. ***Smart Alone, Blind Together*** (2026) is **the closest work in any domain.** It defines an effective-redundancy statistic, measures agents "all wrong together far more often than independence allows: 4.7 to 18.6 times for the Claude models", and states its own aim as "we ask what agreement does to a team that acts on its beliefs". Separated from Claim 2 **only by modality**: zero occurrences of "visual" or "perception"; its settings are Hanabi and task assignment.
2. **Agent Behavioral Contracts II** (2026) - the conjunction again, outside perception, and on the outcome side the strongest instance found: 18,000 preregistered missions, two agents co-failing on 90.0% of missions where either fails (phi = 0.916). Zero occurrences of "percept", "visual", "camera" or "lidar".
3. **Gottschalk, Rottmann & Saltagic** (2021) is **the closest in perception.** It measures error correlation between perception networks, actuates viewpoint by rotating a shared 3D object, and regresses the result against k-out-of-5 voter accuracy. Separated by: one platform rather than distributed agents, synthetic rotations of a toy dataset rather than a real scene with separately actuable channels, and voter accuracy rather than task-lifecycle outcomes.
4. **Harnessing Disagreement** (2026): the statistic and a downstream link, on tabular intrusion-detection and clinical data; indicators, no released benchmark.
5. **GLST / CoDS / LUCIA / MADE**: inter-agent agreement statistics in the target domain, computed over *features* for adversary detection and scored on detection metrics.
6. **RCP-Bench** (CVPR 2025): joint-degradation regimes in the target domain, but no correlation statistic.
7. **Maritime multi-robot** (2026): the visual setting, a lifecycle, and lifecycle-correctness scoring, but it *bounds* correlation rather than estimating it.

## What the adversarial reviews caught

**Round 1** — four errors corrected: a counterexample wrongly said to lack a task lifecycle; "online" asserted as a source claim when the source says "dynamic"; a survey dispositioned as supportive when it is a threat; negative claims made from an abstract page. Two quotations failed verbatim validation and were restated. A fifth finding — that the recency gate was concealing the foundational literature — prompted the ungated phase.

**Round 2** — the rewrite was rejected. Findings, all incorporated:

1. **A spliced quotation on the load-bearing citation.** The survey joined two GCI fragments across an ellipsis so that "rarely evaluated as a benchmark metric" appeared to describe correlated failure. In the source that clause describes **error propagation** and terminates before the "Correlated failures" sentence begins. Each fragment validated individually; the splice did not. Claim 2's gap statement was therefore never source-asserted, and is now stated as this survey's inference.
2. **A correction recorded but never propagated.** Round 1 found GCI was a threat; the finding was written into the meta-section and never into the argument. GCI-Bench and its synergy-condition assignment are now in the L4 table, with GCI's own admissions used to defuse them.
3. **A wrong exclusion ground for GLST**, which uses a pairwise inter-agent distance matrix, not ego references, in two of three branches.
4. **A mislabeled retrieval:** Split Covariance Intersection was marked retrieved when the retained file was a 6.6 KB arXiv landing page. It has since been retrieved in full (21 pages) and its quotations revalidated.
5. **An entire missed literature** (L7), including the metric Claim 2 proposed to construct.
6. **Quotation marks around unretrieved text** (Estornell & Liu), now removed.
7. **An internal contradiction** over which works were cited-only, plus a wrong year and author order for Chong et al.

One round-2 finding was **not** accepted: that ROBOSAC contains zero occurrences of "independent". It contains one, in arXiv page furniture, which is what the survey said. The reviewer's `grep -ci` counted matching lines rather than occurrences.


**Round 3** — nine blocking findings, all incorporated:

1. **A misattributed quotation.** The Dong 2010 row quoted a sentence describing a *different* paper (entry 8) under an "Establishes" header, and that sentence was the 2010 paper's *criticism* of it. Second error of this exact shape; the first was round 1's.
2. **A self-contradiction on the venue sweep** — declared run in the protocol, declared not-run in the limitations.
3. **The non-arbitrariness argument was false**, refuted by three of this survey's own sources (Kuncheva & Whitaker's feature-subset sweep, Pochampally's "different types of information", the N-version difficulty account). Retracted and rewritten.
4. **Claim 2 was still overstated.** *Smart Alone, Blind Together* has both halves of the conjunction and differs only by modality. It now leads the falsifier list.
5. **An in-domain coverage hole** — GLST's own related work names LUCIA and MADE, which this survey held but had not chased. Inter-agent agreement statistics turn out to be routine here, not rare.
6. **Krum mislabeled [A]** when retrieved in full.
7. **Knight & Leveson's provenance undisclosed** — the retained artifact is a third-party critique reproducing the abstract.
8. **An OCR artifact ("CA V") propagated** into two documents as if it were the source's wording.
9. **Stale counts** across the companion documents.

**Round 4** — seven blocking findings. Six were accepted and are fixed above: the retracted identical-input claim still standing in the L7 disposition; a self-refuting *observed-versus-set* formulation in the replacement argument; an incomplete bibliography after round 3's additions; a negative claim resting on [A] entries inside L4; a review-history contradiction; and a count contradiction in the proposal.

**One round-4 finding was rejected with evidence.** It held that no GCI text assigns the correlated-failure case to a named synergy condition. The sentence exists and validates: "The agents share a common blind spot or a homogeneous failure mode, so pooling reinforces a correlated error instead of disambiguating identity; this is a failure of C1." The reviewer searched for the exact phrase "correlated failure" and missed a sentence that says "correlated error". This is the second time a reviewer's negative count claim has been wrong, and it is recorded for the same reason the accepted findings are: the audit trail is only useful if it runs in both directions.


**Round 5** (narrow verification of round-4 fixes) — two blocking findings. The proposal still carried a formulation the survey had retracted the same day. And the survey's replacement argument contained a *new* over-strong universal, falsified by Kuncheva §6.1/6.3, which sets correlation directly in generated oracle outputs with "Classifier type N/A" and no predictors at all. Both fixed. The reviewer independently reproduced and confirmed the round-4 rejection.

**Round 6** (sign-off plus second screener) — eight blocking findings, all incorporated:

1. **The argument failed a fourth time**, refuted by the source added to answer the third. Gottschalk hands each of five networks a different rotation of a shared 3D object with the networks held identical; RCP-Bench actuates shared weather across chosen agents. Rewritten around embodiment and separability instead.
2. **Two of three Gottschalk exclusion grounds were false** and were withdrawn. It is closer to this work than two earlier versions of its row admitted.
3. **A third ground was incomplete**: Gottschalk regresses measured correlation against k-out-of-5 voter accuracy, which the survey had not reported while calling the paper its nearest threat.
4. **The proposal told the advisor an entire literature was unsearched** while the survey said it had been searched and had produced the closest prior work. Gottschalk appeared nowhere in the advisor-facing document.
5. **A literal regex backreference (``) was sitting in the proposal's prose** from a failed substitution.
6. **The source-retention list claimed 33 extracts and named 30**, omitting all three L8 entries.
7. **The citation sweep was misreported and over-claimed.** Its three-axis title screen rejects two of its own six seeds — including the closest prior work in perception and the closest work in any domain — so it cannot support an absence claim. Restated as "no new title-level candidates", and the citation-graph gap is explicitly **not** closed.
8. **Body tables and bibliography disagreed** on three retrieval labels, and one entry carried the wrong title.

**Round 6 also acted as the second screener** the protocol had always lacked. It agreed with the disposition of every L2, L4 and L7 entry it checked, and disagreed on four: it would exclude Gamerdinger and Krum under the stated criteria, would demote Knight & Leveson unless the IEEE record is obtained, and flags that two verdict-bearing L8 entries are [A]. Those disagreements are recorded in the limitations rather than silently resolved.


**Round 7** — eight blocking findings. The most consequential: **the search protocol contained a false statement.** Sweep v2 was described as "gated by an assertion that every seed title survives it"; the assertion covered 3 of 7 seeds and tested a weaker condition than the screen actually applied. Under the real screen v2 rejected 3 of 7 seeds, worse than the v1 it replaced. Also: a sweep candidate miscategorised as consensus work when it is ensemble-diversity work; stale v1 conclusions standing beside v2's; a 45-vs-48 ledger contradiction; counts disagreeing across documents; a stale source-retention list; the proposal omitting the survey's own #2 nearest miss; and the justification argument refuted for a fifth time by the source added to answer its fourth refutation.

**Round 8** — four blocking findings, two of them this survey's own errors of the kind it had twice rejected in reviewers:

1. **"Embodiment alone" was a sixth over-strong universal**, refuted by four retrieved sources — RCP-Bench, the maritime system, Gamerdinger and the assurance-gaps notes — and conceded four lines above itself. Restated as a conjunction, which is what the Claim 2 sentence had said correctly all along.
2. **A false zero-count, in this survey's own text.** Gamerdinger was moved out of the screened ledger on the stated ground of "zero occurrences of ... cooperative perception". The retained text contains **58**, and the phrase is in the paper's title. The entry is restored and excluded on a ground that survives.
3. A count contradiction introduced by the previous round's own fix edits.
4. This round-count contradiction and the missing Round 7 entry.

Round 8 also spot-checked roughly 30 quotations against unbroken source context, hunting the misframe pattern that rounds 2, 3 and 6 each caught, and **found none** — the first clean quotation layer in the trail.

## Explicit non-claims

- Not a new fusion operator; not an improvement on covariance intersection.
- Not a new dependence estimator; L1–L3 supply several.
- **Not a new measurement.** The double-fault statistic predates this work by more than two decades.
- Not the discovery of correlated failure; it is established in L1, L2, L3, L5 and L7.
- Not a field-first claim. Bounded retrieval, not proof of absence.

## Limitations

- **Second-screener disagreements: three accepted, one standing.** Round 6 independently applied the inclusion criteria and disagreed on four entries. **Krum is accepted as an exclusion** - 0 occurrences of "correlat"; it rejects outliers rather than modelling dependence. **Gamerdinger was accepted and then reinstated in round 8**: the ground given for excluding it was a false zero-count by this survey, and on recheck the paper is centrally about cooperative perception. It stays in the screened ledger, excluded from Claim 2 because it computes no between-agent statistic. **Knight & Leveson is demoted**: the retained artifact is a third-party critique, secondary summaries are an exclusion criterion, and the IEEE record was not obtained, so it now carries no verdict and is cited only for the lineage's existence. **One disagreement stands unresolved**: two verdict-bearing L8 entries (IEC 61508 beta-factor, shock models) are [A], which repeats a pattern round 4 blocked on. Neither standard was obtainable here, so the L8 disposition sentence rests partly on publisher records. That is a real weakness and it is left visible rather than argued away.
- **Screening criteria and disposition grounds are used interchangeably.** "Multi-sensor fusion on one platform" is listed as a screening exclusion, yet Gottschalk is included and then dispositioned away from Claim 2 on that same ground. Round 6 identified this as the clearest consequence of having had no second screener until then.
- **Bounded search, not a systematic protocol.** The venue-targeted sweep of CoRL/ICRA/IROS/RSS and a title-level citation-graph sweep over the six load-bearing papers were both run (see Search protocol) - though the citation sweep's screen is too narrow to close that gap, as it records. **Single-rater inclusion is the main structural weakness that remains**: one person applied the inclusion criteria, with no second screener.
- **Depth varies.** Every L4 entry whose exclusion this survey decides is **[R]**, except LUCIA and the GCP / CP-Guard / CoDynTrust line, which are dispositioned from GLST's description of them and are named as such rather than independently read. Krum is retrieved in full and carries no verdict either way. An earlier version claimed no verdict rested on an [A] entry outside L1 and L3; that was false while RCP-Bench and Gamerdinger were abstract-only. Both have since been retrieved.
- **Three works are cited from within other papers:** Bar-Shalom & Campo 1986, Yao et al. 2018, Giacinto & Roli 2001. **One** work could not be retrieved at all: OpenCDA-∞. Two earlier failures were recovered on a second attempt.
- **L5, L6 and L7 are adjacent domains.** Their dispositions bear on whether Claim 2's result would be novel, not on whether the perception-domain gap exists.
- The recency gate from the gated phase is **no longer in force**. Its removal changed the verdict's basis materially — evidence that recency gates are unsafe for novelty assessment.

## Bibliography

**[R]** retrieved in full and searched directly · **[A]** from abstract or publisher record · **[C]** cited from within a retrieved paper

### L1 — Distributed estimation and track fusion
1. **[A]** Julier, S. J., Uhlmann, J. K. "A non-divergent estimation algorithm in the presence of unknown correlations." *Proc. 1997 American Control Conference*, vol. 4, pp. 2369-2373. DOI 10.1109/ACC.1997.609105
2. **[C]** Bar-Shalom, Y., Campo, L. "The effect of the common process noise on the two-sensor fused-track covariance." *IEEE Trans. AES*, 1986.
3. **[R]** Chong, C.-Y., Chang, K. C., Mori, S., Barker, W. H. "Architectures and Algorithms for Track Association and Fusion." *FUSION 1999*. http://fusion.isif.org/proceedings/fusion99CD/C-134.pdf
4. **[R]** "Revisiting Split Covariance Intersection: Correlated Components and Optimality." arXiv:2501.07915, 2025.
5. **[R]** "Overlapping Covariance Intersection." arXiv:2603.16768v2, 2026.
6. **[R]** "DIFNet." arXiv:2508.18854, 2025.

### L2 — Database truth discovery
7. **[R]** Dong, X. L., Berti-Équille, L., Srivastava, D. "Truth Discovery and Copying Detection in a Dynamic World." *PVLDB* 2(1):562-573, 2009.
8. **[A]** Dong, X. L., Berti-Équille, L., Srivastava, D. "Integrating Conflicting Data: The Role of Source Dependence." *PVLDB* 2(1):550-561, 2009.
9. **[R]** Dong, X. L. et al. "Global Detection of Complex Copying Relationships Between Sources." *VLDB* 2010.
10. **[R]** Pochampally, R., Das Sarma, A., Dong, X. L., Meliou, A., Srivastava, D. "Fusing Data with Correlations." *SIGMOD* 2014. arXiv:1503.00306
11. **[C]** Yao, L. et al. "Online truth discovery on time series data." *SIAM ICDM* 2018, pp. 162-170.
12. **[R]** Zhang, H. et al. "Reliable Truth Discovery for Dynamic and Dependent Sources." *IEEE TKDE* 38(1), 2026.

### L3 — Crowdsourcing and label aggregation
13. **[R]** Li, Y., Rubinstein, B. I. P., Cohn, T. "Exploiting Worker Correlation for Label Aggregation in Crowdsourcing." *ICML* 2019.
14. **[R]** Kim, H.-C., Ghahramani, Z. "Bayesian Classifier Combination." *AISTATS* 2012.
15. **[A]** "Learning from multiple inconsistent and dependent annotators." *Neurocomputing*, 2021.

### L4 — Collaborative perception
16. **[R]** "General Collaborative Intelligence: Architecting Cognition for Resilient Multi-Agent Ecosystems." arXiv:2609.22967, 2026.
17. **[R]** Li, Y., Fang, Q., Bai, J., Chen, S., Juefei-Xu, F., Feng, C. "Among Us: Adversarially Robust Collaborative Perception by Consensus." arXiv:2303.09495v3, *ICCV* 2023.
18. **[R]** Hurl, B., Cohen, R., Czarnecki, K., Waslander, S. "TruPercept." arXiv:1909.07867, *IEEE IV* 2020.
19. **[R]** "GLST: Defending Confidence-Driven V2X Collaborative Perception." arXiv:2607.23059, 2026.
20. **[R]** "Decentralized Multi-Robot Obstacle Detection and Tracking in a Maritime Scenario." arXiv:2602.12012v2, 2026.
22. **[R]** Gamerdinger, J. et al. "Robust Local and Cooperative Perception Under Varying Environmental Conditions." Springer 2024, pp. 113-157.
23. **[R]** Du, S. et al. "RCP-Bench: Benchmarking Robustness for Collaborative Perception Under Diverse Corruptions." *CVPR* 2025.
24. **[R]** "STAMP: Scalable Task And Model-agnostic Collaborative Perception." arXiv:2501.18616, 2025.
25. **[R]** Lyu, T., Noor-A-Rahim, M., Pesch, D., O'Driscoll, A. "A Survey and Tutorial of Redundancy Mitigation for Vehicular Cooperative Perception." arXiv:2501.01200, 2025.
25a. **[R]** "CoDS: Robust Collaborative Perception via Expert-driven Detection and BEV Segmentation." arXiv:2608.14085, 2026.

25b. **[R]** Zhao, Y. et al. "Malicious Agent Detection for Robust Multi-Agent Collaborative Perception" (MADE). arXiv:2310.11901, 2023.
25c. **[C]** LUCIA. "From Threat to Trust: Exploiting Attention Mechanisms for Attacks and Defenses in Cooperative Perception." *USENIX Security* 2025. Dispositioned from GLST's description; not independently retrieved.
25d. **[A]** The GCP / CP-Guard / CP-uniGuard / CoDynTrust line of inter-agent consistency defences (arXiv:2501.02450; AAAI 2025; arXiv:2502.08169). Named as a family; individually not retrieved.

### L5 — Multi-agent language models
26. **[R]** Estornell, A., Liu, Y. "Multi-LLM Debate: Framework, Principals, and Interventions." *NeurIPS* 2024. https://proceedings.nips.cc/paper_files/paper/2024/file/32e07a110c6c6acf1afbf2bf82b614ad-Paper-Conference.pdf
26a. **[R]** "Smart Alone, Blind Together: Why Accuracy Fails to Certify Theory of Mind in Multi-Agent Teams." arXiv:2610.19051, 2026.
27. **[R]** "Harnessing Disagreement: Detecting Correlated Agreement Blindness in Multi-Agent Triage." arXiv:2607.19899, 2026.
28. **[R]** Lyu, Y. et al. "KC-Bench: A Dynamic Interactive Benchmark for Evaluating Knowledge Conflicts in LLM Agents." arXiv:2609.03588, 2026.
29. **[A]** CooperBench. https://cooperbench.com/
30. **[R]** Yee, B., Sharma, K. "MoltDynamics: Emergent Social Phenomena in Autonomous AI Agent Populations." arXiv:2603.03555, 2026.

30b. **[R]** Bhardwaj, V. P., Singh, G., Bhardwaj, A. P. "Agent Behavioral Contracts II: Certifying Compositional Reliability Without Assuming Independence." arXiv:2608.12895, 2026.

### L6 — Closed-loop evaluation
31. **[A]** "OpenCDA-∞: A Closed-loop Benchmarking Platform for Cooperative Perception." OpenReview dR2kAeiAo0. *Retrieval failed.*
32. **[R]** "MDrive: Benchmarking Closed-Loop Cooperative Driving." arXiv:2605.10904, 2026.
33. **[R]** "Roadside-Cooperative Autonomous Driving" / V2XBench-AURORA. arXiv:2608.21032, 2026.

### L7 — Classifier-ensemble diversity
34. **[R]** Kuncheva, L. I., Whitaker, C. J. "Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy." *Machine Learning* 51(2):181-207, 2003.
35. **[C]** Giacinto, G., Roli, F. "Design of effective neural network ensembles for image classification purposes." 2001. Cited by source 34 for the double-fault diversity matrix.
36. **[A, abstract verified]** Knight, J. C., Leveson, N. G. "An Experimental Evaluation of the Assumption of Independence in Multiversion Programming." *IEEE Trans. Software Engineering* 12(1):96-109, 1986.
36a. **[A]** Eckhardt, D. E., Lee, L. D. "A theoretical basis for the analysis of multiversion software subject to coincident errors." 1985.


34b. **[R]** Wood, D., Mu, T., Brown, G. "A Unified Theory of Diversity in Ensemble Learning." arXiv:2301.03962, 2023.
34c. **[R]** "Promoting High Diversity Ensemble Learning with EnsembleBench." arXiv:2010.10623, 2020.
34d. **[R]** Liu, L., Wei, W., Chow, K.-H., Loper, M., Gursoy, E., Truex, S., Wu, Y. "Deep Neural Network Ensembles against Deception: Ensemble Diversity, Accuracy and Robustness." arXiv:1908.11091, 2019.

### L8 — Dependability and common-cause failure
37. **[R]** Gottschalk, H., Rottmann, M., Saltagic, M. "Does Redundancy in AI Perception Systems Help to Test for Super-Human Automated Driving Performance?" arXiv:2112.04758, 2021.
38. **[R]** "Safety Integrity Framework for Automated Driving." arXiv:2503.20544, 2025.
39. **[R]** "Towards Identifying and closing Gaps in Assurance of autonomous Road vehicleS - a collection of Technical Notes Part 2." arXiv:2003.00790, 2020.
40. **[A]** IEC 61508-6, beta-factor model for common-cause failure in redundant channels; with alpha-factor, multiple Greek letter and binomial failure rate extensions. Standard not independently obtained.
41. **[A]** Marshall-Olkin and multivariate shock models for common-cause failure (Kvam, Los Alamos; Mercier & Pham 2016; Kozyrev, Rykov & Kolev 2018). Dispositioned from publisher records.

### Context citations — cited in the body, NOT screened as counterexample candidates

These two were in the screened ledger until round 6's second screener objected. Tested against this survey's own inclusion criteria they fail all four, and the objection is accepted. They remain cited where the body uses them, but they are **not** counted as works screened for the gap, and no verdict rests on them.

- **[R]** Blanchard et al. (Krum) remains the only context citation; see below. **Gamerdinger was restored to the screened ledger in round 8** after the ground for demoting it turned out to be a false count of this survey's own making.
- **[R]** Blanchard, P., El Mhamdi, E. M., Guerraoui, R., Stainer, J. "Machine learning with adversaries: Byzantine tolerant gradient descent." *NeurIPS* 2017. Cited as background on robust aggregation. **Zero** occurrences of "correlat": it rejects outliers, it does not model inter-source dependence.

**Count:** 50 works screened across eight literatures. **36 [R]**, 10 [A], 4 [C]. Plus 1 context citation (Krum), not screened. One retrieval failure remains (OpenCDA-infinity, attempted twice); it carries no verdict.

## Source retention

Plain-text extracts of all **36** screened [R] sources are retained locally, plus the 2 context-citation extracts (Gamerdinger, Krum), and every quotation was verified against them with the two disclosed exceptions above.

Rather than enumerate them — a list that has now gone stale twice, in rounds 6 and 7 — the retained corpus is the `sources/` directory of this session's scratchpad, where each [R] entry maps to a `.txt` extract of its full text. Files prefixed `WRONG-PAPER-` are quarantined mis-retrievals and are cited nowhere.

