# WBT party construction and roster selection

This document covers the trainer's battle party, which is a different layer
from the eight-trainer NPC field and bracket construction described in
[`in-game-constructor-categories.md`](in-game-constructor-categories.md).

## What the examined code proves

The development Overlay 55 disassembly contains the random selector from
`wbt_party.c`. One caller passes a literal `6` and consumes six returned
entries, but the recovered source identifies that caller as
`WBTSYS_SetupMyRentalParty`: it generates the player's six Pokémon offered at
the start of a Rental tournament. It is not a universal six-Pokémon roster
builder for every opponent.

The source-level rule table is explicit. `wbt.h` assigns rule IDs 0, 1, 2,
and 3 to single, double, triple, and rotation battles respectively;
`wbt_tool.c` stores `need_pokemon_num` as `3, 4, 6, 4` for those four IDs, and
`WBTTOOL_GetPartyMaxByRule` returns that field. Normal ROM opponents are built
with that returned count; they do not first receive six Pokémon and then have
some hidden. The same table is present in Overlay 55: the getter at
`0x022387FC` indexes the byte table at
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
4. Mark the selected source index unavailable, copy it to the output, and add
   its species and held item to the exclusion state.
5. Refresh candidate availability from that exclusion state and repeat for
   the requested number of entries.

That is random selection without replacement. A selected Pokémon cannot be
selected again by a later iteration of the same request. It also normally
prevents duplicate species and nonzero held items. The species check is
disabled for non-Rental cups using the unrestricted `WBTREG_ALL` regulation;
the source-index and held-item exclusions still apply. The chooser is used
both by normal ROM-party construction and by Rental-party construction.

The field at `work + 0x13e4` belongs specifically to the Rental builder. The
source names it `rental_type`, with branches for weak, strong, and all. In the
`all` branch, the builder requests three Pokémon from the strong range and,
when more are needed, `count - 3` from the weak range. This split is unrelated
to Triple battles. The range-bound table is referenced through the literal
pointers at `0x02239850` and `0x0223985c`.

## Disassembly evidence

| Evidence | Address | Interpretation |
|---|---:|---|
| Six-entry Rental request | `0x0223975A–0x0223976E` | `WBTSYS_SetupMyRentalParty` stores `6` as the player's initial Rental-party count and calls the builder at `0x02239560`. |
| Six-entry Rental output loop | `0x022397AA–0x022397E8` | Builds those Rental entries while `r5 < 6`. |
| Party-size getter | `0x022387FC–0x02238808` | Validates the rule, indexes the size table, and returns one byte. |
| Party-size table | `0x02239B36–0x02239B4E` | Encodes `3, 4, 6, 4` for single, double, triple, and rotation. |
| Rental-type field | `0x022395BA–0x022395CA` | Reads `work + 0x13E4` and dispatches weak, strong, and all Rental-pool modes. |
| Strong-plus-weak Rental split | `0x0223964C–0x02239694` | In the `all` Rental mode, requests `3` strong entries, then `count - 3` weak entries when `count > 3`. |
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

The six-entry random builder is not the code that fixes a lead. For a
non-Rental opponent using its ROM party, the source path in `wbt_battle.c` is
explicit:

1. `wbt_system_lobby.c` sets `has_ace` when the trainer-list row's
   `ace_poke_id` is nonzero.
2. In `makeRomTrainerData`, an ace trainer loads the first entry of the ace
   trainer table (`use_poke_table[0]`) and writes that Pokémon to output
   position `0`.
3. The normal trainer table is then passed to the random chooser for the
   remaining `poke_num - 1` entries. The ace's source index, species, and held
   item are added to the same exclusion state described above, subject to the
   regulation's species-check rule, so the ace record itself cannot be
   selected a second time.

This proves that a trainer marked with an ace has a fixed first Pokémon when
the tournament constructs that trainer's normal ROM party. The remaining
active positions are filled by the no-replacement selector. The rule table
above determines how many of those positions are active (3, 4, 6, or 4), not
which position is first.

### Rental and Mix exceptions

