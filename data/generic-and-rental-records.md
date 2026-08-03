# Generic and Rental candidate records

This page documents the candidate-pool mapping for the examined development
build and the byte-identical USA/Europe retail WBT table. It maps source-table
records and constructor eligibility; it is not a list of six-Pokémon battle
outcomes.

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

## Complete non-regional/generic record groups

The table below groups the records that are not the regional Leader/Champion
rows already listed in
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

### How to read the generic-record map

This is a compact map of the unnamed/generic rows in the 128-record WBT source
table:

- **Indices** are source-table row numbers, not tournament positions.
- **Mask byte 5** determines which static cups may use a row. For example,
  `0x1A` sets the Driftveil, Rental, and Mix eligibility bits.
- **Family byte 6** identifies regional families. `0x00` means the rows in
  this non-named group are not standard named Leader or Champion family rows.
- **Type ID byte 7** is read by the Type Expert constructor. It is not the
  matchup category consumed later by the NPC winner routine.
- **Pool** is the internal constructor bucket, calculated as `byte 8 & 7`.
  Rental requests records from pools 1, 2, and 3.

For Rental, the generic candidates are records `78–127` in pool 1 and
`68–77` in pool 2. Named records `0–4, 8` supply pool 3. These are eligibility
sets, not guaranteed appearances: the constructor randomly selects the
requested number of records from each pool.

Some generic rows do carry specific Type Expert IDs. Records `58–67` use the
following raw byte-7 values:

| Raw Type ID | Type Expert type |
|---:|---|
| `0x03` | Poison |
| `0x04` | Ground |
| `0x06` | Bug |
| `0x07` | Ghost |
| `0x08` | Steel |
| `0x0D` | Psychic |
| `0x0F` | Dragon |
| `0x10` | Dark |

This type-specific interpretation applies to Type Expert filtering only. The
Rental/Mix generic rows use raw byte-7 values `0x12` (records `68–77`) or
`0x11` (records `78–127`); `0x11` is the Type Expert wildcard, not a fixed
Pokémon type. Although that wildcard is numerically the same as decimal 17,
the Type Expert wildcard and the category-17 neutral sentinel belong to
different fields and code paths.

## Packed NPC-result fields for every generic row

The constructor's byte-7 Type ID is not the field used by the displayed NPC
winner routine. The built-in row-conversion path around `0x022421C6` copies a
source row and prepares the common packer at `0x0224208C` as follows:

| Source-table value | Packed runtime field | Meaning |
|---|---|---|
| `byte 8 & 7` | priority bits 4–6 of packed byte 0 | Priority compared first by the NPC result routine. |
| `byte 0` | packed byte 1 | Matchup category read by the type-affinity helper. |
| built-in source-row path | trainer-type flag `0` in packed byte 0 bits 0–2 | NPC record; the player override uses a different flag. |

The converter passes the source row's byte 1 as the sex selector, the row's
bytes 2–3 as `mmdl_id`, and byte 4 as `btl_tr_type`; it also passes the source
row index as the runtime `tr_id`. These are identity/setup fields, not inputs
to the NPC winner calculation. The result below is therefore a complete
mapping of the generic rows' relevant result fields, not a claim that each row
is selected in every cup.

| Source indices | Packed priority | Result category | Category meaning | NPC trainer type |
|---|---:|---:|---|---:|
| `54` | 4 | 17 (`0x11`) | neutral sentinel | 0 |
| `55` | 3 | 17 (`0x11`) | neutral sentinel | 0 |
| `56` | 4 | 17 (`0x11`) | neutral sentinel | 0 |
| `57` | 5 | 17 (`0x11`) | neutral sentinel | 0 |
| `58` | 2 | 3 | Poison | 0 |
| `59` | 2 | 4 | Ground | 0 |
| `60` | 2 | 13 | Psychic | 0 |
| `61` | 2 | 6 | Bug | 0 |
| `62` | 2 | 7 | Ghost | 0 |
| `63` | 2 | 15 | Dragon | 0 |
| `64` | 2 | 8 | Steel | 0 |
| `65` | 2 | 16 | Dark | 0 |
| `66` | 2 | 16 | Dark | 0 |
| `67` | 2 | 16 | Dark | 0 |
| `68–77` | 2 | 17 (`0x11`) | neutral sentinel | 0 |
| `78–127` | 1 | 17 (`0x11`) | neutral sentinel | 0 |

