#!/usr/bin/env python3
"""Inspect-only scope check for a fail-fix change. Never modifies files.

Answers the reviewer's questions about a proposed harness fix:

  * Did the public signature of the fixed function survive? (name, parameter
    names, order, kinds, defaults, annotations)
  * Were any top-level functions or classes removed or renamed?
  * Did the change stay inside the allow-listed files?
  * Was any recipe / SKU XML touched?
  * How big is the change, really?

Usage:
    check_fix_scope.py --before OLD.py --after NEW.py --function NAME \
        [--changed PATH ...] [--allow PATH ...] [--json]

    --before/--after   the harness module before and after the fix (paths to
                       two files; use `git show <base>:<path> > /tmp/before.py`
                       to get the before copy from a git repo)
    --function         the function whose public signature must not change
                       (repeatable)
    --changed          every file the change touches, e.g. from
                       `git diff --name-only <base>`
    --allow            files a fail-fix is allowed to touch (the harness module
                       and its focused test). Any --changed file outside this
                       list is a violation.

Exit codes:
    0  OK, all checks passed
    1  one or more violations (details printed)
    2  usage / parse error
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import sys
from pathlib import Path

XML_SUFFIXES = {".xml", ".xsd"}
RECIPE_HINTS = ("recipe", "sku")


def _signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
    a = fn.args

    def p(arg: ast.arg, kind: str, default: ast.expr | None) -> dict:
        return {
            "name": arg.arg,
            "kind": kind,
            "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
            "default": ast.unparse(default) if default is not None else None,
        }

    params: list[dict] = []
    pos_defaults = [None] * (len(a.posonlyargs) + len(a.args) - len(a.defaults)) + list(a.defaults)
    for arg, d in zip(a.posonlyargs, pos_defaults[: len(a.posonlyargs)]):
        params.append(p(arg, "positional-only", d))
    for arg, d in zip(a.args, pos_defaults[len(a.posonlyargs) :]):
        params.append(p(arg, "positional-or-keyword", d))
    if a.vararg:
        params.append(p(a.vararg, "var-positional", None))
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        params.append(p(arg, "keyword-only", d))
    if a.kwarg:
        params.append(p(a.kwarg, "var-keyword", None))
    return {"name": fn.name, "params": params, "returns": ast.unparse(fn.returns) if fn.returns else None}


def _top_level_defs(tree: ast.Module) -> dict[str, ast.AST]:
    out: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = node
    return out


def check(before_src: str, after_src: str, functions: list[str], changed: list[str], allow: list[str]) -> dict:
    violations: list[str] = []
    notes: list[str] = []

    try:
        before = ast.parse(before_src)
        after = ast.parse(after_src)
    except SyntaxError as e:
        return {"ok": False, "violations": [f"could not parse Python: {e}"], "notes": []}

    bdefs, adefs = _top_level_defs(before), _top_level_defs(after)

    removed = sorted(set(bdefs) - set(adefs))
    if removed:
        violations.append(f"top-level definitions removed or renamed: {', '.join(removed)}")
    added = sorted(set(adefs) - set(bdefs))
    if added:
        notes.append(f"top-level definitions added: {', '.join(added)} (allowed, but a minimal fix usually adds none)")

    for name in functions:
        b, a = bdefs.get(name), adefs.get(name)
        if not isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.append(f"--function {name}: not found as a top-level function in --before")
            continue
        if not isinstance(a, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.append(f"--function {name}: missing from --after (renamed or deleted)")
            continue
        sb, sa = _signature(b), _signature(a)
        if sb != sa:
            violations.append(f"--function {name}: public signature changed\n    before: {json.dumps(sb)}\n    after:  {json.dumps(sa)}")
        else:
            notes.append(f"{name}: public signature preserved")
        if ast.dump(b) == ast.dump(a):
            notes.append(f"{name}: body unchanged (is this the function you meant to fix?)")

    # Unchanged neighbors should stay byte-identical at the AST level.
    for name in sorted(set(bdefs) & set(adefs)):
        if name in functions:
            continue
        if ast.dump(bdefs[name]) != ast.dump(adefs[name]):
            violations.append(f"neighbor '{name}' was modified but is not listed in --function; a minimal fix leaves neighbors alone")

    diff = list(difflib.unified_diff(before_src.splitlines(), after_src.splitlines(), lineterm="", n=0))
    plus = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    minus = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    notes.append(f"module diff: +{plus} / -{minus} lines")
    if plus + minus > 20:
        violations.append(f"module diff is {plus + minus} lines; a fail-fix should be a handful. Reformatting or cleanup mixed in?")

    allow_set = {Path(a).as_posix() for a in allow}
    for c in changed:
        cp = Path(c)
        if cp.suffix.lower() in XML_SUFFIXES or any(h in cp.as_posix().lower() for h in RECIPE_HINTS):
            violations.append(f"recipe/SKU/XML file touched: {c}. fail-fix never rewrites recipe or SKU definitions.")
        elif allow_set and cp.as_posix() not in allow_set:
            violations.append(f"file outside allow-list touched: {c}")
    if changed:
        notes.append(f"changed files: {', '.join(changed)}")

    return {"ok": not violations, "violations": violations, "notes": notes}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True, type=Path)
    ap.add_argument("--after", required=True, type=Path)
    ap.add_argument("--function", action="append", default=[], required=True)
    ap.add_argument("--changed", action="append", default=[])
    ap.add_argument("--allow", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        before_src = args.before.read_text(encoding="utf-8")
        after_src = args.after.read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    result = check(before_src, after_src, args.function, args.changed, args.allow)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("fail-fix scope check:", "OK" if result["ok"] else "VIOLATIONS")
        for n in result["notes"]:
            print(f"  note: {n}")
        for v in result["violations"]:
            print(f"  VIOLATION: {v}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
