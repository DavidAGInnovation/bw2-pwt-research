#!/usr/bin/env python3
"""Decode the built-in WBT normal party tables to CSV.

The normal (non-Rental) opponent parties live in three table sets. Each set is
a trainer-header NARC, a trainer party-index NARC, and a Pokémon-record NARC;
the USA/Europe retail paths are:

* ``wbt1``: ``/a/2/4/8``, ``/a/2/4/9``, ``/a/2/5/0`` (Driftveil, Driftveil
  event, Download ROM references, Rental, Mix);
* ``wbt2``: ``/a/2/5/1``, ``/a/2/5/2``, ``/a/2/5/3`` (the five regional
  Leaders cups);
* ``wbt3``: ``/a/2/5/4``, ``/a/2/5/5``, ``/a/2/5/6`` (Champions, World Leaders,
  Type Expert, Rental Master, Mix Master).

Trainer-list row ``N`` is member ``N + 1`` of both trainer NARCs; member 0 is a
dummy. A header member is three ``u16`` values ``2, 1, ace_record``; the third
is the Pokémon-record index that the fixed-ace path writes to party position
0, which is honoured only when the trainer-list row's ace flag is set. An
index member is ``u16`` values ``2, count, record...``. Each record is a
16-byte ``BSUBWAY_POKEMON_ROM_DATA`` entry, decoded with the same helpers as
the Rental archive.

Members that carry the shared placeholder list ``1, 3, 4, 18`` (Champions in
``wbt1``/``wbt2`` and most non-battling rows) are reported on stderr and
omitted from the CSV unless ``--include-placeholders`` is given. A list that
repeats another trainer's records is kept and labelled ``duplicate of trainer
N`` in ``party_kind``, where ``N`` is the trainer whose header ace record lies
inside the list (Bianca's ``wbt2`` row repeats Chili's records; Hilda, the
Rival, the second Cheren row and Colress repeat Cheren's in ``wbt3``). The
three-record Driftveil-event parties of rows 56 and 57 in ``wbt1`` are
ordinary parties and are kept.

Names come from the retail text NARC ``/a/0/0/2`` (members 64, 90, 403 and the
compressed PWT trainer-name member 409); normal abilities and gender rules
come from personal data ``/a/0/1/6``; the trainer's fixed IV value and ace
flag come from the WBT table ``/a/2/4/7``.
"""

from __future__ import annotations

import argparse
import csv
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from decode_rental_pokemon import (
    NATURES,
    TEXT_MEMBERS,
    decode_record,
    ev_summary,
    ev_values,
    gender_rule,
    get_name,
    possible_abilities,
)
from find_pwt_menu_builder import narc_members
from inspect_wbt_table import RECORD_SIZE as WBT_ROW_SIZE
from inspect_wbt_table import trainer_power_rnd


TRAINER_NAME_MEMBER = 409
ACE_FLAG_OFFSET = 14
PLACEHOLDER_LIST = (1, 3, 4, 18)
RETAIL_PATHS = {
    "wbt1": ("/a/2/4/8", "/a/2/4/9", "/a/2/5/0"),
    "wbt2": ("/a/2/5/1", "/a/2/5/2", "/a/2/5/3"),
    "wbt3": ("/a/2/5/4", "/a/2/5/5", "/a/2/5/6"),
}


@dataclass(frozen=True)
class TrainerParty:
    table: str
    trainer_id: int
    ace_record: int
    records: tuple[int, ...]


def decode_header(data: bytes) -> tuple[int, int, int]:
    """Decode a six-byte trainer header member: ``2, 1, ace_record``."""

    if len(data) != 6:
        raise ValueError(f"expected a 6-byte trainer header, found {len(data)}")
    return struct.unpack("<HHH", data)


