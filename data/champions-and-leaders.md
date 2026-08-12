# WBT records used by the result routine

The table below lists the standard Champion records recovered from the examined
WBT table. It shows the source display metadata and the priority/category fields
consumed by `wbt_calc_result`; raw team/record words are omitted because that
routine does not read them. The USA/Europe retail WBT NARC is `/a/2/4/7`; it is byte-for-byte
identical to the development `/a/2/6/1` table (SHA-256
`0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`), so the
indices and names below are verified for both builds.

`Display code` is the exact `表示コード名` source key. It is an identifier,
not a strength or party-selection rule. `Code meaning` is an English
translation or reader-facing interpretation of the separate source
`ポジション` field.

| Trainer | Display code | Code meaning | WBT index | Priority | Category |
|---|---|---|---:|---:|---:|
| Blue | `RGCHAMPION` | Red/Green Champion | 14 | 4 | 17 |
| Lance | `GSCHAMPION` | Gold/Silver Champion | 15 | 4 | 17 |
| Steven | `RSCHAMPION` | Ruby/Sapphire Champion | 16 | 4 | 17 |
| Wallace | `ECHAMPION` | Emerald Champion | 17 | 4 | 17 |
| Cynthia | `SHIRONA` | Diamond/Pearl Champion (Japanese name: Shirona) | 18 | 4 | 17 |
| Alder | `CHAMPION` | Black/White Champion | 19 | 4 | 17 |
| Red | `RED` | Red/Green protagonist | 53 | 4 | 17 |

The records carry different team/record metadata, but after standard conversion
the result routine sees the same priority/category combination for all seven.

### Meaning of Champion category `17`

Category `17` (`0x11`) is the neutral/sentinel value recognized by the
type-chart helper at `0x02238554`. If either input category is `17`, the helper
returns the neutral comparison score `2` instead of reading an ordinary type
matchup. Consequently, two standard Champions tie at the category-comparison
stage; their later result is determined by the equal-record RNG. A/B only names
the two arguments passed to the symmetric result routine; it is not an
additional winner adjustment. This value is not a bracket `YY` setting.

## Standard Gym Leader records

The standard Gym Leader records are priority 3. The
`Category` column is the decoded type-chart category passed to the result
routine; the label in parentheses is the corresponding Generation V type. It
is a precomputed matchup field, not a simulation of the trainer's individual
Pokémon teams. The WBT index is the record index in the examined development
build's `/a/2/6/1` table, not the order in which a tournament displays the
trainers.

