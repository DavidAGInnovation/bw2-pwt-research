# Result routine and probability model

## Decoded decision order

For the normal NPC simulation call, the routine at `0x02238314` receives two packed trainer records. It extracts priority bits from byte 0 and reads byte 1 as the category used by the type-chart helper. The recovered source implementation is `branches/fes_rom/prog/src/field/wbt_calc_result.c`, function `calcWBTResult`, called by `WBTSYS_CalcResult`.

The behavior is equivalent to:

```text
priorityA = (recordA.byte0 >> 4) & 7
priorityB = (recordB.byte0 >> 4) & 7

if priorityA != priorityB:
    winner = A if priorityA > priorityB else B
elif a_affinity == b_affinity:
    winner = (rand(2) == 0)       # exact 50/50 source branch
else:
    winner = (a_affinity > b_affinity)
    if rand(10) >= 7:              # 3 of 10 source outputs
        winner = not winner        # reverse the type-advantage result

# After this, the source forces player battles: a player in A wins and a
# player in B loses. NPC-vs-NPC calls do not use that override.
```

The two RNG calls are used in different situations:

- **Equal affinities:** `GFL_STD_Rand(context, 2)` returns either `0` or `1`.
  One value selects each side, so the result is exactly 50/50. There is no
  second roll.
- **Unequal affinities:** the side with the better type matchup is selected
  first. Then `GFL_STD_Rand(context, 10)` returns a value from `0` through `9`.
  Values `0–6` (7 of 10 outcomes) keep that type-advantage winner, while
  values `7–9` (3 of 10 outcomes) reverse the result. For example, Clay's
  Ground type has the advantage over Elesa's Electric type, so Clay wins about
  70% of these simulated matches and Elesa wins about 30%. The same calculation
  applies when another Leader has the type advantage.

The source has a `PM_DEBUG`-only `DEBUG_WBT_ReverseJudgeMode` hook that can
invert an unequal-affinity result for debugging. `DEBUG_WBT_ReverseJudgeMode`
defaults to `FALSE`; this is not the normal retail behavior.

### ROM/disassembly cross-check

The examined development ROM's Overlay 55 contains the same control flow at
`0x02238314`. The priority comparison branches to the priority-only path at
`0x022383E2`; when priorities tie, the affinity comparison branches to the
equal-affinity path at `0x02238358` or the unequal-affinity path at
`0x02238386`. The equal path calls the two-way RNG and rejoins at
`0x022383EA`. Only the unequal path reaches the second RNG call at
`0x022383A8–0x022383D4`, compares its result with `7`, and toggles the stored
winner at `0x022383D6–0x022383E0`. The player override begins at
`0x022383EC`. The category-17 neutral check is also present at
`0x02238554–0x02238560`.

The retail Overlay 55 was then extracted from the retained USA/Europe ROM and
decompressed. It has overlay base `0x021E5800`; the result routine is at
`0x021E614C`, and the category-affinity helper is at `0x021E6338`. Its control
flow is the same as the development build, with the corresponding retail
branches at:

| Decision | Retail address evidence |
|---|---|
| Priority comparison | `0x021E6184` → priority path `0x021E6204` |
| Equal-affinity split | `0x021E618E`; equal path calls the two-way RNG at `0x021E6190–0x021E6198` |
| Unequal-affinity path | `0x021E61BE–0x021E61C8` |
| 30% reversal check | `0x021E61CA–0x021E61F6`, threshold `7` |
| Symmetric toggle | `0x021E61F8–0x021E6202` |
| Player override | begins at `0x021E620E` |
| Category-17 neutral check | `0x021E6338–0x021E6342` |

The compressed retail file is overlay file ID 55, ROM range
`0x0011D200–0x0011EAE0` (6,368 bytes); decompression produces 7,616 bytes.
The local decompressed artifact is
`rom/retail-extracted/overlays/055.bin`, SHA-256
`1d7ed4cc8ffb33a1bd715f621a38203f45e2a4453864a8fafb287aa5d744ad33`.
The complete retail disassembly is retained locally as
`analysis/disassembly/retail-ov55.dis`.

