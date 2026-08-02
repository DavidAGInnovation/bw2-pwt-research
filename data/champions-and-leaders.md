# WBT records used by the result routine

The table below lists the standard Champion records recovered from the examined WBT table. “Relevant packed fields” are the fields consumed by `wbt_calc_result`; other raw words identify the trainer/team but are not read by that routine.

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

## Standard Gym Leader categories

The standard Leader records are priority 3. Representative category values from the same table are:

| Trainer | WBT index | Category |
|---|---:|---:|
| Cheren | 0 | 0 |
| Roxie | 1 | 3 |
| Burgh | 2 | 6 |
| Elesa | 3 | 12 |
| Clay | 4 | 4 |
| Skyla | 5 | 2 |
| Drayden | 6 | 15 |
| Marlon | 7 | 10 |
| Bianca | 8 | 17 |
| Chili | 9 | 9 |
| Cress | 10 | 10 |
| Cilan | 11 | 11 |
| Lenora | 12 | 0 |
| Brycen | 13 | 14 |

These categories are used by the game's matchup table, not by a conventional six-Pokémon battle simulation.

