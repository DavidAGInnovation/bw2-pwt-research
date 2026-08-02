# Source trail

## Primary artifacts used for this report

- Archived BW2 development build examined locally (not redistributed).
- Overlay 55 disassembly: result routine at `0x02238314`; type-chart helper at `0x02238554`; chart data at `0x022399EC`.
- Overlay 135 disassembly: WBT record conversion/packing around `0x0224208C`.
- Overlay 135 constructor/selector/shuffle: cup dispatch at `0x02241D02`, candidate selection at `0x02241704`, and common eight-position shuffle at `0x02241DB8`.
- WBT NARC `/a/2/6/1`, resource 261, 128 16-byte records in the examined build;
  the built-in family inventory uses record byte 2.

## Public references

- [Project Pokémon: PWT download tournaments and reverse engineering](https://projectpokemon.org/home/forums/topic/23084-pwt-download-tournaments/page/2/)
- [PWT RNG analysis](https://namofure.hatenablog.com/entry/2025/05/29/214716)
- [namofure/TournamentSearcher](https://github.com/namofure/TournamentSearcher) (fan-made search tool, not official Nintendo source)
- [Serebii: Champion Tournament](https://www.serebii.net/black2white2/pwt/champion.shtml)
- [Serebii: Pokémon World Tournament overview](https://www.serebii.net/black2white2/worldtournament.shtml)
- [Serebii: Kanto Leaders Tournament](https://www.serebii.net/black2white2/pwt/kanto.shtml)
- [WikiDex: Pokémon World Tournament](https://www.wikidex.net/wiki/Pok%C3%A9mon_World_Tournament) (family names and unlock-condition reference; attribution retained in `data/in-game-tournaments.md`)
- [WikiDex: Copyrights](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) (CC BY-SA attribution/share-alike terms for text contributions)
- [Bulbapedia: Champions Tournament](https://bulbapedia.bulbagarden.net/wiki/Champions_Tournament) (built-in Champions roster reference)

## Scope warning

`data/yy-counts.md` counts downloadable `.pwt` artifacts. It is not evidence
for the raw `YY` histogram of a named built-in cup. The built-in cup inventory
is documented separately in `data/in-game-tournaments.md`; it maps the
regional, Champions, and World-Leaders families for the examined development
build and reports the remaining special-mode IDs as open.

The internal constructor/category evidence is documented in
`data/in-game-constructor-categories.md`. Its raw family byte is record offset
2; the constructor's category predicates and slot requests must not be
relabeled as downloadable `YY` bytes without a demonstrated data mapping.
