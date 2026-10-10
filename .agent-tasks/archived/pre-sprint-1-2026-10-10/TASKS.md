# Framework Survey Task Ledger

1. [x] Establish independent survey scope, handoff state, and research-first design policy.
   - Evidence: `.agent-tasks/PLAN.md`, `.agent-tasks/DECISIONS.md`, `docs/PROTOCOL.md`, and `docs/HANDOFF.md`.
2. [x] Build a source-cited landscape of existing multi-robot/agentic orchestration frameworks and public implementations.
   - Acceptance: framework feature matrix, source links, license/release status, and limitations.
3. [x] Build a source-cited comparison of shared-world-model and efficient projection designs.
   - Acceptance: direct evidence for representation, synchronization, provenance, and failure modes.
4. [x] Evaluate simulator-first feasibility, available adapters, model-runtime paths, and physical-demo transition.
   - Acceptance: assumptions explicitly classified as verified, testable, or unknown.
5. [x] Establish a source-cited problem ledger before selecting an implementation contribution.
   - Acceptance: each candidate problem names an affected workflow, failure mode, baseline, measurable outcome, and closest counterexample.
6. [x] Conduct the primary-agent adversarial novelty pass and recommend an implementation contribution.
   - Acceptance: closest counterexamples, direct source checks, failure modes, rating, and bounded release thesis.
7. [x] Consolidate the authoritative survey and zero-context continuation packet.
   - Evidence: `docs/DIRECTION_PROPOSAL.md`, `docs/LANDSCAPE.md`, `docs/PROBLEM_LEDGER.md`, `docs/ADVERSARIAL_NOVELTY_PASS.md`, and `docs/HANDOFF.md`.
8. [x] Validate the working direction against Summer 2027 market and new-grad employability evidence.
   - Evidence: `docs/MARKET_VALIDATION_SUMMER_2027.md`.
   - Acceptance: target-application companies, product/procurement evidence, current hiring evidence, explicit forecast limits, and a scored disposition.
9. [/] Obtain owner, team, and faculty approval of the research direction and proposed application anchor before beginning a separate design phase.
   - Evidence: owner approval on 2026-10-01 fixes the reference mission as two simulated drones verifying a reported road blockage near critical infrastructure (FSD-024).
   - Remaining: confirm recorded team and faculty acceptance before treating the research direction as fully approved.
10. [x] Create a project-adapted prerequisite knowledge-transfer guide without changing the IAS class original.
   - Evidence: `docs/KNOWLEDGE_TRANSFER.md`.
   - Acceptance: explains the evidence-to-belief-to-task lifecycle, gives accessible prerequisites and official/reference links, and separates study material from novelty evidence.
11. [x] Consolidate the active framework survey into the TRACE repository layout.
   - Evidence: `.gitignore`, `.agent-tasks/PLAN.md`, `.agent-tasks/DECISIONS.md`, `.agent-tasks/TASKS.md`, and `docs/`.
   - Acceptance: archived legacy material is excluded from Git; only the root handoff triple remains under `.agent-tasks`; active survey artifacts are in `docs/`.
12. [x] Establish the TRACE branch policy and initial deliverable branch.
   - Evidence: `FSD-013`; `origin/dev` and `origin/main` start at the same validated commit.
   - Acceptance: work integrates through `dev`; `main` is reserved for checked, owner-merged deliverables.
13. [x] Draft and humanize the short project abstract.
   - Evidence: `docs/PROJECT_ABSTRACT.md` and the source record retained under ignored `.agent-tasks/archived/`.
   - Acceptance: approximately 200 words, exactly three body paragraphs, author and advisor attribution, source-linked company examples, bounded solution description, and completed adversarial and humanization passes.
14. [x] Revise the abstract against the instructor rubric.
   - Evidence: `docs/PROJECT_ABSTRACT.md` contains a 215-word body with exactly three paragraphs and LF line endings.
   - Acceptance: paragraph one is domain-only; paragraph two states the problem, consequence, and adjacent company work; paragraph three states the proposed mechanism, baselines, measures, and scope boundary; tentative and imprecise phrasing is removed.
15. [x] Inventory and extract the Canvas assignment package.
   - Evidence: `Submissions/Extracted/canvas_assignments_2026-10-01/` contains the meeting-log instruction page and template; `Submissions/Extracted/canvas_assignments_2026-10-01-workbook/` contains Workbook 1 instructions plus research and development DOCX templates.
   - Acceptance: both archive paths were inspected before extraction; separate extraction targets were used and no pre-existing target was overwritten.
16. [x] Parse the meeting-log and Workbook 1 requirements, templates, and rubrics.
   - Acceptance: exact required sections, development-template formatting constraints, due-date details, and scoring criteria are captured from the extracted artifacts; the research template remains unread and unused.
17. [x] Audit admissible repository evidence for the report and meeting log.
   - Acceptance: `docs/Capstone-TRACE*.md` and `.env` files remain unread; each requirement is classified as present, partial, missing, or unverifiable with exact evidence paths.
