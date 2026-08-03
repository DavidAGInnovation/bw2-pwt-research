# Source trail

## Primary artifacts used for this report

### Source-path convention

The recovered SWAN mirror is one local snapshot of SVN revision `59995`. Some
citations retain historical upstream SVN directory names such as
`branches/fes_rom` and `branches/upper_version`; these are paths inside that
archive, not branches of this GitHub repository. The public repository is
maintained directly on `main`. The two historical source trees are cited for
provenance only; this report does not claim that every file is identical across
them.

- Archived BW2 development build examined locally (not redistributed).
- Recovered SWAN source: `branches/fes_rom/prog/src/field/wbt_calc_result.c`
  contains `calcWBTResult` and `WBTSYS_CalcResult`, including the priority,
  type-affinity, RNG, and player-override branches. This source file is from
  local-only SWAN mirror revision `59995`.
- Overlay 55 disassembly: result routine at `0x02238314`; type-chart helper at `0x02238554`; chart data at `0x022399EC`.
- Overlay 55 ROM control-flow cross-check: priority branch `0x0223834E`
  targets `0x022383E2`; equal-affinity branch `0x02238356` targets
  `0x02238358` and rejoins at `0x022383EA`; unequal-affinity branch targets
  `0x02238386` and alone reaches the threshold/reversal sequence at
  `0x022383A8–0x022383E0`; player override begins at `0x022383EC`.
- Retail USA/Europe Overlay 55 cross-check: compressed overlay file ID 55 is
  ROM range `0x0011D200–0x0011EAE0` (6,368 bytes); decompressed base
  `0x021E5800`, size 7,616 bytes, with result routine at `0x021E614C` and
  matchup-affinity helper at `0x021E6338`. The same priority/equal-affinity,
  unequal-affinity threshold-7, toggle, and player-override branches occur at
  `0x021E6184`, `0x021E618E`, `0x021E61BE`, `0x021E61F4–0x021E6202`, and
  `0x021E620E`. Decompressed SHA-256 is
  `1d7ed4cc8ffb33a1bd715f621a38203f45e2a4453864a8fafb287aa5d744ad33`.
- Local-only retail artifacts: `rom/retail-extracted/overlays/055.bin` and
  `analysis/disassembly/retail-ov55.dis`; the ROM itself is not redistributed.
  Extraction used `ndspy` 2.0.0's `NintendoDSRom.loadArm9Overlays()[55]` and
  Thumb disassembly used Capstone 5.0.7.
- Overlay 135 disassembly: WBT record conversion around `0x022421C6` loads each
  16-byte source row and passes its byte-8 low three bits as the built-in
  priority input and byte 0 as the result category to the common record packer
  around `0x0224208C`. The built-in source-row call passes trainer-type flag
  `0`; the packer writes priority into packed byte-0 bits 4–6 and category into
  packed byte 1. Overlay 55 reads those fields at `0x0223831C–0x02238346`.
- Overlay 135 constructor/selector/shuffle: cup dispatch at `0x02241D02`, candidate selection at `0x02241704`, and common eight-position shuffle at `0x02241DB8`.
- Overlay 135 raw WBT-record predicates: `0x02241874` tests the mode mask at
  record byte 5, family selector at byte 6, and Type Expert type ID at byte 7;
  `0x02241630` compares the low three bits of record byte 8 with the requested
  internal pool. The resulting Rental/Mix candidate map is reproduced by
  `scripts/inspect_wbt_table.py` and documented in
  `data/generic-and-rental-records.md`.
