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
| Constructor priority | `8 & 7` | The selector at `0x02241630` compares these low three bits with `WBT_TRPRI` requests 1–5. |

The relevant disassembly is the predicate at `0x02241874`, the priority
counter at `0x02241630`, and the selector at `0x02241704`. These are internal
source-table fields. The priority is stored differently from downloadable
`.pwt` `YY`, but the recovered source proves that both become the same runtime
`WBTTRAINER.pri` field and have the same numeric and behavioral meaning.

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

## Named special record: Bianca

Bianca is a named candidate in the Rental and Mix data rather than a standard
Leader-tournament entry. Her family byte is `0x00`, so the regional constructor
does not admit her to the Unova Leaders pool. Her separate eligibility flags
admit her to Rental, Mix, and Rental Master; she is not eligible for Mix Master.

| Trainer | Display code | Code meaning | WBT index | Priority | Category | Eligible tournaments |
|---|---|---|---:|---:|---:|---|
| Bianca | `SWBELL` | Black/White character / support | 8 | 3 | 17 (neutral sentinel) | Rental, Mix, Rental Master |

Her priority and category are stored in the source record and are not derived
from the random Pokémon assigned to her in Rental or from her party in Mix.

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
to the NPC winner calculation. The summary table below focuses on the
reader-facing identity and result fields; the low-level identity values remain
reproducible with the decoder and are described above. It is not a claim that
each row is selected in every cup.

This explains why records `58–67` have ordinary type categories when they are
selected by the Type Expert constructor, while Rental/Mix generic records are
neutral in the NPC result routine even though their byte-7 constructor values
are `0x12` or the `0x11` Type Expert wildcard. It also explains why a generic
record does not acquire a category from the six Pokémon later associated with
it: the packed category is copied from the source row before the winner
routine runs. The full per-record result-field table appears below.

The complete raw rows and these derived fields are reproducible with
`--dump-records`:

```sh
python3 scripts/inspect_wbt_table.py rom/extracted/a/2/6/1 --dump-records
```

For named Leader and Champion records, see
[`champions-and-leaders.md`](champions-and-leaders.md). Together, that table,
the Bianca row above, and the mapping below cover every source-table row's
priority and category: 46 standard Leaders, Bianca, 7 standard Champions, and
74 non-regional/generic rows (`0–127` in total).

## Retail PWT names and result fields

The generic rows are not nameless at runtime. In the USA/Europe retail build,
the ordinary text NARC `/a/0/0/2` has a 128-entry PWT-name table (entry 409) and
a parallel 128-entry PWT-class table (entry 410). The WBT converter writes the
source row index to the packed record's `tr_id`, so the text entry at the same
index is the displayed PWT name. This positional mapping is cross-checked by
the known rows: indices 0–13 are the Unova Leaders, 8 is Bianca, 14–19 are
Blue through Alder, and 53 is Red.

The retail PWT class table contains the same generic `Trainer` label for all
128 entries. It therefore does not identify rows as Youngster, Ace Trainer,
and so on. The numeric `btl_tr_type` in the raw data is a separate battle-engine field;
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
are the USA/Europe retail labels; the underlying WBT bytes and identity fields
are the byte-identical table shared with the examined development build. The
three low-level columns (`mmdl_id`, `btl_tr_type`, and the packed NPC
trainer-type flag) are intentionally omitted here because they do not affect
candidate selection or the displayed NPC result.

`Display code` is the exact `表示コード名` source key. It is an identifier,
not a strength or result-setting field. `Code meaning` is an English
reader-facing description of the source role, normally based on the separate
`ポジション` field rather than a literal expansion of the code. Hilda's
`HEROINE` code is therefore described as “Female
protagonist / heroine”; the underlying source row is separately marked as
unused and is not selected by the built-in cup predicates.