18. [x] Produce the rubric-maximization gap analysis and drafting handoff.
   - Evidence: `Submissions/SUBMISSION_READINESS_AUDIT.md`.
   - Acceptance: known gaps are identified without unsupported rubric weighting; owner-supplied facts are separated from project evidence; the immediate next action is explicit.
19. [ ] Obtain confirmed meeting history and current team/advisor decisions before drafting submission content.
   - Acceptance: each meeting fact, individual contribution, approved project choice, and member-owned schedule item has a workspace artifact or direct owner confirmation.
   - Immediate next action: owner provides the meeting-history source or confirms that no qualifying remote/equivalent meeting-note location exists.
20. [x] Verify the remote meeting-folder state without changing branches.
   - Evidence: fetched `origin/main` commit `6e1e606c317a505b461c62c866d7fb99e92b43b1` contains `meetings/folder_purpose.md` and no dated meeting entry.
   - Acceptance: local `dev` and its existing uncommitted work remained unchanged.
21. [x] Create a fact-bounded September 15 advisor-meeting draft without committing or pushing.
   - Evidence: `meetings/2026-09-15-advisor.md` on `codex/meeting-log-sept-15`.
   - Acceptance: confirmed meeting facts are preserved; unconfirmed attendance, due date, and technical decisions are visibly unresolved.
22. [x] Formalize the open project inputs before finalizing the meeting note and Workbook 1 content.
   - Scope: novelty check, dataset search, methodology choice, candidate architecture, feasibility, responsibility allocation, and sprint schedule.
   - Evidence: `docs/ADVERSARIAL_NOVELTY_PASS.md`, `docs/ADVERSARIAL_PREAPPROVAL_REVIEW.md`, `docs/DIRECTION_PROPOSAL.md`, `docs/DATASET_AND_METHOD_REVIEW.md`, and `docs/PROJECT_EXECUTION_PLAN.md`.
   - Acceptance: each input has a source-supported or owner/team-confirmed status and can be cited accurately without claiming future work is complete.
23. [x] Confirm the experiment’s initial data modality and reference workflow.
   - Evidence: FSD-024. The initial workflow is simulator-native observation of a road-blockage report near critical infrastructure, with two simulated drones assigned to verify it.
   - Limitation: this does not select an auxiliary real-world dataset or a simulator adapter.
24. [x] Establish the admissible boundary for TRACE reference drafts.
   - Evidence: FSD-022 and the `TRACE Reference Boundary` in `.agent-tasks/PLAN.md`.
   - Acceptance: conceptual direction is reusable; fabricated-completion claims remain excluded from submissions and decisions.
25. [x] Perform an independent adversarial review before mission approval.
   - Scope: three-person 3-4 month feasibility, novelty boundary, plan/directory adherence, and simulator-plus-dataset suitability.
   - Evidence: `docs/ADVERSARIAL_PREAPPROVAL_REVIEW.md` and `.agent-tasks/preapproval-review/SOURCE_EXCERPTS.md`.
   - Acceptance: current primary sources and workspace evidence support every conclusion; hard blockers and smallest viable scope are explicit.
26. [x] Research and review the primary scenario corpus, auxiliary dataset, and method path for the owner-approved road-blockage mission.
   - Evidence: `docs/DATASET_AND_METHOD_REVIEW.md`, `.agent-tasks/dataset-method-review/SOURCE_EXCERPTS.md`, quote-validator output, and independent adversarial approval.
   - Acceptance: source excerpts validate every external claim; adversarial review accepts the evidence boundaries; the final proposed data/method decision is suitable for Workbook 1 without claiming procurement or integration.
27. [x] Confirm a responsibility split and sprint schedule before finalizing the meeting log and development-track Workbook 1.
   - Evidence: FSD-026, FSD-027, and `docs/PROJECT_EXECUTION_PLAN.md`.
   - Acceptance: all three members have confirmed planned ownership, the sprint schedule is owner-approved, and future-versus-completed contribution language is explicit.
28. [/] Convert the evidence-backed planning artifacts into the development-track Workbook 1 and final fact-bounded meeting note.
   - Completed evidence: `Submissions/WORKBOOK_1_DEVELOPMENT_DRAFT.md` covers every development-template section. It passed section-presence, humanization lexical, and UTF-8/LF checks.
   - Completed evidence: the owner confirmed three team meetings on 2026-09-16, 2026-09-23, and 2026-09-30, each online from 9:30 PM to 10:30 PM with all three students present. Their notes use the required schema and carry a visible reconstruction note because contemporaneous details were unavailable.
   - Remaining: the September advisor note still needs the professor/advisor name and attendance confirmation. The owner requested Markdown rather than DOCX authoring.
   - Immediate next action: owner confirms the professor/advisor name and attendance for the 2026-09-15 meeting, or instructs that the note retain its visible unknown marker.
