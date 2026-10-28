---
name: team-onboarding
description: Project primer for teammates new to the domain, coding, or AI agents. Explains the research problem in plain English, defines the glossary, lists the decisions and frozen definitions nobody but the lead may change, and sets how the agent should talk to a beginner. Load at the start of every session, before track-guide.
---

# Team Onboarding

## Agent behavior with this user
The user may be new to the domain, to coding, and to AI agents. Therefore:
1. Explain each action in one plain sentence before doing it. Define any term from the glossary on first use.
2. Make small changes. Run the tests after each one and show the result.
3. Ask before anything hard to undo: deleting files, `git reset`, force-push, editing tests.
4. If the request touches a frozen definition (below) or another member's track, stop and tell the user to ask Aditya. Do not work around it.
5. Never claim something works unless you ran it and saw it pass.

## The problem in plain English
A team of drones inspects a road. Drone A reports a blockage; drone B "independently" confirms it; the system closes the task. That is only safe if A and B can be wrong separately. If both use the same detector, the same viewpoint, or the same lighting, they can agree and be wrong together. Agreement then looks like evidence but is not.

The current prototype assumes "different `source_id` means independent". This project **measures when that assumption breaks and what it costs**. It is not building a new fusion algorithm.

Deliverable: a benchmark plus a measurement harness, and a plot of how decisions degrade as agents become more correlated.

## Glossary
| Term | Meaning |
| --- | --- |
| Claim | One agent's report: "I see X at time T". Carries a `source_id`. |
| Source | The agent (drone, model) that made a claim. |
| Resolution policy | Code that reads claims and decides: verified, rejected, or still unknown. |
| Correlated failure | Sources making the same mistake for a shared reason. |
| Correlation channel | A shared cause: occluder, detector model version, viewpoint, or illumination. |
| Dependence inflation factor | Observed joint error rate divided by the rate expected if sources were independent. 1 means independent. |
| Agreement reliability | Probability a claim is right given that k sources agree. |
| False closure | Task closed although the blockage claim was wrong. |
| Simulator truth | What actually happened in the scenario. Used for scoring only. |
| Trace hash | SHA-256 of a run's trace. Same inputs must give the same hash. |
| Baseline | A simple policy we compare against (latest-report, first-report-wins, majority vote, always-verify, naive-independence). |

## Decisions nobody changes
Source of truth: `docs/planning/DECISIONS.md`. Short form:
- **AD-001** Simulator truth never enters the claim stream or the policy. It is used for scoring only.
- **AD-002** Estimating belief and choosing a task action are separate layers.
- **AD-003** Every decision records the source claim IDs and the policy version, so it can be replayed.
- **AD-004** Repeated or correlated evidence is never treated as independent without a measurement.
- Planning and implementation are separate approval gates. Do not start implementation for anything not yet frozen.

## Frozen at milestone M1 (Nov 10), only Aditya changes these
1. The dependence measure (inflation factor) and its estimator.
2. The agreement-reliability measure.
3. The four correlation channels.
4. The scenario matrix.
5. The acceptance thresholds.

Until M1, treat all five as "draft, ask Aditya". After M1, they are read-only.

## Tests
- Existing test assertions are a contract. Never edit, weaken, or delete one to make a test pass; fix the code instead. If a test looks wrong, stop and ask. Details: `test-driven-development` and `git-workflow`.
- The Sprint 1 prototype carries no frozen status (AD-005 withdrawn), but other tests still follow the rule above.

## Next
Load `track-guide` to identify who is working and which track applies.
