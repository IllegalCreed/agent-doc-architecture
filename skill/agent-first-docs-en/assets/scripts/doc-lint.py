#!/usr/bin/env python3
"""Check documentation rules. The rules are the project's documentation model (shared layer: references/general-model.md in the agent-first-docs-en skill)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from doclint.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
