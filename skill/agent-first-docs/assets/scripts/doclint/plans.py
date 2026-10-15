"""plan 索引与 bundle 检查。"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from . import vocab
from .model import Finding, md_links, parse_meta, parse_tables

INDEX = "docs/plans/index.md"
PLANS = "docs/plans"
DEFAULT_BUNDLE_ROOT = "docs/plans"
RESERVED_DIRS = frozenset({"tracks", "archive"})


@dataclass
class IndexRow:
    line: int
    cells: dict[str, str]
    links: list[str]
    width: int = 0


def read_index(root: Path) -> tuple[list[str], list[IndexRow], list[str]]:
    path = root / INDEX
    if not path.exists():
        return [], [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    for _, header, rows in parse_tables(lines):
        if header and header[0] == "Stable ID":
            parsed = [
                IndexRow(n, dict(zip(header, cells)), md_links(cells[-1]) if cells else [], len(cells))
                for n, cells in rows
            ]
            return header, parsed, lines
    return [], [], lines


def bundle_root(baseline: dict) -> str:
    """bundle 根目录：新项目平铺在 docs/plans/ 下；存量项目由接入配置 bundle_root 声明。"""
    return baseline.get("bundle_root", DEFAULT_BUNDLE_ROOT)


def bundle_link_re(base: str) -> re.Pattern:
    prefix = os.path.relpath(base, PLANS)
    prefix = "" if prefix == "." else prefix + "/"
    return re.compile(rf"^{re.escape(prefix)}([^/.][^/]*)/")


def row_bundle(row: IndexRow, pattern: re.Pattern) -> str | None:
    for link in row.links:
        match = pattern.match(link)
        if match:
            return match.group(1)
    return None


def check_index(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not (root / INDEX).exists():
        return [Finding("ERROR", "PLAN-INDEX-MISSING", INDEX, "缺变更计划索引")]
    header, rows, lines = read_index(root)
    if header != vocab.INDEX_HEADER:
        findings.append(Finding(
            "ERROR", "PLAN-INDEX-HEADER", INDEX,
            f"表头应为「{' | '.join(vocab.INDEX_HEADER)}」，实际「{' | '.join(header)}」",
        ))
    for n, line in enumerate(lines):
        if line.startswith("> 20"):
            findings.append(Finding("ERROR", "PLAN-INDEX-BANNER", f"{INDEX}:{n + 1}", "索引禁止日期横幅，移到 roadmap 或 bundle"))
    h1 = next((n for n, line in enumerate(lines) if line.startswith("# ")), None)
    if h1 is not None:
        end = next((n for n in range(h1 + 1, len(lines)) if lines[n].startswith(("## ", "|"))), len(lines))
        preamble = [line for line in lines[h1 + 1:end] if line.strip() and not line.startswith("> 20")]
        if len(preamble) > 1:
            findings.append(Finding(
                "ERROR", "PLAN-INDEX-PREAMBLE", f"{INDEX}:{h1 + 2}",
                f"H1 与表格之间只允许一行说明，实际 {len(preamble)} 行；进度叙述移到 roadmap 或 bundle",
            ))
    first_seen: dict[str, int] = {}
    for row in rows:
        loc = f"{INDEX}:{row.line + 1}"
        if row.width != len(header):
            findings.append(Finding("ERROR", "PLAN-ROW-COLUMNS", loc, f"列数 {row.width} 与表头 {len(header)} 不一致"))
            continue
        sid = row.cells.get("Stable ID", "")
        if sid in first_seen:
            findings.append(Finding("ERROR", "PLAN-ID-DUP", loc, f"{sid} 与第 {first_seen[sid]} 行重复"))
        first_seen.setdefault(sid, row.line + 1)
        status = row.cells.get("状态", "")
        if status not in vocab.PLAN_STATUSES:
            findings.append(Finding("ERROR", "PLAN-STATUS", loc, f"状态「{status}」不在词表"))
        typ = row.cells.get("Type", "")
        if typ not in vocab.PLAN_TYPES:
            findings.append(Finding("ERROR", "PLAN-TYPE", loc, f"类型「{typ}」不在词表"))
        if len(row.cells.get("标题", "")) > vocab.TITLE_MAX:
            findings.append(Finding("ERROR", "PLAN-TITLE-LEN", loc, f"标题超过 {vocab.TITLE_MAX} 字"))
        if len(row.cells.get("下一步", "")) > vocab.NEXT_MAX:
            findings.append(Finding("ERROR", "PLAN-NEXT-LEN", loc, f"下一步超过 {vocab.NEXT_MAX} 字"))
    return findings


def check_bundles(root: Path, baseline: dict) -> list[Finding]:
    if not (root / INDEX).exists():
        return []  # 登记关系依赖索引；缺索引只报 PLAN-INDEX-MISSING 一条，先建索引
    header, rows, _ = read_index(root)
    rows = [row for row in rows if row.width == len(header)]
    base = bundle_root(baseline)
    pattern = bundle_link_re(base)
    registered: dict[str, IndexRow] = {}
    for row in rows:
        name = row_bundle(row, pattern)
        if name:
            registered.setdefault(name, row)
    exceptions = set(baseline.get("bundle_file_exceptions", []))
    since = baseline.get("rules_effective_since", "")
    findings: list[Finding] = []
    base_dir = root / base
    candidates = [] if not base_dir.is_dir() else [
        p for p in base_dir.iterdir() if p.is_dir() and p.name not in RESERVED_DIRS
    ]
    for bundle in sorted(candidates):
        findings += _check_bundle(bundle, base, registered.get(bundle.name), exceptions, since)
    return findings


def _check_bundle(bundle: Path, base: str, row: IndexRow | None, exceptions: set[str], since: str) -> list[Finding]:
    """since 为接入配置里的规则生效日期；空串表示新项目，全部严格检查。"""
    rel = f"{base}/{bundle.name}"
    match = vocab.BUNDLE_DIR_RE.match(bundle.name)
    if not match:
        return [Finding("ERROR", "BUNDLE-NAME", rel, "目录名应为 YYYYMMDD-<字母>NNN-<slug>")]
    findings: list[Finding] = []
    if row is None:
        findings.append(Finding("ERROR", "BUNDLE-UNREGISTERED", rel, f"未登记 {INDEX}"))
    requirements = bundle / "requirements.md"
    if not requirements.exists():
        return findings + [Finding("ERROR", "BUNDLE-META-MISSING", rel, "缺 requirements.md")]
    text = requirements.read_text(encoding="utf-8")
    meta = parse_meta(text)
    missing = [key for key in vocab.META_REQUIRED if key not in meta]
    if missing:
        findings.append(Finding("ERROR", "BUNDLE-META-MISSING", f"{rel}/requirements.md", f"元信息缺 {', '.join(missing)}"))
    date, letter, number = match.groups()
    expected_id = f"{letter.upper()}-{date}-{number}"
    if meta.get("Stable ID", expected_id) != expected_id:
        findings.append(Finding(
            "ERROR", "BUNDLE-META-MISMATCH", f"{rel}/requirements.md",
            f"Stable ID {meta['Stable ID']} 与目录推出的 {expected_id} 不符",
        ))
    if row is not None:
        if row.cells.get("Stable ID") != expected_id:
            findings.append(Finding(
                "ERROR", "BUNDLE-META-MISMATCH", rel,
                f"索引 Stable ID {row.cells.get('Stable ID')} 与目录推出的 {expected_id} 不符",
            ))
        for key, column in (("Status", "状态"), ("Type", "Type")):
            if key in meta and meta[key] != row.cells.get(column):
                findings.append(Finding(
                    "ERROR", "BUNDLE-META-MISMATCH", f"{rel}/requirements.md",
                    f"元信息 {key}={meta[key]} 与索引 {row.cells.get(column)} 不一致",
                ))
    typ = meta.get("Type")
    if date >= since and typ in vocab.PLAN_TYPES and vocab.PLAN_TYPES[typ] != letter.upper():
        findings.append(Finding("ERROR", "BUNDLE-ID-LETTER", rel, f"Type {typ} 的首字母应为 {vocab.PLAN_TYPES[typ]}"))
    names = {p.name for p in bundle.iterdir() if not p.name.startswith(".")}
    for name in sorted(names - vocab.BUNDLE_STANDARD):
        if not vocab.BUNDLE_OPTIONAL_RE.match(name) and f"{bundle.name}/{name}" not in exceptions:
            findings.append(Finding("ERROR", "BUNDLE-FILE", f"{rel}/{name}", "不在 bundle 文件白名单；脚本放 scripts/"))
    status = meta.get("Status")
    if status in vocab.RECORD_REQUIRED_STATUSES:
        if "design.md" in names:
            lacking = [n for n in ("implementation.md", "test-cases.md") if n not in names]
            if lacking:
                findings.append(Finding("ERROR", "BUNDLE-RECORD", rel, f"标准形态状态 {status} 缺 {', '.join(lacking)}"))
        elif vocab.RECORD_HEADING not in text.splitlines():
            findings.append(Finding(
                "ERROR", "BUNDLE-RECORD", f"{rel}/requirements.md",
                f"轻量形态状态 {status} 缺「{vocab.RECORD_HEADING}」节",
            ))
    return findings
