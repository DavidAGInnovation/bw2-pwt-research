# Generic and Rental candidate records

This page closes the remaining candidate-pool question for the examined
development build and the byte-identical USA/Europe retail WBT table. It is a
mapping of source-table records and constructor eligibility; it is not a list
of six-Pokémon battle outcomes.

## Source-record fields used by the constructor

The one-member WBT table has 128 records of 16 bytes. Overlay 135 reads these
fields directly from each record:

| Record field | Offset | Use in the code |
|---|---:|---|
| Constructor eligibility mask | `5` | Cup IDs 4, 10, 11, 12, 13, 14, and 15 test one bit here. |
| Family selector | `6` | Cup IDs 1 and 5–9 accept records whose value equals the cup ID. |
| Type Expert type ID | `7` | Cup ID 2 accepts the requested type or `0x11` (`POKETYPE_NULL`) as a wildcard. |
| Constructor pool | `8 & 7` | The selector at `0x02241630` compares these low three bits with pool requests 1–5. |

The relevant disassembly is the predicate at `0x02241874`, the pool counter at
`0x02241630`, and the selector at `0x02241704`. These are internal source-table
fields, not downloadable `.pwt` `YY` values.

The mask bits used by the static cup predicates are:

| Cup ID | Mode | Test |
|---:|---|---|
| 4 | Driftveil | `byte[5] & 0x02` |
| 10 | World Leaders | `byte[5] & 0x04` |
| 11 | Driftveil event | `byte[5] & 0x01` |
| 12 | Rental | `byte[5] & 0x08` |
| 13 | Rental Master | `byte[5] & 0x20` |
| 14 | Mix | `byte[5] & 0x10` |
| 15 | Mix Master | `byte[5] & 0x40` |

Cup IDs 1 and 5–9 use the family-selector comparison instead. The Download
path (ID 3) uses its separate generic/download constructor. Type Expert (ID 2)
uses the type-ID comparison and its dynamic leader/mob/weak-mob grouping.

## Complete non-named record groups

The table below groups the records that are not the named regional
Leader/Champion rows already listed in
[`champions-and-leaders.md`](champions-and-leaders.md). `type ID` is raw byte 7;
`pool` is raw byte 8 masked with `7`.

| Indices | Mask byte 5 | Family byte 6 | Type ID | Pool | Static eligibility |
|---|---:|---:|---:|---:|---|
| `54` | `0x00` | `0x00` | `0x12` | 4 | None of IDs 4, 10–15 |
| `55` | `0x01` | `0x00` | `0x12` | 3 | ID 11 |
| `56` | `0x01` | `0x00` | `0x12` | 4 | ID 11 |
| `57` | `0x01` | `0x00` | `0x12` | 5 | ID 11 |
| `58–67` | `0x00` | `0x00` | `3, 4, 6, 7, 8, 13, 15, 16` | 2 | None of IDs 4, 10–15 |
| `68–77` | `0x1A` | `0x00` | `0x12` | 2 | IDs 4, 12, and 14 |
| `78–127` | `0x1B` | `0x00` | `0x11` | 1 | IDs 4, 11, 12, and 14 |

The complete 16-byte row for every index, including the exact per-record values
in the `58–67` range, is reproducible with the decoder's `--dump-records`
option. The dump includes both the raw bytes and the decoded constructor fields;
the grouped table above is a compact view of that exact output.
The `0x11` type ID in records 78–127 is the Type Expert wildcard; it is
separate from the category-17 neutral sentinel used by the NPC winner routine.

## Rental and Mix pools

The constructor calls and the table predicates produce these exact pools:

| Mode | Requested pools | Eligible records by pool |
|---|---|---|
| Rental (ID 12) | 3 from pool 1; 2 from pool 2; 2 from pool 3 | Pool 1: `78–127`; pool 2: `68–77`; pool 3: `0–4, 8` |
| Rental Master (ID 13) | 7 from pool 3 | Pool 3: `0–13, 20–52` |
| Mix (ID 14) | 3 from pool 1; 2 from pool 2; 2 from pool 3 | Pool 1: `78–127`; pool 2: `68–77`; pool 3: `0–4, 8` |
| Mix Master (ID 15) | 7 from pool 3 | Pool 3: `0–7` |

The selector chooses the requested number from each eligible pool; it does not
assign a permanent personal win/loss record to a trainer.

### Named records in those pools

- Rental and Mix pool 3 (`0–4, 8`) is Cheren, Roxie, Burgh, Elesa, Clay, and
  Bianca. The constructor selects two records from these six pool-3
  candidates, so no individual record is guaranteed to appear in every run.
- Rental Master pool 3 (`0–13, 20–52`) contains all 13 standard Unova Leaders,
  Bianca, and every Kanto, Johto, Hoenn, and Sinnoh Leader (47 records total).
- Mix Master pool 3 (`0–7`) contains Cheren, Roxie, Burgh, Elesa, Clay, Skyla,
  Drayden, and Marlon.
- The seven standard Champions (`14–19, 53`) are absent from all four pools:
  their mask byte is `0x00`, while each Rental/Mix predicate requires a set
  mask bit.

## What the record-packing path proves

Rental selection admits records through the pool predicates without replacing
their stored result-routine category with a type derived from the Rental
Pokémon. For example, record index 3 (Elesa) stores category 12 (Electric), as
shown in [`champions-and-leaders.md`](champions-and-leaders.md). The common
record packer at `0x0224208C` supplies the selected record to the same winner
routine documented in [`RESEARCH.md`](../RESEARCH.md), which reads the packed
priority/category fields and never inspects the six-Pokémon roster. The same
principle applies to every selected record: its stored category remains the
input to the displayed NPC result calculation. Standard Champions are not
selected by Rental or Rental Master in this table, so their priority/category
values are not used there through the standard Champion records.

## Reproduction

With the extracted development WBT NARC:

```sh
python3 scripts/inspect_wbt_table.py rom/extracted/a/2/6/1 \
  --cup 12 --cup 13 --cup 14 --cup 15

# Optional: print all 128 complete source rows and decoded constructor fields.
python3 scripts/inspect_wbt_table.py rom/extracted/a/2/6/1 --dump-records --cup 12
```

The USA/Europe retail WBT NARC is `/a/2/4/7`; its member is byte-for-byte
identical to the development table used above.
