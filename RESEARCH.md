# Result routine and probability model

## Decoded decision order

For the normal NPC simulation call, the routine at `0x02238314` receives two packed trainer records. It extracts priority bits from byte 0 and reads byte 1 as the category used by the type-chart helper.

The behavior is equivalent to:

```text
priorityA = (recordA.byte0 >> 4) & 7
priorityB = (recordB.byte0 >> 4) & 7

if priorityA != priorityB:
    winner = A if priorityA > priorityB else B
else:
    a_value = chart(recordA.byte1, recordB.byte1)
    b_value = chart(recordB.byte1, recordA.byte1)
    if a_value != b_value:
        winner = A if a_value > b_value else B
    else:
        winner = rng_bit()       # initial tie result

    # Normal NPC path only: this is reached only for equal priority.
    # If the current result is B, about 30% of those B results flip to A.
    if winner == B and rng_roll_times_10() >= 7:
        winner = A

# A later trainer-type override exists for special records (type 3).
# Standard Champion and Gym Leader records in the examined table use type 0.
```

The `rng_roll_times_10()` operation is implemented with the game's 64-bit RNG and integer multiply/divide sequence. The threshold is seven out of ten in the resulting quotient, hence “about 30%,” not a floating-point probability guaranteed to be exactly 30.000%.

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

## What “flip B to A” means

Suppose the initial comparison has selected B. The routine performs a second check. When that check reaches the threshold, it stores A instead of B. It does not replay a Pokémon battle and does not change the bracket; it only changes the simulated winner flag returned by this routine. If A was already selected, this particular adjustment does nothing.

For equal records:

```text
100 hypothetical calls
50 initial A results       -> remain A
50 initial B results       -> about 15 flip to A, 35 remain B
final                       A ≈ 65, B ≈ 35
```

The asymmetry belongs to the A/B positions in the call. Swapping the two records swaps which named trainer receives the advantage; it is not a hidden preference for Red, Blue, Lance, or another name.

## Examples

### Champion versus Champion

All seven standard Champion entries decode to priority 4, category 17, trainer type 0. A Red-vs-Blue call therefore follows the equal-record path: if Red is A, Red is approximately 65%; if Red is B, Red is approximately 35%. The same applies to Red-vs-Lance and every other Champion pair. The bracket generator may decide whether the pair appears and in which round, but it does not change this winner routine.

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
assignment is what produces the approximately 65/35 result.

### Champion versus standard Gym Leader

Champions decode to priority 4; standard Gym Leaders decode to priority 3. Since the priorities differ, the routine selects the Champion immediately and skips the equal-priority upside check. Thus a standard Champion-vs-Leader simulation is Champion 100% in this routine (subject to any separate special-mode code not covered by this analysis).

### Gym Leader versus Gym Leader

Both records normally have priority 3, so the type-chart fields matter. For example, Elesa's category is Electric (12) and Clay's is Ground (4). If A=Elesa and B=Clay, the chart favors B; B remains the winner about 70% and the A-slot adjustment produces Elesa about 30%. If A=Clay and B=Elesa, Clay has the advantage and remains A, so Clay is 100% in this routine.

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
to choose among them. If only Red has `YY=05`, there is no Red-versus-Steven
qualifying match whose 65/35 result decides whether Red becomes the finalist;
Red is the selected final-category opponent. The player's battle against Red
is a player battle, so `wbt_calc_result` is not used for that encounter.

The earlier illustrative full-bracket diagram that put Cynthia versus Lance or Red versus Steven before the player's later round was therefore not a faithful model of the required `YY=04/05` schedule. It is possible for the game to simulate other all-NPC matches elsewhere, but the bracket tag itself does not invoke or modify the NPC winner routine.

