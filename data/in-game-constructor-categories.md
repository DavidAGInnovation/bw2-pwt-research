# Built-in PWT constructor/category data

This document separates the permanent, in-game PWT cups from downloadable
`.pwt` bracket files.  It records what the examined development build does at
the constructor and candidate-table level.  It does not treat the internal
fields as downloadable `YY` values unless the data mapping is demonstrated.

## What the constructor does

The match builder receives a cup ID, creates an eight-trainer field (player
plus seven NPCs), and selects NPC records from the internal WBT table.  A
constructor request such as `category 3, count 7` means “request seven records
accepted by the internal category-3 predicate.”  It is a slot request, not a
claim that the source table contains seven records or a literal `YY=03` byte.

The relevant overlay-135 routines are:

| Address | Role |
|---|---|
| `0x02241D02` | Reads the cup ID and dispatches IDs `0..15`. |
| `0x02241920` | Builds the per-record internal category flags. |
| `0x02241874` | Tests one record against a cup/category predicate. |
| `0x02241630` | Counts candidates matching a requested internal pool. |
| `0x02241704` | Selects a requested number of candidates using RNG. |
| `0x022415E0` | Finalizes the selected seven NPC records. |
| `0x02241A88` | Fixed/flagged path; selects records whose packed flag at offset `6` is set. |
| `0x02241C0C` | Dynamic leader/mob/weak-mob path used by Type Expert. |

## Cup-ID dispatch (confirmed)

The jump table at `0x02241D20–0x02241D3E` and the calls following it give this
exact mapping in the examined build.  The switch reads one signed 16-bit
displacement per ID and adds it to the Thumb PC base `0x02241D22`; this matters
because the table is not an array of absolute addresses.  “Cat. 1–5” are
internal selector categories.

| Cup ID | Constructor | Cat. 1 | Cat. 2 | Cat. 3 | Cat. 4 | Cat. 5 | Code-level description |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | default/error path, then `0x02241B20` | 4 | 1 | 2 | 0 | 0 | Four cat. 1, one cat. 2, two cat. 3 |
| 1 | `0x02241A88` | flagged | — | — | — | — | Select packed-flagged records |
| 2 | `0x02241C0C` | dynamic | dynamic | dynamic | — | — | Leader/mob/weak-mob pools |
| 3 | `0x02241998` | — | — | — | — | — | Generic/download-style shuffle path |
| 4 | `0x02241B20` | 4 | 1 | 2 | 0 | 0 | Four cat. 1, one cat. 2, two cat. 3 |
| 5 | `0x02241B08` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 6 | `0x02241B08` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 7 | `0x02241B08` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 8 | `0x02241B08` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 9 | `0x02241B08` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 10 | `0x02241AF0` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 11 | `0x02241B4C` | 4 | 0 | 1 | 1 | 1 | Four cat. 1, one each cat. 3/4/5 |
| 12 | `0x02241B84` | 3 | 2 | 2 | 0 | 0 | Three cat. 1, two cat. 2, two cat. 3 |
| 13 | `0x02241BDC` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 14 | `0x02241BB0` | 3 | 2 | 2 | 0 | 0 | Three cat. 1, two cat. 2, two cat. 3 |
| 15 | `0x02241BF4` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |

Cup ID 0 reaches the same constructor as cup 4 after logging the
`WBTCUP_NULL!!` error path; it is not a separate named cup in this artifact.

The corrected rows above are the result of evaluating that switch table
directly.  In particular, ID 12 branches to `0x02241B84`, ID 14 to
`0x02241BB0`, and ID 15 to `0x02241BF4`; an earlier table had those three
constructor addresses shifted.

## Mapping to named permanent cups

The script-level mapping below resolves the player-facing names for every
ordinary built-in mode.  The cup IDs come from the dispatch above and the
names come from the actual PWT menu/description branch in script member 1277
(documented in the static-evidence section below).  The family byte is raw
record **byte 2**.  It is not the downloadable `.pwt` `YY` byte.