This explains why records `58–67` have ordinary type categories when they are
selected by the Type Expert constructor, while Rental/Mix generic records are
neutral in the NPC result routine even though their byte-7 constructor values
are `0x12` or the `0x11` Type Expert wildcard. It also explains why a generic
record does not acquire a category from the six Pokémon later associated with
it: the packed category is copied from the source row before the winner
routine runs.

The complete raw rows and these derived fields are reproducible with
`--dump-records`:

```sh
python3 scripts/inspect_wbt_table.py rom/extracted/a/2/6/1 --dump-records
```

For named Leader and Champion records, including the special Bianca row, see
[`champions-and-leaders.md`](champions-and-leaders.md). Together, that table
and the mapping above cover every source-table row's priority, category, and
built-in NPC trainer-type fields: 46 standard Leaders, Bianca, 7 standard
Champions, and 74 non-regional/generic rows (`0–127` in total).

## Retail PWT names and identity fields

The generic rows are not nameless at runtime. In the USA/Europe retail build,
the ordinary text NARC `/a/0/0/2` has a 128-entry PWT-name table (entry 409) and
a parallel 128-entry PWT-class table (entry 410). The WBT converter writes the
source row index to the packed record's `tr_id`, so the text entry at the same
index is the displayed PWT name. This positional mapping is cross-checked by
the known rows: indices 0–13 are the Unova Leaders, 8 is Bianca, 14–19 are
Blue through Alder, and 53 is Red.

The retail PWT class table contains the same generic `Trainer` label for all
128 entries. It therefore does not identify rows as Youngster, Ace Trainer,
and so on. The numeric `btl_tr_type` below is a separate battle-engine field;
it is not the packed NPC-result `npc_trainer_type` flag (which is 0 for the
built-in path). Cross-referencing the normal BW2 trainer-class table shows
that the generic rows use the generic `Trainer` class-domain values
`0`, `104–111`, `145`, `183`, and `228–230`; row 56 uses `115` (`Leader`) and
row 57 uses `186` (`Team Plasma`). Those normal class labels do not override
the PWT-specific class table's generic `Trainer` display text.

`mmdl_id` is the internal model/appearance resource identifier copied into the
runtime record. Equal IDs use the same model resource; resolving an ID to a
rendered sprite or a human-readable outfit name requires the separate model
resource table, which is not part of the 16-byte WBT table. `sex` is the row's
male/female selector (`0` male, `1` female).

The following table maps every non-regional/generic row. Names and class text
are the USA/Europe retail labels; the WBT bytes and identity fields are the
byte-identical table shared with the examined development build.

