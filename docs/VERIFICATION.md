# BW2 PWT findings verification

Reviewed on 2026-10-14. **Ready within reviewed scope.** The principal mechanics
and data are supported after the corrections below. Coverage is **complete**
for the stated document and artifact scope, including all nine selected
download hashes. Every requested README, RESEARCH section, and Data page was inspected;
repetitive raw tables received full record comparisons where stated below.
The corrections are documentation changes. The reviewed scope includes the
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

## Corrected mechanics and evidence

1. **Rental and Mix category override.** The original generic-records page
   traced record conversion but missed the later `WBTSYS_SetupTrainer`
   overwrite. All participants in cup IDs 12–15 receive neutral category 17.
   Equal-priority NPC results in these modes are 50/50, including named Leaders;
   their stored type advantages do not apply. Different priorities still give
   a deterministic win to the higher value. **Fixed:** the README, RESEARCH,
   generic-record and Leader explanations now distinguish source fields from
   final runtime categories. Evidence: `wbt_system_lobby.c:254–265`, development
   Overlay 135 `0x022424DE–0x022424FC`, retail `0x021EF8D0–0x021EF8EE`.

2. **Player override and bracket qualification.** The pseudocode incorrectly
   said player B loses. `upside_win = FALSE` means A loses and player B wins.
   The bracket notes also said the player directly battles the top-ranked
   candidate, although that candidate must survive the opposite half's NPC
   matches. **Fixed:** boolean semantics and survival conditions are explicit.
   Evidence: `wbt_calc_result.c:198–206`, result pass `:271–307` and opponent
   lookup `:76–146`; placement in `wbt_makematch.c:698–713`.

3. **Priority sort behavior.** Equal-priority records do not necessarily retain
   their shuffled order. Nonadjacent swaps with stronger records can reverse
   them: `[2A, 2B, 3C]` becomes `[3C, 2B, 2A]`. **Fixed:** the bracket notes
   describe the actual exchange sort and clarify how multiple priority-5
   entries can displace priority 4. Evidence: `wbt_makematch.c:679–690` and
   development `0x02241EDA–0x02241F32`. When all NPC priorities are equal,
   including the Champion cup, no sorting swaps occur.

4. **Rival party exception.** The claim that every unmarked Trainer uses the
   WBT random chooser omitted the event Rival. `WBTSYS_SetupEnemyParty`
   instead selects ordinary Trainer ID 368, 369 or 370 according to the
   player's starter. The first Pokémon is respectively Pignite, Dewott or
   Servine; the party is stored in a fixed order. **Fixed:** normal-builder
   coverage and the Rival exception are documented separately. Evidence:
   `wbt_battle.c:666–681,786–807`, development Overlay 134
   `0x0224389E–0x022438B0`, retail `0x021F040E–0x021F0420`, and ordinary retail
   Trainer archives `/a/0/9/1` and `/a/0/9/2`.

5. **Party archive and address citations.** Fixed-ace indices read the runtime
   normal `wbt1n_pd`/`wbt2n_pd`/`wbt3n_pd` archives, rather than the generated
   `a_pd` artifacts. The Rental range pointers are literal-pool words at
   `0x0223949C` and `0x022394A0`, pointing to `0x0223A3EC`/`0x0223A3EE`.
   The previous addresses were misleading instruction decodes of data.
   **Fixed:** citations and the dummy Trainer-member offset are corrected;
   all eligible ace species still match.

6. **Provenance and scope.** Source archives moved to the sibling
   `original-builds/TeraLeak 13_10_2024` directory; their identities were
   verified against the historical manifest. The Unova download hash omitted
   two characters and is now corrected to the independently verified 64-character
   SHA-256. **Fixed:** stale paths and that hash. The NPC-only restriction for
   IDs 78–127 now explicitly applies to normal built-in construction; custom
   downloads can override priorities. The manifest was regenerated for current
   local contents, preserving the previous manifest separately.

## Remaining limits

The four historical hashes questioned during the first pass are now verified
against their exact original webpage downloads: corrected English Junior,
Master and Senior, and Japanese Legendary Rotation. Each is 4,884 bytes;
its SHA-256 exactly matches the documented value, and its bracket histogram
matches both the documentation and the corresponding GitHub copy.

The normal browser download controls supplied the original files. Their
whole-file differences from the GitHub copies occur only after the bracket
records, at offsets `0x1214`, `0x1218–0x12FF`, and/or `0x1304`, depending on
the file. The historical hashes require no correction. The four original
files and a reproducible hash/comparison check are retained under
`verification/`.

Only the development build and one Black 2 USA/Europe retail image were checked.
White 2 retail and other regions/revisions have not been independently verified.
The RNG probabilities describe the routine's branch behavior; for a fixed seed
and ordered participant list, outcomes are deterministic. No emulator battle
playthrough was performed.

The historical gzip source copy was not found. File-integrity checks cover
the local artifact bundle. Its ROMs, source archives and manifests are local
evidence and are not redistributed in this repository.

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
and ROM images are not included here. Numeric source line references above
refer to that revision. The JSON results record inspected hashes, ranges,
disassembly anchors and complete row comparisons.
