# Normal WBT party tables

This page documents the stored parties that the normal (non-Rental) ROM-party
builder reads for built-in opponents: the three `wbt1`/`wbt2`/`wbt3` table
sets named in [`wbt-party-selection.md`](wbt-party-selection.md). It covers
the retail archive paths, the member layout, and what the decoded records
show. Which cup reads which set, and how the builder picks three to six of the
stored records, is documented on that page; this page is about the stored
data. The complete decode is
[`wbt-normal-parties.csv`](wbt-normal-parties.csv).

The examined build is the USA/Europe Black 2 retail ROM already used for the
other retail cross-checks. The development resources `/a/2/6/2`→`/a/2/6/4`,
`/a/2/6/5`→`/a/2/6/7` and `/a/2/6/8`→`/a/2/7/0` recorded in
[`SOURCES.md`](../SOURCES.md) were not re-examined here, so byte identity with
the development build is not claimed for these nine archives.

## Retail archives

| Set | Trainer headers | Party index lists | Pokémon records | Cups that read it |
|---|---|---|---|---|
| `wbt1` | `/a/2/4/8` (120 members × 6 B) | `/a/2/4/9` (120 members) | `/a/2/5/0` (1,000 × 16 B, 988 non-empty) | Driftveil, Driftveil event, Download ROM references, Rental, Mix |
| `wbt2` | `/a/2/5/1` (120 × 6 B) | `/a/2/5/2` (120) | `/a/2/5/3` (1,000 × 16 B, 988 non-empty) | Unova, Kanto, Johto, Hoenn and Sinnoh Leaders |
| `wbt3` | `/a/2/5/4` (69 × 6 B) | `/a/2/5/5` (69) | `/a/2/5/6` (1,000 × 16 B, 384 non-empty) | Champions, World Leaders, Type Expert, Rental Master, Mix Master |

SHA-256 values for all nine archives are in [`SOURCES.md`](../SOURCES.md).
The member counts match the trainer coverage already established: 119 rows
plus a dummy for `wbt1`/`wbt2`, 68 rows plus a dummy for `wbt3`. The Rental
archive `/a/2/5/7` sits directly after these; retail `/a/2/1/1` is a second
copy of it in a different NARC wrapper.

## Member layout

Trainer-list row `N` is member `N + 1` of both trainer NARCs of a set; member
0 is a dummy (`0, 1, 0`).