Therefore the recovered source, development Overlay 55, and this retail
Overlay 55 all agree on the A/B-symmetric winner routine.

### Category `17` (`0x11`) is a neutral sentinel

The type-chart helper at `0x02238554` checks for category `0x11` before it
indexes the ordinary matchup table. Its behavior is equivalent to:

```text
if categoryA == 0x11 or categoryB == 0x11:
    return 2       # neutral comparison score
```

Thus `chart(17, x)` and `chart(x, 17)` both return the same neutral score for
any category `x`. Category `17` is therefore a special neutral/sentinel value;
it is not a normal Pokémon type and is unrelated to downloadable bracket
`YY` values. Since all seven standard Champions use category `17`, Champion
pairs have no type-chart advantage and proceed to the equal-record tie path.

## What the 30% reversal means

For unequal type affinities, the source first chooses the side with the better
affinity, then performs `GFL_STD_Rand(context, 10) >= 7`. Three outcomes (`7`,
`8`, or `9`) reverse that result. This does not replay a Pokémon battle or
change the bracket; it only changes the simulated winner flag. The reversal
applies in either direction, not specifically from B to A.

For 100 hypothetical unequal-affinity calls where A has the advantage:

```text
70 A wins
30 B wins (the type-advantage result was reversed)
```

If B has the advantage, the probabilities swap. For equal affinities, the
source uses only `GFL_STD_Rand(context, 2)`, giving A and B 50% each.

## Examples

### Champion versus Champion

All seven standard Champion entries decode to priority 4, category 17, trainer type 0. Source `PokeType` defines the null/sentinel value immediately after the 16 ordinary types (17), and `BTL_CALC_TypeAff` returns the neutral score when either side is null. Champion pairs therefore have equal affinities and use the source's exact 50/50 `GFL_STD_Rand(context, 2)` branch. Red-vs-Blue and Red-vs-Lance are not name-biased; whichever name is A or B has the same 50% chance. The bracket generator may decide whether the pair appears and in which round, but it does not change this winner routine.

### Champion selection versus slot placement

The built-in Champion cup has two separate steps:

1. The cup-ID dispatch routes the Champion cup to `0x02241A88`. That path scans
   the source table and copies records whose packed flag at record offset 6 is
   set. In the examined build, exactly the seven standard Champion records are
   flagged: Blue, Lance, Steven, Wallace, Cynthia, Alder, and Red. This path
   does not use the category-selection RNG to choose a subset of Champions.
2. The common match builder then creates eight participant pointers (the player
   plus seven NPCs) and calls the shuffle routine at `0x02241DB8` with a count
   of 8. The routine performs an RNG-based permutation; subsequent code records
   the player's position and finalizes the match slots.

Therefore, the Champion roster is fixed, but the participant positions and the
player's scheduled path can change from run to run. The shuffle does not favor
Red, Blue, or any other name. It only determines which name receives the A/left
or B/right slot in an automatic NPC match; for equivalent Champions, that slot
assignment does not change the source's 50/50 result.

### Champion versus standard Gym Leader

Champions decode to priority 4; standard Gym Leaders decode to priority 3. Since the priorities differ, the routine selects the Champion immediately and skips the equal-priority upside check. Thus, a standard Champion-vs-Leader simulation is Champion 100% in this routine.

### Gym Leader versus Gym Leader

Both records normally have priority 3, so their matchup categories decide the odds. If the categories tie, either Leader wins 50% of the time. If one category has the advantage, that Leader wins about 70% of the time, while the other still has about a 30% chance. For example, Clay's Ground category has the advantage over Elesa's Electric category, so Clay wins about 70% and Elesa about 30%; reversing their A/B positions does not change those percentages.

## Bracket settings are a separate selection process

The public downloadable PWT format notes describe `YY=04` as a semifinalist
tier and `YY=05` as a finalist tier. The development-build selector in overlay
135 (`wbt_makematch.c`) makes internal category/count selection calls including
one record from category 5, one from category 4, one from category 3, and four
from category 1 for one seven-opponent construction path (the call sequence
begins around `0x02241B4C`; candidate selection is around `0x02241704`). This
is a constructor request, not proof that the built-in cups store literal
downloadable-style `YY` bytes. See `data/in-game-tournaments.md` for the
built-in scope and `data/yy-counts.md` for the separate downloadable appendix.

