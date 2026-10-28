# First Session Setup

Do these once per machine. Stop at the first failure and tell the user the exact error.

1. **Install the agent CLI (Codex).** Linux/macOS: `curl -fsSL https://chatgpt.com/codex/install.sh | sh`, then open a new terminal and run `codex` once. Docs: https://learn.chatgpt.com/docs/codex/cli#getting-started. Windows install steps are not documented here yet; ask Aditya.
2. **Install `uv`** (Python package manager). Check with `uv --version`. Python 3.12 or newer is required.
3. **Clone and enter the repo**, then run:
   ```bash
   git switch dev
   git pull
   uv sync
   ```
4. **Check the tests pass:**
   ```bash
   uv run pytest
   ```
5. **Run the demo scenario** to see a claim stream become a trace:
   ```bash
   uv run python -m evidence_resolution --scenario tests/fixtures/oracle/supported.json --output-dir artifacts/demo
   ```
   Open `artifacts/demo/` and read the two output files with the user. Explain that `.trace.jsonl` is the decision log and `.oracle.json` says whether it matched the expected answer.
6. **Install the project git hook** so test edits are caught (see `git-workflow`):
   ```bash
   uv run python .agents/skills/git-workflow/scripts/install_hooks.py
   ```

Never read, edit, or search `.env` files; use `.env.example`.
