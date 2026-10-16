"""用例主表检查与派生视图生成。"""

from __future__ import annotations

from pathlib import Path

from . import vocab
from .model import Finding, parse_tables

CASES = "docs/testing/cases"
MAIN_ANCHOR = vocab.MAIN_ANCHOR
GENERATED_NOTE = vocab.GENERATED_NOTE


def read_main(root: Path) -> tuple[list[str], int, list[tuple[int, list[str], list[tuple[int, list[str]]]]]]:
    path = root / CASES / "index.md"
    if not path.exists():
        return [], 0, []
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(MAIN_ANCHOR) if MAIN_ANCHOR in lines else len(lines)
    tables = []
    for header_line, header, rows in parse_tables(lines[start:]):
        if header and header[0] == "Case ID":
            tables.append((start + header_line, header, [(start + n, cells) for n, cells in rows]))
    return lines, start, tables


def main_rows(root: Path) -> list[dict[str, str]]:
    _, _, tables = read_main(root)
    rows: list[dict[str, str]] = []
    for _, header, table_rows in tables:
        if header == vocab.CASE_HEADER:
            rows += [dict(zip(header, cells)) for _, cells in table_rows if len(cells) == len(header)]
    return rows


def _view_header(*columns: str) -> str:
    return "| " + " | ".join(columns) + " |"


def render_by_layer(rows: list[dict[str, str]]) -> str:
    out = [vocab.VIEW_BY_LAYER_TITLE, "", GENERATED_NOTE, ""]
    header = _view_header("Case ID", vocab.COL_TITLE, vocab.COL_MODULE, vocab.COL_STATUS)
    for layer in vocab.CASE_LAYERS:
        group = [r for r in rows if r[vocab.COL_LAYER] == layer]
        if not group:
            continue
        out += [f"## {layer}", "", header, "| --- | --- | --- | --- |"]
        out += [
            f"| {r['Case ID']} | {r[vocab.COL_TITLE]} | {r[vocab.COL_MODULE]} | {r[vocab.COL_STATUS]} |"
            for r in group
        ]
        out.append("")
    return "\n".join(out)


def module_of(row: dict[str, str]) -> str:
    return row[vocab.COL_MODULE].split(" / ")[0].strip() or vocab.UNGROUPED


def render_by_module(rows: list[dict[str, str]]) -> str:
    out = [vocab.VIEW_BY_MODULE_TITLE, "", GENERATED_NOTE, ""]
    header = _view_header("Case ID", vocab.COL_TITLE, vocab.COL_LAYER, vocab.COL_STATUS)
    modules: list[str] = []
    for row in rows:
        if module_of(row) not in modules:
            modules.append(module_of(row))
    for module in modules:
        out += [f"## {module}", "", header, "| --- | --- | --- | --- |"]
        out += [
            f"| {r['Case ID']} | {r[vocab.COL_TITLE]} | {r[vocab.COL_LAYER]} | {r[vocab.COL_STATUS]} |"
            for r in rows if module_of(r) == module
        ]
        out.append("")
    return "\n".join(out)


VIEWS = {"by-layer.md": render_by_layer, "by-module.md": render_by_module}


def gen_views(root: Path) -> bool:
    """主表不存在时不生成（返回 False），避免在缺索引的仓库里凭空造出派生视图。"""
    if not (root / CASES / "index.md").exists():
        return False
    rows = main_rows(root)
    for name, render in VIEWS.items():
        (root / CASES / name).write_text(render(rows), encoding="utf-8")
    return True


def check_cases(root: Path, baseline: dict | None = None) -> list[Finding]:
    """baseline 为接入配置；其 case_id_exceptions 列出存量旧格式 Case ID（ID 稳定不可改名）。"""
    exceptions = set((baseline or {}).get("case_id_exceptions", []))
    findings: list[Finding] = []
    rel = f"{CASES}/index.md"
    if not (root / CASES / "index.md").exists():
        return [Finding("ERROR", "CASE-INDEX-MISSING", rel, "missing the global case index")]
    lines, start, tables = read_main(root)
    for n, line in enumerate(lines[:start]):
        if line.startswith("| TC-"):
            findings.append(Finding(
                "ERROR", "CASE-NARRATIVE", f"{rel}:{n + 1}",
                f"case rows may appear only after \"{vocab.MAIN_ANCHOR}\"; put batch narrative in the owner plan",
            ))
    seen: dict[str, int] = {}
    for header_line, header, rows in tables:
        if header != vocab.CASE_HEADER:
            findings.append(Finding("ERROR", "CASE-HEADER", f"{rel}:{header_line + 1}", f"header must be \"{' | '.join(vocab.CASE_HEADER)}\""))
            continue
        for n, cells in rows:
            if len(cells) != len(header):
                findings.append(Finding(
                    "ERROR", "CASE-ROW-COLUMNS", f"{rel}:{n + 1}", f"column count {len(cells)} does not match the header ({len(header)})",
                ))
                continue
            row = dict(zip(header, cells))
            loc = f"{rel}:{n + 1}"
            cid = row.get("Case ID", "")
            if cid not in exceptions and not vocab.CASE_ID_RE.match(cid):
                findings.append(Finding("ERROR", "CASE-ID", loc, f"Case ID \"{cid}\" has an illegal format"))
            elif cid in seen:
                findings.append(Finding("ERROR", "CASE-ID", loc, f"{cid} duplicates the row at line {seen[cid]}"))
            seen.setdefault(cid, n + 1)
            if row.get(vocab.COL_LAYER) not in vocab.CASE_LAYERS:
                findings.append(Finding("ERROR", "CASE-LAYER", loc, f"layer \"{row.get(vocab.COL_LAYER)}\" is not in the vocabulary"))
            if row.get(vocab.COL_STATUS) not in vocab.CASE_STATUSES:
                findings.append(Finding("ERROR", "CASE-STATUS", loc, f"status \"{row.get(vocab.COL_STATUS)}\" is not in the vocabulary"))
    rows_for_views = main_rows(root)
    for name, render in VIEWS.items():
        path = root / CASES / name
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != render(rows_for_views):
            findings.append(Finding("ERROR", "CASE-VIEW-STALE", f"{CASES}/{name}", "does not match the main table; run `python3 scripts/doc-lint.py gen-views`"))
    return findings
