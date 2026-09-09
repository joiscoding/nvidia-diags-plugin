#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

SUPPORTED_KINDS = {"step", "gate"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def read_blocks(path: Path) -> list[tuple[str, str]]:
    root = ET.parse(path).getroot()
    blocks: list[tuple[str, str]] = []

    for element in root.iter():
        kind = local_name(element.tag)
        block_id = element.get("id")
        if kind in SUPPORTED_KINDS and block_id:
            blocks.append((kind, block_id))

    return blocks


def nearest_existing(
    blocks: list[tuple[str, str]],
    start: int,
    target: set[tuple[str, str]],
    direction: int,
) -> tuple[str, str] | None:
    index = start + direction
    while 0 <= index < len(blocks):
        if blocks[index] in target:
            return blocks[index]
        index += direction
    return None


def format_block(block: tuple[str, str] | None) -> str:
    if block is None:
        return "file boundary"
    return f"{block[0]}:{block[1]}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List sibling step/gate IDs missing from a target XML recipe."
    )
    parser.add_argument("sibling", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    sibling = read_blocks(args.sibling)
    target = read_blocks(args.target)
    target_set = set(target)

    missing = [
        (index, block)
        for index, block in enumerate(sibling)
        if block not in target_set
    ]

    if not missing:
        print("No sibling step or gate IDs are missing from the target.")
        return 0

    for index, block in missing:
        before = nearest_existing(sibling, index, target_set, -1)
        after = nearest_existing(sibling, index, target_set, 1)
        print(
            f"MISSING {format_block(block)} "
            f"between {format_block(before)} and {format_block(after)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
