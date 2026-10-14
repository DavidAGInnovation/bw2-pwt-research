# Pokémon Black 2 / White 2 — Pokémon World Tournament mechanics research

This repository documents how Pokémon Black 2 and White 2 construct and
resolve Pokémon World Tournament (PWT) brackets, opponents, parties, Rental
Pokémon, and simulated NPC results. It began with a practical question: when
two NPC Trainers are shown battling, are they equally likely to win, or does
the game use another rule?

## Short answer

- In the normal NPC simulation path, priority and type-chart category determine
  the NPC winner. The packed trainer-type field is used for the separate player
  override; it is not an additional NPC strength value.
- Standard Champion records (Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red) all decode to the same relevant values: priority 4, trainer type 0, and category 17. The result routine does not read the trainer name or ID.
- Therefore, a Champion-vs-Champion tie is exactly 50/50 in the source routine: both have equal priority and neutral category-17 affinity, so the code calls `GFL_STD_Rand(context, 2)`.
- A priority-4 Champion beats a standard priority-3 Gym Leader before the tie/random branch, so the standard Champion-vs-Leader result is deterministic in favor of the Champion.
- Standard Gym Leaders all have priority 3. In modes that retain their stored type categories, Leader-vs-Leader results compare those categories in both directions. The effectiveness levels are ranked from best to worst as super effective, neutral, not very effective, and no effect. If both directions produce the same effectiveness, the match is exactly 50/50. If one Leader has the better result—even if it is super effective versus no effect, or neutral versus not very effective—that Leader wins about 70% of the time, while the other still wins about 30% of the time.
- Rental, Rental Master, Mix, and Mix Master overwrite every participant's matchup category with neutral category 17. Equal-priority NPC matches in those modes are therefore 50/50, including Leader pairs whose source types would otherwise give a 70/30 result. Different priorities still give the higher-priority NPC a deterministic win.

## Other verified findings

- Red's normal party receives 30 IVs in every stat. The other six standard
  Champions receive 25, and all 46 standard Gym Leader records receive 20.
- Every built-in opponent uses the same complete battle-AI configuration. Red
  has higher IVs, but not a stronger AI setting.
- Ace-marked Trainers place their ace in party position 0 when the normal ROM
  party builder is used. Rental modes bypass that party, while Mix modes can
  exchange the ace away before battle.
- The three visible Rental tickets secretly select the Weak, Strong, and All
  record ranges. Under All, the opponent receives three strong records and
  fills any remaining party positions from the weak range.
- Simulated bracket results are deterministic once the stored 64-bit PWT seed
  and ordered participant records are known. Waiting after PWT creation does
  not change that result stream.
- Rental Pokémon records 909–988 contain complete legendary builds, but every
  built-in Rental range ends at 908, so those records cannot be selected.
- In normal built-in cup construction, Trainer IDs 78–127 are NPC-only bracket
  fillers. They can occupy simulated bracket positions but cannot become the
  player's opponent. A custom downloadable file can override their priorities,
  so this restriction does not describe every possible download.

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
- PWT RNG initialization: development Overlay 55 calls the global MT19937 generator twice at `0x022379D0/0x022379D6`; retail does the same at `0x021E5BBC/0x021E5BC2`. The resulting 64-bit seed is replayed by a private LCG for bracket-result calculation.
- Record packing/conversion: overlay 135, including the packer around `0x0224208C`.
- Development WBT table: NARC `/a/2/6/1` (ARC resource 261; 128 records of 16 bytes in the examined build).
- USA/Europe retail cross-check: Overlay 135 has the same constructor, Type Expert eligibility predicate, 16-case cup dispatch, and eight-position shuffle roles at relocated addresses. The retail WBT table is `/a/2/4/7`, whose SHA-256 exactly matches the development `/a/2/6/1` table; the retail `/a/2/6/1` path is a different 1,000-member NARC.
- Only the USA/Europe retail ROM is available in the local evidence set; Japanese, Korean, and other regional/revision retail builds remain unverified.
- Examined development-build main image SHA-256: `ac4fb3e97b90831bd878f4e6ab0bed4ad355311ff90becba79ab79456f4e12da`.

## Documentation map

- [`RESEARCH.md`](RESEARCH.md): winner routine, probability model, exact PWT
  RNG transition, bracket call order, and practical prediction limits.
- [`data/champions-and-leaders.md`](data/champions-and-leaders.md): Champion
  and Gym Leader display codes, meanings, priorities, categories, IVs, and
  shared AI behavior.
- [`data/bracket-settings.md`](data/bracket-settings.md): downloadable `.pwt`
  priority field and bracket-selector behavior.
- [`data/in-game-tournaments.md`](data/in-game-tournaments.md): built-in cup
  families, source-table counts, cup IDs, and unlock predicates.
- [`data/in-game-constructor-categories.md`](data/in-game-constructor-categories.md):
  constructor dispatch, candidate pools, and slot-request patterns.
- [`data/wbt-party-selection.md`](data/wbt-party-selection.md): active-party
  sizes, random selection without replacement, fixed-ace construction, Rental
  and Mix exceptions, and complete ace/no-ace coverage.
- [`data/rental-pokemon-pools.md`](data/rental-pokemon-pools.md): Rental and
  Rental Master ranges, hidden ticket choices, IV rules, selectable species,
  excluded legendary records, and build-field interpretation.
- [`data/rental-pokemon-builds.csv`](data/rental-pokemon-builds.csv): all 908
  selectable builds and 80 valid excluded legendary builds, including species,
  form, item, moves, nature, EVs, IV rules, abilities, gender, and friendship.
- [`data/generic-and-rental-records.md`](data/generic-and-rental-records.md):
  generic and special Trainer names, display codes and meanings, source
  groups, priorities, categories, IV assignments, and verified Rental/Mix
  candidate pools.
- [`data/yy-counts.md`](data/yy-counts.md): separate downloadable `.pwt`
  appendix; these counts do not describe the built-in tournaments.

## Retail/source cross-check

The USA/Europe Black 2 retail ROM independently confirms the relocated winner
routine, seed initialization, built-in constructor dispatch, Type Expert
predicate, participant shuffle, and WBT source table used in the development
analysis. The relevant retail table is byte-identical to the examined
development table. Detailed addresses, archive paths, hashes, and the resolved
Join Avenue/PWT command distinction are retained in [`RESEARCH.md`](RESEARCH.md)
and the corresponding pages under [`data/`](data/); ROM and recovered source
artifacts are not redistributed.

## Independent verification

The [2026-10-14 findings review](docs/VERIFICATION.md) documents the source and
ROM cross-checks, corrected mechanics and complete download-hash verification.
The [verification evidence](verification/) includes decoded results and
independent checks. ROM images and recovered source files remain local.

```sh
python3 verification/verify_historical_downloads.py
```

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