The `Cheren` row at index `56` is a separate special/event record from the
standard Unova Leader Cheren at index `0`. Their priorities and categories are
therefore different; the side-by-side explanation is in
[`champions-and-leaders.md`](champions-and-leaders.md#two-distinct-wbt-records-named-cheren).

| Index | Retail PWT name | Display code | Code meaning | Sex | Packed priority | Result category | Category meaning |
|---:|---|---|---|---:|---:|---:|---|
| 54 | Hilda | `HEROINE` | Female protagonist / heroine | 1 | 4 | 17 (`0x11`) | neutral sentinel |
| 55 | Rival | `SWRIVAL` | Event Rival | 0 | 3 | 17 (`0x11`) | neutral sentinel |
| 56 | Cheren | `SWLEADER1` | Event Gym Leader 1 | 0 | 4 | 17 (`0x11`) | neutral sentinel |
| 57 | Colress | `SWBOSS` | Event Boss | 0 | 5 | 17 (`0x11`) | neutral sentinel |
| 58 | Castor | `ASSISTANTM` | Scientist (male) | 0 | 2 | 3 | Poison |
| 59 | Homer | `MOUNTMAN` | Hiker | 0 | 2 | 4 | Ground |
| 60 | Delphine | `ESPW` | Psychic (female) | 1 | 2 | 13 | Psychic |
| 61 | Walter | `VETERANM` | Veteran Trainer (male) | 0 | 2 | 6 | Bug |
| 62 | Ferly | `ESPM` | Psychic (male) | 0 | 2 | 7 | Ghost |
| 63 | Drakon | `TRAINERM` | Elite Trainer (male) | 0 | 2 | 15 | Dragon |
| 64 | Margaret | `VETERANW` | Veteran Trainer (female) | 1 | 2 | 8 | Steel |
| 65 | Vito | `VETERANM` | Veteran Trainer (male) | 0 | 2 | 16 | Dark |
| 66 | Impera | `VETERANW` | Veteran Trainer (female) | 1 | 2 | 16 | Dark |
| 67 | Bonnie | `TRAINERW` | Elite Trainer (female) | 1 | 2 | 16 | Dark |
| 68 | X | `TRAINERM` | Elite Trainer (male) | 0 | 2 | 17 (`0x11`) | neutral sentinel |
| 69 | Makina | `TRAINERW` | Elite Trainer (female) | 1 | 2 | 17 (`0x11`) | neutral sentinel |
| 70 | Fidel | `VETERANM` | Veteran Trainer (male) | 0 | 2 | 17 (`0x11`) | neutral sentinel |
| 71 | Theodora | `VETERANW` | Veteran Trainer (female) | 1 | 2 | 17 (`0x11`) | neutral sentinel |
| 72 | Allan | `FIGHTERM` | Black Belt | 0 | 2 | 17 (`0x11`) | neutral sentinel |
| 73 | Jocelyn | `FIGHTERW` | Battle Girl | 1 | 2 | 17 (`0x11`) | neutral sentinel |
| 74 | Dmitri | `ASSISTANTM` | Scientist (male) | 0 | 2 | 17 (`0x11`) | neutral sentinel |
| 75 | Levina | `ASSISTANTW` | Scientist (female) | 1 | 2 | 17 (`0x11`) | neutral sentinel |
| 76 | Rylan | `ESPM` | Psychic (male) | 0 | 2 | 17 (`0x11`) | neutral sentinel |
| 77 | Destiny | `ESPW` | Psychic (female) | 1 | 2 | 17 (`0x11`) | neutral sentinel |
| 78 | Ted | `BOY2` | Youngster | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 79 | Seamus | `BOY2` | Youngster | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 80 | Kendal | `GIRL2` | Lass | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 81 | Uno | `GIRL2` | Lass | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 82 | Nanaka | `WOMAN3` | Nursery Aide | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 83 | Enid | `WOMAN3` | Nursery Aide | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 84 | Masashi | `MIDDLEMAN1` | Pokémon Fan (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 85 | Dorian | `MIDDLEMAN1` | Pokémon Fan (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 86 | Yareli | `MIDDLEWOMAN1` | Pokémon Fan (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 87 | Makayla | `MIDDLEWOMAN2` | Pokémon Fan (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 88 | Tristan | `BREEDERM` | Pokémon Breeder (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 89 | Yosef | `BREEDERM` | Pokémon Breeder (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 90 | Karlie | `BREEDERW` | Pokémon Breeder (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 91 | Naomi | `BREEDERW` | Pokémon Breeder (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 92 | Hernando | `RANGERM` | Pokémon Ranger (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 93 | Indy | `RANGERM` | Pokémon Ranger (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 94 | Hannah | `RANGERW` | Pokémon Ranger (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 95 | Clarissa | `RANGERW` | Pokémon Ranger (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 96 | Lester | `WAITER` | Waiter | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 97 | Minoru | `WAITER` | Waiter | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 98 | Willa | `WAITRESS` | Waitress | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 99 | Hailey | `WAITRESS` | Waitress | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 100 | Kaden | `FIGHTERM` | Black Belt | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 101 | Roddy | `FIGHTERM` | Black Belt | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 102 | Chloe | `FIGHTERW` | Battle Girl | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 103 | Tessa | `FIGHTERW` | Battle Girl | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 104 | Berke | `BACKPACKERM` | Backpacker (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 105 | Sunan | `BACKPACKERM` | Backpacker (male) | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 106 | Sudapon | `BACKPACKERW` | Backpacker (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 107 | Anupa | `BACKPACKERW` | Backpacker (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 108 | Jax | `BUSINESSMAN` | Businessman | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 109 | Franco | `BUSINESSMAN` | Businessman | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 110 | Hayden | `OL` | Office Lady | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 111 | Maxie | `OL` | Office Lady | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 112 | Bobhiko | `POLICEMAN` | Police Officer | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 113 | Bobmasa | `POLICEMAN` | Police Officer | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 114 | Nokko | `MUSICIANW` | Guitarist (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 115 | Liz | `MUSICIANW` | Guitarist (female) | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 116 | Yen | `GENTLEMAN` | Gentleman | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 117 | Cents | `GENTLEMAN` | Gentleman | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 118 | Wanda | `LADY` | Lady | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 119 | Euro | `LADY` | Lady | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 120 | Celsius | `DOCTOR` | Doctor | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 121 | Ren | `DOCTOR` | Doctor | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 122 | Kelly | `NURSE` | Nurse | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 123 | Alison | `NURSE` | Nurse | 1 | 1 | 17 (`0x11`) | neutral sentinel |
| 124 | Butch | `BADMAN` | Skinhead | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 125 | Carver | `BADMAN` | Skinhead | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 126 | Gavin | `BADRIDER` | Biker | 0 | 1 | 17 (`0x11`) | neutral sentinel |
| 127 | Larry | `BADRIDER` | Biker | 0 | 1 | 17 (`0x11`) | neutral sentinel |

Result category is raw source byte 0. Rental/Mix generic rows (68–127) use the
neutral category, while Type Expert rows (58–67) have type-specific categories.
The value `0x11` is the NPC result routine's neutral sentinel; it is separate
from the Type Expert wildcard in raw byte 7.

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

### Rental opponent IV assignments

The dedicated Rental party builder does not roll each opponent Pokémon's IVs
independently. It reads the selected opponent Trainer's fixed `PowerRnd` and
copies that one value to all six IVs of every rental Pokémon created for that
Trainer. Actual Rental opponents therefore have IV `8` or `20`. The
priority-1 bracket fillers store `PowerRnd = 0`, but never reach the player
and do not have an opponent party constructed in normal play.

The `20` shown for the named Rental and Rental Master opponents is not a
special value assigned only by those tournaments. Every one of the 46 standard
Gym Leader source rows already stores `PowerRnd = 20`, and the normal WBT party
builder uses the same value for their regional Leader and World Leaders teams.
Bianca's separate named record also stores `20`. The complete Leader mapping
and the normal-party scope are documented in
[`champions-and-leaders.md`](champions-and-leaders.md#standard-gym-leader-records).

| Tournament | Stored IV value | Trainer records and English names |
|---|---:|---|
| Rental | `20` | `0–4, 8`: Cheren, Roxie, Burgh, Elesa, Clay, and Bianca |
| Rental | `8` | `68–77`: X, Makina, Fidel, Theodora, Allan, Jocelyn, Dmitri, Levina, Rylan, and Destiny |
| Rental | `0` | `78–127`: Ted, Seamus, Kendal, Uno, Nanaka, Enid, Masashi, Dorian, Yareli, Makayla, Tristan, Yosef, Karlie, Naomi, Hernando, Indy, Hannah, Clarissa, Lester, Minoru, Willa, Hailey, Kaden, Roddy, Chloe, Tessa, Berke, Sunan, Sudapon, Anupa, Jax, Franco, Hayden, Maxie, Bobhiko, Bobmasa, Nokko, Liz, Yen, Cents, Wanda, Euro, Celsius, Ren, Kelly, Alison, Butch, Carver, Gavin, and Larry |
| Rental Master | `20` | `0–13, 20–52`: Cheren, Roxie, Burgh, Elesa, Clay, Skyla, Drayden, Marlon, Bianca, Chili, Cress, Cilan, Lenora, Brycen, Brock, Misty, Lt. Surge, Erika, Sabrina, Blaine, Giovanni, Falkner, Bugsy, Whitney, Morty, Chuck, Jasmine, Pryce, Clair, Janine, Roxanne, Brawly, Wattson, Flannery, Norman, Winona, Tate, Liza, Juan, Roark, Gardenia, Fantina, Maylene, Crasher Wake, Byron, Candice, and Volkner |

The ten priority-2 Rental/Mix generic records have the following roles. These
are source roles and displayed names; they do not restrict the randomly
assigned Rental Pokémon to a matching elemental type.

| ID | Trainer | Source role | Rental priority | IVs in every stat |
|---:|---|---|---:|---:|
| 68 | X | Elite Trainer (male) | 2 | 8 |
| 69 | Makina | Elite Trainer (female) | 2 | 8 |
| 70 | Fidel | Veteran Trainer (male) | 2 | 8 |
| 71 | Theodora | Veteran Trainer (female) | 2 | 8 |
| 72 | Allan | Black Belt | 2 | 8 |
| 73 | Jocelyn | Battle Girl | 2 | 8 |
| 74 | Dmitri | Scientist (male) | 2 | 8 |
| 75 | Levina | Scientist (female) | 2 | 8 |
| 76 | Rylan | Psychic (male) | 2 | 8 |
| 77 | Destiny | Psychic (female) | 2 | 8 |

The 50 records at IDs `78–127` are the priority-1 Rental/Mix generic group;
each stores `PowerRnd = 0`. If their party builder were invoked, that value
would produce IV `0` in all six stats, but the normal bracket path never does
so. Their individual English names and roles are in
the complete [Retail PWT names and result fields](#retail-pwt-names-and-result-fields)
table above.

The source also identifies IDs `78–127` as non-battling mob Trainers. They are
real named bracket participants, not unused Trainer records, but occupy the
NPC-only filler path and are eliminated through simulated bracket results
before becoming the player's opponent. The final nine, IDs `119–127` (Euro,
Celsius, Ren, Kelly, Alison, Butch, Carver, Gavin, and Larry), consequently
have no normal `wbt1`, `wbt2`, or `wbt3` party-table rows. Their missing party
data is intentional because the normal game flow never constructs a battle
party for them.

Thus, within these two ordinary Rental generic groups, priority 2 coincides
with stored IV 8 and priority 1 coincides with stored IV 0. The fields remain
independent: the game does not calculate IVs from priority; both values are
stored in the same Trainer source record and used by different runtime
routines.

These Trainer groups do not have group-specific EV values. EV allocation comes
from the randomly selected Rental Pokémon record's EV mask, so the same source
Pokémon build receives the same EV distribution whether its opponent is a
priority-1 generic Trainer, a priority-2 generic Trainer, or a named Leader.
Only the Trainer-supplied IV value changes between those cases.

The player's initial six rental Pokémon are separate: the player setup path
always passes `20`, regardless of which source records are selected. The
record-level Pokémon table therefore describes opponent IVs as Trainer-fixed
and links back to this mapping; `0`, `8`, and `20` are not three outcomes of a
per-Pokémon random roll.

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
