#!/usr/bin/env python3
"""Print the seven bracket records and YY histogram from a BW2 .pwt file."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument(
        "--offset",
        type=lambda value: int(value, 0),
        default=0x11F4,
        help="byte offset of the first bracket record (default: 0x11f4)",
    )
    args = parser.parse_args()

    data = args.file.read_bytes()
    end = args.offset + 7 * 4
    if args.offset < 0 or end > len(data):
        raise SystemExit("offset does not leave room for seven four-byte records")

    records = [
        tuple(data[args.offset + 4 * i : args.offset + 4 * (i + 1)])
        for i in range(7)
    ]
    counts = Counter(record[1] for record in records)

    for index, record in enumerate(records, start=1):
        print(f"record {index}: {' '.join(f'{byte:02X}' for byte in record)}")
    print("YY counts:", " ".join(f"{yy}={counts.get(yy, 0)}" for yy in range(6)))


if __name__ == "__main__":
    main()
