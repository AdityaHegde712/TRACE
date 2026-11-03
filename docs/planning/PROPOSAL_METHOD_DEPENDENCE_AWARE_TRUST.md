# Testing and Repairing the Independence Assumption in Multi-Agent Perception Trust

**Author:** Aditya Hegde
**Advisor:** Dr. Kaikai Liu
**Date:** 2026-10-29
**Status:** Proposal for advisor review. Supersedes `PROPOSAL_CORRELATED_FAILURE.md`, which framed the same subject as a novelty gap rather than a method improvement.
**Revised:** 2026-11-03, after the one-week spike. Section 0 is the measured result; Sections 3, 4.1, 5, 6, 7, 8 and 9 were revised to match it. Where the spike contradicted an earlier prediction, the prediction is shown and marked falsified rather than quietly removed.

---

## 0. Headline result: the assumption was tested, and it failed

The one-week spike proposed in Section 8 has been run. MATE's independence
assumption does not hold in this setting.

| Measure | Value |
| --- | --- |
| Dependence inflation ratio | **1.671**, 95% bootstrap CI **[1.500, 1.870]** |
| Observed joint-error rate (double-fault) | 0.2143 |
| Rate independence predicts | 0.1282 |
| Scope | 54 CARLA 0.9.16 scenes, 448 objects visible to both agents |

A ratio of 1.0 means independent. The interval sits clear of 1.0, so the two
agents were wrong about the same object substantially more often than
independence allows.

Two follow-up experiments qualify the headline:

1. **It is not an artifact of shared object difficulty.** Both agents observe
   the same object, so an object that is small and far is hard for both, and
   that alone could produce inflation. Conditioning on apparent object size,
   inflation survives in every size tercile (1.324, 1.725, 1.782; every
   interval above 1.0).
2. **A shared detector contributes, but does not explain it.** Running a second
   detector of a different architecture (RT-DETR-L) over the same frames,
   agents sharing a detector are measurably more associated than agents running
   different ones (+0.0915 phi, paired 95% CI [+0.0466, +0.1401]). Yet
   heterogeneous agents remain strongly associated (phi 0.285, odds ratio
   roughly 4.0). The dominant shared cause is the scene itself — the same
   objects, the same geometry, the same occlusion — not the shared weights.

**This broadens the claim rather than weakening it.** The failure is not
confined to teams that deploy identical perception models. It appears between
agents running different models, which is the configuration a system designer
would reach for precisely to obtain independence. Section 3 cites a 2026 survey
naming "homogeneous agents with identical perception models" as the susceptible
case; this measurement says the susceptible case is wider than that.

Reports and the commands that generate them: `docs/spike/SPIKE_RESULT.md`,
`docs/spike/SPIKE_STRATIFIED_ANALYSIS.md`, `docs/spike/SPIKE_CONTRAST_CONDITION.md`.

**Limits of this measurement**, carried forward rather than resolved: one town,
one frame per scene, one IoU threshold, and two detectors that are both
COCO-pretrained on overlapping data, so "different model" here is not
"independently trained on disjoint data". The spike establishes that the effect
is real and worth building on. It does not fully isolate the mechanism.

---

## 1. What changed, and why

An earlier version of this proposal asked whether anyone had measured correlated failure between perception agents. Eight rounds of adversarial literature review answered that badly: each round found prior work, and the claim had to be narrowed five times until what remained was defensible but thin. That is what novelty-by-exclusion does.

This proposal asks a different question. Not *has anyone studied this*, but **is the current solution good, and can it be improved**. The deliverable is measured against a named baseline rather than against a literature search, and the 50-work survey becomes supporting evidence that the baseline is real and widespread rather than a threat to the claim.

## 2. The baseline

**MATE: the Multi-Agent Trust Estimator** (Hallyburton & Pajic, arXiv:2503.04954, 2025) is current work on exactly this problem: security-aware sensor fusion across a multi-agent perception network. It is built the same way this project is — "Trust estimation can be cast as a hidden Markov model" — and it estimates per-agent and per-track trust online to weight fusion.

MATE rests on a conditional-independence claim, stated plainly:

> "Optimal data fusion at AGG occurs when data fused from agents are uncorrelated. Agents observing the same environment from their own independent platform-level sensors will see similar state estimates but, **given the environment, their tracks will importantly not contain any correlations.**"

Three facts about that sentence make it the right thing to attack.

1. **It is an assertion, not a result.** No experiment in the paper establishes it.
2. **The authors know it is untested.** They write: "Future works will experimentally evaluate the independence assumption."
3. **They already know the hazard it creates**, describing "nodes where information can be double-counted by neglecting to model correlations."

The same assumption is not unique to MATE. It appears as a scalar beta factor in IEC 61508, as an explicit simplification in a 2025 safety-integrity analysis of a camera/lidar/radar voter, and — in this project's own Sprint 1 prototype — as a rule that treats a differing `source_id` as statistical independence. It is the default, and it is unexamined.

## 3. Why the assumption is likely false

