"""共用数据结构与 Markdown 解析。"""

from __future__ import annotations

import re
from dataclasses import dataclass

META_RE = re.compile(r"^>\s*([A-Za-z][A-Za-z ]*[A-Za-z]):\s*(.*)$")
LAST_REVIEWED_RE = re.compile(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
SEPARATOR_RE = re.compile(r"^\|\s*:?-{3,}")


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.level} {self.code} {self.path}: {self.message}"


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_tables(lines: list[str]) -> list[tuple[int, list[str], list[tuple[int, list[str]]]]]:
    """返回 [(表头行号, 表头单元格, [(行号, 单元格)])]，行号从 0 起。"""
    tables = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and SEPARATOR_RE.match(lines[i + 1]):
            header = split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append((j, split_row(lines[j])))
                j += 1
            tables.append((i, header, rows))
            i = j
        else:
            i += 1
    return tables


def parse_meta(text: str) -> dict[str, str]:
    """读取 H1 之后、第一个 `## ` 之前的英文键元信息。"""
    meta: dict[str, str] = {}
    for line in text.splitlines()[1:]:
        if line.startswith("## "):
            break
        match = META_RE.match(line)
        if match:
            meta.setdefault(match.group(1), match.group(2).strip())
    return meta


def last_reviewed(text: str) -> str | None:
    match = LAST_REVIEWED_RE.search("\n".join(text.splitlines()[:15]))
    return match.group(1) if match else None


def md_links(text: str) -> list[str]:
    return LINK_RE.findall(text)
