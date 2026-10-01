---
name: token-compressor
description: Structurally compress prompts, instructions, skills, or rules to reduce token count without removing any semantic content or detail. Triggers on prompt-debloater, compress prompts, debloat instructions, reduce prompt tokens, or tighten skill definitions.
---

# Token Compressor (Prompt Debloater)

## Overview
Compresses prompts, agent skills, system rules, and context documents to minimize LLM token consumption while preserving 100% of all rules, constraints, edge cases, examples, and semantic details.

## Theoretical Basis & Mechanics
Based on BPE tokenizer characteristics and prompt compression literature (LLMLingua, Jiang et al. 2023; LongLLMLingua, Pan et al. 2024):
- **List Overhead**: Vertical single-item bullets (`\n- `) cost 2-3 extra tokens per item compared to inline delimited sequences.
- **Structural Framing**: ASCII art diagrams, repetitive block quotes, and multi-line code fences for simple linear sequences add redundant boundary tokens without increasing model comprehension.
- **Whitespace Overhead**: Excessive blank lines produce multi-newline tokens that dilate the context window.

## Compression Techniques

### 1. Inlining Bullet Trees
Convert single-phrase or single-word multi-line bullet lists into inline comma- or pipe-delimited series.
- *Before*:
  ```markdown
  Allowed Categories:
  - feat
  - fix
  - docs
  - chore
  ```
- *After*:
  ```markdown
  Allowed Categories: `feat`, `fix`, `docs`, `chore`
  ```

### 2. Linearizing Workflows & ASCII Diagrams
Replace multi-line ASCII flowcharts and padded numbered lists with inline arrow pipelines:
- *Before*:
  ```text
  findings
    -> review
    -> revision
  ```
- *After*:
  `Pipeline: findings -> review -> revision (repeat until approved).`

### 3. Delimiting Code Examples
Replace multi-line fenced code blocks that only contain single lines of text with inline code blocks or backticked expressions (`|` separated).

### 4. Dense Completion Checklists
Consolidate related verification checks into compact compound checklist items rather than one item per line.

## Zero-Loss Guarantee Checklist
When performing compression, verify:
- [ ] Every rule, constraint, and requirement is present.
- [ ] All examples, keywords, parameters, and commands are retained.
- [ ] Edge-case warnings and failure modes remain explicit.
- [ ] Formatting remains unambiguous and valid Markdown.

## Token Measurement Utility
Use the included script to measure or verify savings:
```bash
# Measure single file:
python .agents/skills/token-compressor/scripts/verify_tokens.py measure --file <path>

# Compare before and after:
python .agents/skills/token-compressor/scripts/verify_tokens.py diff --before <original_file> --after <compressed_file>
```
