# PWT bracket settings (`YY`)

> Scope note: the public byte-level `YY` documentation is for downloadable
> `.pwt` files. Built-in cups use separate internal constructor/category data;
> the literal raw-byte equivalence has not been proved. See
> [`in-game-tournaments.md`](in-game-tournaments.md).

Each downloadable `.pwt` file has seven opponent records with a four-byte
bracket record. The second byte is the bracket-setting field discussed in the
Project Pokémon reverse-engineering notes. Do not silently transfer that file
format to built-in cups.

| `YY` | Documented role | Practical meaning |
|---:|---|---|
| `00` | Unknown/special | Not fully identified in the public notes. |
| `01` | Filler Trainer | Used to fill ordinary opponent slots. |
| `02` | Possible First Battle | Eligible for the player's first-round encounter. |
| `03` | Possible Whenever battle | Flexible opponent category. |
| `04` | Required Semifinalist Battle | Candidate reserved for the player's semifinal encounter. |
| `05` | Required Finalist Battle | Candidate reserved for the player's final encounter. |

## What the selector does

The development-build `wbt_makematch.c` code selects seven opponents plus the player. One observed downloadable-style selection path calls the candidate selector with internal categories/counts equivalent to:

```text
category 5: 1 record   # required finalist
category 4: 1 record   # required semifinalist
category 3: 1 record   # flexible/whenever
category 1: 4 records  # fillers
```

The relevant selector call sequence is in overlay 135 around `0x02241B4C`, with candidate matching around `0x02241704`. This is bracket/opponent assignment, not match-result calculation.

### Same-tier selection

If two or more downloadable records share `YY=04`, the game chooses among those semifinal-tier candidates using RNG. If two or more share `YY=05`, it chooses among those finalist-tier candidates using RNG. If only Red has `YY=05`, Red is selected without a same-tier name choice. The count of records carrying each tier is fixed by the file; built-in per-family histograms are documented separately in [`in-game-tournaments.md`](in-game-tournaments.md).

### No hidden victory roll

The `YY` selector does not call the NPC result routine to make a tagged trainer qualify. A required finalist record is reserved as the player's final opponent category; the player then battles that trainer directly. The 65/35 A-slot result documented in [`../RESEARCH.md`](../RESEARCH.md) applies only when two NPC records are actually passed to `wbt_calc_result` for an all-NPC simulated match.

## Relation to the bracket screen

The bracket settings answer “which opponent is scheduled for which player round?” They do not by themselves answer “which NPC wins an NPC-vs-NPC match?” Those are separate pieces of code and separate RNG uses.

## Evidence and scope

- Project Pokémon notes label the fields “Required Finalist” and “Required Semifinalist” and state that same-setting entries are selected randomly.
- The archived development build contains the selector trace and debug format `SELECT TRAINER(...):pri(... )btl(... )candidate(...)` in overlay 135.
- No original Nintendo source code is available; these are disassembly/data findings from an archived development build.
- Exact `YY` assignments can vary by downloadable tournament file. The category semantics above describe that file selector, not a guarantee that every retail or built-in tournament uses every category.
