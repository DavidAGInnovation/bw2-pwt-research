from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import find_pwt_menu_builder as menu_builder  # noqa: E402
import find_pwt_state_script as state_script  # noqa: E402
import inspect_wbt_table as wbt_table  # noqa: E402


def make_narc(members: list[bytes]) -> bytes:
    """Build the minimal NARC structure consumed by the scanners."""

    btaf = bytearray(0x0C + 8 * len(members))
    btaf[:4] = b"BTAF"
    struct.pack_into("<H", btaf, 8, len(members))

    payload = bytearray()
    for index, member in enumerate(members):
        start = len(payload)
        payload.extend(member)
        struct.pack_into("<II", btaf, 0x0C + 8 * index, start, len(payload))

    gmif = b"GMIF" + struct.pack("<I", 8 + len(payload)) + payload
    return bytes(btaf) + gmif


def make_menu_member() -> bytes:
    member = bytearray()
    for candidate in menu_builder.EXPECTED:
        block = bytearray(menu_builder.BLOCK_SIZE)
        block[:2] = menu_builder.CMD_GET
        struct.pack_into("<H", block, 2, candidate)
        struct.pack_into("<H", block, 4, 0x8010)
        block[6:14] = menu_builder.CMD_IF_PREFIX
        block[0x19:0x1B] = b"\xab\x00"
        struct.pack_into("<H", block, 0x1B, 0x20 + candidate)
        struct.pack_into("<H", block, 0x1D, 0xFFFF)
        struct.pack_into("<H", block, 0x1F, candidate)
        member.extend(block)
    return bytes(member)


class ScannerTests(unittest.TestCase):
    def test_wbt_constructor_pool_decoder(self) -> None:
        table = bytearray(wbt_table.TABLE_SIZE)
        # Synthetic rows exercising the Rental and Rental Master masks and
        # the low-three-bit constructor pool field.
        table[0 * 16 + wbt_table.MASK_OFFSET] = 0x08
        table[0 * 16 + wbt_table.FAMILY_OFFSET] = 0x05
        table[0 * 16 + wbt_table.POOL_OFFSET] = 0x03
        table[1 * 16 + wbt_table.MASK_OFFSET] = 0x20
        table[1 * 16 + wbt_table.FAMILY_OFFSET] = 0x05
        table[1 * 16 + wbt_table.POOL_OFFSET] = 0x03
        table[2 * 16 + wbt_table.MASK_OFFSET] = 0x08
        table[2 * 16 + wbt_table.POOL_OFFSET] = 0x02
        table[3 * 16 + wbt_table.MASK_OFFSET] = 0x08
        table[3 * 16 + wbt_table.POOL_OFFSET] = 0x01

        self.assertEqual(wbt_table.candidate_indices(bytes(table), 12), [0, 2, 3])
        self.assertEqual(wbt_table.candidate_indices(bytes(table), 13), [1])
        self.assertEqual(wbt_table.pool_indices(bytes(table), 12, 3), [0])
        self.assertEqual(wbt_table.compact_indices([0, 1, 2, 5, 7, 8]), "0–2, 5, 7–8")

    def test_narc_and_menu_builder(self) -> None:
        members = menu_builder.narc_members(make_narc([make_menu_member()]))
        self.assertEqual(len(members), 1)
        result = menu_builder.find_builder(members[0])
        self.assertIsNotNone(result)
        self.assertEqual(
            [candidate for _, candidate, _, _ in result],
            list(menu_builder.EXPECTED),
        )

    def test_state_signature(self) -> None:
        data = bytearray()
        for record_id in state_script.IDS:
            data.extend(state_script.CMD_GET)
            data.extend(struct.pack("<H", record_id))
        data.extend(b"\x00" * 4)
        signature_offset = len(data)
        data.extend(state_script.BRANCH_SIGNATURE)
        message_113_offset = len(data)
        data.extend(state_script.CMD_MESSAGE_113)
        data.extend(b"\x00" * 3)
        message_114_offset = len(data)
        data.extend(state_script.CMD_MESSAGE_114)

        found = list(
            state_script.find_candidate(bytes(data), max_gap=0x40, message_window=0x800)
        )
        self.assertEqual(len(found), 1)
        offsets, found_113, found_114, found_signature = found[0]
        self.assertEqual(offsets[0], 0)
        self.assertEqual(found_113, message_113_offset)
        self.assertEqual(found_114, message_114_offset)
        self.assertEqual(found_signature, signature_offset)

    def test_invalid_narc_is_a_cli_error(self) -> None:
        with tempfile.NamedTemporaryFile() as invalid:
            invalid.write(b"not a NARC")
            invalid.flush()
            for script in ("find_pwt_menu_builder.py", "find_pwt_state_script.py"):
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / script), invalid.name],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 2, msg=result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