def decode_index_list(data: bytes) -> tuple[int, ...]:
    """Decode a trainer index member: ``2, count, record...``."""

    if len(data) < 4 or len(data) % 2:
        raise ValueError(f"invalid trainer index member of {len(data)} bytes")
    _tag, count = struct.unpack_from("<HH", data, 0)
    if 4 + 2 * count != len(data):
        raise ValueError(f"index member declares {count} records in {len(data)} bytes")
    return struct.unpack_from(f"<{count}H", data, 4)


def parties(table: str, headers: list[bytes], lists: list[bytes]) -> Iterable[TrainerParty]:
    if len(headers) != len(lists):
        raise ValueError(f"{table}: {len(headers)} headers but {len(lists)} index members")
    for member in range(1, len(headers)):
        _tag, _one, ace_record = decode_header(headers[member])
        yield TrainerParty(table, member - 1, ace_record, decode_index_list(lists[member]))


def decode_compressed_text_member(data: bytes) -> list[str]:
    """Decode a Gen-V message member whose entries use 9-bit packing.

    The PWT trainer-name member (409) stores every entry with the ``0xF100``
    compression marker, which the plain decoder rejects.
    """

    section_count, entry_count = struct.unpack_from("<HH", data, 0)
    if section_count < 1:
        raise ValueError("text member has no sections")
    section_offset = struct.unpack_from("<I", data, 12)[0]
    position = section_offset + 4
    entries: list[tuple[int, int]] = []
    for _ in range(entry_count):
        offset, char_count, _unknown = struct.unpack_from("<IHH", data, position)
        entries.append((offset, char_count))
        position += 8

    result: list[str] = []
    for offset, char_count in entries:
        words = list(struct.unpack_from(f"<{char_count}H", data, section_offset + offset))
        key = words[-1] ^ 0xFFFF
        for index in range(char_count - 1, -1, -1):
            words[index] ^= key
            key = ((key >> 3) | (key << 13)) & 0xFFFF
        if not words or words[0] != 0xF100:
            result.append("".join(chr(code) for code in words if code != 0xFFFF))
            continue
        codes: list[int] = []
        buffer = 0
        bits = 0
        for word in words[1:]:
            buffer |= word << bits
            bits += 16
            while bits >= 9:
                code = buffer & 0x1FF
                buffer >>= 9
                bits -= 9
                if code == 0x1FF:
                    bits = -1
                    break
                codes.append(code)
            if bits < 0:
                break
        result.append("".join(chr(code) for code in codes if code not in (0, 0xFFFF)))
    return result


