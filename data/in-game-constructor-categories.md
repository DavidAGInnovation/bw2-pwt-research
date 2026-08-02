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
| `0x02241C0C` | Dynamic leader/mob/weak-mob path used by World Leaders. |

## Cup-ID dispatch (confirmed)

The jump table at `0x02241D20–0x02241D3E` and the calls following it give this
exact mapping in the examined build.  “Cat. 1–5” are internal selector
categories.

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
| 12 | `0x02241BB0` | 3 | 2 | 2 | 0 | 0 | Three cat. 1, two cat. 2, two cat. 3 |
| 13 | `0x02241BDC` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 14 | `0x02241BF4` | 0 | 0 | 7 | 0 | 0 | Seven cat.-3 selections |
| 15 | `0x02241B84` | 3 | 2 | 2 | 0 | 0 | Three cat. 1, two cat. 2, two cat. 3 |

Cup ID 0 reaches the same constructor as cup 4 after logging the
`WBTCUP_NULL!!` error path; it is not a separate named cup in this artifact.

## Mapping to named permanent cups

The following seven mappings are high-confidence for this build.  The cup IDs
come from the dispatch above; the names are matched to the fixed family byte
in NARC `/a/2/6/1` and to the published PWT rosters.  The family byte is raw
record **byte 2**.  It is not the downloadable `.pwt` `YY` byte.

| Named cup | Cup ID | Constructor | Raw family byte 2 | Source-table records in this build | Confidence |
|---|---:|---|---:|---|---|
| Champions | 1 | `0x02241A88` | `0x01` | indices `14–19, 53` (7 records) | High: fixed Champion roster and flagged path |
| World Leaders | 2 | `0x02241C0C` | leader families plus the Unova wildcard | Cross-region candidate set; not one contiguous slice | High: dynamic leader/mob/weak-mob path |
| Unova/Teselia Leaders | 5 | `0x02241B08` | primarily `0x05` | indices `0–13` (14 possible NPCs: 13 standard Leaders + Bianca wildcard at index 8) | High: family roster/order and cup progression |
| Kanto Leaders | 6 | `0x02241B08` | `0x06` | indices `20–26, 35` (8 records) | High: family roster/order |
| Johto Leaders | 7 | `0x02241B08` | `0x07` | indices `27–34` (8 records) | High: family roster/order |
| Hoenn Leaders | 8 | `0x02241B08` | `0x08` | indices `36–44` (9 records) | High: family roster/order |
| Sinnoh Leaders | 9 | `0x02241B08` | `0x09` | indices `45–52` (8 records) | High: family roster/order |

The regional names and rosters agree with the public PWT listings for the
[regional Leaders cups](https://www.serebii.net/black2white2/worldtournament.shtml),
[Kanto Leaders](https://www.serebii.net/black2white2/pwt/kanto.shtml), and
[Champions](https://www.serebii.net/black2white2/pwt/champion.shtml).  The
development table also contains the seven Champion records (Blue, Lance,
Steven, Wallace, Cynthia, Alder, and Red) described by those references.

## Remaining IDs and special modes

IDs `0`, `3`, `4`, `10–15` are present in the same dispatch, but this artifact
does not yet prove which of them is the Driftveil, Rental, Mix, Super Rental,
Super Mix, Type Expert, or a downloadable/special mode.  In particular, it
would be a guess to label IDs `10`, `13`, and `14` as the three “super/type”
cups merely because they all request seven category-3 records. The source
table's family-`0x00` records (indices `8, 54–127`, 75 records) are
special/other data. Index 8 is the known Unova-cup wildcard (Bianca); the
remaining `54–127` records are special or download-related, but their
player-facing names are not mapped here.

## World Leaders special path

Constructor `0x02241C0C` counts and selects three groups rather than using one
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

Therefore World Leaders is a dynamic candidate-pool selection, not a fixed
downloadable-style `YY` histogram.

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
- No original Nintendo C/C++ source was obtained. These are disassembly
  addresses, not official source symbols.
- Retail verification is still desirable before treating every address or
  unused/special ID as universal across regional releases.
