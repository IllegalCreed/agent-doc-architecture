"""测试用最小仓库。"""

from __future__ import annotations

import tempfile
from pathlib import Path

INDEX_HEAD = (
    "# 变更计划索引\n\n"
    "| Stable ID | Type | 标题 | 状态 | 下一步 | Plan |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)


def make_repo(files: dict[str, str]) -> tuple[tempfile.TemporaryDirectory, Path]:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name).resolve()
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp, root


def index_row(sid: str, typ: str, title: str, status: str, nxt: str, link: str) -> str:
    return f"| {sid} | {typ} | {title} | {status} | {nxt} | {link} |\n"


def meta(sid: str, status: str, typ: str, created: str = "2026-10-01") -> str:
    return (
        f"# 标题\n\n> Status: {status}\n> Stable ID: {sid}\n> Type: {typ}\n> Created: {created}\n"
        f"> Last reviewed: {created}\n> Replaces: none\n> Replaced by: none\n\n## 背景\n"
    )
