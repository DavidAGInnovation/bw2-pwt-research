# WBT party construction and roster selection

This document covers the trainer's battle party, which is a different layer
from the eight-trainer NPC field and bracket construction described in
[`in-game-constructor-categories.md`](in-game-constructor-categories.md).

## What the examined code proves

The development Overlay 55 disassembly contains the `wbt_party.c` party
builder. Its caller passes a literal `6` to the builder, and the returned
party is consumed in a loop whose index runs from `0` through `5`. In this
build, every WBT trainer therefore receives a six-entry roster before the
battle-rule table determines the number of active entries.

The source-level rule table is explicit. `wbt.h` assigns rule IDs 0, 1, 2,
and 3 to single, double, triple, and rotation battles respectively;
`wbt_tool.c` stores `need_pokemon_num` as `3, 4, 6, 4` for those four IDs, and
`WBTTOOL_GetPartyMaxByRule` returns that field. The same table is present in
Overlay 55: the getter at `0x022387FC` indexes the byte table at
`0x02239B36`, whose four entries decode to `3, 4, 6, 4`. Consequently the
active-party mapping is verified as:

| Battle rule | Internal rule ID | Active Pokémon |
|---|---:|---:|
| Single | 0 | 3 |
| Double | 1 | 4 |
| Triple | 2 | 6 |
| Rotation | 3 | 4 |

The random-selection helper works as follows:

1. Count candidate records whose `available` flag is still set.
2. Obtain one RNG value and reduce it to a choice in the current
   `0..available_count-1` range.
3. Convert that ordinal to a source index by skipping unavailable records.
4. Clear the selected record's `available` flag and copy it to the output.
5. Repeat for the requested number of entries.

That is random selection without replacement. A selected Pokémon cannot be
selected again by a later iteration of the same request. The chooser is fed
by rule-dependent range descriptors: the battle-rule field at `work + 0x13e4`
dispatches internal branches `0`, `1`, and `2`. Branch `2` explicitly makes a
request of three entries and, when more are needed, a second request of
`count - 3` entries. The range-bound table itself is referenced through the
literal pointers at `0x02239850` and `0x0223985c`.

## Disassembly evidence

| Evidence | Address | Interpretation |
|---|---:|---|
| Six-entry request | `0x0223975A–0x0223976E` | Caller stores `6` as the party-builder count and calls `0x02239560`. |
| Six-entry output loop | `0x022397AA–0x022397E8` | Builds entries while `r5 < 6`. |
| Party-size getter | `0x022387FC–0x02238808` | Validates the rule, indexes the size table, and returns one byte. |
| Party-size table | `0x02239B36–0x02239B4E` | Encodes `3, 4, 6, 4` for single, double, triple, and rotation. |
| Battle-rule field | `0x022395BA–0x022395CA` | Reads `work + 0x13E4` and dispatches values `0`, `1`, and `2`. |
| Three-plus-remainder split | `0x0223964C–0x02239694` | Requests `3`, then requests `count - 3` when `count > 3`. |
| Available-record count | `0x02239280–0x022392C2` | Counts records whose availability byte is nonzero. |
| Ordinal-to-index mapping | `0x022392C4–0x022392F6` | Walks records, skipping unavailable entries. |
| Remove and copy selection | `0x02239308–0x02239352` | Writes availability `0`, then copies the selected record. |
| RNG selection loop | `0x02239368–0x022393F6` | Repeats for the requested count, calls the RNG wrapper, reduces by the available count, and records each index. |

The same source file's debug strings (`"wbt_party.c"`, `"available_count >=
cnt - set_count"`, and `"choose range"`) make the routine identification
independent of guessed function names. Run the small audit script with the
archived disassembly to check these signatures, including the party-size
getter and all four table entries:

```sh
python3 scripts/audit_wbt_party.py
```

## Fixed first Pokémon (ace path)

The six-entry builder is not the code that fixes a lead. The source path in
`wbt_battle.c` is explicit:

1. `wbt_system_lobby.c` sets `has_ace` when the trainer-list row's
   `ace_poke_id` is nonzero.
2. In `makeRomTrainerData`, an ace trainer loads the first entry of the ace
   trainer table (`use_poke_table[0]`) and writes that Pokémon to output
   position `0`.
3. The normal trainer table is then passed to the random chooser for the
   remaining `poke_num - 1` entries. The ace's source index is registered as
   unavailable, so it cannot be selected a second time.

This proves that a trainer marked with an ace has a fixed first Pokémon; the
remaining active positions are filled by the no-replacement selector. The
rule table above determines how many of those positions are active (3, 4, 6,
or 4), not which position is first.

## Complete trainer coverage

The source `wbt_trainer_list.txt` contains 128 trainer rows. Its ace marker is
compiled by `wbt_trainer.rb` into `ace_poke_id`; `wbt_system_lobby.c` then
turns a nonzero value into `has_ace`. The complete coverage audit is:

| Data scope | Trainer rows | Ace-marked | Unmarked | Result |
|---|---:|---:|---:|---|
| Trainer list | 128 | 74 | 54 | Metadata for the full list. |
| `wbt1` / `wbt2` party tables (IDs 0–118) | 119 | 74 | 45 | Every ace row resolves to a valid, nonzero species record; unmarked rows use the normal selector. |
| `wbt3` party tables (IDs 0–67) | 68 | 64 | 4 | Every present ace row resolves to a valid, nonzero species record; the four unmarked rows use the normal selector. |
| Trainer-list IDs 119–127 | 9 | 0 | 9 | No corresponding `wbt1/2/3` party-table rows, so no party-order claim is made from these resources. |

For the 74 ace-marked trainers, both `wbt1n_pd.narc` and `wbt2n_pd.narc`
contain a nonzero Pokémon record at the ace index supplied by the matching
`wbt1a_tr.tdm`/`wbt2a_tr.tdm` row. The 64 ace-marked trainers represented in
`wbt3` pass the same check against `wbt3n_pd.narc`. Therefore the fixed-first
algorithm is verified across every ace-marked trainer that has a party-table
record in the examined build.

The unmarked rows do not enter the ace branch at all: their complete party is
selected from the normal candidate list by the no-replacement chooser. In the
Champion data set, the visible unmarked examples are Green (ID 14), Red (ID
53), Touko (ID 54), and the Rival (ID 55). They do not have a fixed first
Pokémon in this code path.
