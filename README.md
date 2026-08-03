# Pokémon Black 2 / White 2 PWT NPC-vs-NPC result research

This repository documents a reverse-engineering result for the Pokémon World Tournament (PWT) in Pokémon Black 2 and White 2. It answers a long-standing practical question: when the game displays a match between two NPC trainers, is the winner always a 50/50 random choice?

## Short answer

- Downloadable `.pwt` bracket data assigns opponent roles separately from the winner calculation. `YY=04` and `YY=05` are the documented required-semifinalist and required-finalist categories for those files; they are not win bonuses. Built-in cups use internal constructor/category data, and the public evidence does not prove a literal `YY` histogram for them.
- In the normal NPC simulation path, trainer records are reduced to a small set of fields: a priority, a type-chart category, and a trainer-type flag.
- Standard Champion records (Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red) all decode to the same relevant values: priority 4, trainer type 0, and category 17. The result routine does not read the trainer name or ID.
- Therefore, a Champion-vs-Champion tie is exactly 50/50 in the source routine: both have equal priority and neutral category-17 affinity, so the code calls `GFL_STD_Rand(context, 2)`. “A” means the first/left slot, not a particular named Champion.
- A priority-4 Champion beats a standard priority-3 Gym Leader before the tie/random branch, so the standard Champion-vs-Leader result is deterministic in favor of the Champion.
- Leader-vs-Leader matches can be type-directed. If the two affinity values tie, the result is 50/50. If one side has the type advantage, that side wins about 70% and the other about 30%; the source's 30% reversal applies in either direction.
- A downloadable `YY=04` or `YY=05` tag is a placement/candidate tier for the player's semifinal or final path; it is not a win bonus. If several records share a tier, the selector can choose among them. Built-in constructor categories must not be relabeled as `YY` without a demonstrated data mapping.
- `YY=00` is the downloadable record's `pri` field with source value `WBT_TRPRI_NULL` (numeric priority 0, “undefined”). The game copies it into the trainer record, so it is the lowest/unprioritized value for bracket sorting and NPC-result comparison; it is not a hidden win bonus or a separate built-in cup category. The public labels for `YY=01`–`05` describe observed placement consequences, while the source implements the underlying field as numeric priority.
- The built-in menu mapping is now recoverable statically, without an emulator: ID 1 is Champions, ID 2 Type Expert, ID 3 Download, ID 4 Driftveil, IDs 5–9 the regional Leaders cups, ID 10 World Leaders, ID 11 the source-defined Driftveil event cup, and IDs 12–15 Rental/Mix plus their Master variants. ID 0 is the null/error path.
- The original SWAN source now resolves the built-in cup IDs and unlock logic.
  `WBTCUP_HODOMOE_EVENT` is ID 11 and is enabled while the ordinary Driftveil
  win counter is zero; the ordinary Driftveil cup (ID 4) requires that counter
  to be nonzero. The same source maps the other in-game IDs and their unlock
  predicates in `wbt.h` and `wbt_tool.c`.
- The PWT menu is built dynamically: member 1277 checks each candidate with
  `CMD_3EE`, conditionally emits `ListMenuAdd` with that candidate as its UID
  (including UID 11), stores the selected UID in `0x8023`, and passes it to
  `CMD_3F3`. There is no literal `CMD_3F3 11` because the setter receives the
  menu result.
- The recovered source file `wbt_calc_result.c` verifies the winner routine:
  unequal priorities are deterministic, equal affinities use `rand(2)`, and
  unequal affinities use the type-favored result with a three-in-ten reversal.
- The original Nintendo source is now available in the recovered SWAN mirror.
  For the Join Avenue/Resonance Resort command table, it names `CMD_3EA`
  `EvCmdResortGetData` in
  `branches/fes_rom/prog/src/field/resonance_resort/scrcmd_resort.c`, and the
  command table registers it as `EV_SEQ_RESORT_GET_DATA`. The source's
  parameters 17–24 are the eight shop-selection cases seen in the retail and
  development dispatches. The shared source macro starts overlay command IDs
  at 1000; two preceding entries put this function at 1002 (`0x3EA`). The
  WBT uses the same numeric command slot in its own table: `CMD_3EA` is
  `EvCmdWBTSystemCheckEnable`, while `EvCmdWBTGetVictoryCount` is `CMD_3FA`.
  The corresponding stripped-binary **Resort** dispatches are overlay-specific,
  at `0x02237618` (development) / `0x021e5950` (retail), with the shared helper
  at `0x02248d54` / `0x021f522c`.

