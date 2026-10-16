"""doc-lint 命令行入口。"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from . import cases, onboard, plans, repo_checks, templates, vocab
from .model import Finding

BASELINE = Path(__file__).resolve().parent / "baseline.json"


def load_baseline() -> dict:
    """接入配置；不存在时按新项目处理（无豁免、基线为零、bundle 平铺在 docs/plans/）。"""
    return json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}


def run(root: Path, release: bool = False, baseline: dict | None = None) -> list[Finding]:
    if baseline is None:
        baseline = load_baseline()
    findings: list[Finding] = []
    findings += plans.check_index(root)
    findings += plans.check_bundles(root, baseline)
    findings += cases.check_cases(root, baseline)
    findings += repo_checks.check_links(root, baseline)
    findings += repo_checks.check_naming(root, baseline)
    findings += repo_checks.check_inheritance(root, baseline.get("inherit_pairs", []))
    findings += repo_checks.check_freshness(root, release, repo_checks.latest_tag_date(root), baseline)
    findings += templates.check_templates(root, baseline)
    findings += onboard.check_baseline_stale(root, baseline)
    return findings


def init_baseline(root: Path, bundle_root: str | None, frozen: list[str] | None, write: bool) -> int:
    config, must_fix = onboard.build_baseline(root, load_baseline(), bundle_root, frozen)
    if must_fix:
        for finding in must_fix:
            print("must-fix " + finding.render()[len(finding.level) + 1:])
        print(f"init-baseline: {len(must_fix)} item(s) cannot be exempted; fix them and rerun (did not write {onboard.BASELINE_FILE})")
        return 1
    text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if not write:
        print(text, end="")
        return 0
    BASELINE.write_text(text, encoding="utf-8")
    counts = ", ".join(f"{key} {len(config[key])}" for key in onboard.LIST_KEYS)
    print(f"wrote {onboard.BASELINE_FILE}: broken-link baseline {config['broken_links_total']}, {counts}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="doc-lint", description="Check documentation rules")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--release", action="store_true", help="release-seal mode")
    sub = parser.add_subparsers(dest="command")
    next_parser = sub.add_parser("next-id", help="take the next free Stable ID")
    next_parser.add_argument("--type", required=True, choices=sorted(vocab.PLAN_TYPES))
    next_parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    sub.add_parser("gen-views", help="regenerate by-layer.md and by-module.md")
    init_parser = sub.add_parser("init-baseline", help="onboard an existing tree: register current violations as exemptions")
    init_parser.add_argument("--bundle-root", help=f"bundle root; default keeps the current config, or {onboard.DETECTED_BUNDLE_ROOT} when that directory exists")
    init_parser.add_argument("--frozen", nargs="+", action="extend", metavar="DIR", help="frozen directories (skip template checks)")
    init_parser.add_argument("--write", action="store_true", help=f"write {onboard.BASELINE_FILE}; default is print only")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "next-id":
        base = plans.bundle_root(load_baseline())
        stable_id, directory = repo_checks.next_id(root, args.type, args.date, base)
        print(stable_id)
        print(directory)
        return 0
    if args.command == "gen-views":
        if not cases.gen_views(root):
            print(f"missing {cases.CASES}/index.md: create the case table from the singleton/cases-index.md template, then generate the views")
            return 1
        print(f"regenerated {cases.CASES}/by-layer.md and by-module.md")
        return 0
    if args.command == "init-baseline":
        return init_baseline(root, args.bundle_root, args.frozen, args.write)
    findings = run(root, args.release)
    for finding in findings:
        print(finding.render())
    errors = sum(f.level == "ERROR" for f in findings)
    warnings = sum(f.level == "WARN" for f in findings)
    print(f"doc-lint: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0
