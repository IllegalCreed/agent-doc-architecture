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
        return [Finding("ERROR", "PLAN-INDEX-MISSING", INDEX, "missing the change-plan index")]
    header, rows, lines = read_index(root)
    if header != vocab.INDEX_HEADER:
        findings.append(Finding(
            "ERROR", "PLAN-INDEX-HEADER", INDEX,
            f"header must be \"{' | '.join(vocab.INDEX_HEADER)}\", got \"{' | '.join(header)}\"",
        ))
    for n, line in enumerate(lines):
        if line.startswith("> 20"):
            findings.append(Finding("ERROR", "PLAN-INDEX-BANNER", f"{INDEX}:{n + 1}", "date banners are not allowed in the index; move them to the roadmap or the bundle"))
    h1 = next((n for n, line in enumerate(lines) if line.startswith("# ")), None)
    if h1 is not None:
        end = next((n for n in range(h1 + 1, len(lines)) if lines[n].startswith(("## ", "|"))), len(lines))
        preamble = [line for line in lines[h1 + 1:end] if line.strip() and not line.startswith("> 20")]
        if len(preamble) > 1:
            findings.append(Finding(
                "ERROR", "PLAN-INDEX-PREAMBLE", f"{INDEX}:{h1 + 2}",
                f"only one line of preamble is allowed between the H1 and the table, found {len(preamble)}; move progress narrative to the roadmap or the bundle",
            ))
    first_seen: dict[str, int] = {}
    for row in rows:
        loc = f"{INDEX}:{row.line + 1}"
        if row.width != len(header):
            findings.append(Finding("ERROR", "PLAN-ROW-COLUMNS", loc, f"column count {row.width} does not match the header ({len(header)})"))
            continue
        sid = row.cells.get("Stable ID", "")
        if sid in first_seen:
            findings.append(Finding("ERROR", "PLAN-ID-DUP", loc, f"{sid} duplicates the row at line {first_seen[sid]}"))
        first_seen.setdefault(sid, row.line + 1)
        status = row.cells.get(vocab.COL_STATUS, "")
        if status not in vocab.PLAN_STATUSES:
            findings.append(Finding("ERROR", "PLAN-STATUS", loc, f"status \"{status}\" is not in the vocabulary"))
        typ = row.cells.get("Type", "")
        if typ not in vocab.PLAN_TYPES:
            findings.append(Finding("ERROR", "PLAN-TYPE", loc, f"type \"{typ}\" is not in the vocabulary"))
        if len(row.cells.get(vocab.COL_TITLE, "")) > vocab.TITLE_MAX:
            findings.append(Finding("ERROR", "PLAN-TITLE-LEN", loc, f"title exceeds {vocab.TITLE_MAX} characters"))
        if len(row.cells.get(vocab.COL_NEXT, "")) > vocab.NEXT_MAX:
            findings.append(Finding("ERROR", "PLAN-NEXT-LEN", loc, f"next step exceeds {vocab.NEXT_MAX} characters"))
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
    known_ids = {row.cells.get("Stable ID") for row in rows}
    for bundle in sorted(candidates):
        findings += _check_bundle(bundle, base, registered.get(bundle.name), exceptions, since, known_ids)
    return findings


def _check_bundle(
    bundle: Path, base: str, row: IndexRow | None, exceptions: set[str], since: str, known_ids: set[str | None],
) -> list[Finding]:
    """since 为接入配置里的规则生效日期；空串表示新项目，全部严格检查。"""
    rel = f"{base}/{bundle.name}"
    match = vocab.BUNDLE_DIR_RE.match(bundle.name)
    if not match:
        return [Finding("ERROR", "BUNDLE-NAME", rel, "directory name must be YYYYMMDD-<letter>NNN-<slug>")]
    findings: list[Finding] = []
    if row is None:
        findings.append(Finding("ERROR", "BUNDLE-UNREGISTERED", rel, f"not registered in {INDEX}"))
    requirements = bundle / "requirements.md"
    if not requirements.exists():
        return findings + [Finding("ERROR", "BUNDLE-META-MISSING", rel, "missing requirements.md")]
    text = requirements.read_text(encoding="utf-8")
    meta = parse_meta(text)
    missing = [key for key in vocab.META_REQUIRED if key not in meta]
    if missing:
        findings.append(Finding("ERROR", "BUNDLE-META-MISSING", f"{rel}/requirements.md", f"metadata missing {', '.join(missing)}"))
    date, letter, number = match.groups()
    expected_id = f"{letter.upper()}-{date}-{number}"
    if meta.get("Stable ID", expected_id) != expected_id:
        findings.append(Finding(
            "ERROR", "BUNDLE-META-MISMATCH", f"{rel}/requirements.md",
            f"Stable ID {meta['Stable ID']} does not match {expected_id} derived from the directory",
        ))
    if row is not None:
        if row.cells.get("Stable ID") != expected_id:
            findings.append(Finding(
                "ERROR", "BUNDLE-META-MISMATCH", rel,
                f"index Stable ID {row.cells.get('Stable ID')} does not match {expected_id} derived from the directory",
            ))
        for key, column in (("Status", vocab.COL_STATUS), ("Type", "Type")):
            if key in meta and meta[key] != row.cells.get(column):
                findings.append(Finding(
                    "ERROR", "BUNDLE-META-MISMATCH", f"{rel}/requirements.md",
                    f"metadata {key}={meta[key]} does not match the index value {row.cells.get(column)}",
                ))
    typ = meta.get("Type")
    if date >= since and typ in vocab.PLAN_TYPES and vocab.PLAN_TYPES[typ] != letter.upper():
        findings.append(Finding("ERROR", "BUNDLE-ID-LETTER", rel, f"type {typ} must use initial letter {vocab.PLAN_TYPES[typ]}"))
    names = {p.name for p in bundle.iterdir() if not p.name.startswith(".")}
    for name in sorted(names - vocab.BUNDLE_STANDARD):
        if not vocab.BUNDLE_OPTIONAL_RE.match(name) and f"{bundle.name}/{name}" not in exceptions:
            findings.append(Finding("ERROR", "BUNDLE-FILE", f"{rel}/{name}", "not on the bundle file allowlist; put scripts in scripts/"))
    status = meta.get("Status")
    if status == "superseded" and date >= since:
        successors = re.findall(r"[A-Z]-\d{8}-\d{3}", meta.get("Replaced by", ""))
        if not successors or any(s not in known_ids for s in successors):
            findings.append(Finding(
                "ERROR", "BUNDLE-SUPERSEDE", f"{rel}/requirements.md",
                "a superseded document's Replaced by must be a successor Stable ID registered in the index",
            ))
    if status in vocab.RECORD_REQUIRED_STATUSES:
        if "design.md" in names:
            lacking = [n for n in ("implementation.md", "test-cases.md") if n not in names]
            if lacking:
                findings.append(Finding("ERROR", "BUNDLE-RECORD", rel, f"standard shape at status {status} is missing {', '.join(lacking)}"))
        elif vocab.RECORD_HEADING not in text.splitlines():
            findings.append(Finding(
                "ERROR", "BUNDLE-RECORD", f"{rel}/requirements.md",
                f"lightweight shape at status {status} is missing the \"{vocab.RECORD_HEADING}\" section",
            ))
    return findings
