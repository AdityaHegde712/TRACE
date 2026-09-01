---
name: git-workflow
description: Enforce this project's Git branching, rebasing, commit, remote-merge, and continuation workflow. Invoke for branch creation, sprint or feature startup, rebasing, committing, post-merge continuation, or any operation that changes or depends on repository Git state.
---

# Git Workflow

## Branch Model
Assume repository uses: `main` (stable/primary), `dev` (integration/dev), and dedicated feature branches for active sprint/feature work. Inspect actual repo state before modifying Git state.

## New Sprint / Feature
Every new sprint/feature MUST use a new feature branch based on `dev`:
1. Ensure remote state is current -> 2. Base new branch on `dev` -> 3. Perform work only on that branch.
Never implement feature work directly on `main` or `dev`.

## Rebasing / Continuation
When user asks to **rebase and continue** (after turn end, interruption, resume, context switch, or continuation event), rebase active feature branch onto **`dev`**, never `main` (`feature/* <- rebase onto dev`). Do not use `main` unless explicitly instructed.

## Merges
The agent MUST NOT perform merges (merges executed remotely by user; do not merge feature branches into `dev` or `dev` into `main` locally or remotely).
If user returns after remote merge: (1) Fetch remote state -> (2) Prune stale remote-tracking branches -> (3) Inspect resulting branch state -> (4) Reconcile local view before continuing. Avoid stale branch assumptions.

## Commits
Commit messages MUST be concise, simple, specific, and prefixed with a conventional category.

- **Allowed Prefixes**: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `chore:`, `build:`, `ci:`, `perf:`, `style:`
- **Examples**: `feat: add profile search` | `fix: handle empty API response` | `test: cover expired session` | `refactor: simplify token parsing` | `docs: update setup steps` | `chore: remove unused config`
- **Avoid Vague Messages**: `update stuff`, `changes`, `fix code`, `work in progress`
  Do not claim any Git operation succeeded unless verified.

## Completion Check
Before completing, verify relevant items:

- [ ] Current branch/repo state inspected.
- [ ] New sprint/feature branch based on `dev` (no direct work on `main`/`dev`).
- [ ] Rebases targeted `dev`, not `main`.
- [ ] No merge performed by agent; post-merge continuation began with fetch + prune.
- [ ] Commits use concise conventional prefixes; reported operations actually succeeded.
