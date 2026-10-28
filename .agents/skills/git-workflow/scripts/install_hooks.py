"""Point git at the tracked .githooks/ folder so the test-change guard runs on commit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[4]
HOOKS_DIR: Path = REPO_ROOT / ".githooks"


def main() -> int:
    if not HOOKS_DIR.is_dir():
        print(f"Missing {HOOKS_DIR}. Pull the latest dev branch and retry.")
        return 1

    for hook in HOOKS_DIR.iterdir():
        hook.chmod(0o755)

    subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"], cwd=REPO_ROOT, check=True
    )
    print("Hooks installed. Test edits will now be checked before each commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