This establishes the important distinction:

```text
Download `YY=05`: finalist-tier candidate for the player's final path
Download `YY=04`: semifinal-tier candidate for the player's semifinal path
Download `YY=03`: flexible/whenever opponent
Download `YY=01`: filler opponent
```

For downloadable files, if several entries share a tier, the selector uses RNG
to choose among them.

This bracket selection affects who the player meets and in which round they meet. It does not give a trainer an intrinsic win advantage in an all-NPC match. When two NPC records are actually passed to `wbt_calc_result`, the source priority/type-affinity/RNG rules documented above apply independently.

## Built-in cup constructor mapping

The permanent cups use a separate constructor dispatch from the downloadable
`.pwt` role bytes. Overlay 135 reads the cup ID at `0x02241D02`, dispatches IDs
`0..15`, and uses the internal WBT table at NARC `/a/2/6/1`. In the examined
build, record byte 2 identifies the source family: `0x05` is the primary Unova
Leaders slice (13 records, plus one known wildcard at index 8),
`0x06`/`0x07`/`0x08`/`0x09` are the Kanto/Johto/Hoenn/Sinnoh slices, and `0x01`
is the seven-record Champions slice. The static menu/script mapping resolves
ID 1 for Champions, ID 2 for Type Expert, ID 3 for Download, ID 4 for
Driftveil, IDs 5–9 for the five regional Leaders cups, ID 10 for World
Leaders, IDs 12–15 for Rental/Mix and their Master variants, and leaves only
ID 11 as the source-defined Driftveil event cup (`WBTCUP_HODOMOE_EVENT`).

The full dispatch and source-record indices are
documented in [`data/in-game-constructor-categories.md`](data/in-game-constructor-categories.md)
and [`data/in-game-tournaments.md`](data/in-game-tournaments.md). These family
bytes are not downloadable `YY` values, and the number of source records is
not the same thing as the seven NPC slots selected for one run.

The development build's Japanese text archive independently names the
permanent modes. NARC `/a/2/3/9`, member 11, entries 151–162 decode in order to
Champions, Driftveil, Unova, Kanto, Johto, Hoenn, Sinnoh, World Leaders, Rental,
Rental Master, Mix, and Mix Master. The numeric linkage is recovered from the
menu script: `/a/0/5/9`, member 1277, stores the list result in `0x8023`,
passes it to `EvCmdWBTSetWBTCup` (`CMD_3F3`) at member offset `0x02E7`, and
dispatches description text by comparing the same value at offsets
`0x0B95–0x0DC0`. The neighboring reception-ID setter is `CMD_3F7`; `CMD_3EF`
is a different WBT command. The resulting
mapping is:

```text
ID 1  Champions       ID 2  Type Expert       ID 3  Download
ID 4  Driftveil       ID 5  Unova Leaders     ID 6  Kanto Leaders
ID 7  Johto Leaders   ID 8  Hoenn Leaders     ID 9  Sinnoh Leaders
ID 10 World Leaders   ID 11 Driftveil event  ID 12 Rental
ID 13 Rental Master   ID 14 Mix               ID 15 Mix Master
```

The text bank is NARC `/a/0/0/5`, member 668: lines 7–20 are the long
descriptions and lines 23–36 are the short labels. ID 11 instead selects line
113, a special message saying “this Driftveil tournament”; it has no ordinary
menu label. ID 0 is the null/error path. The static script mapping assigns ID 2
to Type Expert and ID 10 to World Leaders. The external retail symbol
`LoadPWTTournamentTypeText` at `0x021C98F5` is consistent with a separate text
loader, but the retail address is not treated as a development-build code
address.

`CMD_3EF` is a different WBT command. No literal
`CMD_3F3`/`EvCmdWBTSetWBTCup` call with value `11` occurs in the examined
script archive; member 1277 supplies the general menu result and description
mapping. ID 11 is defined by the source as:

