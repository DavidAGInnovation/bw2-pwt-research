# Source trail

## Primary artifacts used for this report

- Archived BW2 development build examined locally (not redistributed).
- Overlay 55 disassembly: result routine at `0x02238314`; type-chart helper at `0x02238554`; chart data at `0x022399EC`.
- Overlay 135 disassembly: WBT record conversion/packing around `0x0224208C`.
- Overlay 135 constructor/selector/shuffle: cup dispatch at `0x02241D02`, candidate selection at `0x02241704`, and common eight-position shuffle at `0x02241DB8`.
- Script NARC `/a/0/5/9`, member 1277: the PWT menu result (`ListMenuInitTL` at
  member offset `0x05E2`), the cup-ID setter (`CMD_3F3` at `0x02E7`, passing
  the selected work variable), and the ID-to-description switch at
  `0x0B95–0x0DC0` (the offsets include the member's four-byte prefix).
- Script NARC `/a/0/5/9`, zero-based NARC entry 1280, sequence 7 at raw member
  offset `0x3807` (through `0x38E0`): the WBT state/reception sequence that
  calls `CMD_3EA` for PWT save-record IDs `17,18,21,20,19,22,23,24`, compares
  each returned value with `1`, increments accumulator `0x8055` for exact
  matches, then selects messages 113 or 114 according to the final
  `0x8055 == 1` gate at `0x38FF`.
  This is the identified story/event invocation of the special branch; the
  separate menu/resource producer of numeric cup ID 11 is not a literal
  `CMD_3F3 11` script call.
- Overlay 55 disassembly: `EvCmdWBTSetWBTCup` (`CMD_3F3`) starts at
  `0x02237728`; `EvCmdWBTSetReceptionID` (`CMD_3F7`) starts at
  `0x022377CC`; `CMD_3F8` is the reception-ID getter at `0x022377F4`.
- Overlay 55 dispatch table: `EvCmdWBTGetVictoryCount` is the separate
  `CMD_3FA` handler at `0x02237860`; this must not be relabeled as the
  Overlay-58 `CMD_3EA` wrapper.
- Text NARC `/a/0/0/5`, member 668: PWT description/menu strings used by that
  switch. Text NARC `/a/2/3/9`, member 11: the compact permanent-mode labels.
- WBT NARC `/a/2/6/1`, resource 261, 128 16-byte records in the examined build;
  the built-in family inventory uses record byte 2.
- `scripts/find_pwt_state_script.py`: static NARC scanner for the eight-record
  `CMD_3EA` sequence and nearby message IDs 113/114; it reproduces member 1280
  on both the development archive and the downloaded retail `/a/0/5/6`.
- Complete Black 2 USA/Europe retail ROM, downloaded from the Internet Archive
  item
  [`pokemon-black-version-2-usa-europe-ndsi-enhanced_202209`](https://archive.org/details/pokemon-black-version-2-usa-europe-ndsi-enhanced_202209).
  Its header/FAT extraction of `/a/0/5/6` has 1,289 members; the scanner finds
  the equivalent state-check sequence in zero-based member 1280 at offsets
  `0x3807–0x38E0`, with the message-113/114 calls at `0x3926` and `0x3958`.
  This is a public mirror source, not a legally verified user dump.

## Public references

- [Project Pokémon: B2W2 scripting thread](https://projectpokemon.org/home/forums/topic/25852-b2w2-scripting-thread/) (script-NARC extraction and command-format reference)
- [Project Pokémon RawDB: Black 2 NARC list](https://projectpokemon.org/rawdb/black2/narc.php) (retail file-system inventory; lists `/a/0/5/6` as the large script archive)
- [Project Pokémon: PWT download tournaments and reverse engineering](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [namofure/TournamentSearcher](https://github.com/namofure/TournamentSearcher) (fan-made search tool, not official Nintendo source)
- [Serebii: Champion Tournament](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [Serebii: Pokémon World Tournament overview](https://www.serebii.net/black2white2/worldtournament.shtml)
- [Serebii: Unova Leaders Tournament](https://www.serebii.net/black2white2/pwt/unova.shtml) (includes Bianca in the selectable roster)
- [Serebii: Kanto Leaders Tournament](https://www.serebii.net/black2white2/pwt/kanto.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (family names and unlock-condition reference; attribution retained in `data/in-game-tournaments.md`)
- [WikiDex: Copyrights](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) (CC BY-SA attribution/share-alike terms for text contributions)
- [Bulbapedia: Champions Tournament](https://bulbapedia.bulbagarden.net/wiki/Champions_Tournament) (built-in Champions roster reference)
- [Tdavide04/pokemon-bw2-reverse-engineering](https://github.com/Tdavide04/pokemon-bw2-reverse-engineering) (public retail symbol database; `LoadPWTTournamentTypeText` is listed at `0x021C98F5`)
- [kwsch/PKHeX: PWTRecordID](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen5/PWTRecordID.cs) (save-record labels; useful cross-check, but not assumed to be the constructor's 0–15 dispatch enum)
- [kwsch/PKHeX: PWTBlock5](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen5/PWTBlock5.cs) (16-bit PWT record access at `0x5C + 2 * id`)
- [FlagBrew/PKSM: B2W2 scripts](https://github.com/FlagBrew/PKSM-Scripts/blob/master/src/scriptsB2W2.txt) (Champion unlock writes `10` at `0x2378C`; all-record PWT payload starts at `0x2375C`)
- [ds-pokemon-hacking/PokeScriptSDK5: B2W2 Overlay 58 command table](https://github.com/ds-pokemon-hacking/PokeScriptSDK5/blob/92ae570f98e2eeb2ff1d8075edb3976e2c8b364e/yml/B2W2/Overlay%2058.yml) (public signature for `CMD_3EA`; the function brief remains TODO)

## Scope warning

`data/yy-counts.md` counts downloadable `.pwt` artifacts. It is not evidence
for the raw `YY` histogram of a named built-in cup. The built-in cup inventory
is documented separately in `data/in-game-tournaments.md`; the static menu
branch maps all ordinary built-in names for the examined development build.
Only dispatch ID 11 is left as a reserved/current-tournament branch without an
ordinary menu label. Its entry-113 wording matches the first/story Driftveil
tournament. The development script checks PWT save-record IDs
`17,18,21,20,19,22,23,24`. Independent save-layout and unlock-script evidence
resolves `CMD_3EA`'s returned value as the 16-bit PWT progress/victory count;
the script's `== 1` is an exact one-win test. The exact Overlay-58 wrapper
symbol is not recovered; Overlay 55's debug symbol `EvCmdWBTGetVictoryCount`
is a separate `CMD_3FA` handler. The retail script member is now verified
against a public
Black 2 extraction: `/a/0/5/6`, member 1280, with the same offsets listed
above. The source is retained locally only; a user-owned dump is still needed
for a legally reproducible redistribution. ID 0 is the null/error path.

The internal constructor/category evidence is documented in
`data/in-game-constructor-categories.md`. Its raw family byte is record offset
2; the constructor's category predicates and slot requests must not be
relabeled as downloadable `YY` bytes without a demonstrated data mapping.
The static menu branch now supplies that demonstrated numeric mapping for the
ordinary built-in modes. Only dispatch ID 11 remains a reserved/current-
tournament branch without an ordinary menu label; its gate is expressed in
PWT save-record state. The exact Overlay-58 wrapper symbol is not recovered,
but its returned value is resolved as the PWT progress/victory count. The
retail script member is verified as member 1280 in the downloaded retail NARC.
ID 0 is the null/error path.

The archived development artifact stores the analyzed scripts in NARC
`/a/0/5/9` (1,291 entries, including zero-based entry 1280). Public retail
file-system listings identify `/a/0/5/6` as the large B2W2 script archive, so
the downloaded complete ROM's `/a/0/5/6` has 1,289 entries and independently
matches member 1280 and the same offsets. The static scanner can be rerun on a
user-owned retail dump to confirm a regional/revision variant before
redistribution.
