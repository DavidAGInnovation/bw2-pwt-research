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

## Cup-ID dispatch

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

The rows above are the result of evaluating that switch table directly. In
particular, ID 12 branches to `0x02241B84`, ID 14 to `0x02241BB0`, and ID 15
to `0x02241BF4`.

## Mapping to named permanent cups

The script-level mapping below resolves the player-facing names for every
ordinary built-in mode.  The cup IDs come from the dispatch above and the
names come from the actual PWT menu/description branch in script member 1277
(documented in the static-evidence section below).  The family byte is raw
record **byte 2**.  It is not the downloadable `.pwt` `YY` byte.

| Named cup | Cup ID | Constructor | Raw family byte 2 | Source-table records in this build | Evidence status |
|---|---:|---|---:|---|---|
| Champions | 1 | `0x02241A88` | `0x01` | indices `14–19, 53` (7 records) | Confirmed: menu branch + fixed Champion roster |
| Type Expert | 2 | `0x02241C0C` | dynamic | Type/category-specific leader/mob/weak-mob pools | Confirmed: menu branch + dynamic constructor |
| Download | 3 | `0x02241998` | download/special | Generic/download-style shuffle path | Confirmed: menu branch + constructor; payload is mode-specific |
| Driftveil | 4 | `0x02241B20` | mixed | Four cat. 1, one cat. 2, two cat. 3 | Confirmed: menu branch + constructor |
| Unova/Teselia Leaders | 5 | `0x02241B08` | primarily `0x05` | indices `0–13` (14 possible NPCs: 13 standard Leaders + Bianca wildcard at index 8) | Confirmed: family roster/order + cup progression |
| Kanto Leaders | 6 | `0x02241B08` | `0x06` | indices `20–26, 35` (8 records) | Confirmed: family roster/order |
| Johto Leaders | 7 | `0x02241B08` | `0x07` | indices `27–34` (8 records) | Confirmed: family roster/order |
| Hoenn Leaders | 8 | `0x02241B08` | `0x08` | indices `36–44` (9 records) | Confirmed: family roster/order |
| Sinnoh Leaders | 9 | `0x02241B08` | `0x09` | indices `45–52` (8 records) | Confirmed: family roster/order |
| World Leaders | 10 | `0x02241AF0` | mixed leader families | Seven cat.-3 selections | Confirmed: menu branch + constructor |
| Rental | 12 | `0x02241B84` | special | Three cat. 1, two cat. 2, two cat. 3 | Confirmed: menu branch + constructor |
| Rental Master | 13 | `0x02241BDC` | special | Seven cat.-3 selections | Confirmed: menu branch + constructor |
| Mix | 14 | `0x02241BB0` | special | Three cat. 1, two cat. 2, two cat. 3 | Confirmed: menu branch + constructor |
| Mix Master | 15 | `0x02241BF4` | special | Seven cat.-3 selections | Confirmed: menu branch + constructor |
| Driftveil event | 11 | `0x02241B4C` | `WBTCUP_HODOMOE_EVENT` | Four cat. 1, one each cat. 3/4/5 | Confirmed: source enum + menu branch + enable predicate |

“Confirmed” means the mapping is deterministic and supported by the source,
script menu/description branch, and constructor evidence for the examined build;
the matching USA/Europe retail data/code path was cross-checked where noted.
It does not mean that every regional or revision ROM must use the same addresses
or data.

