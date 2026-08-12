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

The ace trainer table (`wbt1a_tr.tdm` / `wbt2a_tr.tdm`) supplies an index into
the matching ace Pokémon archive (`wbt1a_pd.narc` / `wbt2a_pd.narc`);
`wbt3a_tr.tdm` and `wbt3a_pd.narc` provide the limited-data equivalent. The
first u16 in the selected PDM record is the species ID. For all 74 ace rows in
`wbt1`/`wbt2` and the 64 rows represented in `wbt3`, that species record is
nonzero. Therefore the fixed-first algorithm is verified across every
ace-marked trainer that has a party-table record in the examined build.

### Complete ace-marked trainer list

The following is the complete set of 74 rows whose `エースポケモン` field is
marked `○` in `wbt_trainer_list.txt`. These are the trainers that enter the
fixed-first (ace) path above. IDs and display codes are the source keys; the
names use the English/common names for recognizable characters. For the
generic rows, the Japanese source name is included in parentheses so the label
cannot be confused with a language-specific localization.

`Display code` is the exact `表示コード名` source key. `Code meaning`
translates the source `ポジション` field, so the display code's runtime role
is visible rather than just its symbolic name.

The ace values below are filtered to the built-in tournaments in which each
trainer is eligible. They are not three Pokémon used in one battle. The selected
cup's `btdata_id` chooses one archive before `makeRomTrainerData` loads the
ace record; the trainer then starts with the listed Pokémon if selected. A
randomized cup may not include every eligible trainer on every run, so the
tournament names describe eligibility, not guaranteed appearance. When several
tournaments use the same ace, they are grouped together.

Download is omitted from the per-trainer cells because its roster comes from a
user-supplied `.pwt` payload; the runtime permits any ROM trainer there, so it
does not define a fixed built-in trainer appearance.

The source tournament table maps cup IDs to the archive used at runtime:

| Cup ID | Tournament | Ace archive |
|---:|---|---|
| 1 | Champions | WBT3 |
| 2 | Type Expert | WBT3 |
| 3 | Download | WBT1 |
| 4 | Driftveil | WBT1 |
| 5 | Unova/Teselia Leaders | WBT2 |
| 6 | Kanto Leaders | WBT2 |
| 7 | Johto Leaders | WBT2 |
| 8 | Hoenn Leaders | WBT2 |
| 9 | Sinnoh Leaders | WBT2 |
| 10 | World Leaders | WBT3 |
| 11 | Driftveil event | WBT1 |
| 12 | Rental | WBT1 |
| 13 | Super Rental / Rental Master | WBT3 |
| 14 | Mix | WBT1 |
| 15 | Super Mix / Mix Master | WBT3 |

For Wallace (ID 017), the only built-in eligibility is the Champions cup.
That cup uses WBT3, so his fixed first Pokémon is **Milotic**.