Rental and Super Rental / Rental Master do not use the named participant's
normal ROM party. They assign random rental Pokémon to both the player and
the opponents, using the Rental mode's candidate data and random
without-replacement builder. The participant record still determines which
Trainer appears in the field and bracket, but its ace metadata does not force
a Pokémon into that rental party.

The random Rental party also does not rewrite the participant record's stored
priority or matchup category. Those fields still govern simulated NPC-versus-
NPC bracket results, independently of the Pokémon randomly assigned for the
playable battle.

Consequently, an eligible Trainer such as Volkner can appear in Rental Master
without Electivire. If Electivire is assigned there, it comes from the Rental
selection itself, not from Volkner's normal ace metadata. The fixed first-
Pokémon statements and the `Ace Pokémon` column below therefore exclude Rental
and Rental Master appearances.

Mix and Super Mix / Mix Master begin by constructing the opponent's normal
ROM party, so the ace is initially placed in position `0`. Before the battle,
however, `WBTSYS_SetupMixParty` exchanges selected Pokémon between the two
parties (two exchanges in Triple battles). If the opponent's ace is selected
for exchange, that Trainer enters the battle without it. The ace is therefore
not unconditionally used in Mix modes either.

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
ace-marked trainer that has a party-table record in the examined build when
the normal ROM-party path is used. Rental modes use the separate random path,
and Mix modes can subsequently exchange the ace out of the constructed party.

### Complete ace-marked trainer list

The following is the complete set of 74 rows whose `エースポケモン` field is
marked `○` in `wbt_trainer_list.txt`. These are the trainers that enter the
fixed-first (ace) path when their normal ROM party is constructed. IDs and
display codes are the source keys; the Trainer column uses the English/USA-
Europe retail PWT names. `Display code` and ID remain the source keys, while
`Code meaning` gives the source trainer role in English.

`Display code` is the exact `表示コード名` source key. It is an identifier,
not a strength or party-selection rule. `Code meaning` is a reader-facing
English interpretation of the source role, normally translated from the
separate `ポジション` field; it should not be read as a literal expansion of
every display code.

The table separates each trainer's built-in ace from the built-in
tournaments whose trainer pool can include that row. `Ace Pokémon (normal
party build)` is the species loaded into position 0 when the trainer's normal
ROM party is constructed. `Eligible tournaments` lists every pool in which
that Trainer can appear. Rental eligibility does not mean the ace is used;
Mix eligibility means the ace is initially constructed but can be exchanged
away before the battle. Randomized cups may not include every eligible Trainer
on every run.

Download is omitted from the per-trainer cells because its roster comes from a
user-supplied `.pwt` payload; the runtime permits any ROM trainer there, so it
does not define a fixed built-in trainer appearance.

The source tournament table and the special-mode branches determine the
opponent's party source. Most built-in cups use one of the three normal WBT
archive families. Download reads its supplied payload, while Rental and Rental
Master bypass normal ace/party construction and use the dedicated Rental
Pokémon archive with different candidate ranges:

| Cup ID | Tournament | Opponent party source |
|---:|---|---|
| 1 | Champions | WBT3 |
| 2 | Type Expert | WBT3 |
| 3 | Download | Download payload; ROM-trainer references use WBT1 |
| 4 | Driftveil | WBT1 |
| 5 | Unova/Teselia Leaders | WBT2 |
| 6 | Kanto Leaders | WBT2 |
| 7 | Johto Leaders | WBT2 |
| 8 | Hoenn Leaders | WBT2 |
| 9 | Sinnoh Leaders | WBT2 |
| 10 | World Leaders | WBT3 |
| 11 | Driftveil event | WBT1 |
| 12 | Rental | Dedicated Rental archive, standard Rental ranges |
| 13 | Super Rental / Rental Master | Dedicated Rental archive, Rental Master ranges |
| 14 | Mix | WBT1 |
| 15 | Super Mix / Mix Master | WBT3 |

