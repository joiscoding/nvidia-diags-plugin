#!/usr/bin/env python3

import argparse
import collections
import xml.etree.ElementTree as ET
from pathlib import Path

BLOCK_KINDS = {"step", "gate"}
TRANSITIONS = ("on_pass", "on_fail", "on_skip")
TERMINALS = {"stop"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate direct on_pass/on_fail/on_skip targets in an XML recipe."
    )
    parser.add_argument("recipe", type=Path)
    parser.add_argument(
        "--allow-target",
        action="append",
        default=[],
        help="Allow an additional terminal transition value.",
    )
    args = parser.parse_args()

    root = ET.parse(args.recipe).getroot()
    blocks = [
        element
        for element in root.iter()
        if local_name(element.tag) in BLOCK_KINDS
    ]

    errors: list[str] = []
    block_ids = [element.get("id") for element in blocks if element.get("id")]
    counts = collections.Counter(block_ids)

    for element in blocks:
        if not element.get("id"):
            errors.append(f"<{local_name(element.tag)}> is missing an id")

    for block_id, count in counts.items():
        if count > 1:
            errors.append(f"duplicate id: {block_id}")

    known_ids = set(block_ids)
    allowed_targets = TERMINALS | set(args.allow_target)

    for element in blocks:
        source = element.get("id", f"<{local_name(element.tag)} without id>")
        for attribute in TRANSITIONS:
            destination = element.get(attribute)
            if not destination or destination in allowed_targets:
                continue
            if destination not in known_ids:
                errors.append(
                    f"{source} has unresolved {attribute} target: {destination}"
                )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(
        f"PASS: {len(known_ids)} IDs are unique and all direct transitions resolve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
