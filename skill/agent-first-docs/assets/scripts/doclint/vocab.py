"""文档规则词表：状态 / 类型 / 层级词表、表头、命名正则。

本地化文档标签时只需从这里入手（单一入口）。随附的标签是中文：plan 索引表头（INDEX_HEADER）、
用例主表表头（CASE_HEADER）、实施记录标题（RECORD_HEADING）。要换成其他语言，
从本文件这几个常量改起（并同步模板与规则文档）；plans.py / cases.py 按列名取单元格
（如「状态」「层级」）、cases.py 生成视图的标题，改表头时搜索这些列名一并替换；
检查输出信息本身是中文。本工具不做多语言切换。
修改词表时同步修改项目的文档模型规则文档。
"""

from __future__ import annotations

import re

PLAN_STATUSES = (
    "draft", "approved", "in-progress", "implemented", "verified",
    "superseded", "deprecated", "obsolete", "cancelled",
)
TERMINAL_STATUSES = frozenset({"verified", "superseded", "deprecated", "obsolete", "cancelled"})
RECORD_REQUIRED_STATUSES = frozenset({"implemented", "verified"})
PLAN_TYPES = {
    "feature": "F", "bugfix": "B", "refactor": "R", "test-infrastructure": "T",
    "docs": "D", "ops": "O", "release": "C",
}
CASE_STATUSES = ("active", "stale", "deprecated", "obsolete")
CASE_LAYERS = ("L1", "L2", "L3", "L4", "L5", "manual")

INDEX_HEADER = ["Stable ID", "Type", "标题", "状态", "下一步", "Plan"]
CASE_HEADER = ["Case ID", "标题", "所属功能 / 模块", "Owner Plan", "层级", "自动化路径", "状态", "最后验证", "备注"]
META_REQUIRED = ("Status", "Stable ID", "Type", "Created", "Last reviewed", "Replaces", "Replaced by")
TITLE_MAX = 50
NEXT_MAX = 80
RECORD_HEADING = "## 实施记录"
ROADMAP_BANNER_MAX = 5

BUNDLE_DIR_RE = re.compile(r"^(\d{8})-([a-z])(\d{3})-[a-z0-9-]+$")
CASE_ID_RE = re.compile(r"^TC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}$")
BUNDLE_STANDARD = frozenset({"requirements.md", "design.md", "implementation.md", "test-cases.md"})
BUNDLE_OPTIONAL_RE = re.compile(
    r"^(?:impact-map|handoff|manual-test-cases|stages)\.md$"
    r"|^stage\d+[a-z]?-[a-z0-9-]+\.md$"
    r"|^review-[a-z0-9]+-\d{8}\.md$"
)
NAMING_DIRS = ("docs/reports", "docs/testing/infrastructure", "docs/releases")
NAMING_RE = re.compile(r"^\d{8}-[a-z0-9.-]+\.md$")
RELEASE_NAMING_RE = re.compile(r"^v\d+\.\d+\.\d+(?:-delivery)?\.md$")