| Index | Retail PWT name | Sex | `mmdl_id` | `btl_tr_type` |
|---:|---|---:|---:|---:|
| 54 | Hilda | 1 | `0x0004` | 183 |
| 55 | Rival | 0 | `0x0123` | 145 |
| 56 | Cheren | 0 | `0x00DF` | 115 |
| 57 | Colress | 0 | `0x00FA` | 186 |
| 58 | Castor | 0 | `0x0049` | 104 |
| 59 | Homer | 0 | `0x0040` | 105 |
| 60 | Delphine | 1 | `0x00B8` | 107 |
| 61 | Walter | 0 | `0x0020` | 108 |
| 62 | Ferly | 0 | `0x00B7` | 106 |
| 63 | Drakon | 0 | `0x001E` | 110 |
| 64 | Margaret | 1 | `0x0021` | 109 |
| 65 | Vito | 0 | `0x0020` | 108 |
| 66 | Impera | 1 | `0x0021` | 109 |
| 67 | Bonnie | 1 | `0x001F` | 111 |
| 68 | X | 0 | `0x001E` | 110 |
| 69 | Makina | 1 | `0x001F` | 111 |
| 70 | Fidel | 0 | `0x0020` | 108 |
| 71 | Theodora | 1 | `0x0021` | 109 |
| 72 | Allan | 0 | `0x002E` | 228 |
| 73 | Jocelyn | 1 | `0x002F` | 229 |
| 74 | Dmitri | 0 | `0x0049` | 104 |
| 75 | Levina | 1 | `0x004A` | 230 |
| 76 | Rylan | 0 | `0x00B7` | 106 |
| 77 | Destiny | 1 | `0x00B8` | 107 |
| 78 | Ted | 0 | `0x000B` | 0 |
| 79 | Seamus | 0 | `0x000B` | 0 |
| 80 | Kendal | 1 | `0x000F` | 0 |
| 81 | Uno | 1 | `0x000F` | 0 |
| 82 | Nanaka | 1 | `0x0017` | 0 |
| 83 | Enid | 1 | `0x0017` | 0 |
| 84 | Masashi | 0 | `0x0018` | 0 |
| 85 | Dorian | 0 | `0x0018` | 0 |
| 86 | Yareli | 1 | `0x001A` | 0 |
| 87 | Makayla | 1 | `0x001B` | 0 |
| 88 | Tristan | 0 | `0x0022` | 0 |
| 89 | Yosef | 0 | `0x0022` | 0 |
| 90 | Karlie | 1 | `0x0023` | 0 |
| 91 | Naomi | 1 | `0x0023` | 0 |
| 92 | Hernando | 0 | `0x0024` | 0 |
| 93 | Indy | 0 | `0x0024` | 0 |
| 94 | Hannah | 1 | `0x0025` | 0 |
| 95 | Clarissa | 1 | `0x0025` | 0 |
| 96 | Lester | 0 | `0x002A` | 0 |
| 97 | Minoru | 0 | `0x002A` | 0 |
| 98 | Willa | 1 | `0x002B` | 0 |
| 99 | Hailey | 1 | `0x002B` | 0 |
| 100 | Kaden | 0 | `0x002E` | 0 |
| 101 | Roddy | 0 | `0x002E` | 0 |
| 102 | Chloe | 1 | `0x002F` | 0 |
| 103 | Tessa | 1 | `0x002F` | 0 |
| 104 | Berke | 0 | `0x0030` | 0 |
| 105 | Sunan | 0 | `0x0030` | 0 |
| 106 | Sudapon | 1 | `0x0031` | 0 |
| 107 | Anupa | 1 | `0x0031` | 0 |
| 108 | Jax | 0 | `0x0034` | 0 |
| 109 | Franco | 0 | `0x0034` | 0 |
| 110 | Hayden | 1 | `0x0035` | 0 |
| 111 | Maxie | 1 | `0x0035` | 0 |
| 112 | Bobhiko | 0 | `0x0048` | 0 |
| 113 | Bobmasa | 0 | `0x0048` | 0 |
| 114 | Nokko | 1 | `0x0128` | 0 |
| 115 | Liz | 1 | `0x0128` | 0 |
| 116 | Yen | 0 | `0x002C` | 0 |
| 117 | Cents | 0 | `0x002C` | 0 |
| 118 | Wanda | 1 | `0x002D` | 0 |
| 119 | Euro | 1 | `0x002D` | 0 |
| 120 | Celsius | 0 | `0x0032` | 0 |
| 121 | Ren | 0 | `0x0032` | 0 |
| 122 | Kelly | 1 | `0x0033` | 0 |
| 123 | Alison | 1 | `0x0033` | 0 |
| 124 | Butch | 0 | `0x003D` | 0 |
| 125 | Carver | 0 | `0x003D` | 0 |
| 126 | Gavin | 0 | `0x003E` | 0 |
| 127 | Larry | 0 | `0x003E` | 0 |

### Result categories for these identities

For clarity, the NPC winner routine's stored result category is mapped to the
identity-table rows as follows. This is raw source byte 0; it is not
`mmdl_id`, `btl_tr_type`, or the Type Expert raw byte-7 field.

| Indices | Result category | Meaning | Packed priority |
|---|---:|---|---:|
| 54–57 | 17 (`0x11`) | neutral sentinel | 4, 3, 4, 5 respectively |
| 58 | 3 | Poison | 2 |
| 59 | 4 | Ground | 2 |
| 60 | 13 | Psychic | 2 |
| 61 | 6 | Bug | 2 |
| 62 | 7 | Ghost | 2 |
| 63 | 15 | Dragon | 2 |
| 64 | 8 | Steel | 2 |
| 65–67 | 16 | Dark | 2 |
| 68–77 | 17 (`0x11`) | neutral sentinel | 2 |
| 78–127 | 17 (`0x11`) | neutral sentinel | 1 |

Thus the Rental/Mix generic pools (68–127) are neutral in the displayed NPC
result routine. The ordinary type categories occur in the Type Expert-oriented
rows 58–67. The `0x11` value in rows 54–57 and 68–127 is the NPC routine's
neutral sentinel; it must not be confused with the Type Expert wildcard in
raw byte 7.

This answers the identity question at the level supported by the recovered
data: we can name every row and identify its model resource and internal
battle-trainer-type value. We cannot yet attach a canonical portrait or a
human-readable trainer-class label to each `mmdl_id`/`btl_tr_type` without
decoding the separate model and battle-type definition resources.

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
