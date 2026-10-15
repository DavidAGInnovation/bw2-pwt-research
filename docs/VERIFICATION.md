# BW2 PWT findings verification

Reviewed on 2026-10-14. **Ready within reviewed scope.** The principal mechanics
and data are supported by the reviewed evidence. Coverage is **complete**
for the stated document and artifact scope, including all nine selected
download hashes. Every requested README, RESEARCH section, and Data page was inspected;
repetitive raw tables received full record comparisons where stated below.
The reviewed scope includes the
local artifact bundle README as well as this repository's research documents. ROMs, source archives, raw
CSV data, and the historical checksum manifest were preserved.

## Evidence and scope

The controlling evidence is the retained development ROM, the complete Black 2
USA/Europe retail ROM, and SWAN SVN revision 59995. The external development
archive and renamed `swanmirror-007.tar` exactly match the original bundle's
SHA-256 entries. The development archive passes `7z t`. Source enum and code
checks used the recovered revision, then matched consequential behavior to the
actual development and retail binaries.

- All 128 WBT rows were checked, including the seven Champion and 46 Leader
  priorities, categories and IV inputs, generic names, eligibility masks and
  candidate pools. All 15 cup enable predicates and constructor requests agree
  with the source. Built-in setup supplies the same complete AI flags.
- All 988 CSV builds were independently decoded from ROM inputs, including
  species, form, item, moves, nature, EV allocation, abilities, gender,
  friendship, pool labels and IV-rule labels. There were zero mismatches.
  The four selectable ranges and 80 excluded legendary builds agree with the
  actual range table. All 74 ace markers and eligible runtime ace species
  agree with the party notes after correcting the archive mapping.
- The source winner control flow, 64-bit LCG, seed initialization, fresh seed
  replay and six-call result order agree with the binaries. All 289 type-chart
  bytes match both builds. The 5,800 development and 3,519 retail Overlay 55
  instruction-byte records in the retained disassemblies match their binaries.
- Six retained retail NARCs and Overlays 55/135 were independently extracted
  from the complete ROM and match the retained copies. The development and
  retail WBT/Rental NARCs are byte-identical at their documented paths.
- All nine downloadable YY histograms agree with independently downloaded
  [Project Pokémon EventsGallery files](https://github.com/projectpokemon/EventsGallery/tree/master/Released/Gen%205/World%20Tournaments).
  The additional preset counts agree with the original
  [reverse-engineering post](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/).

## Shared battle AI mechanics

Checked on 2026-10-15 against the same Black 2 USA/Europe retail image.
The complete retail AI archive `/a/1/6/9` is byte-for-byte identical to the
recovered SVN revision 59995 archive: 44,400 bytes, SHA-256
`eb4caa69e2a4d0464bd38cda8b5ce6403aeb8a626e5736b0c4e578c573a668af`.
The shared Strong script's KO and relative-damage branches support the
move-scoring explanation in [champions-and-leaders.md](../data/champions-and-leaders.md#shared-move-scoring-mechanics).

Native checks identify retail Overlay 170 `0x0218045C` as the comparison
with all known moves, `0x02180870` as the KO helper, and
`0x0217F90C–0x0217F96A` as the highest-score tie selector. Overlay 167
`0x021AB954` and `0x021AB8EC` substitute Illusion's impersonated party
member in damage and type-effectiveness simulation. The damage simulation
branch sets the minimum multiplier to 85 at `0x021A5A34`. Six controlled
executions of the relevant retail bytecode confirmed ordinary damage
ranking, two- and four-move KO ties, comparison with an unavailable strongest
move, and favorable twofold/fourfold type matchups. These were bytecode
checks with controlled helper inputs, not emulator playthroughs or a full
audit of every move effect, ability, or AI routine.

## Review coverage

Counts below use scoped document, comparison and data-family units, not source
rows or an overall accuracy percentage. A zero means no remaining demonstrated
defect in that category; the reviewed scope excludes other retail regions and revisions.
These counts describe the original artifact-bundle review, including its
README; the archived component mappings remain in that local bundle.

### Documentation quality

| Category | Observed defects | Assessment |
|---|---|---|
| Usefulness and completeness | 0 / 12 | All requested documents inspected; all nine selected download hashes verified. |
| Analytical clarity | 0 / 12 | Corrected distinctions between source metadata, runtime overrides and simulated qualification. |
| Visual and interaction consistency | N/A | Static Markdown and CSV; no interactive dashboard or exported page layout. |

### Analytical correctness and robustness

| Category | Observed defects | Assessment |
|---|---|---|
| Source authority and confidence | 0 / 12 | ROM and source identities confirmed; all selected download hashes verified. |
| Value accuracy | 0 / 12 | Raw tables, CSV fields, counts and consequential code branches checked. |
| Within-chart agreement | N/A | No charts in the requested materials. |
| Complete source details | 0 / 12 | Source paths and citations corrected; original webpage files retained with matching hashes. |
| Cross-artifact consistency | 0 / 4 | Winner logic, runtime categories, party selection and source provenance reconciled. |
| Data-quality controls | 0 / 4 | WBT rows, Rental rows, download records and archive identities checked independently. |
| Conclusion support | 0 / 11 | Principal prose claims checked and corrected; CSV counted under value accuracy. |

## Reproduction

[`../verification/`](../verification/) retains the JSON results, the downloaded
PWT files and independent verification scripts. The PWT check needs only Python
and rechecks the four historical hashes, bracket counts and differences from
the GitHub copies:

```sh
python3 -m unittest discover -s tests -v
python3 verification/verify_historical_downloads.py
```

The independent Rental decoder reads the locally retained ROMs without invoking
the original CSV generator. It requires `ndspy==2.0.0` and the artifact-bundle
layout described in the research sources. Supply that local directory and a
separate output path:

```sh
python3 -m pip install -r verification/requirements.txt
python3 verification/verify_rental_independently.py \
  --artifacts /path/to/local-artifact-bundle \
  --output /tmp/rental-check.json
```

The source archive remains external; inspection uses `svnlook` against its
recovered `export/svn2/swan_mirror` repository at revision 59995. Source files
and ROM images are not included here. The JSON results record inspected hashes, ranges,
disassembly anchors and complete row comparisons.
