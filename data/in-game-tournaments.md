# Built-in PWT families: constructor and source-table inventory

The companion page [`in-game-constructor-categories.md`](in-game-constructor-categories.md)
contains the cup-ID jump table and the exact constructor calls.  This page
maps the named permanent cups to the source-table families that can be proven
in the examined development build.

## Scope

This covers the ten permanent, in-game tournament families in Pokémon Black 2
and White 2:

1. Unova/Teselia Leaders
2. Kanto Leaders
3. Johto Leaders
4. Hoenn Leaders
5. Sinnoh Leaders
6. World Leaders
7. Champions
8. Super Rental (Rental Master)
9. Super Mix (Mix Master)
10. Type Expert

The downloadable/Wi-Fi `.pwt` files are deliberately out of scope. Their raw
`XX YY ZZZZ` records are tabulated separately in [`yy-counts.md`](yy-counts.md).
The family names and unlock progression are summarized from [WikiDex's PWT
article](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament), with the
required [CC BY-SA attribution](https://www.wikidex.net/wiki/WikiDex%3ACopyrights)
retained.

| Family | Unlock condition in the reference list |
|---|---|
| Unova/Teselia Leaders | Pass the Pokémon League / enter the Hall of Fame. |
| Kanto, Johto, Hoenn, Sinnoh Leaders | Win Unova/Teselia Leaders once. |
| World Leaders | Win all five regional Leaders cups once. |
| Champions | Win World Leaders ten times. |
| Super Rental / Rental Master | Win Rental plus all five regional Leaders cups. |
| Super Mix / Mix Master | Win Mix plus all five regional Leaders cups. |
| Type Expert | Win the regional Leaders cups (the exact reference wording differs by edition/translation). |

## What is being counted

NARC `/a/2/6/1` (resource 261) in the examined build contains 128 records of
16 bytes.  The family inventory is the raw **byte at record offset 2**:

| Family byte 2 | Record indices | Count | Roster/family identified |
|---:|---|---:|---|
| `0x05` | `0–7, 9–13` | 13 | Primary Unova/Teselia Leaders family |
| `0x01` | `14–19, 53` | 7 | Champions |
| `0x06` | `20–26, 35` | 8 | Kanto Leaders |
| `0x07` | `27–34` | 8 | Johto Leaders |
| `0x08` | `36–44` | 9 | Hoenn Leaders |
| `0x09` | `45–52` | 8 | Sinnoh Leaders |
| `0x00` | `8, 54–127` | 75 | Special/other records; index 8 is Bianca, a wildcard included by the Unova Leaders constructor (and listed on the [Unova roster](https://www.serebii.net/black2white2/pwt/unova.shtml)) |

This byte is a built-in source-table family selector. It is **not** a claim
that the record is a downloadable `YY=00`–`05` bracket record. The table counts
source records; a cup can also include a named wildcard from another family
code (Unova includes index 8). Each normal run still selects seven NPCs for the
player's eight-trainer field.

## Per-family mapping

| Built-in family | Cup ID | Constructor | Source family/count | Status |
|---|---:|---|---|---|
| Unova/Teselia Leaders | 5 | `0x02241B08` | indices `0–13`: 14 records (13 byte2 `0x05` + wildcard index 8) | Mapped in this build |
| Kanto Leaders | 6 | `0x02241B08` | byte2 `0x06`: 8 records | Mapped in this build |
| Johto Leaders | 7 | `0x02241B08` | byte2 `0x07`: 8 records | Mapped in this build |
| Hoenn Leaders | 8 | `0x02241B08` | byte2 `0x08`: 9 records | Mapped in this build |
| Sinnoh Leaders | 9 | `0x02241B08` | byte2 `0x09`: 8 records | Mapped in this build |
| World Leaders | 10 | `0x02241AF0` | mixed leader families; seven cat.-3 selections | Mapped in this build |
| Champions | 1 | `0x02241A88` | byte2 `0x01`: 7 records | Mapped in this build |
| Type Expert | 2 | `0x02241C0C` | dynamic leader/mob/weak-mob pools | Mapped in this build |
| Rental | 12 | `0x02241B84` | 3 cat. 1 + 2 cat. 2 + 2 cat. 3 | Mapped in this build |
| Mix | 14 | `0x02241BB0` | 3 cat. 1 + 2 cat. 2 + 2 cat. 3 | Mapped in this build |
| Super Rental / Rental Master | 13 | `0x02241BDC` | seven cat.-3 selections | Mapped in this build |
| Super Mix / Mix Master | 15 | `0x02241BF4` | seven cat.-3 selections | Mapped in this build |
| Driftveil | 4 | `0x02241B20` | 4 cat. 1 + 1 cat. 2 + 2 cat. 3 | Mapped in this build |
| Download | 3 | `0x02241998` | generic/download-style shuffle | Mapped in this build |
| Driftveil event | 11 | `0x02241B4C` | 4 cat. 1 + 1 each cat. 3/4/5 | `WBTCUP_HODOMOE_EVENT`; enabled while ordinary Driftveil wins are zero |

The named mappings are based on the exact cup-ID dispatch, the matching
family slices, and the published rosters.  The Champions slice agrees with the
[Serebii Champions roster](https://www.serebii.net/black2white2/pwt/champion.shtml),
and the regional cup names/rosters are listed in [Serebii's PWT overview](https://www.serebii.net/black2white2/worldtournament.shtml).

## Champion placement

The Champion constructor fixes the participant set: the seven flagged records
are all used in the examined build. After that selection, the common match
builder shuffles eight participant pointers (the player plus seven NPCs) with
RNG at `0x02241DB8` and finalizes the player's position. Thus Champion names
can occupy different bracket slots on different runs even though the Champion
roster itself is fixed. This slot shuffle is separate from the NPC winner
routine and is not a downloadable `YY` field.

## USA/Europe retail cross-check

The complete USA/Europe Black 2 retail ROM was checked against the development
artifact for the WBT constructor code. Retail Overlay 135 is decompressed at
base `0x021EEC80` (4,032 bytes, SHA-256
`30b48d2cc1e724470351f57fa6fa28d2844f195732737052bc9ce41e57ef98b8`). It
contains the same relevant control-flow roles:

| Role | Development build | USA/Europe retail |
|---|---:|---:|
| candidate/category selector | `0x02241704` | `0x021EEE08` |
| category/type-affinity helper | `0x022418E2` | `0x021EEF90` |
| cup-ID dispatch and 16-entry switch | `0x02241CF8` / `0x02241D20` | `0x021EF298` / `0x021EF2C0` |
| common eight-position shuffle | `0x02241DB8` | `0x021EF344` |

The retail selector still filters records by the packed category bits, the
helper still treats category `0x11` as neutral/sentinel, the dispatch still
accepts cup IDs `0..15`, and the common builder still performs the RNG-based
participant-position shuffle. The compiler-generated addresses and some stack
layout differ, so this establishes behavior rather than address identity.

The retail file-system path for this same WBT table is `/a/2/4/7`, not
`/a/2/6/1`: it is a 2,108-byte NARC with one 2,048-byte member and its
SHA-256 is exactly the development table's
`0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`.
Therefore the development record indices and named roster mapping carry over
byte-for-byte to the examined USA/Europe retail ROM. The retail
`/a/2/6/1` file is a different 24,052-byte NARC with 1,000 16-byte members
(SHA-256 `416ddd7a37b89bcada27e977dc0a59df818ccddf4b9e47dd2f3ae39d742b5980`)
and is not the WBT table used for this mapping.

## Constructor slot requests

The internal request pattern should not be confused with source-record counts:

| Cup IDs | Constructor | Requests |
|---|---|---|
| `5–9` | `0x02241B08` | seven category-3 selections |
| `1` | `0x02241A88` | all records whose packed flag is set, then up to seven are used |
| `2` | `0x02241C0C` | dynamic leader/mob/weak-mob selection, totaling seven NPCs (Type Expert) |
| `4` (and default/0 after its error log) | `0x02241B20` | 4 cat. 1 + 1 cat. 2 + 2 cat. 3 |
| `11` | `0x02241B4C` | 4 cat. 1 + 1 cat. 3 + 1 cat. 4 + 1 cat. 5 |
| `12`, `14` | `0x02241B84`, `0x02241BB0` | 3 cat. 1 + 2 cat. 2 + 2 cat. 3 |
| `10`, `13`, `15` | `0x02241AF0`, `0x02241BDC`, `0x02241BF4` | seven category-3 selections |
| `3` | `0x02241998` | generic/download-style path |

The ID-to-constructor rows above are decoded from the signed halfword switch
at `0x02241D20–0x02241D3E` in overlay 135, not inferred from the menu order.
The corrected special rows are ID 12 → `0x02241B84`, ID 14 → `0x02241BB0`,
and ID 15 → `0x02241BF4`.

The candidate pool size is fixed by the data table. RNG chooses among eligible
records when a constructor requests fewer records than the eligible pool; it
does not regenerate the number of source records on each entry.

## Type Expert detail

Type Expert (ID 2) is not “all records with equal probability.” Its constructor
first counts candidate records in the leader, mob, and weak-mob groups, then
selects those groups and fills the remaining slots. The code checks:

```text
1 + leader_num + mob_num + weak_mob_num == WBT_TRAINER_NUM
```

The public [TournamentSearcher reverse-engineering project](https://github.com/namofure/TournamentSearcher)
also treats this dynamic path as a structured participant/shuffle problem, not
as a simple downloadable `YY` histogram. World Leaders is ID 10 and uses its
separate seven-category-3 constructor path.

## Static menu-to-ID evidence

The names are linked to numeric IDs without an emulator. In `/a/0/5/9`, member
1277, the script shows the tournament prompt at `0x05D6`; the list-menu
command begins at `0x05E2` and writes its result to work variable `0x8023`.
At `0x02E7`, `CMD_3F3` (`EvCmdWBTSetWBTCup`) stores that value as the cup ID,
and the description switch at `0x0B95–0x0DC0` compares the same value. The
neighboring reception-ID setter is `CMD_3F7`; `CMD_3EF` is a different WBT
command. The description lines are from `/a/0/0/5`, member 668:

| ID | Text line | Mode |
|---:|---:|---|
| 1 | `0x08` | Champions |
| 2 | `0x07` | Type Expert |
| 3 | `0x09` | Download |
| 4 | `0x0A` | Driftveil |
| 5–9 | `0x0B–0x0F` | Unova, Kanto, Johto, Hoenn, Sinnoh Leaders |
| 10 | `0x10` | World Leaders |
| 11 | `0x71` (`113`) | Driftveil event cup (`WBTCUP_HODOMOE_EVENT`) |
| 12 | `0x11` | Rental |
| 13 | `0x13` | Rental Master |
| 14 | `0x12` | Mix |
| 15 | `0x14` | Mix Master |

Text line 113 says “this Driftveil tournament” and is distinct from the
ordinary Driftveil description at line 10. The recovered source now resolves
the numeric ID rather than leaving it reserved: `wbt.h` defines ID 11 as
`WBTCUP_HODOMOE_EVENT`, and `wbt_lobby.ev` requests it first in the menu as
`SCR_WBT_CUP_HODOMOE_EVENT`. ID 0 remains the null/error path.

The menu still supplies cup IDs dynamically. Member 1277 checks each candidate
with `CMD_3EE`, conditionally emits `ListMenuAdd` with that candidate as UID
(including 11), stores the selected UID in `0x8023`, and passes it to
`CMD_3F3`; therefore no literal `CMD_3F3 11` is required.

The exact enable predicate is in the original `wbt_tool.c` source:

```text
ID 11 (WBTCUP_HODOMOE_EVENT): ordinary Driftveil win count == 0
ID 4  (WBTCUP_HODOMOE):       ordinary Driftveil win count != 0
```

Thus the event cup is enabled before the ordinary Driftveil cup has a win
recorded. It is not gated by the previously reported eight-record `CMD_3EA`
sequence.

The source also resolves the command-name ambiguity. `scrcmd_wbt_table.cdat`
registers WBT `CMD_3EA` as `EvCmdWBTSystemCheckEnable`, while the separate
Join Avenue `scrcmd_resort_table.cdat` registers Resort `CMD_3EA` as
`EvCmdResortGetData`. `EvCmdWBTGetVictoryCount` is WBT `CMD_3FA`. The same
numeric command is therefore overlay/table-specific, not one global function.

Retail member 1280 is `resort_scr.bin`, the Join Avenue script containing the
Resort command sequence. Its matching bytes in `/a/0/5/6` verify the source
mapping, but they are not a PWT unlock script.

## Source-defined cup enable predicates

The recovered WBT source makes the in-game menu predicates explicit. These are
the predicates used by `WBTTOOL_CheckCupEnable` in `wbt_tool.c`; they are not
the downloadable `.pwt` `YY` fields.

| ID | Source enum | Enable condition |
|---:|---|---|
| 1 | `WBTCUP_CHAMPION` | World Leaders win count is at least 10 |
| 2 | `WBTCUP_POKETYPE` | All five regional Leader win counts are nonzero |
| 3 | `WBTCUP_DOWNLOAD` | Ordinary Driftveil win count is nonzero |
| 4 | `WBTCUP_HODOMOE` | Ordinary Driftveil win count is nonzero |
| 5 | `WBTCUP_ISSYU` | `SYS_FLAG_GAME_CLEAR` is set |
| 6–9 | `WBTCUP_KANTO`…`WBTCUP_SINOU` | Unova Leader win count is nonzero |
| 10 | `WBTCUP_WORLD` | All five regional Leader win counts are nonzero |
| 11 | `WBTCUP_HODOMOE_EVENT` | Ordinary Driftveil win count is zero |
| 12 | `WBTCUP_RENTAL` | Ordinary Driftveil win count is nonzero |
| 13 | `WBTCUP_RENTALMASTER` | Rental win count is nonzero and all regions are cleared |
| 14 | `WBTCUP_MIX` | Ordinary Driftveil win count is nonzero |
| 15 | `WBTCUP_MIXMASTER` | Mix win count is nonzero and all regions are cleared |

The lobby source `wbt_lobby.ev` requests ID 11 first, then ID 4. This explains
why Bianca's selectable Unova roster entry and the special Driftveil event are
not excluded: roster membership and cup availability are separate source
decisions.

This also corrects the earlier tentative ID assignment: ID 2 is Type Expert,
not World Leaders; ID 10 is World Leaders.

## Remaining uncertainty

The mapping is for the archived development build and the matching Black 2
USA/Europe retail script. Other regional/revision builds should still be
checked before assuming that every address and roster byte is identical.
The source-level cup enum, ID-11 predicate, menu producer, and command symbols
are no longer unresolved.

## Static-only status

The constructor dispatch, source-table counts, Champion roster, slot shuffle,
NPC winner routine, cup enable predicates, and menu-name-to-ID mapping can all
be reproduced from the archived ROM files, disassembly, scripts, and recovered
source without an emulator. ID 11 is now identified as
`WBTCUP_HODOMOE_EVENT`; WBT `CMD_3EA` is `EvCmdWBTSystemCheckEnable`, Resort
`CMD_3EA` is `EvCmdResortGetData`, and WBT `CMD_3FA` is
`EvCmdWBTGetVictoryCount`. Remaining work is only cross-region/build
verification, not symbol or event-condition recovery.
