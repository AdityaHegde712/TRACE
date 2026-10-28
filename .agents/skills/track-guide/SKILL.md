---
name: track-guide
description: Session opener for team members. Asks who is working, saves the answer, loads that person's track (owned work, off-limits files, starter prompts), and keeps the agent inside that scope. Use at the start of every session, after team-onboarding, and whenever a task might cross into another member's track.
---

# Track Guide

**Current gate (Aditya updates this line):** M0 pending (advisor approval due Nov 3). Until M0 passes, work is limited to setup, reading, and drafting questions. No implementation.

## 1. Identify who is working
1. Read `.agent-tasks/WHO.md`. If it exists, confirm in one line: "You are <name>, Track <letter>. Correct?"
2. If it is missing or the user says no, ask exactly this and wait:
   > Which team member are you? 1) Aditya  2) Rishi  3) Pranav
3. Create or overwrite `.agent-tasks/WHO.md`:
   ```
   name: <name>
   track: <A|B|C>
   set: <YYYY-MM-DD>
   ```
   `.agent-tasks/` is gitignored, so this stays on the user's machine. Create the folder if it does not exist.

## 2. Load the track
Read only the matching file, then follow its "Read first" list:
- Aditya: `references/aditya-track.md`
- Rishi: `references/rishi-track.md`
- Pranav: `references/pranav-track.md`

If the user has not set up their machine yet, or `uv run pytest` fails, read `references/first-session.md` first.

## 3. Offer a start
After loading the track, show that file's three starter prompts and say: "Pick one, or tell me what you want to work on." If the user is unsure, propose the first open item from their track that is not blocked by the current gate.

## 4. Stay in scope
- Work only on items in the user's track. Reading other tracks' files is fine; editing them is not.
- Need a change in another track's files? Do not make it. Write the request in `.agent-tasks/TASKS.md` under "Handoffs", address it to the owner, and tell the user to send it to that person.
- Need to change a frozen definition (see `team-onboarding`)? Stop and tell the user to ask Aditya.
- A request is outside the current gate (for example implementation before M0)? Say so, name the gate, and propose the allowed alternative.
- Reading and explaining anything is always allowed. When the user asks "what does this mean", answer in plain English.

## 5. Keep state
After each completed step, tick the item in `.agent-tasks/TASKS.md` and write one line saying what is next. If the folder is missing, create `PLAN.md`, `DECISIONS.md`, `TASKS.md` with a heading each. This lets the next session, or another person, resume cold.

## 6. Finishing
Before saying work is done: tests pass (`uv run pytest`), lint passes (`uv run ruff check .`), and the change is committed on a feature branch. Then load `git-workflow` and follow its pull request steps.