These percentages are for the observed normal NPC path and are approximate because the game uses integer arithmetic on its RNG output. They describe the encoded routine, not the strength of the teams in an actual battle.

## Evidence

The analysis was performed on an archived BW2 development build and cross-checked
against a complete, locally retained Black 2 retail ROM. The recovered SWAN
source mirror is used only to identify the original command symbol and
constants; it is retained locally and not redistributed here. The result
routine was also independently checked in the decompressed retail Overlay 55.
The repository records hashes, table indexes, decoded fields, disassembly
locations, and reproducible pseudocode; the ROM/source mirror provenance is
documented separately and is not a legally verified dump.

- Result routine: overlay 55, RAM address `0x02238314` (`wbt_calc_result.c` debug string nearby).
- Type-chart helper: `0x02238554`; type table: `0x022399EC`.
- Retail Overlay 55: base `0x021E5800`, result routine `0x021E614C`, type-chart helper `0x021E6338`; its control flow matches the development routine.
- Record packing/conversion: overlay 135, including the packer around `0x0224208C`.
- Development WBT table: NARC `/a/2/6/1` (ARC resource 261; 128 records of 16 bytes in the examined build).
- USA/Europe retail cross-check: Overlay 135 has the same constructor, category helper, 16-case cup dispatch, and eight-position shuffle roles at relocated addresses. The retail WBT table is `/a/2/4/7`, whose SHA-256 exactly matches the development `/a/2/6/1` table; the retail `/a/2/6/1` path is a different 1,000-member NARC.
- Only the USA/Europe retail ROM is available in the local evidence set; Japanese, Korean, and other regional/revision retail builds remain unverified.
- Examined development-build main image SHA-256: `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.

See [`RESEARCH.md`](RESEARCH.md) for the routine and [`data/champions-and-leaders.md`](data/champions-and-leaders.md) for decoded records.
See [`data/bracket-settings.md`](data/bracket-settings.md) for the bracket-setting fields and the selector trace.
See [`data/in-game-tournaments.md`](data/in-game-tournaments.md) for the ten built-in tournament families, source-table family counts, and cup-ID mappings established for the examined development build.
See [`data/in-game-constructor-categories.md`](data/in-game-constructor-categories.md) for the constructor dispatch, internal category pools, and confirmed slot-request patterns.
See [`data/yy-counts.md`](data/yy-counts.md) only for the separate downloadable `.pwt` appendix; it is not a count for the built-in tournaments.

## Retail/source cross-check

The complete Black 2 USA/Europe ROM is retained at the artifact level under
`rom/retail-source/`; its header/FAT extraction of `/a/0/5/6` has 1,289
members. Member 1280 matches the development `resort_scr.bin` Join Avenue
script, not a PWT unlock script. The PWT unlock behavior is instead directly
identified by the recovered SWAN source: `wbt_lobby.ev` requests
`_WBT_CHECK_CUP_ENABLE` and `wbt_tool.c` evaluates the corresponding counters.
The retail ROM's compressed Overlay 55 (file ID 55) was also extracted and
decompressed: its 7,616-byte image has SHA-256
`1d7ed4cc8ffb33a1bd715f621a38203f45e2a4453864a8fafb287aa5d744ad33`. The
retail result routine at `0x021E614C` has the same equal-affinity `rand(2)`
branch and the same symmetric unequal-affinity threshold-7 toggle as the
development routine. The extracted binary and full disassembly are retained
locally under the artifact directory and are not redistributed.

## Important scope note

The public `namofure/TournamentSearcher` project is a fan-made RNG/trainer-ID search tool, not official Nintendo source. Community posts should treat this repository as a source/development reverse-engineering report with a USA/Europe retail cross-check, and invite verification of other regional or revision ROMs.

## Sources and discussion

- [Project Pokémon PWT reverse-engineering discussion](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis (Japanese)](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [TournamentSearcher](https://github.com/namofure/TournamentSearcher)
- [Serebii Champion Tournament roster](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (built-in family names and unlock conditions; attribution retained in `data/in-game-tournaments.md`)
- [Bulbapedia: Pokémon World Tournament](https://bulbapedia.bulbagarden.net/wiki/PWT) (cross-check for permanent tournament groups)
