# Pokémon Black 2 / White 2 PWT NPC-vs-NPC result research

This repository documents how Pokémon Black 2 and White 2 construct and resolve Pokémon World Tournament (PWT) matches between NPC trainers. It answers a practical question: when two NPC trainers are shown battling, is either one equally likely to win, or does the game use another rule?

## Short answer

- In the normal NPC simulation path, trainer records are reduced to a small set of fields: a priority, a type-chart category, and a trainer-type flag.
- Standard Champion records (Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red) all decode to the same relevant values: priority 4, trainer type 0, and category 17. The result routine does not read the trainer name or ID.
- Therefore, a Champion-vs-Champion tie is exactly 50/50 in the source routine: both have equal priority and neutral category-17 affinity, so the code calls `GFL_STD_Rand(context, 2)`.
- A priority-4 Champion beats a standard priority-3 Gym Leader before the tie/random branch, so the standard Champion-vs-Leader result is deterministic in favor of the Champion.
- Standard Gym Leaders all have priority 3, so Leader-vs-Leader results are decided by comparing their stored type categories in both directions. The effectiveness levels are ranked from best to worst as super effective, neutral, not very effective, and no effect. If both directions produce the same effectiveness, the match is exactly 50/50. If one Leader has the better result—even if it is super effective versus no effect, or neutral versus not very effective—that Leader wins about 70% of the time, while the other still wins about 30% of the time.

## Verified scope

The source-level conclusions and cup-name mapping are definitive for the
archived development build examined here. The USA/Europe retail ROM
cross-check confirms the corresponding WBT table and relocated Overlay 55/135
behavior. This is not a claim that every Japanese, Korean, or later regional
revision has identical addresses, data, or scripts; those builds remain outside
the verified evidence set.

## Evidence

The analysis was performed on an archived BW2 development build and cross-checked
against a complete, locally retained Black 2 retail ROM. The recovered SWAN
source mirror is used to verify source-level structures and behavior—including
the winner routine, downloadable priority field, cup IDs, unlock predicates,
and command symbols/constants. It is retained locally and not redistributed
here. The result routine was also independently checked in the decompressed
retail Overlay 55.
The repository records hashes, table indexes, decoded fields, disassembly
locations, and reproducible pseudocode. The ROM and source artifacts are
retained locally and are not redistributed here.

- Result routine: overlay 55, RAM address `0x02238314` (`wbt_calc_result.c` debug string nearby).
- Type-chart helper: `0x02238554`; type table: `0x022399EC`.
- Retail Overlay 55: base `0x021E5800`, result routine `0x021E614C`, type-chart helper `0x021E6338`; its control flow matches the development routine.
- Record packing/conversion: overlay 135, including the packer around `0x0224208C`.
- Development WBT table: NARC `/a/2/6/1` (ARC resource 261; 128 records of 16 bytes in the examined build).
- USA/Europe retail cross-check: Overlay 135 has the same constructor, Type Expert eligibility predicate, 16-case cup dispatch, and eight-position shuffle roles at relocated addresses. The retail WBT table is `/a/2/4/7`, whose SHA-256 exactly matches the development `/a/2/6/1` table; the retail `/a/2/6/1` path is a different 1,000-member NARC.
- Only the USA/Europe retail ROM is available in the local evidence set; Japanese, Korean, and other regional/revision retail builds remain unverified.
- Examined development-build main image SHA-256: `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.

See [`RESEARCH.md`](RESEARCH.md) for the routine and [`data/champions-and-leaders.md`](data/champions-and-leaders.md) for decoded records.
See [`data/bracket-settings.md`](data/bracket-settings.md) for the bracket-setting fields and the selector trace.
See [`data/in-game-tournaments.md`](data/in-game-tournaments.md) for the ten unlockable built-in tournament families, source-table family counts, and the additional base/event cup-ID mappings established for the examined development build.
See [`data/in-game-constructor-categories.md`](data/in-game-constructor-categories.md) for the constructor dispatch, internal category pools, and confirmed slot-request patterns.
See [`data/generic-and-rental-records.md`](data/generic-and-rental-records.md) for the complete source-record masks, generic record groups, retail PWT names, model IDs, battle-trainer-type fields, derived priority/category/trainer-type fields, and the proved Rental/Mix candidate pools.
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

## Sources and discussion

- [Project Pokémon PWT reverse-engineering discussion](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis (Japanese)](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [TournamentSearcher](https://github.com/namofure/TournamentSearcher)
- [Serebii Champion Tournament roster](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (built-in family names and unlock conditions; attribution retained in `data/in-game-tournaments.md`)
- [Bulbapedia: Pokémon World Tournament](https://bulbapedia.bulbagarden.net/wiki/PWT) (cross-check for permanent tournament groups)

## Tests

The scanner unit tests use small synthetic NARC/script fixtures and do not
require a ROM or recovered source archive:

```sh
python3 -m unittest discover -s tests -v
```