- USA/Europe retail Overlay 135 cross-check: decompressed base `0x021EEC80`, size 4,032 bytes, SHA-256 `30b48d2cc1e724470351f57fa6fa28d2844f195732737052bc9ce41e57ef98b8`; corresponding selector `0x021EEE08`, Type Expert eligibility predicate `0x021EEF90`, cup dispatch `0x021EF298` with switch table `0x021EF2C0`, and common shuffle `0x021EF344`.
- Script NARC `/a/0/5/9`, member 1277: the PWT menu result (`ListMenuInitTL` at
  member offset `0x05E2`), the cup-ID setter (`CMD_3F3` at `0x02E7`, passing
  the selected work variable), and the ID-to-description switch at
  `0x0B95–0x0DC0` (the offsets include the member's four-byte prefix). The
  fifteen availability blocks at `0x0616–0x07E4` call `CMD_3EE` and then
  conditionally `ListMenuAdd`; their candidate order is
  `11,4,5,6,7,8,9,10,1,13,15,2,12,14,3`, so ID 11 is a genuine dynamic menu
  UID even though no literal `CMD_3F3 11` occurs.
- Script NARC `/a/0/5/9`, zero-based NARC entry 1280, sequence 7 at raw member
  offset `0x3807` (through `0x38E0`): a Join Avenue `resort_scr.bin` sequence
  that calls the generic command `CMD_3EA` with selectors 17,18,21,20,19,22,23,24
  and selects messages 113 or 114. Source comparison shows that this is the
  Resort command `EvCmdResortGetData`, not a PWT save-record gate.
- Recovered SWAN WBT source (SVN revision 59995):
  `prog/include/field/wbt.h` defines cup IDs 0–15, including
  `WBTCUP_HODOMOE_EVENT` at ID 11; `prog/src/field/wbt_tool.c` implements
  `checkCupEnable`, including ID 11 enabled when the ordinary Driftveil win
  count is zero; and `resource/fldmapdata/script/wbt_lobby.ev` calls
  `_WBT_CHECK_CUP_ENABLE` for each visible cup.
- Overlay 55 disassembly: `EvCmdWBTSetWBTCup` (`CMD_3F3`) starts at
  `0x02237728`; `EvCmdWBTSetReceptionID` (`CMD_3F7`) starts at
  `0x022377CC`; `CMD_3F8` is the reception-ID getter at `0x022377F4`.
- Overlay 55 dispatch table: `EvCmdWBTGetVictoryCount` is the separate
  `CMD_3FA` handler at `0x02237860`; this must not be relabeled as the
  WBT `CMD_3EA` system-enable handler.
- WBT source command table `branches/fes_rom/prog/src/field/scrcmd_wbt_table.cdat`:
  `INIT_OVERLAY_CMD(wbt)` starts at 1000, so WBT `CMD_3EA` is
  `EvCmdWBTSystemCheckEnable`; `EvCmdWBTGetVictoryCount` is `CMD_3FA`.
- Source `branches/fes_rom/prog/src/field/scrcmd_wbt_st.c` wraps
  `WBTTOOL_CheckCupEnable` and `WBTTOOL_CheckCupUnlock` for script calls.
- Join Avenue Overlay 58/59 dispatch cross-check: Resort `CMD_3EA` enters the
  Overlay-59 subcommand dispatcher at `0x02237618` (development) /
  `0x021e5950` (retail). Cases 17–24 route to the common helper at
  `0x02248d54` (development) / `0x021f522c` (retail), with selectors
  `0,1,3,2,4,5,6,7`. The recovered source names this Resort command
  `EvCmdResortGetData`; its command-table entry is `EV_SEQ_RESORT_GET_DATA`.
- Recovered original source (local-only): SWAN mirror SVN revision `59995`,
  extracted from `rom/original-builds/swanmirror.tar`. The relevant files are
  `branches/fes_rom/prog/src/field/resonance_resort/scrcmd_resort.c` (function
  `EvCmdResortGetData`, including cases 17–24),
  `branches/fes_rom/prog/src/field/resonance_resort/scrcmd_resort_def.h`
  (the named parameter constants), and
  `branches/fes_rom/prog/src/field/resonance_resort/resort_people_def.h`
  (the shop-type values used by the helper calls), and
  `branches/fes_rom/prog/src/field/scrcmd_resort_table.cdat` (the
  `EV_SEQ_RESORT_GET_DATA` registration). The shared
  `resource/fldmapdata/script/scrcmd_table/def_table_macro.h` defines
  `INIT_OVERLAY_CMD` as command base `1000`; the table's two preceding entries
  therefore place `EvCmdResortGetData` at `1002` (`0x3EA`) exactly. The source
  is used for symbol and constant identification and is not copied into this
  repository. The same numeric slot is table-specific: WBT `CMD_3EA` is
  `EvCmdWBTSystemCheckEnable` in `scrcmd_wbt_table.cdat`.
- Text NARC `/a/0/0/5`, member 668: PWT description/menu strings used by that
  switch. Text NARC `/a/2/3/9`, member 11: the compact permanent-mode labels.
- Development WBT NARC `/a/2/6/1`, resource 261, one 2,048-byte member with
  128 16-byte records; the built-in family inventory uses the byte at
  zero-based record offset 6.
- USA/Europe retail WBT NARC `/a/2/4/7`: 2,108 bytes, one 2,048-byte member,
  SHA-256 `0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`,
  exactly matching the development table.
- USA/Europe retail `/a/2/6/1`: a different 24,052-byte NARC with 1,000
  16-byte members, SHA-256
  `416ddd7a37b89bcada27e977dc0a59df818ccddf4b9e47dd2f3ae39d742b5980`; it is
  not used for the WBT roster mapping.
- `scripts/find_pwt_state_script.py`: static NARC scanner for the Join Avenue
  `CMD_3EA` sequence and nearby message IDs 113/114; it reproduces Resort
  member 1280 on both the development archive and the downloaded retail
  `/a/0/5/6`.
- `scripts/find_pwt_menu_builder.py`: static NARC scanner for member 1277's
  fifteen `CMD_3EE` availability blocks and matching `ListMenuAdd` UIDs; it
  reproduces candidate UID 11 and the full candidate order in both archives.
- Complete Black 2 USA/Europe retail ROM, downloaded from the Internet Archive
  item
  [`pokemon-black-version-2-usa-europe-ndsi-enhanced_202209`](https://archive.org/details/pokemon-black-version-2-usa-europe-ndsi-enhanced_202209).
  Its header/FAT extraction of `/a/0/5/6` has 1,289 members; the scanner finds
  the equivalent state-check sequence in zero-based member 1280 at offsets
  `0x3807–0x38E0`, with the message-113/114 calls at `0x3926` and `0x3958`.

## Public references

- [Project Pokémon: B2W2 scripting thread](https://projectpokemon.org/home/forums/topic/25852-b2w2-scripting-thread/) (script-NARC extraction and command-format reference)
- [Project Pokémon RawDB: Black 2 NARC list](https://projectpokemon.org/rawdb/black2/narc.php) (retail file-system inventory; lists `/a/0/5/6` as the large script archive)
- [Project Pokémon: PWT download tournaments and reverse engineering](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis](https://namofure.hatenablog.com/entry/2025/05/29/214716)

The Project Pokémon PWT notes identify byte 1 of a downloadable bracket record
as `Trainer Rank` and provide the observed placement labels for values 01–05.
The recovered SWAN source mirror defines the value: byte 1 is
`WBTDL_MATCH.pri`, and `WBT_TRPRI_NULL = 0` is the source-defined undefined/null
priority. `wbt_system_lobby.c` copies it into `WBTTRAINER.pri`,
`wbt_makematch.c` sorts by it, and `wbt_calc_result.c` compares it before the
affinity/RNG branch. The source mirror is SVN revision 59995; `branches/upper_version`
is the historical upstream SVN path retained in the local archive, not a branch
of this GitHub repository. The source is retained locally under the research
artifact and not redistributed here.

Only a USA/Europe retail ROM was available for the retail cross-check in this
repository. Japanese, Korean, and other regional/revision ROMs remain outside
the verified evidence set.
- [namofure/TournamentSearcher](https://github.com/namofure/TournamentSearcher) (fan-made search tool, not official Nintendo source)
- [Serebii: Champion Tournament](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [Serebii: Pokémon World Tournament overview](https://www.serebii.net/black2white2/worldtournament.shtml)
- [Serebii: Unova Leaders Tournament](https://www.serebii.net/black2white2/pwt/unova.shtml) (public roster reference; it lists Bianca, contrary to the source predicate, which is authoritative for the examined build)
- [Serebii: Kanto Leaders Tournament](https://www.serebii.net/black2white2/pwt/kanto.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (family names and unlock-condition reference; attribution retained in `data/in-game-tournaments.md`)
- [WikiDex: Copyrights](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) (CC BY-SA attribution/share-alike terms for text contributions)
- [Bulbapedia: Champions Tournament](https://bulbapedia.bulbagarden.net/wiki/Champions_Tournament) (built-in Champions roster reference)
- [Tdavide04/pokemon-bw2-reverse-engineering](https://github.com/Tdavide04/pokemon-bw2-reverse-engineering) (public retail symbol database; `LoadPWTTournamentTypeText` is listed at `0x021C98F5`)
- [kwsch/PKHeX: PWTRecordID](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen5/PWTRecordID.cs) (save-record labels; useful cross-check, but not assumed to be the constructor's 0–15 dispatch enum)
- [kwsch/PKHeX: PWTBlock5](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen5/PWTBlock5.cs) (16-bit PWT record access at `0x5C + 2 * id`)
- [FlagBrew/PKSM: B2W2 scripts](https://github.com/FlagBrew/PKSM-Scripts/blob/master/src/scriptsB2W2.txt) (Champion unlock writes `10` at `0x2378C`; all-record PWT payload starts at `0x2375C`)
- [ds-pokemon-hacking/PokeScriptSDK5: B2W2 Overlay 58 command table](https://github.com/ds-pokemon-hacking/PokeScriptSDK5/blob/92ae570f98e2eeb2ff1d8075edb3976e2c8b364e/yml/B2W2/Overlay%2058.yml) (public command signature; the recovered source supplies the symbol/behavior distinction)

## Scope warning

`data/yy-counts.md` counts downloadable `.pwt` artifacts. It is not evidence
for the raw `YY` histogram of a named built-in cup. The built-in cup inventory
is documented separately in `data/in-game-tournaments.md`; the static menu
branch maps all ordinary built-in names for the examined development build.
ID 11 is `WBTCUP_HODOMOE_EVENT`, the Driftveil event cup. `wbt_tool.c` enables it when
the ordinary Driftveil win count is zero; ID 4 is enabled when that count is
nonzero. Member 1277 includes UID 11 in the dynamic availability/menu
candidate list, and the selected UID is passed to `EvCmdWBTSetWBTCup`.
The eight-call sequence in member 1280 is Join Avenue `resort_scr.bin`, not a
PWT save-record gate. Source names are table-specific: WBT `CMD_3EA` is
`EvCmdWBTSystemCheckEnable`, Resort `CMD_3EA` is `EvCmdResortGetData`, and WBT
`EvCmdWBTGetVictoryCount` is `CMD_3FA`. The retail member is verified against
the Black 2 extraction `/a/0/5/6`. ID 0 is the null/error path.

The internal constructor/category evidence is documented in
`data/in-game-constructor-categories.md`. Its raw family byte is the byte at
zero-based record offset 6; the constructor's category predicates and slot
requests must not be relabeled as downloadable `YY` bytes without a demonstrated
data mapping.
The static menu branch supplies the numeric mapping for ordinary built-in
modes and dynamically includes candidate UID 11 when its `CMD_3EE` availability
check passes. ID 11 is the source-defined Driftveil event cup. The recovered
source distinguishes WBT
`EvCmdWBTSystemCheckEnable` (`CMD_3EA`) from Resort `EvCmdResortGetData`
(`CMD_3EA`) and WBT `EvCmdWBTGetVictoryCount` (`CMD_3FA`).

The archived development artifact stores the analyzed scripts in NARC
`/a/0/5/9` (1,291 entries, including zero-based entry 1280). Public retail
file-system listings identify `/a/0/5/6` as the large B2W2 script archive, so
the downloaded complete ROM's `/a/0/5/6` has 1,289 entries and independently
matches member 1280 and the same offsets. The static scanner can be rerun on
another retail extraction to confirm a regional/revision variant.