MATE's claim holds if agent errors come from independent platform-level noise. It fails if agents share anything that shapes *how* they are wrong. Evidence from three literatures says they do:

- **Shared detector weights produce shared blind spots.** Gottschalk, Rottmann and Saltagic measured error correlation between redundant perception networks and concluded independence "cannot be taken simply for granted, even if different sources of data are employed."
- **Shared models and viewpoints are a named failure mode.** A 2026 survey of collaborative perception states that "homogeneous agents with identical perception models and similar viewpoints are susceptible to correlated failures."
- **The same assumption, tested elsewhere, broke badly.** Work on multi-agent reliability describes compositional bounds as resting on "a step licensed by a conditional-independence assumption that is routinely stated and rarely tested," then tests it: two instances of one model co-failed on 90.0% of missions on which either failed.

None of these is in MATE's setting. That was the point of this section when it was written: the assumption had been falsified wherever it had been checked, and MATE's setting was where it had not been checked.

**That gap is now closed.** Section 0 reports the measurement in this project's own setting. The assumption fails there too, and it fails more broadly than the third bullet above would predict: correlation persists between agents running *different* detectors, so shared weights are a contributing channel rather than the operative one.

## 4. Proposed work

### 4.1 Test the assumption (the part MATE invited)

Measure whether agent track errors are conditionally independent given the environment, by comparing the observed joint-error rate between agent pairs against the rate independence predicts. The statistic is the double-fault measure of Kuncheva and Whitaker (2003) expressed as an inflation ratio; it is adopted, not invented.

**Result (2026-11-03), replacing the prediction this section originally carried.** The original prediction was that independence would hold approximately when agents run different detectors from well-separated viewpoints. **That half is falsified.** Agents running different detectors remain strongly associated (phi 0.285, odds ratio roughly 4.0), and the inflation ratio stays above 1.0 at every level of viewpoint overlap tested, including the widest separation.

What survives is the ordering, weakly. Shared-detector pairs are more associated than mixed pairs by +0.0915 phi (paired 95% CI [+0.0466, +0.1401]), and the highest overlap level gave the single largest ratio (1.985 against 1.377 and 1.576). But the ratio is **not monotonic** in viewpoint overlap and the per-stratum intervals overlap, so viewpoint geometry is not established as the operative mechanism.

**Revised prediction for the full sweep:** dependence is present across the whole matrix with a floor set by scene-level sharing, and the controllable channels modulate it rather than switch it on and off. The sweep must therefore be powered to detect *differences between* correlation levels, not merely the presence of correlation, which the spike has already settled.

### 4.2 Show where it fails worst

MATE identifies its own weak regime: "Low density coverage leaves the trust model ineffective; the veracity of a track cannot be determined from a single agent."

Correlation is most damaging in exactly that regime. With two agents that share a blind spot, the correlated pair *is* the entire evidence pool, and a second confirming report carries almost no additional information while appearing to carry a full one. The reference mission for this project is two drones. MATE's admitted weak point is this project's operating point.

### 4.3 Repair the decision rule

Correct the trust update for measured dependence: discount a confirming report by the estimated dependence between its source and the sources already counted. Both the uncorrected and corrected rules are implementations of a single policy interface, so the comparison is like-for-like.

**Success criterion:** fewer incorrect task decisions — false closure, incorrect reopening — at equal or lower verification cost than the uncorrected rule, across the correlation sweep.

## 5. What gets built

| # | Component | Owner |
| --- | --- | --- |
| 1 | CARLA scene generator with four independent correlation knobs, ordered by measured effect: viewpoint overlap, shared occluder, weather, detector model | Rishi Sheth |
| 2 | Perception adapter: a real detector run per agent per viewpoint, producing claims | Pranav Senghal |
| 3 | Dependence estimator: pairwise joint-error inflation from claim streams, no ground truth at inference | Aditya Hegde |
| 4 | Two policies behind one interface: naive-independence baseline and dependence-corrected treatment | Aditya Hegde |
| 5 | Sweep harness: channel x strength x agent count, fixed seeds, retained runs | Pranav Senghal |
| 6 | Scoring: independence test, task-decision errors, verification cost | Aditya Hegde |

**A real detector is non-negotiable.** If claims are generated synthetically with a correlation parameter chosen by the experimenter, the experiment assumes its own conclusion. The shared-model channel only means something if two agents running the same weights produce genuinely correlated errors that are measured rather than imposed. **This condition is now met:** the spike ran YOLO11m and RT-DETR-L over rendered CARLA frames and scored both against simulator ground truth, with truth used for scoring only.

**One revision to the channel list.** The detector-model channel was expected to be the principal one. It is not. It is real but secondary, and the scene-level channels — viewpoint overlap and occlusion — carry the larger share. The sweep should allocate its budget accordingly, and the design gate should not freeze a channel ranking that the spike has already contradicted.

### Carried over from the Sprint 1 prototype

