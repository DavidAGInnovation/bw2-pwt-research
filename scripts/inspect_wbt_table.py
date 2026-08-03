#!/usr/bin/env python3
"""Decode the built-in WBT constructor pools from an extracted table.

The input may be the extracted one-member WBT NARC (for example the
development ``/a/2/6/1`` artifact) or its 2048-byte member.  This is a static
table decoder; it does not require a ROM emulator or the proprietary source
mirror.

Overlay 135 supplies the field meanings used here:

* record byte 5: constructor eligibility mask;
* record byte 6: fixed-family selector for cup IDs 1 and 5--9;
* record byte 7: Type Expert ``type_tournament_id``;
* low three bits of record byte 8: internal constructor pool 1--5.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from find_pwt_menu_builder import narc_members


RECORD_SIZE = 16
RECORD_COUNT = 128
TABLE_SIZE = RECORD_SIZE * RECORD_COUNT
MASK_OFFSET = 5
FAMILY_OFFSET = 6
TYPE_OFFSET = 7
POOL_OFFSET = 8

# Overlay-135's predicate at 0x02241874.  IDs 1 and 5--9 compare the family
# selector; these IDs are listed separately because they do not use byte 5.
FAMILY_CUPS = {1, 5, 6, 7, 8, 9}
MASK_BITS = {
    4: 1,
    10: 2,
    11: 0,
    12: 3,
    13: 5,
    14: 4,
    15: 6,
}

MODE_NAMES = {
    4: "Driftveil",
    10: "World Leaders",
    11: "Driftveil event",
    12: "Rental",
    13: "Rental Master",
    14: "Mix",
    15: "Mix Master",
}

REQUESTS = {
    4: {1: 4, 2: 1, 3: 2},
    10: {3: 7},
    11: {1: 4, 3: 1, 4: 1, 5: 1},
    12: {1: 3, 2: 2, 3: 2},
    13: {3: 7},
    14: {1: 3, 2: 2, 3: 2},
    15: {3: 7},
}


def load_table(path: Path) -> bytes:
    """Load and validate a 128-record WBT table from a member or one-member NARC."""

    blob = path.read_bytes()
    if blob.startswith(b"NARC") or b"BTAF" in blob[:0x100]:
        members = narc_members(blob)
        candidates = [member for member in members if len(member) == TABLE_SIZE]
        if len(candidates) != 1:
            raise ValueError(
                f"expected one {TABLE_SIZE}-byte WBT member, found {len(candidates)}"
            )
        blob = candidates[0]
    if len(blob) != TABLE_SIZE:
        raise ValueError(f"expected {TABLE_SIZE} bytes, found {len(blob)}")
    return blob


def records(table: bytes) -> list[bytes]:
    return [table[i : i + RECORD_SIZE] for i in range(0, len(table), RECORD_SIZE)]


def candidate_indices(table: bytes, cup_id: int) -> list[int]:
    rows = records(table)
    if cup_id in FAMILY_CUPS:
        return [i for i, row in enumerate(rows) if row[FAMILY_OFFSET] == cup_id]
    if cup_id == 3:
        return list(range(len(rows)))
    try:
        bit = MASK_BITS[cup_id]
    except KeyError as exc:
        raise ValueError(
            f"cup {cup_id} needs a runtime Type Expert type or is not a supported static pool"
        ) from exc
    return [i for i, row in enumerate(rows) if row[MASK_OFFSET] & (1 << bit)]


def pool_indices(table: bytes, cup_id: int, pool: int) -> list[int]:
    rows = records(table)
    eligible = set(candidate_indices(table, cup_id))
    return [i for i, row in enumerate(rows) if i in eligible and (row[POOL_OFFSET] & 7) == pool]


def compact_indices(indices: list[int]) -> str:
    """Render sorted indices as compact ranges for human-readable evidence."""

    if not indices:
        return "(none)"
    ranges: list[str] = []
    start = previous = indices[0]
    for value in indices[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = value
    ranges.append(str(start) if start == previous else f"{start}–{previous}")
    return ", ".join(ranges)


def format_record(index: int, row: bytes) -> str:
    """Render one complete source row plus the constructor-visible fields."""

    return (
        f"record {index:03d}: {row.hex(' ')} "
        f"mask=0x{row[MASK_OFFSET]:02x} family=0x{row[FAMILY_OFFSET]:02x} "
        f"type=0x{row[TYPE_OFFSET]:02x} pool={row[POOL_OFFSET] & 7}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="WBT table member or one-member NARC")
    parser.add_argument(
        "--cup",
        type=int,
        choices=sorted(MODE_NAMES),
        action="append",
        dest="cups",
        help="static cup ID to print (may be repeated; defaults to all)",
    )
    parser.add_argument(
        "--dump-records",
        action="store_true",
        help="print every complete 16-byte source row and decoded constructor fields",
    )
    args = parser.parse_args()
    try:
        table = load_table(args.table)
    except (OSError, ValueError, struct.error) as exc:
        parser.error(str(exc))

    cups = args.cups or sorted(MODE_NAMES)
    print(
        f"records={RECORD_COUNT} size={RECORD_SIZE} "
        f"fields=mask@{MASK_OFFSET},family@{FAMILY_OFFSET},"
        f"type@{TYPE_OFFSET},pool=byte{POOL_OFFSET}&7"
    )
    rows = records(table)
    if args.dump_records:
        for index, row in enumerate(rows):
            print(format_record(index, row))
    for cup_id in cups:
        eligible = candidate_indices(table, cup_id)
        predicate = (
            f"family == {cup_id}"
            if cup_id in FAMILY_CUPS
            else f"mask bit {MASK_BITS[cup_id]} (0x{1 << MASK_BITS[cup_id]:02x})"
        )
        print(f"cup {cup_id} {MODE_NAMES[cup_id]}: {predicate}; eligible={compact_indices(eligible)}")
        for pool, count in sorted(REQUESTS[cup_id].items()):
            indices = pool_indices(table, cup_id, pool)
            print(f"  pool {pool} request {count}: {compact_indices(indices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
