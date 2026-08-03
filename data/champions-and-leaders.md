# WBT records used by the result routine

The table below lists the standard Champion records recovered from the examined
WBT table. “Relevant packed fields” are the fields consumed by
`wbt_calc_result`; other raw words identify the trainer/team but are not read by
that routine. The USA/Europe retail WBT NARC is `/a/2/4/7`; it is byte-for-byte
identical to the development `/a/2/6/1` table (SHA-256
`0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`), so the
indices and names below are verified for both builds.

| Trainer | WBT index | Raw word 0 | Raw word 1 | Priority | Trainer type | Category |
|---|---:|---:|---:|---:|---:|---:|
| Blue | 14 | `0x0011` | `0x011D` | 4 | 0 | 17 |
| Lance | 15 | `0x0011` | `0x011E` | 4 | 0 | 17 |
| Steven | 16 | `0x0011` | `0x011F` | 4 | 0 | 17 |
| Wallace | 17 | `0x0011` | `0x0120` | 4 | 0 | 17 |
| Cynthia | 18 | `0x0111` | `0x00D7` | 4 | 0 | 17 |
| Alder | 19 | `0x0011` | `0x0061` | 4 | 0 | 17 |
| Red | 53 | `0x0011` | `0x0177` | 4 | 0 | 17 |

The different raw values (including Red's `0x00F4` field and Cynthia's `0x0111` word 0) encode team/record metadata. After the standard conversion, the result routine sees the same priority/category/trainer-type combination for all seven.

### Meaning of Champion category `17`

Category `17` (`0x11`) is the neutral/sentinel value recognized by the
type-chart helper at `0x02238554`. If either input category is `17`, the helper
returns the neutral comparison score `2` instead of reading an ordinary type
matchup. Consequently, two standard Champions tie at the category-comparison
stage; their later result is determined by the equal-record RNG and A/B-slot
adjustment. This value is not a bracket `YY` setting.

## Standard Gym Leader records

The standard Gym Leader records are priority 3 and use trainer type 0. The
`Category` column is the decoded type-chart category passed to the result
routine; the label in parentheses is the corresponding Generation V type. It
is a precomputed matchup field, not a simulation of the trainer's individual
Pokémon teams. The WBT index is the record index in the examined development
build's `/a/2/6/1` table, not the order in which a tournament displays the
trainers.