| Region | Trainer | Display code | Code meaning | WBT index | Priority | Category (type) |
|---|---|---|---|---:|---:|---:|
| Unova | Cheren | `SWLEADER1` | BW2 Gym Leader | 0 | 3 | 0 (Normal) |
| Unova | Roxie | `SWLEADER2` | BW2 Gym Leader | 1 | 3 | 3 (Poison) |
| Unova | Burgh | `SWLEADER3` | BW2 Gym Leader | 2 | 3 | 6 (Bug) |
| Unova | Elesa | `SWLEADER4` | BW2 Gym Leader | 3 | 3 | 12 (Electric) |
| Unova | Clay | `SWLEADER5` | BW2 Gym Leader | 4 | 3 | 4 (Ground) |
| Unova | Skyla | `SWLEADER6` | BW2 Gym Leader | 5 | 3 | 2 (Flying) |
| Unova | Drayden | `SWLEADER7` | BW2 Gym Leader | 6 | 3 | 15 (Dragon) |
| Unova | Marlon | `SWLEADER8` | BW2 Gym Leader | 7 | 3 | 10 (Water) |
| Unova | Chili | `LEADER1A` | BW Gym Leader | 9 | 3 | 9 (Fire) |
| Unova | Cress | `LEADER1B` | BW Gym Leader | 10 | 3 | 10 (Water) |
| Unova | Cilan | `LEADER1C` | BW Gym Leader | 11 | 3 | 11 (Grass) |
| Unova | Lenora | `LEADER2` | BW Gym Leader | 12 | 3 | 0 (Normal) |
| Unova | Brycen | `LEADER7` | BW Gym Leader | 13 | 3 | 14 (Ice) |
| Kanto | Brock | `RGLEADER1` | Red/Green Gym Leader | 20 | 3 | 5 (Rock) |
| Kanto | Misty | `RGLEADER2` | Red/Green Gym Leader | 21 | 3 | 10 (Water) |
| Kanto | Lt. Surge | `RGLEADER3` | Red/Green Gym Leader | 22 | 3 | 12 (Electric) |
| Kanto | Erika | `RGLEADER4` | Red/Green Gym Leader | 23 | 3 | 11 (Grass) |
| Kanto | Sabrina | `RGLEADER5` | Red/Green Gym Leader | 24 | 3 | 13 (Psychic) |
| Kanto | Blaine | `RGLEADER6` | Red/Green Gym Leader | 25 | 3 | 9 (Fire) |
| Kanto | Giovanni | `RGLEADER7` | Red/Green Gym Leader | 26 | 3 | 4 (Ground) |
| Kanto | Janine | `GSLEADER9` | Gold/Silver Gym Leader / Kanto Gym Leader | 35 | 3 | 3 (Poison) |
| Johto | Falkner | `GSLEADER1` | Gold/Silver Gym Leader | 27 | 3 | 2 (Flying) |
| Johto | Bugsy | `GSLEADER2` | Gold/Silver Gym Leader | 28 | 3 | 6 (Bug) |
| Johto | Whitney | `GSLEADER3` | Gold/Silver Gym Leader | 29 | 3 | 0 (Normal) |
| Johto | Morty | `GSLEADER4` | Gold/Silver Gym Leader | 30 | 3 | 7 (Ghost) |
| Johto | Chuck | `GSLEADER5` | Gold/Silver Gym Leader | 31 | 3 | 1 (Fighting) |
| Johto | Jasmine | `GSLEADER6` | Gold/Silver Gym Leader | 32 | 3 | 8 (Steel) |
| Johto | Pryce | `GSLEADER7` | Gold/Silver Gym Leader | 33 | 3 | 14 (Ice) |
| Johto | Clair | `GSLEADER8` | Gold/Silver Gym Leader | 34 | 3 | 15 (Dragon) |
| Hoenn | Roxanne | `RSLEADER1` | Ruby/Sapphire Gym Leader | 36 | 3 | 5 (Rock) |
| Hoenn | Brawly | `RSLEADER2` | Ruby/Sapphire Gym Leader | 37 | 3 | 1 (Fighting) |
| Hoenn | Wattson | `RSLEADER3` | Ruby/Sapphire Gym Leader | 38 | 3 | 12 (Electric) |
| Hoenn | Flannery | `RSLEADER4` | Ruby/Sapphire Gym Leader | 39 | 3 | 9 (Fire) |
| Hoenn | Norman | `RSLEADER5` | Ruby/Sapphire Gym Leader | 40 | 3 | 0 (Normal) |
| Hoenn | Winona | `RSLEADER6` | Ruby/Sapphire Gym Leader | 41 | 3 | 2 (Flying) |
| Hoenn | Tate | `RSLEADER7` | Ruby/Sapphire Gym Leader | 42 | 3 | 13 (Psychic) |
| Hoenn | Liza | `RSLEADER8` | Ruby/Sapphire Gym Leader | 43 | 3 | 13 (Psychic) |
| Hoenn | Juan | `ELEADER1` | Emerald Gym Leader | 44 | 3 | 10 (Water) |
| Sinnoh | Roark | `DPLEADER1` | Diamond/Pearl Gym Leader | 45 | 3 | 5 (Rock) |
| Sinnoh | Gardenia | `DPLEADER2` | Diamond/Pearl Gym Leader | 46 | 3 | 11 (Grass) |
| Sinnoh | Fantina | `DPLEADER3` | Diamond/Pearl Gym Leader | 47 | 3 | 7 (Ghost) |
| Sinnoh | Maylene | `DPLEADER4` | Diamond/Pearl Gym Leader | 48 | 3 | 1 (Fighting) |
| Sinnoh | Crasher Wake | `DPLEADER5` | Diamond/Pearl Gym Leader | 49 | 3 | 10 (Water) |
| Sinnoh | Byron | `DPLEADER6` | Diamond/Pearl Gym Leader | 50 | 3 | 8 (Steel) |
| Sinnoh | Candice | `DPLEADER7` | Diamond/Pearl Gym Leader | 51 | 3 | 14 (Ice) |
| Sinnoh | Volkner | `DPLEADER8` | Diamond/Pearl Gym Leader | 52 | 3 | 12 (Electric) |

The standard Leader rows above correspond to the in-game regional Leader
tournaments:
[Unova](https://www.serebii.net/black2white2/pwt/unova.shtml),
[Kanto](https://www.serebii.net/black2white2/pwt/kanto.shtml),
[Johto](https://www.serebii.net/black2white2/pwt/johto.shtml),
[Hoenn](https://www.serebii.net/black2white2/pwt/hoenn.shtml), and
[Sinnoh](https://www.serebii.net/black2white2/pwt/sinnoh.shtml). The Unova
pool selected by the examined source predicate has 13 possible NPC trainers:
the 13 standard Gym Leaders; Iris is excluded. Serebii's Unova page also lists
Bianca, so that public roster disagrees with the source-backed result here. The
table above is the complete cup-5 pool for the examined development and
USA/Europe retail builds.

### Two distinct WBT records named Cheren

The retail PWT-name table reuses the display name **Cheren** at two different
source-table indices. They are separate records and must not be merged when
describing priorities, categories, or tournament eligibility:

| WBT index | Record identity | Built-in role | Packed priority | Result category |
|---:|---|---|---:|---:|
| `0` | Standard Unova Gym Leader Cheren | Standard Unova Leader record; also eligible for modes whose constructors reuse the named Leader pool | 3 | `0` (Normal) |
| `56` | Special/event Cheren record | Driftveil event's priority-4 slot; a separate non-regional record | 4 | `17` (`0x11`, neutral sentinel) |

Index `0` is the Cheren listed in the standard Leader table above. Index `56`
is the Cheren row listed in
[`generic-and-rental-records.md`](generic-and-rental-records.md); its family
byte is `0x00`, its static eligibility mask is `0x01`, and its constructor pool
is `4`. The Driftveil-event constructor selects that row for its one
priority-4 / constructor-pool-4 slot. A downloadable tournament can also reference
either source index explicitly, depending on the `.pwt` match records.

Therefore, statements that “Cheren has priority 3” refer to the standard Leader
record at index `0`; statements that “Cheren has priority 4” refer only to the
special/event record at index `56`.