def rows(
    tables: list[tuple[str, list[bytes], list[bytes], list[bytes]]],
    text_members: list[bytes],
    personal_members: list[bytes],
    wbt_rows: bytes | None,
    include_placeholders: bool,
) -> Iterable[dict[str, object]]:
    names = {
        kind: decode_text_member_lenient(text_members[index])
        for kind, index in TEXT_MEMBERS.items()
    }
    trainer_names = decode_compressed_text_member(text_members[TRAINER_NAME_MEMBER])
    for table, headers, lists, records in tables:
        decoded = list(parties(table, headers, lists))
        owners: dict[tuple[int, ...], int] = {}
        for party in decoded:
            if party.ace_record in party.records:
                owners.setdefault(party.records, party.trainer_id)
        for party in decoded:
            owners.setdefault(party.records, party.trainer_id)
        for party in decoded:
            placeholder = party.records == PLACEHOLDER_LIST
            owner = owners[party.records]
            kind = (
                "shared placeholder" if placeholder
                else "normal" if owner == party.trainer_id
                else f"duplicate of trainer {owner}"
            )
            if placeholder:
                print(
                    f"{table} trainer {party.trainer_id} ({trainer_names[party.trainer_id]}): "
                    f"records {', '.join(map(str, party.records))} are the shared placeholder list",
                    file=sys.stderr,
                )
                if not include_placeholders:
                    continue
            ace_flag = None
            power_rnd = None
            if wbt_rows is not None:
                row = wbt_rows[party.trainer_id * WBT_ROW_SIZE : (party.trainer_id + 1) * WBT_ROW_SIZE]
                ace_flag = row[ACE_FLAG_OFFSET]
                power_rnd = trainer_power_rnd(row)
            for slot, archive_index in enumerate(party.records, start=1):
                record = decode_record(records[archive_index])
                personal = personal_members[record.species]
                evs = ev_values(record.ev_mask)
                move_names = [get_name(names["moves"], move, "move") for move in record.moves]
                yield {
                    "table": table,
                    "trainer_id": party.trainer_id,
                    "trainer_name": trainer_names[party.trainer_id],
                    "party_kind": kind,
                    "slot": slot,
                    "archive_index": archive_index,
                    "ace_record": party.ace_record,
                    "is_ace": (
                        "Unknown (no WBT table)" if ace_flag is None
                        else "Yes" if ace_flag and archive_index == party.ace_record
                        else "No"
                    ),
                    "species": get_name(names["species"], record.species, "species"),
                    "form": "Default" if record.form == 0 else record.form,
                    "held_item": get_name(names["items"], record.item, "item") if record.item else "None",
                    "move_1": move_names[0],
                    "move_2": move_names[1],
                    "move_3": move_names[2],
                    "move_4": move_names[3],
                    "nature": NATURES[record.nature],
                    "ev_mask": f"0x{record.ev_mask:02X}",
                    "ev_distribution": ev_summary(evs),
                    "ev_hp": evs[0],
                    "ev_attack": evs[1],
                    "ev_defense": evs[2],
                    "ev_speed": evs[3],
                    "ev_sp_attack": evs[4],
                    "ev_sp_defense": evs[5],
                    "trainer_ivs": "Unknown (no WBT table)" if power_rnd is None else f"{power_rnd} in every stat",
                    "ability_rule": possible_abilities(personal, names["abilities"]),
                    "gender_rule": gender_rule(personal),
                    "friendship": 0 if 218 in record.moves else 255,
                }


def decode_text_member_lenient(data: bytes) -> list[str]:
    """Decode a text member, accepting compressed entries where present."""

    return decode_compressed_text_member(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--table",
        nargs=4,
        action="append",
        metavar=("NAME", "HEADER_NARC", "INDEX_NARC", "POKEMON_NARC"),
        required=True,
        help="one table set, e.g. wbt2 a/2/5/1 a/2/5/2 a/2/5/3; repeatable",
    )
    parser.add_argument("--text", type=Path, required=True, help="extracted retail /a/0/0/2")
    parser.add_argument("--personal", type=Path, required=True, help="extracted retail /a/0/1/6")
    parser.add_argument("--wbt-table", type=Path, help="extracted /a/2/4/7 (adds trainer IVs and ace flags)")
    parser.add_argument("--include-placeholders", action="store_true", help="keep shared placeholder lists")
    parser.add_argument("--output", type=Path, help="CSV path; stdout when omitted")
    args = parser.parse_args()

    try:
        tables = [
            (name, narc_members(Path(h).read_bytes()), narc_members(Path(i).read_bytes()), narc_members(Path(p).read_bytes()))
            for name, h, i, p in args.table
        ]
        wbt_rows = None
        if args.wbt_table:
            blob = args.wbt_table.read_bytes()
            wbt_rows = narc_members(blob)[0] if blob[:4] == b"NARC" else blob
        decoded_rows = list(
            rows(
                tables,
                narc_members(args.text.read_bytes()),
                narc_members(args.personal.read_bytes()),
                wbt_rows,
                args.include_placeholders,
            )
        )
    except (OSError, ValueError, IndexError, struct.error) as exc:
        parser.error(str(exc))

    fieldnames = list(decoded_rows[0])
    destination = args.output.open("w", encoding="utf-8", newline="") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(decoded_rows)
    finally:
        if args.output:
            destination.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
