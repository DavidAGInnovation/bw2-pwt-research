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

The seven opponent records in a player-facing PWT tournament carry bracket-setting bytes (`YY`). The public PWT format notes describe `YY=04` as a required semifinalist battle and `YY=05` as a required finalist battle. The development-build selector in overlay 135 (`wbt_makematch.c`) makes category/count selection calls including one record from category 5, one from category 4, one from category 3, and four from category 1 for a seven-opponent construction path (the call sequence begins around `0x02241B4C`; candidate selection is around `0x02241704`).

This establishes the important distinction:

```text
YY=05: choose/reserve an opponent for the player's final encounter
YY=04: choose/reserve an opponent for the player's semifinal encounter
YY=03: flexible/whenever opponent
YY=01: filler opponent
```

If several entries share a category, the selector uses RNG to choose among them. If only Red has `YY=05`, there is no Red-versus-Steven qualifying match whose 65/35 result decides whether Red becomes the finalist; Red is the selected final-category opponent. The player's battle against Red is a player battle, so `wbt_calc_result` is not used for that encounter.

The earlier illustrative full-bracket diagram that put Cynthia versus Lance or Red versus Steven before the player's later round was therefore not a faithful model of the required `YY=04/05` schedule. It is possible for the game to simulate other all-NPC matches elsewhere, but the bracket tag itself does not invoke or modify the NPC winner routine.

This bracket selection affects who the player meets and in which round. It does not give a trainer an intrinsic win advantage in an all-NPC match. When two NPC records are actually passed to `wbt_calc_result`, the priority/type/A-slot rules documented above apply independently.

## Reproducibility and limitations

- The findings come from an archived development build; retail BW2 verification is still desirable.
- No original Nintendo C/C++ source was obtained. The addresses above are disassembly locations.
- No ROM, overlay, or copyrighted game asset is redistributed here.
- Exact raw record names and IDs are not inputs to the result calculation; only the packed fields described above are read.
