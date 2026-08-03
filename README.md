# Pokémon Black 2 / White 2 PWT NPC-vs-NPC result research

This repository documents a reverse-engineering result for the Pokémon World Tournament (PWT) in Pokémon Black 2 and White 2. It answers a long-standing practical question: when the game displays a match between two NPC trainers, is the winner always a 50/50 random choice?

## Short answer

- Downloadable `.pwt` bracket data assigns opponent roles separately from the winner calculation. `YY=04` and `YY=05` are the documented required-semifinalist and required-finalist categories for those files; they are not win bonuses. Built-in cups use internal constructor/category data, and the public evidence does not prove a literal `YY` histogram for them.
- In the normal NPC simulation path, trainer records are reduced to a small set of fields: a priority, a type-chart category, and a trainer-type flag.
- Standard Champion records (Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red) all decode to the same relevant values: priority 4, trainer type 0, and category 17. The result routine does not read the trainer name or ID.
- Therefore, a Champion-vs-Champion tie is not 50/50 once the routine's slot asymmetry is included: if A and B are otherwise equal, A wins about 65% and B about 35%. “A” means the first/left slot, not a particular named Champion.
- A priority-4 Champion beats a standard priority-3 Gym Leader before the tie/random branch, so the standard Champion-vs-Leader result is deterministic in favor of the Champion.
- Leader-vs-Leader matches can be type-directed. If the two relevant values tie, the same A-slot adjustment applies; if B has the type advantage, the approximate result is A 30% / B 70%.
- A downloadable `YY=04` or `YY=05` tag is a placement/candidate tier for the player's semifinal or final path; it is not a win bonus. If several records share a tier, the selector can choose among them. Built-in constructor categories must not be relabeled as `YY` without a demonstrated data mapping.
- The built-in menu mapping is now recoverable statically, without an emulator: ID 1 is Champions, ID 2 Type Expert, ID 3 Download, ID 4 Driftveil, IDs 5–9 the regional Leaders cups, ID 10 World Leaders, and IDs 12–15 Rental/Mix plus their Master variants. ID 11 is a reserved/current-tournament branch without an ordinary menu label; ID 0 is the null/error path.
- The ID-11 story gate and event invocation are resolved statically: member
  1280, sequence 7 counts how many of eight PWT progress records equal exactly
  one win and selects the special Driftveil text only when that count is one.
  This branch does not itself write cup ID 11; the separate runtime producer of
  that numeric menu value is not present as a literal script call.

These percentages are for the observed normal NPC path and are approximate because the game uses integer arithmetic on its RNG output. They describe the encoded routine, not the strength of the teams in an actual battle.

## Evidence

The analysis was performed on an archived BW2 development build and cross-checked
against a complete, locally retained Black 2 retail ROM and its extracted script
NARC. It is not Nintendo source code. The repository records hashes, table
indexes, decoded fields, disassembly locations, and reproducible pseudocode;
the retail source's public-mirror provenance is documented separately and is
not a legally verified dump.

- Result routine: overlay 55, RAM address `0x02238314` (`wbt_calc_result.c` debug string nearby).
- Type-chart helper: `0x02238554`; type table: `0x022399EC`.
- Record packing/conversion: overlay 135, including the packer around `0x0224208C`.
- WBT table: NARC `/a/2/6/1` (ARC resource 261; 128 records of 16 bytes in the examined build).
- Examined development-build main image SHA-256: `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.

See [`RESEARCH.md`](RESEARCH.md) for the routine and [`data/champions-and-leaders.md`](data/champions-and-leaders.md) for decoded records.
See [`data/bracket-settings.md`](data/bracket-settings.md) for the bracket-setting fields and the selector trace.
See [`data/in-game-tournaments.md`](data/in-game-tournaments.md) for the ten built-in tournament families, source-table family counts, and cup-ID mappings established for the examined development build.
See [`data/in-game-constructor-categories.md`](data/in-game-constructor-categories.md) for the constructor dispatch, internal category pools, and confirmed slot-request patterns.
See [`data/yy-counts.md`](data/yy-counts.md) only for the separate downloadable `.pwt` appendix; it is not a count for the built-in tournaments.

## Retail script cross-check

The complete Black 2 USA/Europe ROM is retained at the artifact level under
`rom/retail-source/`; its header/FAT extraction of `/a/0/5/6` has 1,289
members. The static scanner finds the same state/reception sequence in
zero-based member 1280 as in the development `/a/0/5/9` archive, with the
eight `CMD_3EA` offsets and message branches recorded in `SOURCES.md` and
`RESEARCH.md`.

## Important scope note

The public `namofure/TournamentSearcher` project is a fan-made RNG/trainer-ID search tool, not official Nintendo source. Community posts should treat this repository as a development-build reverse-engineering report and invite retail-ROM verification.

## Sources and discussion

- [Project Pokémon PWT reverse-engineering discussion](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis (Japanese)](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [TournamentSearcher](https://github.com/namofure/TournamentSearcher)
- [Serebii Champion Tournament roster](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (built-in family names and unlock conditions; attribution retained in `data/in-game-tournaments.md`)
- [Bulbapedia: Pokémon World Tournament](https://bulbapedia.bulbagarden.net/wiki/PWT) (cross-check for permanent tournament groups)
