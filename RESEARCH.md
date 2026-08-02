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

### Champion versus standard Gym Leader

Champions decode to priority 4; standard Gym Leaders decode to priority 3. Since the priorities differ, the routine selects the Champion immediately and skips the equal-priority upside check. Thus a standard Champion-vs-Leader simulation is Champion 100% in this routine (subject to any separate special-mode code not covered by this analysis).

### Gym Leader versus Gym Leader

Both records normally have priority 3, so the type-chart fields matter. For example, Elesa's category is Electric (12) and Clay's is Ground (4). If A=Elesa and B=Clay, the chart favors B; B remains the winner about 70% and the A-slot adjustment produces Elesa about 30%. If A=Clay and B=Elesa, Clay has the advantage and remains A, so Clay is 100% in this routine.

## Brackets are a separate RNG process

Tournament construction uses RNG and bracket-placement tiers. Same-tier candidates can be selected randomly, while records marked as semifinalist/finalist are constrained to later positions. This answers “will Red and Blue meet, and when?” It does not override the result routine above.

## Reproducibility and limitations

- The findings come from an archived development build; retail BW2 verification is still desirable.
- No original Nintendo C/C++ source was obtained. The addresses above are disassembly locations.
- No ROM, overlay, or copyrighted game asset is redistributed here.
- Exact raw record names and IDs are not inputs to the result calculation; only the packed fields described above are read.