The replaceable policy interface, the discipline of keeping simulator truth out of the resolver, deterministic replay with trace hashing, and the CLI artifact shape. The claim record itself is rebuilt: it carries one observation timestamp and no arrival time, so it cannot represent late or out-of-order delivery, and arrival order must be controlled separately or it will confound the dependence result.

## 6. Compute plan

**Rendering runs locally. Confirmed working, not projected.** CARLA **0.9.16** on an RTX 5060 Laptop GPU (8 GB), which clears the documented 6 GB floor for the Unreal 4.26 line. CARLA 0.10 is not used: it requires 12-16 GB.

Three corrections from the spike:
- **0.9.16, not 0.9.15.** The 0.9.15 Windows client publishes `cp310` wheels at the latest and cannot install under this project's Python 3.12. 0.9.16 publishes `cp312` and remains on Unreal 4.26, so the VRAM profile is unchanged.
- **Blackwell renders.** The risk that Unreal 4.26 would misbehave on Blackwell silicon did not materialise. 54 scenes rendered in 36 seconds with none skipped.
- **The server cannot change maps in-process.** `client.load_world()` terminates the server on this machine, reproducibly. The town is fixed when the executable is launched, and scene variety comes from the spawn points within it.

**Inference and training run on TACC Vista**, under an existing grant with roughly 900 GPU-hours available until 2026-11-18.

A direct check on a Vista GH node established that CARLA cannot run there: the nodes are `aarch64` with no x86 emulation available, and CARLA ships x86_64 binaries. The graphics stack itself is present — a real `nvidia_icd.aarch64.json` and loadable EGL — so the obstacle is the instruction set, not the GPU. Rendering therefore stays local and Vista is used for what it suits: detector inference at scale, and training the detector pairs that make the shared-model channel controllable. A correlated pair is two fine-tunes of one base model; a decorrelated pair is two different architectures. Building those pairs turns the fourth correlation channel from an assumption into a construction.

## 7. What is not claimed

- **Not a new statistic.** The double-fault measure is from 2003.
- **Not the discovery of correlated failure.** It is established in distributed estimation, truth discovery, crowdsourcing, multi-version software and classifier ensembles.
- **Not a defeat of MATE at its own task.** MATE is an attack-detection system; this work reuses its trust machinery for evidence resolution and task decisions. Any comparison is on the independence assumption they share, not on security performance.
- **No real-world safety claim.** Results establish decision-policy behaviour in simulation.
- **Not an isolated mechanism.** The spike establishes that correlated failure is present and is not an artifact of shared object difficulty. It does not establish *which* shared cause dominates. Viewpoint overlap gave the largest single stratum but the effect is not monotonic in it.
- **Not independent models.** Both detectors in the contrast condition are COCO-pretrained on overlapping data. "Different architecture" is not "independently trained on disjoint data", and the detector-pair training in Section 6 is what would close that gap.

## 8. Risks

Three of the four risks below were retired by the spike. They are retained with their outcomes rather than deleted, so the record shows what was actually checked.

| Risk | Status | Mitigation or outcome |
| --- | --- | --- |
| Rendering plus inference too slow to fill the sweep matrix | **Retired** | 54 scenes rendered in 36 s; 108 frames detected in 12 s (YOLO11m) and 7 s (RT-DETR-L). Throughput is not the constraint. |
| Measured correlation is negligible even with a shared detector | **Retired** | Correlation measured at ratio 1.671, CI [1.500, 1.870]. Reported either way; it did not need to be. |
| CARLA (Unreal 4.26) misbehaves on Blackwell-generation hardware | **Retired** | 0.9.16 renders correctly on the RTX 5060. Separate defect found instead: `client.load_world()` crashes the server, so the town is fixed at launch. |
| Grant hours expire 2026-11-18 | **Open** | Detector-pair training is front-loaded into the first two weeks of November. |
| Sweep cannot separate the correlation channels | **New** | The spike shows dependence is present across the whole matrix, so the sweep must detect *differences between* levels, not the presence of an effect. Power the matrix for the contrast, and treat the scene-level floor as a nuisance parameter rather than a signal. |

## 9. Requested decision

Approval to proceed to a design phase under this framing: freeze the dependence statistic and its estimator, the four correlation channels, the scenario matrix, and the acceptance thresholds. Implementation remains a separate approval gate.

This request now rests on a measurement rather than a projection. The assumption under attack has been tested in this project's own setting and it failed (Section 0), the toolchain that the full study depends on has been run end to end, and the measurement harness is built and under test. Two things should be decided at the design gate in light of the result: the channel ranking, which the spike contradicts (Section 5), and whether the scenario matrix is powered to separate correlation levels rather than merely detect correlation (Section 8).

## Supporting evidence

The literature assessment behind this proposal is in `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`: 50 works across eight literatures, 36 retrieved and searched in full, through eight independent adversarial review rounds. Under the earlier gap framing that survey was a threat to the claim. Under this framing it is the evidence that the baseline assumption is widespread, load-bearing, and untested.

Every quotation in this proposal was verified verbatim against a locally retained copy of its source.