The regional names and rosters agree with the public PWT listings for the
[regional Leaders cups](https://www.serebii.net/black2white2/worldtournament.shtml),
[Kanto Leaders](https://www.serebii.net/black2white2/pwt/kanto.shtml), and
[Champions](https://www.serebii.net/black2white2/pwt/champion.shtml).  The
development table also contains the seven Champion records (Blue, Lance,
Steven, Wallace, Cynthia, Alder, and Red) described by those references.

## ID 11: Driftveil event cup

The original source defines the dispatch value. In
`prog/include/field/wbt.h`, numeric ID 11 is `WBTCUP_HODOMOE_EVENT`; the lobby
script requests it as `SCR_WBT_CUP_HODOMOE_EVENT` before the ordinary Driftveil
cup (ID 4). Text entry 113's “this Driftveil tournament” wording is therefore
the event cup's description. ID 0 remains the null/error path.

The neighboring text entry 112 says that a special tournament is being
prepared and asks the player to wait; this is consistent with the source enum's
event role.

The menu/resource producer is traced statically: member 1277 checks candidate
11 with `CMD_3EE` and conditionally adds it with `ListMenuAdd` using UID 11.
The selected UID is stored in `0x8023` and passed to the cup setter, so a
literal `CMD_3F3 11` call is not expected.

The constructor/description branch is therefore real, and its source enum is
known; it is not merely a reserved numeric slot.

The exact event predicate is in `prog/src/field/wbt_tool.c`:

```text
ID 11 (WBTCUP_HODOMOE_EVENT): ordinary Driftveil win count == 0
ID 4  (WBTCUP_HODOMOE):       ordinary Driftveil win count != 0
```

This is a win-counter test, not a hidden map flag and not the eight-record
sequence in script member 1280.

### Source confirmation and command IDs

`wbt.h` and `wbt_tool.c` define ID 11 as `WBTCUP_HODOMOE_EVENT` and implement its predicate
as ordinary Driftveil win count `== 0`. The lobby script calls
`_WBT_CHECK_CUP_ENABLE` with that enum, then adds the ordinary Driftveil cup.
This is the definitive event/unlock condition for the built-in PWT.

The numeric command ID `0x3EA` is not globally unique. In
`scrcmd_wbt_table.cdat`, WBT command 1002 is `EvCmdWBTSystemCheckEnable`; in
the separate Join Avenue `scrcmd_resort_table.cdat`, command 1002 is
`EvCmdResortGetData`. WBT victory-count access is `EvCmdWBTGetVictoryCount`
at `CMD_3FA`. The source defines both stripped symbols without conflating WBT
and Resort overlays.

The byte sequence in the relevant script member is Join
Avenue `resort_scr.bin`, NARC member 1280, in both the development
`/a/0/5/9` and retail `/a/0/5/6` archives. It is useful as a source/ROM
cross-check for `EvCmdResortGetData`, but it is not a PWT unlock script.

The same retail NARC also contains member 1277's fifteen menu-builder blocks
at `0x0616–0x07E4`, byte-for-byte in the `CMD_3EE` candidate arguments and
UIDs. The retail command-table opcode for `ListMenuAdd` is `0x00AF` (the
development build uses `0x00AB`), but both encode the same option/hint/UID
triples. `scripts/find_pwt_menu_builder.py` verifies this cross-build result.

The script archive also contains the general menu flow: member 1277 stores the
list result in `0x8023` and passes it to `CMD_3F3` (the cup setter) at member
offset `0x02E7`; the description switch then compares that same value. The
fifteen availability blocks at `0x0616–0x07E4` call
`CMD_3EE(candidate, 0x8010)`, compare the returned value with `1`, and
conditionally issue `ListMenuAdd` with the candidate as UID. Their candidate
order is `11,4,5,6,7,8,9,10,1,13,15,2,12,14,3`. Thus the menu/resource path
can produce cup ID 11 dynamically when its availability predicate passes,
even though the archive has no literal `CMD_3F3 11`.

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

## Static script mapping

The menu-to-ID link is recoverable from the archived script data alone. In
`/a/0/5/9`, member 1277, the member's four-byte data prefix is followed by
these relevant commands (offsets below are member-relative, including that
prefix):

* `0x05D6` shows the tournament prompt; the list-menu command begins at
  `0x05E2` and writes its result to work variable `0x8023`.
* `0x02E7` calls `CMD_3F3` (`EvCmdWBTSetWBTCup`) with `0x8023`.  The menu
  result is therefore the cup ID consumed by the WBT constructor.  The
  neighboring reception-ID setter is `CMD_3F7`; `CMD_3EF` is a different WBT
  command and must not be used as evidence for a literal cup 11.
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
| 11 | `0x71` (`113`) | Driftveil event (`WBTCUP_HODOMOE_EVENT`) |
| 12 | `0x11` | Rental |
| 13 | `0x13` | Rental Master |
| 14 | `0x12` | Mix |
| 15 | `0x14` | Mix Master |

The text entries are independently decodable from `/a/0/0/5`, member 668:
entry 7 describes Type Expert, entries 8–20 describe the other named modes,
and entries 23–36 are their short menu labels. Entry 113 is the event
“this Driftveil tournament” message. ID 0 never reaches this description
switch because it is the null/error path.

The direct script branch assigns ID 2 to Type Expert and ID 10 to World Leaders;
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

`WBT_TRAINER_NUM` is 8: the player plus seven NPCs. The equation therefore
means that the three internal groups supply exactly seven NPC slots. For
example, a composition of two Leaders, three Mobs, and two Weak Mobs gives
`1 + 2 + 3 + 2 = 8`; the player is the remaining participant. RNG chooses the
eligible records within those groups, and the common builder then shuffles the
eight participant positions.

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

## USA/Europe retail code-path check

Retail Overlay 135 was decompressed at base `0x021EEC80` (4,032 bytes;
SHA-256 `30b48d2cc1e724470351f57fa6fa28d2844f195732737052bc9ce41e57ef98b8`).
The corresponding retail anchors are candidate selector `0x021EEE08`,
category-17 helper `0x021EEF90`, cup dispatch `0x021EF298` with its 16-entry
switch at `0x021EF2C0`, and common eight-position shuffle `0x021EF344`.
The decoded control flow preserves category filtering, the neutral/sentinel
`0x11` test, cup IDs `0..15`, and RNG-based slot shuffling.

The USA/Europe retail WBT table is `/a/2/4/7`, not `/a/2/6/1`. Its 2,108-byte
NARC (one 2,048-byte member) has the same SHA-256 as the development table,
`0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`.
Consequently, the development byte-2 family inventory and the named indices in
[`champions-and-leaders.md`](champions-and-leaders.md) are byte-for-byte
verified for this USA/Europe retail build. The retail `/a/2/6/1` resource is a
different 24,052-byte, 1,000-member NARC and is not used for this WBT table.

## Reproducibility and limits

The mapping above is confirmed for the archived development build and the
matching USA/Europe retail cross-check: the menu/description branch, cup
dispatch, constructor behavior, source enum, and ID-11 enable predicate agree.
“Confirmed” is therefore definitive for this examined build, but does not
guarantee identical addresses or data in untested regional/revision ROMs.

- The source artifact is an archived development build, SHA-256
  `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.
- NARC `/a/2/6/1` (resource 261) contains 128 records of 16 bytes each in that
  build; the family inventory above is based on raw byte 2.
- The overlay-55 WBT cup setter begins at `0x02237728`, logs
  `EvCmdWBTSetWBTCup <= %d.`, and stores the parsed 16-bit value in the WBT
  work structure at offset `0x0C`. Its command is `CMD_3F3`. The neighboring
  reception-ID setter begins at `0x022377CC` (`CMD_3F7`) and writes a separate
  WBT field; `0x022377F4` is the reception-ID getter (`CMD_3F8`).
- `CMD_3EF` is a different WBT command. No literal `CMD_3F3 11` occurs in the
  examined script archive; the menu result supplies the cup ID dynamically.
- The recovered SWAN source mirror (revision 59995) supplies original C
  symbols and source-level implementation evidence: WBT `CMD_3EA` is
  `EvCmdWBTSystemCheckEnable`, WBT `CMD_3FA` is
  `EvCmdWBTGetVictoryCount`, and Resort `CMD_3EA` is `EvCmdResortGetData`.
  It is retained locally under the artifact's
  `rom/original-builds/swanmirror.tar` and is not copied into this repository.
  The addresses above remain build-specific disassembly cross-checks.
- The USA/Europe retail Overlay 135 and the retail WBT
  table `/a/2/4/7` are cross-checked as described above. Other
  regional/revision builds should still be checked before treating every
  address or roster byte as universal; the source-level enum and enable
  predicate for ID 11 are defined for this examined build.
