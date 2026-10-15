#!/usr/bin/env python3
"""文档规则检查。规则见项目的文档模型（通用层：agent-first-docs skill 的 reference/general-model.md）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from doclint.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
