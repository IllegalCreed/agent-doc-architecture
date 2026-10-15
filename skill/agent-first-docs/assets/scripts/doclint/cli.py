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
        print(f"init-baseline: {len(must_fix)} 项不可豁免，先修复再重跑（未写入 {onboard.BASELINE_FILE}）")
        return 1
    text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if not write:
        print(text, end="")
        return 0
    BASELINE.write_text(text, encoding="utf-8")
    counts = "，".join(f"{key} {len(config[key])} 条" for key in onboard.LIST_KEYS)
    print(f"已写入 {onboard.BASELINE_FILE}：断链基线 {config['broken_links_total']}，{counts}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="doc-lint", description="文档规则检查")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--release", action="store_true", help="封板模式")
    sub = parser.add_subparsers(dest="command")
    next_parser = sub.add_parser("next-id", help="取下一个未占用的 Stable ID")
    next_parser.add_argument("--type", required=True, choices=sorted(vocab.PLAN_TYPES))
    next_parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    sub.add_parser("gen-views", help="重新生成 by-layer.md / by-module.md")
    init_parser = sub.add_parser("init-baseline", help="存量项目接入：把当前违规登记为豁免，生成接入配置")
    init_parser.add_argument("--bundle-root", help=f"bundle 根目录；缺省沿用现有配置，否则 {onboard.DETECTED_BUNDLE_ROOT} 存在时用它")
    init_parser.add_argument("--frozen", nargs="+", action="extend", metavar="DIR", help="冻结目录（不做模板检查）")
    init_parser.add_argument("--write", action="store_true", help=f"写入 {onboard.BASELINE_FILE}；缺省只打印")
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
            print(f"缺 {cases.CASES}/index.md：先从模板 singleton/cases-index.md 建用例主表，再生成视图")
            return 1
        print(f"已重新生成 {cases.CASES}/by-layer.md、by-module.md")
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
