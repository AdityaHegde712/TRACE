# Pull Requests

## Agent: write the title and description
1. Run `git status` and `git diff dev...HEAD --stat`; read the changes. Do not describe work you did not see.
2. **Title:** `<prefix>: <what changed>`, under 70 characters, using the same prefixes as commits (`feat:`, `fix:`, `test:`, `docs:` ...). Specific, not "updates".
3. **Description:** fill every section of `.github/pull_request_template.md`:
   - Summary: what and why, plain English.
   - Track and task: for example "Track B, B1".
   - How it was checked: paste the pass/fail result of `uv run pytest` and `uv run ruff check .`. Never tick a box you did not run.
   - **Test changes:** "None", or each edited, removed, or weakened test, the reason, and who confirmed. A commit made with `ALLOW_TEST_CHANGE` must appear here.
   - Frozen definitions: "No", or stop and ask Aditya.
4. Show the title and description to the user and ask for confirmation before they paste it.

## Human: open the PR on github.com
1. Push your branch: `git push -u origin <your-branch>`.
2. Open the repository on github.com. Click the yellow **Compare & pull request** banner, or **Pull requests** > **New pull request**.
3. Set **base: `dev`** and **compare: your branch**. Never `main`.
4. Paste the title and description.
5. Under **Reviewers** on the right, request **Aditya** and the other teammate.
6. Click **Create pull request**, then tell Aditya in the team chat.

## After review
- Both reviewers approve, then the author clicks **Merge pull request** on GitHub. The agent never merges.
- If changes are requested, push more commits to the same branch; the PR updates itself.
- After the merge, tell the agent "continue after merge": it runs `git fetch --prune`, switches to `dev`, pulls, and starts the next branch from `dev`.
