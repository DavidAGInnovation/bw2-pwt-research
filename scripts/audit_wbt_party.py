"""Check the disassembly signatures used by the WBT party-selection note."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DISASSEMBLY = ROOT.parent / "disassembly" / "ov55.dis"


EVIDENCE = (
    ("six-entry request", "0x0223975a", r"movs r1, 6"),
    ("six-entry output loop", "0x022397e6", r"cmp r5, 6"),
    ("battle-rule field", "0x022395ba", r"0x13e4"),
    ("rule branch 0", "0x022395c0", r"cmp r0, 0"),
    ("rule branch 1", "0x022395c4", r"cmp r0, 1"),
    ("rule branch 2", "0x022395c8", r"cmp r0, 2"),
    ("three-entry split", "0x0223964c", r"movs r0, 3"),
    ("remainder split", "0x02239682", r"subs r0, r4, 3"),
    ("available-record count", "0x02239280", r"push"),
    ("ordinal-to-index mapping", "0x022392c4", r"push"),
    ("remove selected record", "0x0223933c", r"strb r1, \[r0, r4\]"),
    ("RNG call", "0x022393aa", r"bl 0x2238f94"),
    ("reduce by available count", "0x022393b0", r"blx 0x20acca4"),
    ("selection loop", "0x022393f4", r"cmp r4, r0"),
    ("party-size getter", "0x022387fc", r"push"),
    ("party-size table load", "0x02238804", r"0x2239b36"),
    ("single party-size entry", "0x02239b36", r"0300"),
    ("double party-size entry", "0x02239b3e", r"0400"),
    ("triple party-size entry", "0x02239b46", r"0600"),
    ("rotation party-size entry", "0x02239b4e", r"0400"),
)


def audit_text(text: str) -> list[str]:
    """Return the names of evidence signatures missing from *text*."""

    by_address = {}
    for line in text.splitlines():
        # Radare2 prefixes branch targets with box-drawing glyphs, so the
        # address is not necessarily the first non-whitespace token.
        match = re.search(r"(0x[0-9a-f]+)\s+.*$", line, re.IGNORECASE)
        if match:
            by_address[match.group(1).lower()] = line.lower()

    missing = []
    for name, address, pattern in EVIDENCE:
        line = by_address.get(address)
        if line is None or re.search(pattern, line, re.IGNORECASE) is None:
            missing.append(name)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "disassembly",
        nargs="?",
        type=Path,
        default=DEFAULT_DISASSEMBLY,
        help=f"Overlay 55 disassembly (default: {DEFAULT_DISASSEMBLY})",
    )
    args = parser.parse_args()
    try:
        text = args.disassembly.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    missing = audit_text(text)
    if missing:
        print("FAIL: missing signatures: " + ", ".join(missing))
        return 1
    print(f"PASS: {len(EVIDENCE)} WBT party-selection signatures found in {args.disassembly}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
