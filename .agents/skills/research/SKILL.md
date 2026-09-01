---
name: research
description: Perform evidence-grounded research or retrieve references for implementation. Invoke whenever the user asks to research, investigate, compare external evidence, look something up for implementation, gather references, perform a literature or technology review, or make claims that should be grounded in retrieved source material. Retrieved evidence must take precedence over pretrained knowledge.
---

# Research

> **Retrieved information takes precedence over pretrained knowledge.** Use pretrained knowledge for orientation only. Findings must be grounded in retrieved and validated evidence.

## Source Requirements
Sources MUST be created/updated within the **preceding 2 years relative to the present date**.
- **Preferred Sources**: Peer-reviewed papers, academic publications, official documentation, standards bodies, industry-leading engineering/research orgs, industry leader technical blogs, official white papers.
- **Rejected Sources**: SEO/content-farm articles, unattributed summaries, low-quality aggregators, unverifiable secondary claims, sources outside the 2-year window.
- **Preserved Metadata**: Title, author/publisher/org, publication/update date, URL/DOI/identifier, relevance to question.

## Mandatory Research Pipeline

### 1. Gather Evidence
Collect relevant credible sources before producing findings (never search merely to support a pre-formed conclusion). Ensure coverage exposes disagreements, limitations, and competing approaches.

### 2. Extract Findings
For **every factual finding or inference**: (1) Identify supporting source -> (2) Capture exact wording -> (3) Quote verbatim (never alter wording or reconstruct from memory) -> (4) Distinguish **Source claim** (directly asserted) vs. **Inference** (derived reasoning; retain exact quoted evidence used) -> (5) Do not strengthen claims beyond source support.

### 3. Mandatory Adversarial Review
Spawn a subagent to adversarially review findings for unsupported claims, weak evidence, stale sources, quotation mismatches, contradictions, overgeneralization, inference leaps, missing caveats, misinterpretations, or conflicting evidence.
- **Cycle**: `findings -> adversarial review -> revision -> adversarial review...` until reviewer declares findings acceptable (self-review does NOT replace this).

### 4. Validate Research
Validate that quotations exist verbatim in cited sources using the local validator script:
```bash
python .agents/skills/research/scripts/validate_quote.py --file <path_to_source> --quote "<exact wording>"
# Or search across a directory of saved sources:
python .agents/skills/research/scripts/validate_quote.py --dir <sources_folder> --quote "<exact wording>"
```
Verify: quotations exist verbatim in cited sources, source supports claim, and inferences do not exceed evidence.
If unvalidated: treat as unverified -> revise/remove/replace via retrieved evidence -> re-run adversarial review -> re-validate. Never present unvalidated quotations.

### 5. Produce the Survey
Create a survey document directly answering the user's question, citing every factual claim, preserving exact quotations, distinguishing claims from inference, including source metadata, exposing disagreements/limitations/uncertainties without silent reconciliation. Present survey document + brief summary in standard output.

## Evidence Conflict
When retrieved evidence conflicts with pretrained knowledge: prefer retrieved/validated evidence, state disagreement explicitly, avoid silent resolutions, and never override retrieved evidence without supporting evidence.

## Completion Check
Before presenting, verify:
- [ ] Sources within 2-year recency and sufficiently authoritative.
- [ ] Every factual finding/inference backed by retrieved verbatim quotes and distinguished from inferences.
- [ ] Adversarial subagent reviewed and approved findings across required revision cycles.
- [ ] `validate_quote.py` script verified all quotations against source texts.
- [ ] Every claim cited; source disagreements and uncertainties preserved; user received survey and summary.