| Named cup | Cup ID | Constructor | Raw family byte 2 | Source-table records in this build | Confidence |
|---|---:|---|---:|---|---|
| Champions | 1 | `0x02241A88` | `0x01` | indices `14–19, 53` (7 records) | High: menu branch + fixed Champion roster |
| Type Expert | 2 | `0x02241C0C` | dynamic | Type/category-specific leader/mob/weak-mob pools | High: menu branch + dynamic constructor |
| Download | 3 | `0x02241998` | download/special | Generic/download-style shuffle path | High: menu branch; record details are mode-specific |
| Driftveil | 4 | `0x02241B20` | mixed | Four cat. 1, one cat. 2, two cat. 3 | High: menu branch + constructor |
| Unova/Teselia Leaders | 5 | `0x02241B08` | primarily `0x05` | indices `0–13` (14 possible NPCs: 13 standard Leaders + Bianca wildcard at index 8) | High: family roster/order and cup progression |
| Kanto Leaders | 6 | `0x02241B08` | `0x06` | indices `20–26, 35` (8 records) | High: family roster/order |
| Johto Leaders | 7 | `0x02241B08` | `0x07` | indices `27–34` (8 records) | High: family roster/order |
| Hoenn Leaders | 8 | `0x02241B08` | `0x08` | indices `36–44` (9 records) | High: family roster/order |
| Sinnoh Leaders | 9 | `0x02241B08` | `0x09` | indices `45–52` (8 records) | High: family roster/order |
| World Leaders | 10 | `0x02241AF0` | mixed leader families | Seven cat.-3 selections | High: menu branch + constructor |
| Rental | 12 | `0x02241B84` | special | Three cat. 1, two cat. 2, two cat. 3 | High: menu branch + constructor |
| Rental Master | 13 | `0x02241BDC` | special | Seven cat.-3 selections | High: menu branch + constructor |
| Mix | 14 | `0x02241BB0` | special | Three cat. 1, two cat. 2, two cat. 3 | High: menu branch + constructor |
| Mix Master | 15 | `0x02241BF4` | special | Seven cat.-3 selections | High: menu branch + constructor |
| Reserved/special branch | 11 | `0x02241B4C` | special | Four cat. 1, one each cat. 3/4/5 | Static branch is present, but it has no ordinary menu label |