This bracket selection affects who the player meets and in which round. It does not give a trainer an intrinsic win advantage in an all-NPC match. When two NPC records are actually passed to `wbt_calc_result`, the priority/type/A-slot rules documented above apply independently.

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
ID 11 as the reserved/special branch without an ordinary menu label.

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
ID 10 World Leaders   ID 11 reserved/special  ID 12 Rental
ID 13 Rental Master   ID 14 Mix               ID 15 Mix Master
```

The text bank is NARC `/a/0/0/5`, member 668: lines 7–20 are the long
descriptions and lines 23–36 are the short labels. ID 11 instead selects line
113, a special message saying “this Driftveil tournament”; it has no ordinary
menu label. ID 0 is the null/error path. This static script evidence corrects
the earlier tentative assignment of ID 2 to World Leaders: ID 2 is Type Expert,
while ID 10 is World Leaders. The external retail symbol
`LoadPWTTournamentTypeText` at `0x021C98F5` is consistent with a separate text
loader, but the retail address is not treated as a development-build code
address.

The earlier scan of `CMD_3EF` arguments was misinterpreted: it is not
`EvCmdWBTSetWBTCup`. No literal `CMD_3F3`/`EvCmdWBTSetWBTCup` call with value
`11` was found in the examined script archive. Member 1277 supplies the
general menu result and description mapping. Zero-based NARC entry 1280,
sequence 7 at raw member offset `0x3807` (through `0x38E0`), calls `CMD_3EA` for PWT save-record IDs
`17,18,21,20,19,22,23,24`, increments an accumulator for each returned value
that equals `1`, then tests whether the accumulator equals `1` before selecting
messages 113 or 114. Entry 113 says “this Driftveil tournament,” matching the
documented first/story Driftveil wording. The exact gate is therefore **exactly
one** of the eight records at one, not “all eight unlocked.” This is strong
evidence that ID 11 is an introductory/story Driftveil state whose gate is
represented by PWT save-record state.

The `CMD_3EA` behavior is resolved at the save-data level: it returns the
16-bit PWT progress/victory value for the supplied record ID, so `== 1` means
exactly one recorded win. PKHeX maps the IDs to `0x5C + 2 * id` in the PWT
save block, the examined save contains values such as World Leaders `10`, and
PKSM's B2W2 scripts write `10` at `0x2378C` to unlock Champions. Overlay 55
also exposes `EvCmdWBTGetVictoryCount`/`EvCmdWBTIncVictoryCount` with a
`WBTSTAGE_WIN` assertion; its dispatch entry is the separate `CMD_3FA` handler
at `0x02237860`. The exact Overlay-58 `CMD_3EA` Nintendo symbol remains
unknown, but the returned value is not an unresolved boolean.

As a static-analysis correction, the overlay-135 switch table is a signed
halfword table at `0x02241D20–0x02241D3E` with Thumb PC base `0x02241D22`.
Evaluating the displacements routes ID 12 to `0x02241B84`, ID 14 to
`0x02241BB0`, and ID 15 to `0x02241BF4`. These addresses are now reflected in
the built-in-tournament tables; they are not inferred from the visible menu
order.

## Reproducibility and limitations

- The findings come from an archived development build, with the relevant
  script sequence now cross-checked against a complete Black 2 USA/Europe
  retail ROM. The ROM is retained locally under `rom/retail-source/`, and its
  `/a/0/5/6` extraction is retained under `rom/retail-extracted/a/0/5/6`; see
  the artifact-level README for provenance.
- In this development artifact the relevant script NARC is `/a/0/5/9`, with
  zero-based entry 1280 containing the state check. Public retail file-system
  listings use `/a/0/5/6` for the large B2W2 script archive, so the member
  number and offset have now been checked against a retail extraction. The
  retail NARC has 1,289 members and the same state-check sequence is in
  zero-based member 1280 at raw offsets `0x3807, 0x3826, 0x3845, 0x3864,
  0x3883, 0x38A2, 0x38C1, 0x38E0`, with message branches 113 and 114 at
  `0x3926` and `0x3958`. The repository scanner
  `scripts/find_pwt_state_script.py` reproduces these findings.
- No original Nintendo C/C++ source was obtained. The addresses above are disassembly locations.
- The complete retail ROM was downloaded from a public ROM mirror for local
  analysis; its legal extraction provenance is not established, and it should
  not be redistributed. A user-owned cartridge extraction remains the
  appropriate source for a legally reproducible artifact.
- Exact raw record names and IDs are not inputs to the result calculation; only the packed fields described above are read.
