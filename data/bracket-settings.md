# PWT bracket settings (`YY`)

> Scope note: the public byte-level `YY` documentation is for downloadable
> `.pwt` files. Built-in cups use separate internal constructor/category data;
> the literal raw-byte equivalence has not been proved. See
> [`in-game-tournaments.md`](in-game-tournaments.md).

Each downloadable `.pwt` file has seven opponent records with a four-byte
bracket record. The second byte is the bracket-setting field discussed in the
Project Pokémon reverse-engineering notes. Do not silently transfer that file
format to built-in cups.

| `YY` | Public/observed label | Source-backed meaning |
|---:|---|---|
| `00` | `WBT_TRPRI_NULL` (`pri = 0`, undefined) | Lowest/unprioritized numeric value. It does not request a particular player round. |
| `01` | Filler Trainer | Low-priority record normally used for ordinary opponent slots. |
| `02` | Possible First Battle | Priority-2 record; its usual role is a first-round candidate when higher priorities occupy the structured slots. |
| `03` | Possible Whenever battle | Priority-3 flexible record. |
| `04` | Required Semifinalist Battle | Priority-4 record; it is a semifinal candidate when no higher-priority record takes that slot. |
| `05` | Required Finalist Battle | Priority-5 record; the highest-priority record takes the final path, while equal-priority records can fill the next structured positions. |

### `YY=00` is the source-defined null/lowest priority

The recovered SWAN source defines the field precisely. A downloadable record
is declared as `WBTDL_MATCH { type, pri, id }` in
`include/savedata/wbt_download.h`, so byte 1 (`YY`) is copied as `pri`. The
priority enum in `include/field/wbt.h` defines `WBT_TRPRI_NULL = 0`, followed
by priorities 1 through 5. `NULL` means **undefined** in the source enum; it is
not an extra named bracket tier.

During downloadable setup, `wbt_system_lobby.c` assigns each non-player
trainer's `wbt_tr->pri` from the record's `pri`. `WBTSYS_SortTrainer` in
`wbt_makematch.c` then sorts the seven NPCs in descending priority before
placing the highest-priority records into the structured player-path slots and
shuffling the remainder. Consequently, `YY=00` is simply the lowest/
unprioritized value. In a mixed list it sorts behind every record with
`YY=01`–`05`, so it does not itself request a semifinal or final slot. The
sorter is generic, however: if there are not enough higher-priority records, a
priority-0 record can still fill one of the structured positions because the
constructor always places its highest three available records there. `YY=00`
therefore supplies no special guarantee; its effect is only the numeric
priority value.

The same value also reaches `wbt_calc_result.c`. Against another `YY=00`
record, priorities tie and the normal affinity/RNG rule runs; against a record
with `YY=01`–`05`, the higher-priority record wins deterministically before the
affinity branch. This result behavior is separate from the player override.

The sorter does not assign a separate, exclusive round enum to each numeric
value. It first randomizes the trainer order, then sorts the seven NPCs by
descending priority. The highest-priority record is placed on the player's
final path, the second-highest on the semifinal path, and the third-highest in
the first-round path; the remaining four fill the other positions. Equal-
priority records retain their randomized relative order. Consequently, a file
with two `YY=05` records can place one on the final path and the other on the
semifinal path, and `YY=04` is not guaranteed to be the semifinal when a
priority-5 record is present.

The public reverse-engineering notes still use behavioral labels such as
“Filler,” “Possible First,” “Semifinalist,” and “Finalist.” Those labels remain
useful descriptions of the downloadable selector, but the source-level field
behind them is the numeric `pri` value above—not a separate `YY=00` category.

## What the selector does

The development-build `wbt_makematch.c` code selects seven opponents plus the player. The built-in Driftveil event constructor (`entryHodomoeEventTournament`, at `0x02241B4C`) calls the candidate selector with internal categories/counts equivalent to:

```text
category 5: 1 record   # required finalist
category 4: 1 record   # required semifinalist
category 3: 1 record   # flexible/whenever
category 1: 4 records  # fillers
```

The relevant selector call sequence is in overlay 135 around `0x02241B4C`, with candidate matching around `0x02241704`. This is bracket/opponent assignment, not match-result calculation.

### Duplicate priorities

Multiple downloadable records may share the same `YY` value. RNG determines
their relative order among equal-priority records; the generic sorter then
assigns the top three sorted records to the final, semifinal, and first-round
player paths. It does not independently choose one `YY=05` record for the final
and one `YY=04` record for the semifinal. Built-in per-family histograms are
documented separately in [`in-game-tournaments.md`](in-game-tournaments.md).

### No hidden victory roll

The `YY` setup does not call the NPC result routine to make a tagged trainer
qualify. The priority sorter places the highest-ranked available record on the
player's final path; the player then battles that trainer directly. The
source-backed 50/50 equal-affinity or 70/30 type-advantage results documented
in [`../RESEARCH.md`](../RESEARCH.md) apply only when two NPC records are
actually passed to `wbt_calc_result` for an all-NPC simulated match.

## Relation to the bracket screen

The bracket settings answer “which opponent is scheduled for which player round?” They do not by themselves answer “which NPC wins an NPC-vs-NPC match?” Those are separate pieces of code and separate RNG uses.

## Evidence and scope

- Project Pokémon notes label the fields “Required Finalist” and “Required Semifinalist” and state that same-setting entries are selected randomly.
- The archived development build contains the selector trace and debug format `SELECT TRAINER(...):pri(... )btl(... )candidate(...)` in overlay 135.
- The recovered SWAN source mirror (SVN revision 59995, branch
  `branches/upper_version`) confirms the field and its consumers in
  `include/savedata/wbt_download.h`, `include/field/wbt.h`,
  `field/wbt_system_lobby.c`, `field/wbt_makematch.c`, and
  `field/wbt_calc_result.c`. The source is retained locally and is not
  redistributed in this repository.
- The recovered SWAN source identifies the separate Join Avenue/Resort
  `CMD_3EA` wrapper as `EvCmdResortGetData`. WBT uses the same numeric slot for
  `EvCmdWBTSystemCheckEnable`; neither symbol changes the bracket semantics,
  which remain disassembly/data findings from the archived development build.
- Exact `YY` assignments can vary by downloadable tournament file. The category semantics above describe that file selector, not a guarantee that every retail or built-in tournament uses every category.