| Region | Trainer | WBT index | Priority | Trainer type | Category (type) |
|---|---|---:|---:|---:|---:|
| Unova | Cheren | 0 | 3 | 0 | 0 (Normal) |
| Unova | Roxie | 1 | 3 | 0 | 3 (Poison) |
| Unova | Burgh | 2 | 3 | 0 | 6 (Bug) |
| Unova | Elesa | 3 | 3 | 0 | 12 (Electric) |
| Unova | Clay | 4 | 3 | 0 | 4 (Ground) |
| Unova | Skyla | 5 | 3 | 0 | 2 (Flying) |
| Unova | Drayden | 6 | 3 | 0 | 15 (Dragon) |
| Unova | Marlon | 7 | 3 | 0 | 10 (Water) |
| Unova | Chili | 9 | 3 | 0 | 9 (Fire) |
| Unova | Cress | 10 | 3 | 0 | 10 (Water) |
| Unova | Cilan | 11 | 3 | 0 | 11 (Grass) |
| Unova | Lenora | 12 | 3 | 0 | 0 (Normal) |
| Unova | Brycen | 13 | 3 | 0 | 14 (Ice) |
| Kanto | Brock | 20 | 3 | 0 | 5 (Rock) |
| Kanto | Misty | 21 | 3 | 0 | 10 (Water) |
| Kanto | Lt. Surge | 22 | 3 | 0 | 12 (Electric) |
| Kanto | Erika | 23 | 3 | 0 | 11 (Grass) |
| Kanto | Sabrina | 24 | 3 | 0 | 13 (Psychic) |
| Kanto | Blaine | 25 | 3 | 0 | 9 (Fire) |
| Kanto | Giovanni | 26 | 3 | 0 | 4 (Ground) |
| Kanto | Janine | 35 | 3 | 0 | 3 (Poison) |
| Johto | Falkner | 27 | 3 | 0 | 2 (Flying) |
| Johto | Bugsy | 28 | 3 | 0 | 6 (Bug) |
| Johto | Whitney | 29 | 3 | 0 | 0 (Normal) |
| Johto | Morty | 30 | 3 | 0 | 7 (Ghost) |
| Johto | Chuck | 31 | 3 | 0 | 1 (Fighting) |
| Johto | Jasmine | 32 | 3 | 0 | 8 (Steel) |
| Johto | Pryce | 33 | 3 | 0 | 14 (Ice) |
| Johto | Clair | 34 | 3 | 0 | 15 (Dragon) |
| Hoenn | Roxanne | 36 | 3 | 0 | 5 (Rock) |
| Hoenn | Brawly | 37 | 3 | 0 | 1 (Fighting) |
| Hoenn | Wattson | 38 | 3 | 0 | 12 (Electric) |
| Hoenn | Flannery | 39 | 3 | 0 | 9 (Fire) |
| Hoenn | Norman | 40 | 3 | 0 | 0 (Normal) |
| Hoenn | Winona | 41 | 3 | 0 | 2 (Flying) |
| Hoenn | Tate | 42 | 3 | 0 | 13 (Psychic) |
| Hoenn | Liza | 43 | 3 | 0 | 13 (Psychic) |
| Hoenn | Juan | 44 | 3 | 0 | 10 (Water) |
| Sinnoh | Roark | 45 | 3 | 0 | 5 (Rock) |
| Sinnoh | Gardenia | 46 | 3 | 0 | 11 (Grass) |
| Sinnoh | Fantina | 47 | 3 | 0 | 7 (Ghost) |
| Sinnoh | Maylene | 48 | 3 | 0 | 1 (Fighting) |
| Sinnoh | Crasher Wake | 49 | 3 | 0 | 10 (Water) |
| Sinnoh | Byron | 50 | 3 | 0 | 8 (Steel) |
| Sinnoh | Candice | 51 | 3 | 0 | 14 (Ice) |
| Sinnoh | Volkner | 52 | 3 | 0 | 12 (Electric) |

The standard Leader rows above correspond to the in-game regional Leader
tournaments:
[Unova](https://www.serebii.net/black2white2/pwt/unova.shtml),
[Kanto](https://www.serebii.net/black2white2/pwt/kanto.shtml),
[Johto](https://www.serebii.net/black2white2/pwt/johto.shtml),
[Hoenn](https://www.serebii.net/black2white2/pwt/hoenn.shtml), and
[Sinnoh](https://www.serebii.net/black2white2/pwt/sinnoh.shtml). The Unova
pool has 14 possible NPC trainers: 13 standard Gym Leaders plus Bianca as a
special wildcard; Iris is excluded. The table above intentionally lists only
the 13 standard Leader records.

### Bianca wildcard record

Index 8 is Bianca's record. Its family byte is `0x00`, so it is not part of the
standard Unova Leader-family (`0x05`) count. That classification does **not**
exclude Bianca from the Unova Leaders tournament: cup ID 5's constructor uses
the source slice at indices `0–13`, which includes index 8. It can therefore
select Bianca as one of the seven NPCs for a run. The published
[Unova Leaders roster](https://www.serebii.net/black2white2/pwt/unova.shtml)
also lists Bianca, so she is an actual selectable opponent in that cup. Because the constructor
selects seven NPCs from the 14-record pool, Bianca may appear in a given
bracket but is not guaranteed to appear every time. The same record may also
be reused by another WBT mode; reuse does not make it ineligible for Unova
Leaders.

These categories are used by the game's matchup table, not by a conventional
six-Pokémon battle simulation.
