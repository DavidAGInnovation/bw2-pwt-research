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
| Reserved/special branch | 11 | `0x02241B4C` | 4 cat. 1 + 1 each cat. 3/4/5 | No ordinary menu label |

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
| 11 | `0x71` (`113`) | Reserved/current-tournament message; not an ordinary named cup |
| 12 | `0x11` | Rental |
| 13 | `0x13` | Rental Master |
| 14 | `0x12` | Mix |
| 15 | `0x14` | Mix Master |

Text line 113 says “this Driftveil tournament” and is distinct from the
ordinary Driftveil description at line 10, so ID 11 is retained as a
special/reserved branch rather than guessed as a second Driftveil mode. ID 0
is the null/error path. Neighboring text entry 112 says that a special
tournament is being prepared, reinforcing the temporary/event interpretation.

ID 11 is not merely a dead dispatch value: the description branch and the WBT
state script reference it. However, the earlier scan of `CMD_3EF` arguments was
misinterpreted; `CMD_3EF` is not `EvCmdWBTSetWBTCup`. No literal
`CMD_3F3 11` appears in the examined script archive. The safest current label
is **introductory/story Driftveil tournament state (reserved special slot)**,
based on the exact wording of text entry 113 and its use alongside the
eight-record `CMD_3EA` check in zero-based NARC entry 1280.

The eight-record gate is exact, not hypothetical. The script sets accumulator
`0x8055` to zero, reads records `17, 18, 21, 20, 19, 22, 23, 24` with
`CMD_3EA`, and adds one only when a returned counter equals `1`. It then
compares the accumulator with `1`: message 113 (the unrestricted/current
Driftveil text) is selected when **exactly one** of the eight records is at one;
message 114 is selected otherwise. The scanner records the final comparison at
member offset `0x38FF` and reproduces it in both development and retail
archives. This resolves the event condition without an emulator. It should not
be described as a direct assignment of cup ID 11, because the branch does not
call the cup setter.

`CMD_3EA` is a PWT progress-record getter in this script context. It reads the
16-bit value for the supplied record ID and writes it to the output variable;
the script's comparison with `1` is an exact one-win test, not a boolean
unlock test. PKHeX's record map and PKSM's unlock script independently confirm
that these values are victory/progress counters (see the links in
`data/in-game-constructor-categories.md`). Overlay 55's debug name
`EvCmdWBTGetVictoryCount` belongs to its separate `CMD_3FA` handler; the
Overlay-58 `CMD_3EA` wrapper has no recovered Nintendo symbol. The behavior,
however, is no longer unresolved.

The retail member is now verified against the complete downloaded Black 2
USA/Europe ROM: retail stores the script in `/a/0/5/6` (1,289 entries), with
the same state-check sequence in member 1280 and the offsets recorded in
`data/in-game-constructor-categories.md`. The ROM and extracted NARC are
retained locally for comparison; their public-mirror provenance is not a
legally verified user dump.

This also corrects the earlier tentative ID assignment: ID 2 is Type Expert,
not World Leaders; ID 10 is World Leaders.

## Remaining uncertainty

The mapping is for the archived development build identified in the companion
page and its matching Black 2 USA/Europe retail script. Retail regional builds
should be checked before assuming that the same special ID 11 and family-`0x00`
assignments apply everywhere. No original Nintendo source code was obtained;
the only remaining ID-11 question is which runtime menu/resource path can
return numeric value 11 to the cup setter. The event gate and the `CMD_3EA`
counter semantics are statically resolved.

## Static-only status

The constructor dispatch, source-table counts, Champion roster, slot shuffle,
NPC winner routine, and ordinary menu-name-to-ID mapping can all be reproduced
from the archived ROM files, disassembly, and NARC tables without an emulator.
The only built-in dispatch value still without an ordinary player-facing name
is the special ID 11 branch described above. Member 1277 is a menu/controller
script; the menu result is stored with `CMD_3F3` (`EvCmdWBTSetWBTCup`).
`CMD_3F7` is the reception-ID setter. The event condition that selects the
special Driftveil text is fully reproducible from member 1280 and is not an
unresolved flag hypothesis.
