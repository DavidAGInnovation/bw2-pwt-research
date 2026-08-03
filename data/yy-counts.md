# `YY` counts by tournament file

This table counts the seven raw bracket records stored in each downloadable
`.pwt` file. The player is the eighth participant, so every row totals seven
NPC records. `YY` is the second byte of each four-byte bracket record
(`XX YY ZZZZ`).

## Official downloadable tournament files

| Tournament file | `YY=00` | `YY=01` | `YY=02` | `YY=03` | `YY=04` | `YY=05` | Total | Selected artifact / SHA-256 (downloaded 2026-08-02) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [2012 Junior Division Challenge](https://projectpokemon.org/home/files/file/1500-2012-junior-division-challenge/) | 0 | 3 | 0 | 2 | 1 | 1 | 7 | `[ENG10004]`; `5ddb96a6988de79a1458e5a1933274760f58cf6b3aefbf6bf3e6dd1a35d8d7f4` |
| [2012 Master Division Challenge](https://projectpokemon.org/home/files/file/1502-2012-master-division-challenge/) | 0 | 3 | 0 | 2 | 1 | 1 | 7 | `[ENG10005]`; `d0761244cf7be76da9df1cf9878a13b2490638925d7d5fa5a78faa196fac29d6` |
| [You Can Challenge the Unova League Too!](https://projectpokemon.org/home/files/file/1508-you-can-challenge-the-unova-league-too/) | 0 | 3 | 0 | 0 | 2 | 2 | 7 | `[JPN00009]`; `6633294afa8f021bc7080488a5b52c990a47588d6c79d9378afc919897d7b7` |
| [Battle of Legendary Pokémon](https://projectpokemon.org/home/files/file/1507-battle-of-legendary-pok%C3%A9mon/) | 0 | 3 | 0 | 4 | 0 | 0 | 7 | `[JPN00005]`; `a854f94568153442b86925278e4e57e6a2bed6d7907d9c4653c809fd29fb2465` |
| [Legendary Rotation Battle!](https://projectpokemon.org/home/files/file/1506-legendary-rotation-battle/) | 0 | 4 | 1 | 2 | 0 | 0 | 7 | `[JPN00004]`; `fbf0ef1185a341eb9ec0f40d51c42f54adcc746aa8b21727c2f3d9ee194f379c` |
| [Gym Leaders Assemble!](https://projectpokemon.org/home/files/file/1505-gym-leaders-assemble/) | 0 | 3 | 0 | 0 | 0 | 4 | 7 | `[JPN00003]`; `d9419516dd05a95e5c56ac2025f3cbe9a2cc487103d82cc25261aeb1d228acf4` |
| [Challenge Champion Lance!](https://projectpokemon.org/home/files/file/1504-challenge-champion-lance/) | 0 | 3 | 0 | 3 | 0 | 1 | 7 | `[JPN00002]`; `8ff3d77de414b7be617af6c47c65833b3c1ddc6c6ea92140274ecbb0ec5e1443` |
| [2012 VGC Japan Representatives](https://projectpokemon.org/home/files/file/1503-2012-vgc-japan-representatives/) | 0 | 4 | 0 | 3 | 0 | 0 | 7 | `[JPN00001]`; `9c6110ef28ce168670315ba696e47f7cf2d915fc1e9fd6f8b661bddb9e8cfdcc` |
| [2012 Senior Division Challenge](https://projectpokemon.org/home/files/file/1501-2012-senior-division-challenge/) | 0 | 3 | 0 | 2 | 1 | 1 | 7 | `[ENG10002]`; `20f128f31c335acf952d60740184f8b739a7ec0a5a7891196de449e526ab5f5d` |

The public file pages show named-role descriptions (for example, “Finalist
Battle Virgil” and “Semifinalist Battle Stephan/Trip”). Those descriptions are
not a substitute for the raw seven-record count: the Unova file, for example,
contains two `YY=05` and two `YY=04` records even though the page lists only one
finalist and two semifinalists. This is why both the raw histogram and the page
description should be preserved.

Sources:

- [Project Pokémon PWT download category](https://projectpokemon.org/home/files/category/51-pok%C3%A9mon-world-tournaments/)
- [Project Pokémon `YY` format notes](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)

## Additional records listed in the reverse-engineering discussion

These are seven-record presets transcribed from the same Project Pokémon post;
they are useful for comparing internal/older/custom scenarios but are not all
identical to the nine downloadable files above.

| Preset name in the post | `YY=00` | `YY=01` | `YY=02` | `YY=03` | `YY=04` | `YY=05` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Japan Nationals | 0 | 4 | 0 | 3 | 0 | 0 | 7 |
| VGC 2012 | 0 | 3 | 0 | 2 | 1 | 1 | 7 |
| Legendary Rotation | 0 | 4 | 1 | 2 | 0 | 0 | 7 |
| Lance | 0 | 3 | 0 | 3 | 0 | 1 | 7 |
| Gathered Gym | 0 | 3 | 0 | 0 | 0 | 4 | 7 |
| ROM Masters | 0 | 3 | 1 | 1 | 1 | 1 | 7 |
| ROM Seniors | 1 | 1 | 1 | 1 | 0 | 3 | 7 |
| ROM Juniors | 0 | 2 | 1 | 2 | 1 | 1 | 7 |
| Battle of Legendary Singles | 0 | 3 | 0 | 4 | 0 | 0 | 7 |

## What is fixed and what is random?

The count in a file is fixed; the game does not reroll “how many `YY=05`
records exist” on every tournament entry. RNG can still choose among multiple
records sharing a tier, and the constructor can request different tier slots
for different tournament modes. In the observed seven-opponent construction
path, the request was one category-5 slot, one category-4 slot, one category-3
slot, and four category-1 slots. That request is separate from the raw counts
above, and it should not be generalized to every tournament mode without its
constructor data.

## Reproduction

The repository includes `scripts/parse_pwt_bracket.py`. Download a file from a
Project Pokémon file page, then run:

```sh
python3 scripts/parse_pwt_bracket.py path/to/file.pwt --offset 0x11f4
```

The script prints the seven four-byte records and the `YY` histogram. The
`0x11f4` offset is the bracket-record offset in the nine artifacts listed above;
it is an observed format detail, not a claim that every future/custom file has
the same absolute offset.

`YY=00` is retained in the histograms because it occurs in the published
format/preset data. The public notes identify byte 1 as the Trainer Rank field,
but do not establish the bracket role of rank `0x00`. See
[`bracket-settings.md`](bracket-settings.md); do not infer a built-in cup name
or a first-round/finalist meaning from the value alone.

## Scope limitation

This is a complete count for the nine publicly downloadable `.pwt` files and
the additional seven-record presets published in the cited reverse-engineering
post. The USA/Europe retail WBT NARC is `/a/2/4/7` and matches the development
table byte-for-byte; the separate retail `/a/2/6/1` NARC has 1,000 members and
is not the WBT roster table. Neither is folded into these downloadable `YY`
counts. No retail ROM is redistributed here.
