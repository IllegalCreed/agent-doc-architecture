#!/usr/bin/env python3
"""Check local Markdown links under the repository without network access."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]\n]+\]:\s*(\S.*)$", re.MULTILINE)
SKIP_PREFIXES = ("#", "mailto:", "tel:", "data:", "javascript:")
SKIP_DIRS = {".git", ".idea", ".turbo", "dist", "node_modules", "target"}

FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _blank(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def mask_fences(text: str) -> str:
    """逐行识别围栏代码块（CommonMark：0-3 空格缩进、>=3 个同类字符、闭合围栏不短于起始），整块替换为等长空白。"""
    out: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        if fence is None:
            match = FENCE_OPEN_RE.match(body)
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                fence = (match.group(1)[0], len(match.group(1)))
                out.append(_blank(line))
            else:
                out.append(line)
            continue
        out.append(_blank(line))
        char, size = fence
        stripped = body.lstrip(" ")
        if len(body) - len(stripped) <= 3:
            run = len(stripped) - len(stripped.lstrip(char))
            if run >= size and not stripped[run:].strip():
                fence = None
    return "".join(out)


def mask_code(text: str) -> str:
    """围栏代码块与行内代码替换为等长空白（保留换行与偏移），代码里的链接语法不算链接。"""
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), mask_fences(text))


def destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    titled = re.match(r"^(.*?)(?:\s+[\"'].*[\"'])$", value)
    return (titled.group(1) if titled else value).strip()


def iter_markdown(root: Path, selected: list[Path]):
    starts = selected or [root]
    seen: set[Path] = set()
    for start in starts:
        candidate = start if start.is_absolute() else root / start
        candidate = candidate.resolve()
        paths = [candidate] if candidate.is_file() else candidate.rglob("*.md")
        for path in paths:
            if path.suffix.lower() != ".md" or any(part in SKIP_DIRS for part in path.parts):
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path


def check(root: Path, selected: list[Path]) -> list[str]:
    failures: list[str] = []
    for source in iter_markdown(root, selected):
        text = mask_code(source.read_text(encoding="utf-8", errors="replace"))
        matches = list(INLINE_LINK_RE.finditer(text)) + list(REFERENCE_LINK_RE.finditer(text))
        for match in matches:
            raw = destination(match.group(1))
            if not raw or raw.startswith(SKIP_PREFIXES) or raw.startswith("//"):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme:
                continue
            decoded = unquote(parsed.path)
            if not decoded or any(token in decoded for token in ("*", "${", "<NNNN>")):
                continue
            candidate = Path(decoded)
            if candidate.is_absolute():
                continue
            resolved = (source.parent / candidate).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            if resolved.exists():
                continue
            line = text.count("\n", 0, match.start()) + 1
            failures.append(
                f"{source.relative_to(root)}:{line}: {raw} -> {resolved.relative_to(root)}"
            )
    return sorted(set(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--max-broken",
        type=int,
        default=0,
        help="Exit successfully when the broken-link count does not exceed this baseline",
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to check")
    args = parser.parse_args()
    root = args.root.resolve()
    failures = check(root, args.paths)
    if not args.quiet:
        for failure in failures:
            print(failure)
        print(f"broken local Markdown links: {len(failures)}")
    return 1 if len(failures) > args.max_broken else 0


if __name__ == "__main__":
    sys.exit(main())
