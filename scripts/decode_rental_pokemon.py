#!/usr/bin/env python3
"""Decode every selectable BW2 PWT Rental Pokémon build to CSV.

Inputs are extracted USA/Europe retail NARCs:

* ``/a/2/5/7``: the 1,000-member Rental Pokémon archive;
* ``/a/0/0/2``: the general text archive;
* ``/a/0/1/6``: the personal-data archive.

The equivalent development Rental archive is ``/a/2/7/1``. Its selectable
records are byte-identical to retail in the examined builds.
"""

from __future__ import annotations

import argparse
import csv
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from find_pwt_menu_builder import narc_members


RECORD_SIZE = 16
RANGES = (
    ("Rental", "Weak", 1, 132),
    ("Rental", "Strong", 133, 208),
    ("Rental Master", "Weak", 209, 558),
    ("Rental Master", "Strong", 559, 908),
)

TEXT_MEMBERS = {
    "items": 64,
    "species": 90,
    "abilities": 374,
    "moves": 403,
}

NATURES = (
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky",
)

STAT_NAMES = ("HP", "Attack", "Defense", "Speed", "Sp. Atk", "Sp. Def")


@dataclass(frozen=True)
class RentalRecord:
    species: int
    moves: tuple[int, int, int, int]
    ev_mask: int
    nature: int
    item: int
    form: int


def decode_record(data: bytes) -> RentalRecord:
    """Decode the source-defined 16-byte ``BSUBWAY_POKEMON_ROM_DATA``."""

    if len(data) != RECORD_SIZE:
        raise ValueError(f"expected a {RECORD_SIZE}-byte record, found {len(data)}")
    species, move1, move2, move3, move4, ev_mask, nature, item, form = (
        struct.unpack("<H4HBBHH", data)
    )
    if nature >= len(NATURES):
        raise ValueError(f"invalid nature index {nature}")
    return RentalRecord(
        species=species,
        moves=(move1, move2, move3, move4),
        ev_mask=ev_mask,
        nature=nature,
        item=item,
        form=form,
    )


def ev_values(mask: int) -> tuple[int, int, int, int, int, int]:
    """Apply the game's 510/selected-stat allocation, capped at 255."""

    selected = [bool(mask & (1 << index)) for index in range(6)]
    count = sum(selected)
    if count == 0:
        return (0, 0, 0, 0, 0, 0)
    value = min(510 // count, 255)
    return tuple(value if enabled else 0 for enabled in selected)  # type: ignore[return-value]


def ev_summary(values: tuple[int, int, int, int, int, int]) -> str:
    return " / ".join(
        f"{value} {name}" for name, value in zip(STAT_NAMES, values) if value
    ) or "None"


def decode_text_member(data: bytes) -> list[str]:
    """Decode one uncompressed Gen-V message member."""

    if len(data) < 16:
        raise ValueError("text member is too short")
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
        encrypted = list(
            struct.unpack_from(f"<{char_count}H", data, section_offset + offset)
        )
        key = encrypted[-1] ^ 0xFFFF
        for index in range(char_count - 1, -1, -1):
            encrypted[index] ^= key
            key = ((key >> 3) | (key << 13)) & 0xFFFF
        if encrypted and encrypted[0] == 0xF100:
            raise ValueError("compressed text entries are not supported by this decoder")
        result.append("".join(chr(code) for code in encrypted if code != 0xFFFF))
    return result


def get_name(names: list[str], index: int, kind: str) -> str:
    try:
        return names[index]
    except IndexError as exc:
        raise ValueError(f"{kind} ID {index} is outside its name table") from exc


def possible_abilities(personal: bytes, ability_names: list[str]) -> str:
    if len(personal) < 27:
        raise ValueError("personal-data record is too short")
    ability_ids = [personal[24]]
    if personal[25] and personal[25] != personal[24]:
        ability_ids.append(personal[25])
    names = [get_name(ability_names, value, "ability") for value in ability_ids]
    if len(names) == 1:
        return f"{names[0]} (only normal ability)"
    return f"PID selects {names[0]} or {names[1]}"


def gender_rule(personal: bytes) -> str:
    if len(personal) < 19:
        raise ValueError("personal-data record is too short")
    ratio = personal[18]
    if ratio == 0:
        return "Male"
    if ratio == 254:
        return "Female"
    if ratio == 255:
        return "Genderless"
    displayed_ratios = {31: "12.5%", 63: "25%", 127: "50%", 191: "75%"}
    female_percent = displayed_ratios.get(ratio, f"{ratio / 256 * 100:g}%")
    return f"PID-derived ({female_percent} female)"


def opponent_ivs(tournament: str) -> str:
    if tournament == "Rental Master":
        return "20 in every stat"
    return "Trainer PowerRnd: 0, 8, or 20 in every stat"


def rows(
    rental_members: list[bytes],
    text_members: list[bytes],
    personal_members: list[bytes],
) -> Iterable[dict[str, object]]:
    names = {
        kind: decode_text_member(text_members[index])
        for kind, index in TEXT_MEMBERS.items()
    }
    if len(rental_members) != 1000:
        raise ValueError(f"expected 1,000 Rental records, found {len(rental_members)}")

    for tournament, tier, start, end in RANGES:
        for archive_index in range(start, end + 1):
            record = decode_record(rental_members[archive_index])
            try:
                personal = personal_members[record.species]
            except IndexError as exc:
                raise ValueError(
                    f"species {record.species} lacks a personal-data record"
                ) from exc
            evs = ev_values(record.ev_mask)
            move_names = [get_name(names["moves"], move, "move") for move in record.moves]
            friendship = 0 if 218 in record.moves else 255
            yield {
                "tournament": tournament,
                "tier": tier,
                "archive_index": archive_index,
                "species": get_name(names["species"], record.species, "species"),
                "form": "Default" if record.form == 0 else record.form,
                "held_item": get_name(names["items"], record.item, "item"),
                "move_1": move_names[0],
                "move_2": move_names[1],
                "move_3": move_names[2],
                "move_4": move_names[3],
                "nature": NATURES[record.nature],
                "ev_distribution": ev_summary(evs),
                "ev_hp": evs[0],
                "ev_attack": evs[1],
                "ev_defense": evs[2],
                "ev_speed": evs[3],
                "ev_sp_attack": evs[4],
                "ev_sp_defense": evs[5],
                "player_ivs": "20 in every stat",
                "opponent_ivs": opponent_ivs(tournament),
                "ability_rule": possible_abilities(personal, names["abilities"]),
                "gender_rule": gender_rule(personal),
                "friendship": friendship,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rental_narc", type=Path, help="extracted /a/2/5/7 or /a/2/7/1")
    parser.add_argument("text_narc", type=Path, help="extracted retail /a/0/0/2")
    parser.add_argument("personal_narc", type=Path, help="extracted retail /a/0/1/6")
    parser.add_argument("--output", type=Path, help="CSV path; stdout when omitted")
    args = parser.parse_args()

    try:
        decoded_rows = list(
            rows(
                narc_members(args.rental_narc.read_bytes()),
                narc_members(args.text_narc.read_bytes()),
                narc_members(args.personal_narc.read_bytes()),
            )
        )
    except (OSError, ValueError, struct.error) as exc:
        parser.error(str(exc))

    fieldnames = list(decoded_rows[0])
    if args.output:
        destination = args.output.open("w", encoding="utf-8", newline="")
    else:
        import sys

        destination = sys.stdout
    try:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decoded_rows)
    finally:
        if args.output:
            destination.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