| Cup ID | Source enum | Source enable predicate |
|---:|---|---|
| 1 | `WBTCUP_CHAMPION` | World Leaders win count `>= 10` |
| 2 | `WBTCUP_POKETYPE` | All five regional Leader win counts are nonzero |
| 3 | `WBTCUP_DOWNLOAD` | Ordinary Driftveil win count is nonzero |
| 4 | `WBTCUP_HODOMOE` | Ordinary Driftveil win count is nonzero |
| 5 | `WBTCUP_ISSYU` | `SYS_FLAG_GAME_CLEAR` is set |
| 6–9 | `WBTCUP_KANTO`…`WBTCUP_SINOU` | Unova Leader win count is nonzero |
| 10 | `WBTCUP_WORLD` | All five regional Leader win counts are nonzero |
| 11 | `WBTCUP_HODOMOE_EVENT` | Ordinary Driftveil win count is zero |
| 12 | `WBTCUP_RENTAL` | Ordinary Driftveil win count is nonzero |
| 13 | `WBTCUP_RENTALMASTER` | Rental win count nonzero and all regions cleared |
| 14 | `WBTCUP_MIX` | Ordinary Driftveil win count is nonzero |
| 15 | `WBTCUP_MIXMASTER` | Mix win count nonzero and all regions cleared |

These are the original source definitions in `prog/include/field/wbt.h` and
`prog/src/field/wbt_tool.c`, not inferred labels. The lobby script calls
`_WBT_CHECK_CUP_ENABLE` for ID 11 as `SCR_WBT_CUP_HODOMOE_EVENT`, followed by
the ordinary Driftveil ID 4. Thus the special event cup is enabled before the
ordinary Driftveil cup has a win recorded; it is not gated by the eight-record
sequence in member 1280.

The source defines the table-specific command names. Each overlay command
table starts at numeric ID 1000. In `scrcmd_wbt_table.cdat`, the third WBT
entry is `EvCmdWBTSystemCheckEnable`, so WBT `CMD_3EA` is that handler. In the
separate Join Avenue table, `EvCmdResortTalkStart` and
`EvCmdResortTalkEnd` precede `EvCmdResortGetData`, so Resort `CMD_3EA` is
`EvCmdResortGetData`. `EvCmdWBTGetVictoryCount` is a distinct WBT `CMD_3FA`
entry. The same number therefore has different symbols depending on the
active overlay/table; it is not one global Nintendo function.

The recovered Resort implementation is in
`branches/fes_rom/prog/src/field/resonance_resort/scrcmd_resort.c` and is
registered by `scrcmd_resort_table.cdat` (SWAN mirror revision 59995). Its
parameters 17–24 and `RESORT_UTIL_GetReleaseMyShop` selector order
`0,1,3,2,4,5,6,7` match the stripped Resort dispatch at
`0x02237618`/`0x021e5950`, with helper `0x02248d54`/`0x021f522c` in the
development/retail builds.

The PWT victory counters themselves are exposed by the WBT source and by
`EvCmdWBTGetVictoryCount`/`EvCmdWBTIncVictoryCount`; `wbt_tool.c` reads them
through `WBTSAVE_GetWinCount`. The eight-call sequence at member 1280 is a
Join Avenue `resort_scr.bin` sequence, not a PWT save-record gate.

The separate numeric cup-ID producer is documented in the script archive.
Member 1277 contains fifteen repeated availability blocks at offsets
`0x0616–0x07E4`. Each block calls `CMD_3EE(candidate, 0x8010)`, tests the
result for `1`, and conditionally executes `ListMenuAdd` with the candidate as
the menu UID. The first block is candidate `11`; the complete candidate order
is `11,4,5,6,7,8,9,10,1,13,15,2,12,14,3`. The resulting list UID is stored in
`0x8023` and supplied to `CMD_3F3` at `0x02E7`. Thus ID 11 is a real runtime
menu candidate when its availability predicate passes; a literal setter call
with constant `11` is neither required nor present.

