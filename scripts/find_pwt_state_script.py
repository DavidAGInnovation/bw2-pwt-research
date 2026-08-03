#!/usr/bin/env python3
"""Locate the Join Avenue Resort CMD_3EA script in a Gen-V script NARC.

This is a static scanner; it does not need an emulator or a ROM image in
memory.  Give it an extracted retail ``/a/0/5/6`` NARC (or the development
``/a/0/5/9`` NARC).  It looks for a distinctive Resort ``CMD_3EA`` selector
sequence and reports the member and member-relative offsets.  The command
parser is deliberately conservative:
the bytes are only treated as a candidate when all eight IDs occur in order
with small gaps and the nearby script contains CMD_3EB message IDs 113 and
114.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


IDS = (17, 18, 21, 20, 19, 22, 23, 24)
CMD_GET = b"\xea\x03"
CMD_MESSAGE_113 = b"\xeb\x03\x71\x00"
CMD_MESSAGE_114 = b"\xeb\x03\x72\x00"
# The sequence is retained as a reproducible cross-build byte signature. It is
# a Resort/Join Avenue script, not a PWT unlock predicate; the PWT cup-enable
# logic comes from the recovered WBT source in wbt_tool.c.
BRANCH_SIGNATURE = bytes.fromhex(
    "0900558008000100110001001f00ff2c000000"
)


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


def find_candidate(data: bytes, max_gap: int, message_window: int):
    """Yield (command offsets, message-113 offset, message-114 offset).

    The final tuple member is the literal branch shape used by the retail and
    development Resort scripts. It is reported for byte-level reproducibility;
    it is not interpreted here as a PWT unlock condition.
    """

    first = 0
    while True:
        offsets: list[int] = []
        cursor = first
        for record_id in IDS:
            needle = CMD_GET + struct.pack("<H", record_id)
            pos = data.find(needle, cursor)
            if pos < 0 or (offsets and pos - offsets[-1] > max_gap):
                offsets = []
                break
            offsets.append(pos)
            cursor = pos + len(needle)
        if len(offsets) != len(IDS):
            first = data.find(CMD_GET, first + 1)
            if first < 0:
                return
            continue

        end = offsets[-1] + message_window
        msg113 = data.find(CMD_MESSAGE_113, offsets[-1], end)
        msg114 = data.find(CMD_MESSAGE_114, offsets[-1], end)
        signature = data.find(
            BRANCH_SIGNATURE, offsets[-1] + len(CMD_GET) + 2, end
        )
        if msg113 >= 0 and msg114 >= 0 and signature >= 0:
            yield offsets, msg113, msg114, signature
        first = offsets[0] + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("narc", type=Path, help="extracted script NARC")
    parser.add_argument("--max-gap", type=int, default=0x40)
    parser.add_argument("--message-window", type=int, default=0x800)
    args = parser.parse_args()

    members = narc_members(args.narc.read_bytes())
    found = False
    for member_id, member in enumerate(members):
        for offsets, msg113, msg114, signature in find_candidate(
            member, args.max_gap, args.message_window
        ):
            found = True
            print(
                f"member {member_id}: CMD_3EA offsets "
                + ", ".join(f"0x{x:X}" for x in offsets)
                + f"; CMD_3EB(113)=0x{msg113:X}; CMD_3EB(114)=0x{msg114:X}"
                + f"; branch signature at 0x{signature:X}"
            )
    if not found:
        print("no matching Resort CMD_3EA script found")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
