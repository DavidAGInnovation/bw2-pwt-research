#!/usr/bin/env python3
"""Recheck the four original webpage downloads against historical hashes."""

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    audit = json.loads((HERE / "historical-download-verification.json").read_text())
    for record in audit["records"]:
        data = (HERE / "historical-downloads" / record["file"]).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert len(data) == record["size"] == 4884
        assert digest == record["expected_sha256"] == record["actual_sha256"]
        bracket = data[0x11F4:0x1210]
        assert bracket.hex() == record["bracket_hex"]
        assert Counter(bracket[1::4]) == {
            int(key): value for key, value in record["YY_counts"].items()
        }
        github = (HERE / "downloads" / record["github_comparison"]["file"]).read_bytes()
        assert hashlib.sha256(github).hexdigest() == record["github_comparison"]["sha256"]
        assert len(github) == len(data)
        assert github[0x11F4:0x1210] == bracket
        differences = [i for i, (a, b) in enumerate(zip(data, github)) if a != b]
        expected_differences = [
            i
            for start, end in record["github_comparison"]["different_ranges_inclusive"]
            for i in range(int(start, 16), int(end, 16) + 1)
        ]
        assert differences == expected_differences
        assert len(differences) == record["github_comparison"]["different_byte_count"]
        assert all(i >= 0x1210 for i in differences)
        print(f"{record['artifact']}: historical SHA-256 and bracket counts verified")
    assert len(audit["records"]) == audit["verified_artifacts"] == 4


if __name__ == "__main__":
    main()