The overlay-135 switch table is a signed halfword table at
`0x02241D20–0x02241D3E` with Thumb PC base `0x02241D22`.
Evaluating the displacements routes ID 12 to `0x02241B84`, ID 14 to
`0x02241BB0`, and ID 15 to `0x02241BF4`. These addresses are now reflected in
the built-in-tournament tables; they are not inferred from the visible menu
order.

## USA/Europe retail Overlay 135 and WBT-table cross-check

The complete USA/Europe retail ROM was independently extracted with the same
NARC/overlay tooling. Retail Overlay 135 (file ID 135) decompresses to 4,032
bytes at `0x021EEC80`, SHA-256
`30b48d2cc1e724470351f57fa6fa28d2844f195732737052bc9ce41e57ef98b8`. Its
corresponding constructor anchors are:

```text
candidate/category selector   0x021EEE08
category-17 affinity helper   0x021EEF90
cup dispatch                  0x021EF298
16-entry switch table         0x021EF2C0
eight-position shuffle        0x021EF344
```

The retail code retains the development behavior: category filtering is done
by packed record bits, category `0x11` is accepted as the neutral/sentinel
affinity, cup IDs `0..15` dispatch through the same 16-case structure, and the
common builder uses RNG to shuffle the eight participant positions. The
addresses and compiler stack layout are relocated, so these are behavioral
cross-checks, not claims of identical address values.

The retail file-system path for this WBT table is `/a/2/4/7`, not
`/a/2/6/1`. It is a 2,108-byte NARC with one 2,048-byte member and SHA-256
`0a32d2956f75a6e6365f292eb20e129c5247fe9ec093ca881dd469ea698d00ca`, exactly
matching the development `/a/2/6/1` table. This closes the retail record/name
mapping: the development indices in `data/champions-and-leaders.md` apply
unchanged to the examined USA/Europe retail ROM. The separate retail
`/a/2/6/1` path is a 24,052-byte NARC with 1,000 16-byte members (SHA-256
`416ddd7a37b89bcada27e977dc0a59df818ccddf4b9e47dd2f3ae39d742b5980`) and is
not the WBT roster table.

The downloadable-format notes call the second record byte `Trainer Rank`. The
recovered SWAN source makes its implementation precise: `WBTDL_MATCH.pri` is
the second byte, `WBT_TRPRI_NULL` is the explicit value 0 (“undefined”), and
downloadable setup copies `pri` into each non-player `WBTTRAINER`. The common
sorter orders trainers by this value, so `YY=00` is the lowest/unprioritized
value; the result routine likewise treats it as priority 0. Two `YY=00`
records therefore reach the equal-priority affinity/RNG path, while a
`YY=00` record loses deterministically to any record with `YY=01`–`05` in an
NPC-vs-NPC comparison. Only this USA/Europe retail ROM was available locally,
so other regional or revision ROMs have not been cross-checked.

## Reproducibility and limitations

- The findings come from an archived development build, with the relevant
  script sequence now cross-checked against a complete Black 2 USA/Europe
  retail ROM. The ROM is retained locally under `rom/retail-source/`, and its
  `/a/0/5/6` extraction is retained under `rom/retail-extracted/a/0/5/6`; see
  the artifact-level README for provenance.
- In this development artifact the relevant Join Avenue script NARC is
  `/a/0/5/9`, with zero-based entry 1280 (`resort_scr.bin`). Public retail
  file-system listings use `/a/0/5/6` for the large B2W2 script archive; its
  1,289-member extraction contains the same `resort_scr.bin` bytes and offsets.
  The repository scanner `scripts/find_pwt_state_script.py` reproduces the
  byte match; the sequence is a Join Avenue data query, not a PWT unlock
  script.
- The recovered SWAN source mirror is available locally. It identifies the
  original Resort command as `EvCmdResortGetData` and the WBT command-table
  entry at the same numeric slot as `EvCmdWBTSystemCheckEnable`; the source
  artifact is not redistributed in this repository. The binary addresses are
  build-specific dispatch cross-checks.
- Exact raw record names and IDs are not inputs to the result calculation; only the packed fields described above are read.
