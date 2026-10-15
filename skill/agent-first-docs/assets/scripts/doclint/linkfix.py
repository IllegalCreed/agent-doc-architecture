"""迁移共用：移动 Markdown 文本时重算相对链接、按二级标题插入内容。"""

from __future__ import annotations

import os
import re

LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "#", "/")


def rebase_links(text: str, old_dir: str, new_dir: str) -> str:
    """old_dir / new_dir 为仓库相对目录（POSIX 写法）。"""

    def replace(match: re.Match) -> str:
        target = match.group(2)
        if target.startswith(SKIP_PREFIXES):
            return match.group(0)
        path, sep, anchor = target.partition("#")
        absolute = os.path.normpath(os.path.join(old_dir, path))
        relative = os.path.relpath(absolute, new_dir)
        return f"{match.group(1)}{relative}{sep}{anchor}{match.group(3)}"

    return LINK_RE.sub(replace, text)


def append_under(text: str, section: str | None, block: str) -> str:
    """把 block 放到 section（二级标题）下一个二级标题之前；section 为 None 时追加到文末。"""
    if section is None:
        return text.rstrip("\n") + "\n\n" + block
    lines = text.rstrip("\n").split("\n")
    if section not in lines:
        return "\n".join(lines) + f"\n\n{section}\n\n" + block
    i = lines.index(section) + 1
    while i < len(lines) and not lines[i].startswith("## "):
        i += 1
    head = "\n".join(lines[:i]).rstrip("\n")
    tail = "\n".join(lines[i:])
    return head + "\n\n" + block + ("\n" + tail + "\n" if tail else "")
