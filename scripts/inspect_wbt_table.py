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

The source row also carries the runtime identity fields copied by the common
WBT record packer: byte 1 is the sex selector, bytes 2--3 are ``mmdl_id``
(the model/appearance resource ID), and byte 4 is ``btl_tr_type`` (the battle
engine's trainer-type field).  These are distinct from the packed NPC-result
trainer-type flag printed below.

For built-in NPC rows, Overlay 135's row-conversion path also copies raw byte 0
to the packed result category and uses the low three bits of byte 8 as the
packed priority.  The built-in path passes trainer-type flag 0.  These derived
result fields are printed by ``--dump-records``; byte 7 remains a separate
Type Expert constructor field.
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
SEX_OFFSET = 1
MMDL_OFFSET = 2
BTL_TRAINER_TYPE_OFFSET = 4
RESULT_CATEGORY_OFFSET = 0
NPC_TRAINER_TYPE = 0

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


def npc_result_fields(row: bytes) -> tuple[int, int, int]:
    """Return (priority, category, trainer_type) for a built-in NPC row.

    Overlay 135's built-in row converter prepares the common record packer at
    ``0x0224208C`` with ``byte[8] & 7`` as the priority input and ``byte[0]``
    as the packed category.  Its built-in source-table path uses trainer-type
    flag 0; player/download records can use other paths and are outside this
    helper's scope.
    """

    return (
        row[POOL_OFFSET] & 7,
        row[RESULT_CATEGORY_OFFSET],
        NPC_TRAINER_TYPE,
    )


def format_record(index: int, row: bytes) -> str:
    """Render one complete source row plus decoded constructor/result fields."""

    priority, category, trainer_type = npc_result_fields(row)

    return (
        f"record {index:03d}: {row.hex(' ')} "
        f"mask=0x{row[MASK_OFFSET]:02x} family=0x{row[FAMILY_OFFSET]:02x} "
        f"type=0x{row[TYPE_OFFSET]:02x} pool={row[POOL_OFFSET] & 7} "
        f"sex={row[SEX_OFFSET]} mmdl_id=0x{int.from_bytes(row[MMDL_OFFSET:MMDL_OFFSET + 2], 'little'):04x} "
        f"btl_tr_type={row[BTL_TRAINER_TYPE_OFFSET]} "
        f"result_priority={priority} result_category={category} "
        f"npc_trainer_type={trainer_type}"
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
        help=(
            "print every complete 16-byte source row and decoded constructor "
            "and built-in NPC result fields"
        ),
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
        f"type@{TYPE_OFFSET},pool=byte{POOL_OFFSET}&7,"
        f"result_priority=byte{POOL_OFFSET}&7,result_category=byte{RESULT_CATEGORY_OFFSET},"
        f"npc_trainer_type={NPC_TRAINER_TYPE}"
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