| ID | Trainer | Display code | Code meaning | Ace Pokémon (normal party build) | Eligible tournaments |
|---:|---|---|---|---|---|
| 000 | Cheren | `SWLEADER1` | BW2 Gym Leader | Stoutland | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 001 | Roxie | `SWLEADER2` | BW2 Gym Leader | Scolipede | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 002 | Burgh | `SWLEADER3` | BW2 Gym Leader | Leavanny | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 003 | Elesa | `SWLEADER4` | BW2 Gym Leader | Zebstrika | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 004 | Clay | `SWLEADER5` | BW2 Gym Leader | Excadrill | Driftveil, Rental, Mix, Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 005 | Skyla | `SWLEADER6` | BW2 Gym Leader | Swanna | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 006 | Drayden | `SWLEADER7` | BW2 Gym Leader | Haxorus | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 007 | Marlon | `SWLEADER8` | BW2 Gym Leader | Jellicent | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Super Mix / Mix Master, Type Expert |
| 008 | Bianca | `SWBELL` | BW character / support | Musharna | Rental, Mix, Super Rental / Rental Master |
| 009 | Chili | `LEADER1A` | BW Gym Leader | Simisear | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 010 | Cress | `LEADER1B` | BW Gym Leader | Simipour | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 011 | Cilan | `LEADER1C` | BW Gym Leader | Simisage | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 012 | Lenora | `LEADER2` | BW Gym Leader | Watchog | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 013 | Brycen | `LEADER7` | BW Gym Leader | Cryogonal | Unova/Teselia Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 015 | Lance | `GSCHAMPION` | Gold/Silver Champion | Dragonite | Champions |
| 016 | Steven | `RSCHAMPION` | Ruby/Sapphire Champion | Metagross | Champions |
| 017 | Wallace | `ECHAMPION` | Emerald Champion | Milotic | Champions |
| 018 | Cynthia | `SHIRONA` | Diamond/Pearl Champion (Japanese name: Shirona) | Garchomp | Champions |
| 019 | Alder | `CHAMPION` | Black/White Champion | Volcarona | Champions |
| 020 | Brock | `RGLEADER1` | Red/Green Gym Leader | Onix | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 021 | Misty | `RGLEADER2` | Red/Green Gym Leader | Starmie | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 022 | Lt. Surge | `RGLEADER3` | Red/Green Gym Leader | Raichu | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 023 | Erika | `RGLEADER4` | Red/Green Gym Leader | Vileplume | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 024 | Sabrina | `RGLEADER5` | Red/Green Gym Leader | Alakazam | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 025 | Blaine | `RGLEADER6` | Red/Green Gym Leader | Arcanine | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 026 | Giovanni | `RGLEADER7` | Red/Green Gym Leader | Rhyperior | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 027 | Falkner | `GSLEADER1` | Gold/Silver Gym Leader | Pidgeot | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 028 | Bugsy | `GSLEADER2` | Gold/Silver Gym Leader | Scizor | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 029 | Whitney | `GSLEADER3` | Gold/Silver Gym Leader | Miltank | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 030 | Morty | `GSLEADER4` | Gold/Silver Gym Leader | Gengar | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 031 | Chuck | `GSLEADER5` | Gold/Silver Gym Leader | Poliwrath | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 032 | Jasmine | `GSLEADER6` | Gold/Silver Gym Leader | Steelix | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 033 | Pryce | `GSLEADER7` | Gold/Silver Gym Leader | Mamoswine | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 034 | Clair | `GSLEADER8` | Gold/Silver Gym Leader | Kingdra | Johto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 035 | Janine | `GSLEADER9` | Gold/Silver Gym Leader / Kanto Gym Leader | Venomoth | Kanto Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 036 | Roxanne | `RSLEADER1` | Ruby/Sapphire Gym Leader | Probopass | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 037 | Brawly | `RSLEADER2` | Ruby/Sapphire Gym Leader | Hariyama | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 038 | Wattson | `RSLEADER3` | Ruby/Sapphire Gym Leader | Manectric | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 039 | Flannery | `RSLEADER4` | Ruby/Sapphire Gym Leader | Torkoal | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 040 | Norman | `RSLEADER5` | Ruby/Sapphire Gym Leader | Slaking | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 041 | Winona | `RSLEADER6` | Ruby/Sapphire Gym Leader | Altaria | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 042 | Tate | `RSLEADER7` | Ruby/Sapphire Gym Leader | Solrock | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 043 | Liza | `RSLEADER8` | Ruby/Sapphire Gym Leader | Lunatone | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 044 | Juan | `ELEADER1` | Emerald Gym Leader | Kingdra | Hoenn Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 045 | Roark | `DPLEADER1` | Diamond/Pearl Gym Leader | Rampardos | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 046 | Gardenia | `DPLEADER2` | Diamond/Pearl Gym Leader | Roserade | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 047 | Fantina | `DPLEADER3` | Diamond/Pearl Gym Leader | Mismagius | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 048 | Maylene | `DPLEADER4` | Diamond/Pearl Gym Leader | Lucario | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 049 | Crasher Wake | `DPLEADER5` | Diamond/Pearl Gym Leader | Floatzel | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 050 | Byron | `DPLEADER6` | Diamond/Pearl Gym Leader | Bastiodon | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 051 | Candice | `DPLEADER7` | Diamond/Pearl Gym Leader | Froslass | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 052 | Volkner | `DPLEADER8` | Diamond/Pearl Gym Leader | Electivire | Sinnoh Leaders, World Leaders, Super Rental / Rental Master, Type Expert |
| 056 | Cheren (event) | `SWLEADER1` | Event Gym Leader 1 | Stoutland | Driftveil event |
| 057 | Colress | `SWBOSS` | Event Boss | Magneton | Driftveil event |
| 058 | Castor | `ASSISTANTM` | Scientist (male) | Muk | Type Expert |
| 059 | Homer | `MOUNTMAN` | Hiker | Krookodile | Type Expert |
| 060 | Delphine | `ESPW` | Psychic (female) | Starmie | Type Expert |
| 061 | Walter | `VETERANM` | Veteran Trainer (male) | Heracross | Type Expert |
| 062 | Ferly | `ESPM` | Psychic (male) | Cofagrigus | Type Expert |
| 063 | Drakon | `TRAINERM` | Elite Trainer (male) | Salamence | Type Expert |
| 064 | Margaret | `VETERANW` | Veteran Trainer (female) | Aggron | Type Expert |
| 065 | Vito | `VETERANM` | Veteran Trainer (male) | Shiftry | Type Expert |
| 066 | Impera | `VETERANW` | Veteran Trainer (female) | Umbreon | Type Expert |
| 067 | Bonnie | `TRAINERW` | Elite Trainer (female) | Drapion | Type Expert |
| 068 | X | `TRAINERM` | Elite Trainer (male) | Archeops | Driftveil, Rental, Mix |
| 069 | Makina | `TRAINERW` | Elite Trainer (female) | Tirtouga | Driftveil, Rental, Mix |
| 070 | Fidel | `VETERANM` | Veteran Trainer (male) | Whimsicott | Driftveil, Rental, Mix |
| 071 | Theodora | `VETERANW` | Veteran Trainer (female) | Lilligant | Driftveil, Rental, Mix |
| 072 | Allan | `FIGHTERM` | Black Belt | Throh | Driftveil, Rental, Mix |
| 073 | Jocelyn | `FIGHTERW` | Battle Girl | Sawk | Driftveil, Rental, Mix |
| 074 | Dmitri | `ASSISTANTM` | Scientist (male) | Golduck | Driftveil, Rental, Mix |
| 075 | Levina | `ASSISTANTW` | Scientist (female) | Lopunny | Driftveil, Rental, Mix |
| 076 | Rylan | `ESPM` | Psychic (male) | Cofagrigus | Driftveil, Rental, Mix |
| 077 | Destiny | `ESPW` | Psychic (female) | Mr. Mime | Driftveil, Rental, Mix |

The unmarked rows do not enter the ace branch at all: their complete party is
selected from the normal candidate list by the no-replacement chooser. The
four unmarked records represented in WBT3 are Blue (ID 14), Red (ID 53), Hilda
(ID 54), and the Rival (ID 55). Only Blue and Red are eligible for the built-in
Champions roster; Hilda is unused data and the Rival belongs to the Driftveil
event. None of the four has a fixed first Pokémon in the normal ROM-party path.
