#!/usr/bin/env python3
"""Verify the built-in PWT menu's dynamic cup-ID producer.

The script works on an extracted ``/a/0/5/9`` development NARC or retail
``/a/0/5/6`` NARC.  It recognizes the repeated member-1277 command shape:
``CMD_3EE(candidate, 0x8010)`` followed by a conditional ``ListMenuAdd`` whose
UID is the same candidate.  This is static byte analysis; an emulator is not
required.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


CMD_GET = b"\xee\x03"
CMD_IF_PREFIX = bytes.fromhex("0900108008000100")
LIST_MENU_ADD_OPCODES = {b"\xab\x00", b"\xaf\x00"}
EXPECTED = (11, 4, 5, 6, 7, 8, 9, 10, 1, 13, 15, 2, 12, 14, 3)
BLOCK_SIZE = 0x21


def narc_members(blob: bytes) -> list[bytes]:
    """Return raw NARC members, preserving each member's script header."""

    btaf = blob.find(b"BTAF")
    gmif = blob.find(b"GMIF")
    if btaf < 0 or gmif < 0:
        raise ValueError("input is not a NARC (BTAF/GMIF block missing)")
    count = struct.unpack_from("<H", blob, btaf + 8)[0]
    entries = [
        struct.unpack_from("<II", blob, btaf + 0x0C + 8 * i)
        for i in range(count)
    ]
    data_start = gmif + 8
    gmif_size = struct.unpack_from("<I", blob, gmif + 4)[0]
    if gmif_size < 8 or gmif + gmif_size > len(blob):
        raise ValueError("invalid GMIF block size")
    payload_size = gmif_size - 8
    for start, end in entries:
        if start > end or end > payload_size:
            raise ValueError("NARC member range exceeds GMIF payload")
    return [blob[data_start + start : data_start + end] for start, end in entries]


def find_builder(member: bytes):
    """Return the candidate blocks if this member contains the menu builder."""

    for start in range(len(member)):
        if member[start : start + 2] != CMD_GET:
            continue
        blocks = []
        cursor = start
        for candidate in EXPECTED:
            block = member[cursor : cursor + BLOCK_SIZE]
            if (
                len(block) != BLOCK_SIZE
                or block[:2] != CMD_GET
                or struct.unpack_from("<H", block, 2)[0] != candidate
                or struct.unpack_from("<H", block, 4)[0] != 0x8010
                or block[6:14] != CMD_IF_PREFIX
                or block[0x19:0x1B] not in LIST_MENU_ADD_OPCODES
                or struct.unpack_from("<H", block, 0x1D)[0] != 0xFFFF
                or struct.unpack_from("<H", block, 0x1F)[0] != candidate
            ):
                break
            blocks.append((cursor, candidate, block[0x19:0x1B], struct.unpack_from("<H", block, 0x1B)[0]))
            cursor += BLOCK_SIZE
        if len(blocks) == len(EXPECTED):
            return blocks
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("narc", type=Path, help="extracted script NARC")
    args = parser.parse_args()

    try:
        members = narc_members(args.narc.read_bytes())
    except (OSError, ValueError, struct.error) as exc:
        parser.error(str(exc))
    for member_id, member in enumerate(members):
        blocks = find_builder(member)
        if blocks is None:
            continue
        print(f"member {member_id}: {len(blocks)} availability blocks")
        for offset, candidate, opcode, option in blocks:
            print(
                f"  0x{offset:04X}: CMD_3EE({candidate}, 0x8010); "
                f"{opcode.hex()} ListMenuAdd(option=0x{option:04X}, "
                f"hint=0xFFFF, uid={candidate})"
            )
        return 0
    print("no PWT menu-builder sequence found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