| ID | Trainer | Display code | Code meaning | Actual tournament ace(s) |
|---:|---|---|---|---|
| 000 | Cheren | `SWLEADER1` | BW2 Gym Leader | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Stoutland |
| 001 | Roxie | `SWLEADER2` | BW2 Gym Leader | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Scolipede |
| 002 | Burgh | `SWLEADER3` | BW2 Gym Leader | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Leavanny |
| 003 | Elesa | `SWLEADER4` | BW2 Gym Leader | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Zebstrika |
| 004 | Clay | `SWLEADER5` | BW2 Gym Leader | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Excadrill |
| 005 | Skyla | `SWLEADER6` | BW2 Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Swanna |
| 006 | Drayden | `SWLEADER7` | BW2 Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Haxorus |
| 007 | Marlon | `SWLEADER8` | BW2 Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert — Jellicent |
| 008 | Bianca | `SWBELL` | BW character / support | Rental, Mix, Super Rental / Rental Master — Musharna |
| 009 | Chili | `LEADER1A` | BW Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Simisear |
| 010 | Cress | `LEADER1B` | BW Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Simipour |
| 011 | Cilan | `LEADER1C` | BW Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Simisage |
| 012 | Lenora | `LEADER2` | BW Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Rotom-Mow |
| 013 | Brycen | `LEADER7` | BW Gym Leader | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Cryogonal |
| 015 | Lance | `GSCHAMPION` | Gold/Silver Champion | Champions — Dragonite |
| 016 | Steven | `RSCHAMPION` | Ruby/Sapphire Champion | Champions — Metagross |
| 017 | Wallace | `ECHAMPION` | Emerald Champion | Champions — Milotic |
| 018 | Cynthia | `SHIRONA` | Diamond/Pearl Champion | Champions — Garchomp |
| 019 | Alder | `CHAMPION` | Black/White Champion | Champions — Volcarona |
| 020 | Brock | `RGLEADER1` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Onix |
| 021 | Misty | `RGLEADER2` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Starmie |
| 022 | Lt. Surge | `RGLEADER3` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Raichu |
| 023 | Erika | `RGLEADER4` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Vileplume |
| 024 | Sabrina | `RGLEADER5` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Alakazam |
| 025 | Blaine | `RGLEADER6` | Red/Green Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Arcanine |
| 026 | Giovanni | `RGLEADER7` | Red/Green Gym Leader / enemy character | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Rhyperior |
| 027 | Falkner | `GSLEADER1` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Pidgeot |
| 028 | Bugsy | `GSLEADER2` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Scizor |
| 029 | Whitney | `GSLEADER3` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Miltank |
| 030 | Morty | `GSLEADER4` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Gengar |
| 031 | Chuck | `GSLEADER5` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Poliwrath |
| 032 | Jasmine | `GSLEADER6` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Steelix |
| 033 | Pryce | `GSLEADER7` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Mamoswine |
| 034 | Clair | `GSLEADER8` | Gold/Silver Gym Leader | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Kingdra |
| 035 | Janine | `GSLEADER9` | Gold/Silver Gym Leader / Kanto Gym Leader | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Venomoth |
| 036 | Roxanne | `RSLEADER1` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Probopass |
| 037 | Brawly | `RSLEADER2` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Hariyama |
| 038 | Wattson | `RSLEADER3` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Manectric |
| 039 | Flannery | `RSLEADER4` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Torkoal |
| 040 | Norman | `RSLEADER5` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Slaking |
| 041 | Winona | `RSLEADER6` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Altaria |
| 042 | Tate | `RSLEADER7` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Solrock |
| 043 | Liza | `RSLEADER8` | Ruby/Sapphire Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Lunatone |
| 044 | Juan | `ELEADER1` | Emerald Gym Leader | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Kingdra |
| 045 | Roark | `DPLEADER1` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Rampardos |
| 046 | Gardenia | `DPLEADER2` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Roserade |
| 047 | Fantina | `DPLEADER3` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Mismagius |
| 048 | Maylene | `DPLEADER4` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Lucario |
| 049 | Crasher Wake | `DPLEADER5` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Floatzel |
| 050 | Byron | `DPLEADER6` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Bastiodon |
| 051 | Candice | `DPLEADER7` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Froslass |
| 052 | Volkner | `DPLEADER8` | Diamond/Pearl Gym Leader | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert — Electivire |
| 056 | Cheren (event) | `SWLEADER1` | Event Gym Leader 1 | Driftveil event — Stoutland |
| 057 | Colress | `SWBOSS` | Event Boss | Driftveil event — Magneton |
| 058 | Botsuri (ボツリ) | `ASSISTANTM` | Scientist (male), battleable generic | Type Expert — Muk |
| 059 | Ieji (イエジ) | `MOUNTMAN` | Hiker, battleable generic | Type Expert — Krookodile |
| 060 | Karuto (カルト) | `ESPW` | Psychic (female), battleable generic | Type Expert — Starmie |
| 061 | Walter (ウォルター) | `VETERANM` | Veteran Trainer (male), battleable generic | Type Expert — Heracross |
| 062 | Rensuke (レンスケ) | `ESPM` | Psychic (male), battleable generic | Type Expert — Cofagrigus |
| 063 | Ryuichi (リュウイチ) | `TRAINERM` | Elite Trainer (male), battleable generic | Type Expert — Salamence |
| 064 | Thatcher (サッチャー) | `VETERANW` | Veteran Trainer (female), battleable generic | Type Expert — Aggron |
| 065 | Vito (ヴィトー) | `VETERANM` | Veteran Trainer (male), battleable generic | Type Expert — Shiftry |
| 066 | Ilsane (イルサーネ) | `VETERANW` | Veteran Trainer (female), battleable generic | Type Expert — Umbreon |
| 067 | Bonnie (ボニー) | `TRAINERW` | Elite Trainer (female), battleable generic | Type Expert — Drapion |
| 068 | Ex (エクス) | `TRAINERM` | Elite Trainer (male), clear-before generic | Driftveil, Rental, Mix — Archeops |
| 069 | Makina (マキナ) | `TRAINERW` | Elite Trainer (female), clear-before generic | Driftveil, Rental, Mix — Tirtouga |
| 070 | Castro (カストロ) | `VETERANM` | Veteran Trainer (male), clear-before generic | Driftveil, Rental, Mix — Whimsicott |
| 071 | Tsugumi (ツグミ) | `VETERANW` | Veteran Trainer (female), clear-before generic | Driftveil, Rental, Mix — Lilligant |
| 072 | Arashiyama (アラシヤマ) | `FIGHTERM` | Black Belt, clear-before generic | Driftveil, Rental, Mix — Throh |
| 073 | Jane (ジェーン) | `FIGHTERW` | Battle Girl, clear-before generic | Driftveil, Rental, Mix — Sawk |
| 074 | Shuichi (シュウイチ) | `ASSISTANTM` | Scientist (male), clear-before generic | Driftveil, Rental, Mix — Golduck |
| 075 | Eclaire (エクレア) | `ASSISTANTW` | Scientist (female), clear-before generic | Driftveil, Rental, Mix — Lopunny |
| 076 | Rurio (ルリオ) | `ESPM` | Psychic (male), clear-before generic | Driftveil, Rental, Mix — Cofagrigus |
| 077 | Soprano (ソプラノ) | `ESPW` | Psychic (female), clear-before generic | Driftveil, Rental, Mix — Mr-Mime |

The unmarked rows do not enter the ace branch at all: their complete party is
selected from the normal candidate list by the no-replacement chooser. In the
Champion data set, the visible unmarked examples are Green (ID 14), Red (ID
53), Touko (ID 54), and the Rival (ID 55). They do not have a fixed first
Pokémon in this code path.
