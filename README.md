# Pokémon Black 2 / White 2 PWT NPC-vs-NPC result research

This repository documents a reverse-engineering result for the Pokémon World Tournament (PWT) in Pokémon Black 2 and White 2. It answers a long-standing practical question: when the game displays a match between two NPC trainers, is the winner always a 50/50 random choice?

## Short answer

- The bracket and pairings are randomized separately from the winner calculation.
- In the normal NPC simulation path, trainer records are reduced to a small set of fields: a priority, a type-chart category, and a trainer-type flag.
- Standard Champion records (Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red) all decode to the same relevant values: priority 4, trainer type 0, and category 17. The result routine does not read the trainer name or ID.
- Therefore, a Champion-vs-Champion tie is not 50/50 once the routine's slot asymmetry is included: if A and B are otherwise equal, A wins about 65% and B about 35%. “A” means the first/left slot, not a particular named Champion.
- A priority-4 Champion beats a standard priority-3 Gym Leader before the tie/random branch, so the standard Champion-vs-Leader result is deterministic in favor of the Champion.
- Leader-vs-Leader matches can be type-directed. If the two relevant values tie, the same A-slot adjustment applies; if B has the type advantage, the approximate result is A 30% / B 70%.

These percentages are for the observed normal NPC path and are approximate because the game uses integer arithmetic on its RNG output. They describe the encoded routine, not the strength of the teams in an actual battle.

## Evidence

The analysis was performed on an archived BW2 development build. It is not Nintendo source code, and the ROM is not included here. The repository records hashes, table indexes, decoded fields, disassembly locations, and reproducible pseudocode only.

- Result routine: overlay 55, RAM address `0x02238314` (`wbt_calc_result.c` debug string nearby).
- Type-chart helper: `0x02238554`; type table: `0x022399EC`.
- Record packing/conversion: overlay 135, including the packer around `0x0224208C`.
- WBT table: NARC `/a/2/6/1` (ARC resource 261; 128 records of 16 bytes in the examined build).
- Examined development-build main image SHA-256: `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.

See [`RESEARCH.md`](RESEARCH.md) for the routine and [`data/champions-and-leaders.md`](data/champions-and-leaders.md) for decoded records.

## Important scope note

The public `namofure/TournamentSearcher` project is a fan-made RNG/trainer-ID search tool, not official Nintendo source. Community posts should treat this repository as a development-build reverse-engineering report and invite retail-ROM verification.

## Sources and discussion

- [Project Pokémon PWT reverse-engineering discussion](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis (Japanese)](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [TournamentSearcher](https://github.com/namofure/TournamentSearcher)
- [Serebii Champion Tournament roster](https://www.serebii.net/black2white2/pwt/champion.shtml)