The regional names and rosters agree with the public PWT listings for the
[regional Leaders cups](https://www.serebii.net/black2white2/worldtournament.shtml),
[Kanto Leaders](https://www.serebii.net/black2white2/pwt/kanto.shtml), and
[Champions](https://www.serebii.net/black2white2/pwt/champion.shtml).  The
development table also contains the seven Champion records (Blue, Lance,
Steven, Wallace, Cynthia, Alder, and Red) described by those references.

## Reserved/special ID 11

ID 11 is the only value in the `0..15` dispatch without one of the fourteen
ordinary built-in menu names.  Its script branch displays text entry 113,
which says (in Japanese) that “this Driftveil tournament” is an unrestricted
tournament.  That is a special/current-tournament message, not the ordinary
Driftveil menu description (ID 4, text entry 10), so the available static data
does not justify renaming ID 11 as a second Driftveil cup.  ID 0 is the null
/ error path and likewise is not a named cup.

The source table's family-`0x00` records (indices `8, 54–127`, 75 records) are
special/other data.  Index 8 is the known Unova-cup wildcard (Bianca); the
remaining `54–127` records are special or download-related and should not be
silently counted as regional Leader records.

### Built-in tournament-name text table

The Japanese development build contains a contiguous tournament-name table in
NARC `/a/2/3/9`, member 11. Entries 151–162 decode as follows:

| Text entry | Japanese label | English gloss |
|---:|---|---|
| 151 | チャンピオン | Champions |
| 152 | ホドモエ | Driftveil |
| 153 | イッシュ | Unova |
| 154 | カントー | Kanto |
| 155 | ジョウト | Johto |
| 156 | ホウエン | Hoenn |
| 157 | シンオウ | Sinnoh |
| 158 | ワールドリーダーズ | World Leaders |
| 159 | レンタル | Rental |
| 160 | レンタルマスター | Rental Master |
| 161 | ミックス | Mix |
| 162 | ミックスマスター | Mix Master |

This confirms the player-facing permanent-mode names independently of the
downloadable `.pwt` role bytes. The same names also occur in the
menu-description bank used by the static script branch below: NARC
`/a/0/0/5`, member 668, entries 7–20 and 23–36.

## Static script mapping (no emulator)

The menu-to-ID link is recoverable from the archived script data alone. In
`/a/0/5/9`, member 1277, the member's four-byte data prefix is followed by
these relevant commands (offsets below are member-relative, including that
prefix):

* `0x05D6` shows the tournament prompt and calls `ListMenuInitTL` with result
  work variable `0x8023`.
* `0x02E7` calls `CMD_3F3` (`EvCmdWBTSetWBTCup`) with `0x8023`, proving that
  the selected menu value is the cup ID passed to the constructor.
* `0x0B95–0x0DC0` compares `0x8023` with each ID and calls `MsgActorEx` with
  the corresponding description-text line.

The resulting static mapping is:

| Cup ID | Description line | Player-facing mode |
|---:|---:|---|
| 1 | `0x08` | Champions |
| 2 | `0x07` | Type Expert |
| 3 | `0x09` | Download |
| 4 | `0x0A` | Driftveil |
| 5 | `0x0B` | Unova Leaders |
| 6 | `0x0C` | Kanto Leaders |
| 7 | `0x0D` | Johto Leaders |
| 8 | `0x0E` | Hoenn Leaders |
| 9 | `0x0F` | Sinnoh Leaders |
| 10 | `0x10` | World Leaders |
| 11 | `0x71` (`113`) | Reserved/special current-tournament branch; no ordinary menu label |
| 12 | `0x11` | Rental |
| 13 | `0x13` | Rental Master |
| 14 | `0x12` | Mix |
| 15 | `0x14` | Mix Master |

The text entries are independently decodable from `/a/0/0/5`, member 668:
entry 7 describes Type Expert, entries 8–20 describe the other named modes,
and entries 23–36 are their short menu labels. Entry 113 is the special
“this Driftveil tournament” message noted above. ID 0 never reaches this
description switch because it is the null/error path.

This corrects the earlier tentative assignment of ID 2 to World Leaders. The
direct script branch assigns ID 2 to Type Expert and ID 10 to World Leaders;
the constructor code independently agrees that ID 2 is the dynamic
leader/mob/weak-mob path while ID 10 requests seven category-3 records.

The retail reverse-engineering symbol `LoadPWTTournamentTypeText` (listed at
`0x021C98F5` in the public BW2 symbol database) supports the existence of such
a loader, but that retail address is not assumed to be identical to the
development-build layout used for the constructor disassembly.

## Type Expert special path

Constructor `0x02241C0C` (cup ID 2) counts and selects three groups rather than using one
fixed histogram:

```text
leader candidates
mob candidates
weak-mob candidates
remaining candidates
```

Its debug strings are `SELECT LEADER:%d,rest=%d`, `SELECT MOB:%d,rest=%d`, and
`SELECT WEAK MOB:%d,rest=%d`.  The final invariant is:

```text
1 + leader_num + mob_num + weak_mob_num == WBT_TRAINER_NUM
```

Therefore Type Expert is a dynamic candidate-pool selection, not a fixed
downloadable-style `YY` histogram. World Leaders is cup ID 10 and uses its
separate seven-category-3 constructor path.

## Relationship to the winner routine

Construction, slot placement, and result calculation remain separate:

```text
cup ID
  → constructor/category selection
  → seven NPC records + player
  → common eight-position shuffle/finalization
  → automated NPC-vs-NPC match (if simulated)
       → wbt_calc_result
```

The constructor decides which records are present. The common match builder
then shuffles the eight participant pointers with RNG at `0x02241DB8` before
recording the player's position and finalizing slots. The winner routine
receives packed records and evaluates their priority/type/slot fields; it does
not read the trainer name or the family byte as a hidden win bonus.

## Reproducibility and limits

- The source artifact is an archived development build, SHA-256
  `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.
- NARC `/a/2/6/1` (resource 261) contains 128 records of 16 bytes each in that
  build; the family inventory above is based on raw byte 2.
- The overlay-55 WBT cup setter begins at `0x02237724`, logs
  `EvCmdWBTSetWBTCup <= %d.`, and stores the parsed 16-bit value in the WBT
  work structure at offset `0x0C`. In the examined script streams the command
  is followed by the next opcode after that one value. The archived public
  PokeSDK YAML also describes command `0x3F3` as one `ushort`; the disassembly
  is the authoritative source for the handler's actual write.
- A static scan of the script NARC found command `0x3F3` with literal value `4`
  in member `1278` (two entry scripts). This confirms a real script-side use of
  cup ID 4, but the script archive does not label that value with a menu name;
  it therefore does not by itself prove “Driftveil.”
- No original Nintendo C/C++ source was obtained. These are disassembly
  addresses, not official source symbols.
- Retail verification is still desirable before treating every address or
  unused/special ID as universal across regional releases.