| Member | Layout | Meaning |
|---|---|---|
| Trainer header (6 bytes) | `u16 2`, `u16 1`, `u16 ace_record` | `ace_record` is the Pokémon-archive index that `makeRomTrainerData` writes to position `0` when the row's ace flag is set. |
| Party index list (6–16 bytes) | `u16 2`, `u16 count`, `u16 record[count]` | The candidate records handed to the no-replacement chooser. |
| Pokémon record (16 bytes) | `BSUBWAY_POKEMON_ROM_DATA` | Species, four moves, EV mask, nature, item, form, as documented for the Rental archive in [`rental-pokemon-pools.md`](rental-pokemon-pools.md#what-each-configured-record-controls). |

Every battling trainer's list holds six consecutive records. The ace record
is one of them but not necessarily the lowest: Clair's `wbt2` and `wbt3`
headers both name record 164, Kingdra, the second of her six (163–168), which
agrees with her entry in the ace-marked trainer list. Blue's and Red's `wbt3`
headers hold 346 (Alakazam) and 382 (Pikachu) although their trainer-list rows
clear the ace flag, so those values are stored but unused.

Rows that a set's cups can never select do not carry real data in it:

| Set | Rows with the shared placeholder list `1, 3, 4, 18` | Rows that repeat another row's six records | Notes |
|---|---|---|---|
| `wbt1` | 7 (Marlon), 14–54, 58–67, 78–118 (93 rows) | none | Rows 56 (second Cheren) and 57 (Colress) hold three-record Driftveil-event parties: Stoutland, Cinccino, Watchog with Stoutland as ace, and Klink, Elgyem, Magneton with Magneton as ace. Headers of Unova rows that no `wbt1` cup admits (5, 6, 9–13) and of the Rival (55) hold values outside their own lists. |
| `wbt2` | 14–19 (Champions), 53–55, 57–118 (71 rows) | 8 (Bianca) points at Chili's records 49–54 | Row 56 (second Cheren) has its own six records but its header names record 67, Lenora's Watchog; that row belongs to the Driftveil event and is never built from `wbt2`. |
| `wbt3` | none | 54 (Hilda), 55 (Rival), 56 (second Cheren), 57 (Colress) point at Cheren's records 1–6 | 64 rows have their own party, matching the 64 rows represented in `wbt3` in the coverage audit. |

The placeholder rows' headers hold values that are not records of their lists
(73 for the six Champion rows in `wbt2`, otherwise numbers near the member
index); nothing reads them. The Champions' and Red's real
parties are `wbt3` rows 14–19 and 53.

## What the records show

The CSV contains 846 rows: 150 for `wbt1` (26 parties), 288 for `wbt2` (48
rows, 47 distinct parties) and 408 for `wbt3` (68 rows, 64 distinct parties).
Distinct parties only are counted below.

**EV masks.** All 14 Unova rows (Cheren through Brycen, Bianca included) store
EV mask `0x00` for every record of their `wbt2` party, so an Unova Leader in
the Unova Leaders cup has no EVs. Every Kanto, Johto, Hoenn and Sinnoh Leader's
`wbt2` party and every `wbt3` party uses at least two stats. In `wbt1`, 19 of
the 26 parties store mask `0x00` (the five Driftveil Leaders, Bianca, the
Rival, both event rows and the ten generic Driftveil trainers) and 108 of the
150 records hold no item; the seven Unova rows that `wbt1` cannot select
store EVs and items. Three- and four-stat masks occur and follow the
`510 / count` rule (170 or 127 each):

| Set | Trainer | Pokémon | EVs |
|---|---|---|---|
| `wbt1` | Skyla | Mandibuzz | 170 HP / 170 Defense / 170 Sp. Def |
| `wbt1` | Drayden | Salamence; Kingdra | 170 Attack / 170 Speed / 170 Sp. Def; 170 HP / 170 Speed / 170 Sp. Atk |
| `wbt1` | Chili | Darmanitan | 170 HP / 170 Attack / 170 Speed |
| `wbt1` | Cress | Lanturn | 170 Defense / 170 Sp. Atk / 170 Sp. Def |
| `wbt2` | Cheren (row 56) | Haxorus; Serperior; Emboar; Samurott | three stats each |
| `wbt3` | Lenora | Braviary | 170 Attack / 170 Speed / 170 Sp. Def |
| `wbt3` | Brock | Tyranitar | 127 HP / 127 Attack / 127 Sp. Atk / 127 Sp. Def |
| `wbt3` | Misty | Lapras | 127 HP / 127 Defense / 127 Sp. Atk / 127 Sp. Def |
| `wbt3` | Whitney | Ursaring | 170 HP / 170 Attack / 170 Sp. Def |
| `wbt3` | Morty | Mismagius | 170 HP / 170 Defense / 170 Sp. Atk |
| `wbt3` | Chuck | Poliwrath | 170 Attack / 170 Speed / 170 Sp. Def |
| `wbt3` | Clair | Kingdra | 170 HP / 170 Speed / 170 Sp. Atk |
| `wbt3` | Janine | Weezing; Nidoqueen | 170 HP / 170 Defense / 170 Sp. Def; 170 Speed / 170 Sp. Atk / 170 Sp. Def |
| `wbt3` | Flannery | Camerupt | 127 HP / 127 Attack / 127 Speed / 127 Sp. Atk |
| `wbt3` | Norman | Slaking | 170 Attack / 170 Speed / 170 Sp. Def |
| `wbt3` | Winona | Altaria; Tropius | 170 HP / 170 Defense / 170 Sp. Def; 170 HP / 170 Speed / 170 Sp. Def |
| `wbt3` | Liza | Xatu | 170 HP / 170 Attack / 170 Sp. Atk |

**Natures.** `wbt2` parties: Adamant 68, Jolly 60, Timid 47, Modest 27 of 282
records. `wbt3` parties: Adamant 87, Jolly 71, Timid 54, Modest 44 of 384.

**Forms.** Blaine's `wbt3` Rotom stores form `1` (Heat), Wattson's form `2`
(Wash) and Volkner's form `4` (Fan). Wattson's `wbt3` Ampharos stores form
`5`, which the species does not have; the game displays the base form. No
`wbt1` or `wbt2` record stores a nonzero form.

**Duplicate move.** Record 64 of `wbt2`, Cilan's Jumpluff, stores Leech Seed,
Cotton Spore, Cotton Spore, Sleep Powder.

**Ace coverage.** In `wbt2`, 46 of the 47 distinct parties have the flagged
ace among their records (the exception is row 56 noted above); in `wbt3`, 62
of 64 (Blue and Red are unflagged). In `wbt1`, the 18 flagged rows that a
`wbt1` cup can select all name a record of their own party.

**Trainer IVs** are not stored here. The CSV repeats each row's `PowerRnd`
from the WBT table (20 for Leaders, 25 for Champions, 30 for Red, 12 for the
Rival, second Cheren and Colress rows, 16 or 8 for Type Expert rows, 0 for
generic rows), as documented in
[`champions-and-leaders.md`](champions-and-leaders.md).

### Example: Brock

| Set | Record | Pokémon | Item | Moves | Nature | EVs | Ace |
|---|---:|---|---|---|---|---|---|
| `wbt2` | 79 | Onix | Salac Berry | Sand Tomb, Protect, Stealth Rock, Sandstorm | Jolly | 255 HP / 255 Speed | Yes |
| `wbt2` | 80 | Golem | Dark Gem | Stone Edge, Earthquake, Sucker Punch, Iron Defense | Adamant | 255 Attack / 255 Defense | |
| `wbt2` | 81 | Kabutops | Liechi Berry | Stone Edge, Aqua Jet, Superpower, Swords Dance | Jolly | 255 Attack / 255 Speed | |
| `wbt2` | 82 | Omastar | Rindo Berry | Hydro Pump, Ancient Power, Earth Power, Ice Beam | Modest | 255 Sp. Atk / 255 Sp. Def | |
| `wbt2` | 83 | Aerodactyl | Charti Berry | Rock Slide, Earthquake, Thunder Fang, Tailwind | Jolly | 255 Attack / 255 Speed | |
| `wbt2` | 84 | Relicanth | Rock Gem | Rock Slide, Waterfall, Rock Polish, Yawn | Adamant | 255 Attack / 255 Sp. Def | |

Brock's `wbt3` party (records 79–84 of that archive) keeps Onix as the ace
with a different build (Eviolite; Stone Edge, Earthquake, Iron Head,
Sandstorm; Impish; 255 HP / 255 Defense) and replaces Omastar and Relicanth
with Tyranitar and Rhyperior.

## External cross-check

Serebii's World Tournament pages list species, held item and moves for the 46
Leaders' regional and World Leaders parties and the seven Champions' parties
(594 records). All of them match the decoded `wbt2`/`wbt3` records except
Cilan's regional Jumpluff, where Serebii lists Giga Drain in place of the
duplicated Cotton Spore. Serebii lists no natures or EVs for these parties, so
those columns of the CSV have no public counterpart.

## Reproduction

With the nine party NARCs, the text archive, personal data and the WBT table
extracted from the retail ROM:

```sh
python3 scripts/decode_wbt_parties.py \
  --table wbt1 rom/a/2/4/8 rom/a/2/4/9 rom/a/2/5/0 \
  --table wbt2 rom/a/2/5/1 rom/a/2/5/2 rom/a/2/5/3 \
  --table wbt3 rom/a/2/5/4 rom/a/2/5/5 rom/a/2/5/6 \
  --text rom/a/0/0/2 --personal rom/a/0/1/6 --wbt-table rom/a/2/4/7 \
  --output data/wbt-normal-parties.csv
```

Placeholder rows are listed on stderr; `--include-placeholders` keeps them in
the CSV. The script reuses the record, EV, text, ability and gender decoders
of `scripts/decode_rental_pokemon.py` and adds a decoder for the 9-bit-packed
PWT name member 409.
