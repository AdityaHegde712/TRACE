---
name: research
description: Perform evidence-grounded research or retrieve references for implementation. Invoke whenever the user asks to research, investigate, compare external evidence, look something up for implementation, gather references, perform a literature or technology review, or make claims that should be grounded in retrieved source material. Retrieved evidence must take precedence over pretrained knowledge.
---

# Research

> **Retrieved information takes precedence over pretrained knowledge.** Use pretrained knowledge for orientation only. Findings must be grounded in retrieved and validated evidence.

## Pick the workflow
| Situation | Read |
| --- | --- |
| Result feeds the proposal, report, novelty claim, advisor material, or any literature or technology review | `references/full-pipeline.md` (adversarial review and quote validation mandatory) |
| Quick lookup while building: library usage, term definition, tool choice | `references/condensed-workflow.md` |
| Unsure which applies | Use `full-pipeline.md` and ask the user |

Read only the chosen file. If a quick lookup grows into something the report will cite, switch to the full pipeline and tell the user.

Quote validator (full pipeline only): `.agents/skills/research/scripts/validate_quote.py`.
