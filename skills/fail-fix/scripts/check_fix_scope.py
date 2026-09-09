#!/usr/bin/env python3

import argparse
import ast
import difflib
import json
from pathlib import Path

XML_SUFFIXES = {".xml", ".xsd"}
RECIPE_HINTS = ("recipe", "sku")


def param(arg: ast.arg, kind: str, default: ast.expr | None) -> dict:
    return {
        "name": arg.arg,
        "kind": kind,
        "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
        "default": ast.unparse(default) if default is not None else None,
    }


def signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
    args = fn.args
    pos_defaults = [None] * (
        len(args.posonlyargs) + len(args.args) - len(args.defaults)
    ) + list(args.defaults)

    params = []
    for arg, default in zip(args.posonlyargs, pos_defaults[: len(args.posonlyargs)]):
        params.append(param(arg, "positional-only", default))
    for arg, default in zip(args.args, pos_defaults[len(args.posonlyargs) :]):
        params.append(param(arg, "positional-or-keyword", default))
    if args.vararg:
        params.append(param(args.vararg, "var-positional", None))
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        params.append(param(arg, "keyword-only", default))
    if args.kwarg:
        params.append(param(args.kwarg, "var-keyword", None))

    return {
        "name": fn.name,
        "params": params,
        "returns": ast.unparse(fn.returns) if fn.returns else None,
    }


def top_level_defs(tree: ast.Module) -> dict[str, ast.AST]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def check(
    before_src: str,
    after_src: str,
    functions: list[str],
    changed: list[str],
    allow: list[str],
) -> dict:
    violations: list[str] = []
    notes: list[str] = []

    before_defs = top_level_defs(ast.parse(before_src))
    after_defs = top_level_defs(ast.parse(after_src))

    removed = sorted(set(before_defs) - set(after_defs))
    if removed:
        violations.append(
            f"top-level definitions removed or renamed: {', '.join(removed)}"
        )

    added = sorted(set(after_defs) - set(before_defs))
    if added:
        notes.append(f"top-level definitions added: {', '.join(added)}")

    for name in functions:
        before_fn = before_defs.get(name)
        after_fn = after_defs.get(name)
        if not isinstance(before_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.append(
                f"--function {name}: not found as a top-level function in --before"
            )
            continue
        if not isinstance(after_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.append(f"--function {name}: missing from --after")
            continue

        before_sig = signature(before_fn)
        after_sig = signature(after_fn)
        if before_sig != after_sig:
            violations.append(
                f"--function {name}: public signature changed\n"
                f"    before: {json.dumps(before_sig)}\n"
                f"    after:  {json.dumps(after_sig)}"
            )
        else:
            notes.append(f"{name}: public signature preserved")

        if ast.dump(before_fn) == ast.dump(after_fn):
            notes.append(f"{name}: body unchanged")

    for name in sorted(set(before_defs) & set(after_defs)):
        if name in functions:
            continue
        if ast.dump(before_defs[name]) != ast.dump(after_defs[name]):
            violations.append(f"neighbor '{name}' was modified")

    diff = list(
        difflib.unified_diff(
            before_src.splitlines(), after_src.splitlines(), lineterm="", n=0
        )
    )
    plus = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    minus = sum(
        1 for line in diff if line.startswith("-") and not line.startswith("---")
    )
    notes.append(f"module diff: +{plus} / -{minus} lines")
    if plus + minus > 20:
        violations.append(f"module diff is {plus + minus} lines")

    allow_set = {Path(path).as_posix() for path in allow}
    for path in changed:
        changed_path = Path(path)
        posix = changed_path.as_posix().lower()
        if changed_path.suffix.lower() in XML_SUFFIXES or any(
            hint in posix for hint in RECIPE_HINTS
        ):
            violations.append(f"recipe/SKU/XML file touched: {path}")
        elif allow_set and changed_path.as_posix() not in allow_set:
            violations.append(f"file outside allow-list touched: {path}")
    if changed:
        notes.append(f"changed files: {', '.join(changed)}")

    return {"ok": not violations, "violations": violations, "notes": notes}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect-only scope check for a fail-fix harness change."
    )
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--function", action="append", default=[], required=True)
    parser.add_argument("--changed", action="append", default=[])
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = check(
        args.before.read_text(encoding="utf-8"),
        args.after.read_text(encoding="utf-8"),
        args.function,
        args.changed,
        args.allow,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("fail-fix scope check:", "OK" if result["ok"] else "VIOLATIONS")
        for note in result["notes"]:
            print(f"  note: {note}")
        for violation in result["violations"]:
            print(f"  VIOLATION: {violation}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
