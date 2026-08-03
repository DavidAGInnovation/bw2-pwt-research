#!/usr/bin/env python3
"""Locate the PWT state/reception script in a Gen-V script NARC.

This is a static scanner; it does not need an emulator or a ROM image in
memory.  Give it an extracted retail ``/a/0/5/6`` NARC (or the development
``/a/0/5/9`` NARC).  It looks for the distinctive CMD_3EA record-ID sequence
used by the introductory/current Driftveil state and reports the member and
member-relative offsets.  The command parser is deliberately conservative:
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
# After the eighth getter, the script pushes the accumulator (0x8055),
# pushes literal 1, compares them with StackCmp(1), and conditionally skips
# to the alternate message.  Keeping this byte pattern here prevents the
# scanner from treating an unrelated eight-ID run as the state gate.
FINAL_GATE = bytes.fromhex(
    "0900558008000100110001001f00ff2c000000"
)


def narc_members(blob: bytes) -> list[bytes]:
    """Return raw NARC members, preserving each member's script header."""

    btaf = blob.find(b"BTAF")
    gmif = blob.find(b"GMIF")
    if btaf < 0 or gmif < 0:
        raise ValueError("input is not a NARC (BTAF/GMIF block missing)")
    count = struct.unpack_from("<H", blob, btaf + 8)[0]
    starts = [
        struct.unpack_from("<I", blob, btaf + 0x0C + 8 * i)[0]
        for i in range(count)
    ]
    ends = starts[1:] + [struct.unpack_from("<I", blob, btaf + 0x0C + 8 * count)[0]]
    data_start = gmif + 8
    return [blob[data_start + start : data_start + end] for start, end in zip(starts, ends)]


def find_candidate(data: bytes, max_gap: int, message_window: int):
    """Yield (command offsets, message-113 offset, message-114 offset).

    The final tuple member is the literal gate shape used by the retail and
    development scripts: the accumulator at ``0x8055`` is compared with
    ``1`` before the two message branches.  The script VM's documented
    comparison mode 1 is ``!=``; the ``0xFF`` jump tests that comparison
    result, so the first message is reached only when the accumulator equals
    one.
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
        gate = data.find(FINAL_GATE, offsets[-1] + len(CMD_GET) + 2, end)
        if msg113 >= 0 and msg114 >= 0 and gate >= 0:
            yield offsets, msg113, msg114, gate
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
        for offsets, msg113, msg114, gate in find_candidate(
            member, args.max_gap, args.message_window
        ):
            found = True
            print(
                f"member {member_id}: CMD_3EA offsets "
                + ", ".join(f"0x{x:X}" for x in offsets)
                + f"; CMD_3EB(113)=0x{msg113:X}; CMD_3EB(114)=0x{msg114:X}"
                + f"; final accumulator gate (0x8055 == 1) at 0x{gate:X}"
            )
    if not found:
        print("no matching PWT state script found")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
