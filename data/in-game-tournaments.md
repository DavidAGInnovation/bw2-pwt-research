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
| `0x00` | `8, 54–127` | 75 | Special/other records; index 8 is Bianca, a wildcard included by the Unova Leaders constructor |

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
| World Leaders | 2 | `0x02241C0C` | cross-region candidate pools plus the Unova wildcard | Dynamic; not one fixed count |
| Champions | 1 | `0x02241A88` | byte2 `0x01`: 7 records | Mapped in this build |
| Super Rental / Rental Master | not assigned | one of remaining constructors | likely special/family-`0x00` data; exact ID not proven | Open |
| Super Mix / Mix Master | not assigned | one of remaining constructors | likely special/family-`0x00` data; exact ID not proven | Open |
| Type Expert | not assigned | one of remaining constructors | likely special/family-`0x00` data; exact ID not proven | Open |

The seven named mappings are based on the exact cup-ID dispatch, the matching
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
| `2` | `0x02241C0C` | dynamic leader/mob/weak-mob selection, totaling seven NPCs |
| `4` (and default/0 after its error log) | `0x02241B20` | 4 cat. 1 + 1 cat. 2 + 2 cat. 3 |
| `11` | `0x02241B4C` | 4 cat. 1 + 1 cat. 3 + 1 cat. 4 + 1 cat. 5 |
| `12`, `15` | `0x02241BB0`, `0x02241B84` | 3 cat. 1 + 2 cat. 2 + 2 cat. 3 |
| `10`, `13`, `14` | `0x02241AF0`, `0x02241BDC`, `0x02241BF4` | seven category-3 selections |
| `3` | `0x02241998` | generic/download-style path |

The candidate pool size is fixed by the data table. RNG chooses among eligible
records when a constructor requests fewer records than the eligible pool; it
does not regenerate the number of source records on each entry.

## World Leaders detail

World Leaders is not “all 54 records with equal probability.” Its constructor
first counts candidate records in the leader, mob, and weak-mob groups, then
selects those groups and fills the remaining slots. The code checks:

```text
1 + leader_num + mob_num + weak_mob_num == WBT_TRAINER_NUM
```

The public [TournamentSearcher reverse-engineering project](https://github.com/namofure/TournamentSearcher)
also treats World Leaders as a structured participant/shuffle problem, not as a
simple downloadable `YY` histogram.

## Remaining uncertainty

The mapping is for the archived development build identified in the companion
page. Retail regional builds should be checked before assuming that the same
unused/special cup IDs and family-`0x00` assignments apply everywhere. No
original Nintendo source code was obtained; the evidence is disassembly plus
the extracted table and public roster references.
