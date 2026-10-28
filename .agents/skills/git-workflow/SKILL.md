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
The agent MUST NOT perform merges (merges executed remotely by user; do not merge feature branches into `dev` or `dev` into `main` locally or remotely). Team members click **Merge pull request** on GitHub themselves, only after both reviewers (Aditya and the other teammate) approve.
If user returns after remote merge: (1) Fetch remote state -> (2) Prune stale remote-tracking branches -> (3) Inspect resulting branch state -> (4) Reconcile local view before continuing. Avoid stale branch assumptions.

## Commits
Commit messages MUST be concise, simple, specific, and prefixed with a conventional category.

- **Allowed Prefixes**: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `chore:`, `build:`, `ci:`, `perf:`, `style:`
- **Examples**: `feat: add profile search` | `fix: handle empty API response` | `test: cover expired session` | `refactor: simplify token parsing` | `docs: update setup steps` | `chore: remove unused config`
- **Avoid Vague Messages**: `update stuff`, `changes`, `fix code`, `work in progress`
  Do not claim any Git operation succeeded unless verified.

## Handing Off (Pull Request)
When work is finished and committed, read `references/pull_requests.md`. Generate the PR title and description for the user, then walk them through opening the PR on github.com against `dev` with Aditya and the other teammate as reviewers.

## Test Change Escalation
First-time setup: `uv run python .agents/skills/git-workflow/scripts/install_hooks.py`. A pre-commit hook then blocks any commit that deletes a test file, removes or weakens an assertion, drops a parametrize case, or changes fixture data under `tests/`. Added tests pass.

When the hook blocks a commit:
1. **Stop.** Do not retry, edit the test again, split the commit, use `--no-verify`, or set `ALLOW_TEST_CHANGE` yourself.
2. If you changed the test this session: tell the user which assertion changed and why, then ask them to confirm.
3. If you did not make the change (user edit, merge, or you lack context): flag it as an issue, list the files the hook reported, and ask the user to confirm regardless.
4. Only after an explicit "yes" from the user, the user runs the commit with `ALLOW_TEST_CHANGE="<reason>"`.
5. Record every approved change in the PR "Test changes" section. Aditya reviews it before merge.

The hook can be bypassed locally; the PR review is the real gate.

## Stuck State Recipe
1. Run `git status` and `git branch --show-current`; show the output to the user.
2. Do not force-push, `reset --hard`, `clean -fd`, or delete branches without the user's explicit yes.
3. Unsure which branch you are on, or the working tree is messy: stop and ask Aditya.
4. Merge conflict: do not guess. Show the conflicted files and ask the user.

## Completion Check
Before completing, verify relevant items:

- [ ] Current branch/repo state inspected.
- [ ] New sprint/feature branch based on `dev` (no direct work on `main`/`dev`).
- [ ] Rebases targeted `dev`, not `main`.
- [ ] No merge performed by agent; post-merge continuation began with fetch + prune.
- [ ] Commits use concise conventional prefixes; reported operations actually succeeded.
- [ ] Hook-blocked test changes were escalated, not bypassed, and listed in the PR "Test changes" section.
