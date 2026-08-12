# Rental Pokémon strength pools

This page documents the dedicated Pokémon-record pools used by Rental and
Super Rental / Rental Master. These are party records, not Trainer-candidate
pools; Trainer selection is documented separately in
[`generic-and-rental-records.md`](generic-and-rental-records.md).

The examined development archive `/a/2/7/1` and USA/Europe retail archive
`/a/2/5/7` are byte-identical NARCs with SHA-256
`2644c167f8a5775b5161c8e9b878255d2ae7cf5c0ec7431ae1dad257051d1110`.
They contain 1,000 sixteen-byte configured Pokémon records. The Rental builder
uses only indices `1–908`:

| Tournament | Strength tier | Inclusive indices | Records | Unique species | Records per species |
|---|---|---:|---:|---:|---:|
| Rental | Weak | `1–132` | 132 | 66 | 2 |
| Rental | Strong | `133–208` | 76 | 38 | 2 |
| Rental Master | Weak | `209–558` | 350 | 175 | 2 |
| Rental Master | Strong | `559–908` | 350 | 175 | 2 |

## Records excluded from every PWT Rental range

The remaining archive members are not an additional selectable tier:

| Indices | Records | Contents | PWT use |
|---|---:|---|---|
| `0` | 1 | Zero-filled dummy record | Never selected |
| `909–988` | 80 | Complete legendary Pokémon builds | Outside every hardcoded Rental range |
| `989–999` | 11 | Zero-filled dummy records | Never selected |

Records `909–988` are valid rather than blank or corrupt. They contain four
configured builds for each of 20 species: Articuno, Zapdos, Moltres, Raikou,
Entei, Suicune, Regirock, Regice, Registeel, Cobalion, Terrakion, Virizion,
Tornadus, Thundurus, Latias, Latios, Heatran, Cresselia, Landorus, and
Regigigas. The Rental source conversion table references these records, which
explains why the converter emitted them into the 1,000-member archive.

The runtime `getRentalRange` table nevertheless ends at index `908` for all
Weak, Strong, and All branches in both Rental tournaments. These legendary
builds are therefore retained source data but cannot be drawn by the built-in
PWT Rental builder. This is distinct from records `0` and `989–999`, which are
actually zero-filled placeholders.

“Weak” and “strong” classify complete configured records, not merely species.
A record includes the species together with its held item, moves, and other
battle parameters. The two records for a species within one tier are distinct.

The complete record-level decode is available as
[`rental-pokemon-builds.csv`](rental-pokemon-builds.csv). It lists all 908
selectable records plus the 80 valid but excluded records at `909–988`, with
their species, form, held item, four moves, nature, EV allocation, player and
opponent IV rules, possible normal abilities, gender rule, and friendship.
The excluded rows use `Excluded from PWT` in the `tournament` column and
`Not selectable` in the `tier` column; both IV columns are marked not
applicable because the PWT builder never instantiates those records. The 12
zero-filled placeholders are omitted because they are not Pokémon builds.

For ordinary Rental, the weak and strong tiers contain different species
sets. For Rental Master, both tiers contain the same 175 species, but the 350
weak records and 350 strong records are different configurations. Therefore,
a species appearing in both Rental Master tiers can still have a weaker or
stronger build.

## What each configured record controls

The source defines each 16-byte archive member as
`BSUBWAY_POKEMON_ROM_DATA`:

| Offset | Size | Field | Runtime use |
|---:|---:|---|---|
| `0x00` | 2 | Species | Copied directly. |
| `0x02` | 8 | Four moves | Copied directly. |
| `0x0A` | 1 | EV mask | Selects which of HP, Attack, Defense, Speed, Sp. Atk, and Sp. Def receive EVs. |
| `0x0B` | 1 | Nature | Copied directly. |
| `0x0C` | 2 | Held item | Copied directly. |
| `0x0E` | 2 | Form | Copied directly; all selectable records in the examined archive use form `0`. |

EVs are not stored as six individual values. The builder counts the selected
bits in the EV mask and gives each selected stat `510 / selected-stat count`,
capped at `255`; unselected stats receive `0`. Thus the common two-stat mask
produces `255/255`, while a three-stat mask produces `170/170/170`.

IVs are not stored in these records. `FBI_TOOL_MakePokemonParam` receives one
`pow_rnd` value and assigns it to all six IVs:

| Rental Pokémon owner | IV rule |
|---|---|
| Player | Always `20` in every stat (`MY_RENTAL_POWER_RND`). |
| Built-in Rental opponent | Its selected Trainer's `PowerRnd`: `8` or `20` in every stat. Priority-1 bracket fillers store `0` but cannot become the player's opponent. |
| Built-in Rental Master opponent | `20` in every stat; every eligible built-in Trainer has `PowerRnd = 20`. |

The complete Trainer-to-IV mapping, including every English Trainer name, is
in [Rental opponent IV assignments](generic-and-rental-records.md#rental-opponent-iv-assignments).

The personal RNG value is generated at runtime. The builder permits either
normal ability and then selects ability 1 or ability 2 from the generated
personality value; Hidden Abilities are not selected by this path. Gender is
also personality-derived under the species' normal gender ratio. The form is
record-controlled, not random. Friendship defaults to `255`, except that a
record containing Frustration receives friendship `0`.

### Record-level example: Milotic

Milotic illustrates why Rental Master cannot be separated into weak and
strong species lists:

| Tier | Index | Item | Moves | Nature | EVs | IVs | Ability | Gender |
|---|---:|---|---|---|---|---|---|---|
| Weak | `369` | Enigma Berry | Surf, Recover, Mirror Coat, Confuse Ray | Bold | 255 HP / 255 Defense | 20 all stats | Marvel Scale | PID-derived, 50% female |
| Weak | `544` | Leftovers | Hydro Pump, Toxic, Attract, Aqua Ring | Quiet | 255 HP / 255 Defense | 20 all stats | Marvel Scale | PID-derived, 50% female |
| Strong | `719` | Wide Lens | Hydro Pump, Blizzard, Mirror Coat, Recover | Calm | 255 Sp. Atk / 255 Sp. Def | 20 all stats | Marvel Scale | PID-derived, 50% female |
| Strong | `894` | Leftovers | Ice Beam, Rest, Sleep Talk, Surf | Impish | 255 HP / 255 Sp. Def | 20 all stats | Marvel Scale | PID-derived, 50% female |

These IV values are fixed here because the example is specifically Rental
Master. The same archive record would still receive the runtime owner's IV
value if invoked through a different code path.

## Hidden lottery mapping and party composition

The lobby does not present choices explicitly named Weak, Strong, and All.
Instead, its three visible choices are the right, middle, and left tickets.
Their order in `wbt_lobby.ev` is passed directly through the script constants
and `EvCmdWBTSetupRentalParty` to the runtime `rental_type` field:

| Visible ticket | Script value | Internal branch | Range behavior |
|---|---:|---|---|
| Right | `0` | Weak | Select only from the relevant weak range. |
| Middle | `1` | Strong | Select only from the relevant strong range. |
| Left | `2` | All | Select three strong records, then fill the remainder from the weak range. |

The selected ticket applies to both the player's offered Rental Pokémon and
the opponents' parties. The player is always offered six Pokémon before
choosing the active team, so the offer itself is:

| Ticket | Six Pokémon offered to the player |
|---|---|
| Right / Weak | 6 weak |
| Middle / Strong | 6 strong |
| Left / All | 3 strong + 3 weak |

The opponent does not receive six and then discard extras. Its party builder
requests the format's active count directly, producing:

| Ticket | Single (3) | Double (4) | Triple (6) | Rotation (4) |
|---|---|---|---|---|
| Right / Weak | 3 weak | 4 weak | 6 weak | 4 weak |
| Middle / Strong | 3 strong | 4 strong | 6 strong | 4 strong |
| Left / All | 3 strong | 3 strong + 1 weak | 3 strong + 3 weak | 3 strong + 1 weak |

Thus, under the Left/All ticket, a Single opponent receives three strong
records, but the player receives a six-Pokémon offer containing three strong
and three weak records and chooses the three used in battle. The fixed number
three is the strong portion of the All mix; it does not denote a Triple
Battle.

Selection is random within each chosen range. The party builder always
excludes a selected source record and duplicate nonzero held items; its
duplicate-species check follows the regulation-specific rule described in
[`wbt-party-selection.md`](wbt-party-selection.md).

The exact right/middle/left behavior was also recorded independently by the
[Japanese Pokémon BW2 strategy wiki](https://w.atwiki.jp/pkmnbw2/pages/33.html).
A contemporary [GameFAQs discussion](https://gamefaqs.gamespot.com/boards/661226-pokemon-black-version-2/64815086)
mentions the same three tickets and the observation that the middle ticket was
the strongest, but does not decode the underlying ranges.

## Standard Rental species

### Weak range (`1–132`)

Patrat, Venipede, Pidove, Lillipup, Litwick, Roggenrola, Cottonee, Petilil,
Mienfoo, Purrloin, Gothita, Solosis, Munna, Sandile, Tympole, Foongus, Blitzle,
Minccino, Klink, Deino, Pansage, Pansear, Panpour, Yamask, Golett, Timburr,
Ducklett, Vanillite, Ferroseed, Cubchoo, Shelmet, Snivy, Tepig, Oshawott,
Sewaddle, Woobat, Darumaka, Karrablast, Joltik, Axew, Dwebble, Tynamo, Drilbur,
Trubbish, Zorua, Deerling, Frillish, Elgyem, Pawniard, Scraggy, Rufflet,
Krokorok, Tirtouga, Tranquill, Whirlipede, Larvesta, Duosion, Lampent, Vullaby,
Herdier, Swadloon, Palpitoad, Boldore, Gothorita, Vanillish, and Archen.

### Strong range (`133–208`)

Gurdurr, Fraxure, Mienshao, Servine, Dewott, Pignite, Watchog, Zweilous,
Swoobat, Emolga, Klang, Audino, Liepard, Basculin, Maractus, Simisage,
Simisear, Simipour, Amoonguss, Eelektrik, Cinccino, Alomomola, Stunfisk,
Galvantula, Swanna, Garbodor, Scolipede, Crustle, Sawsbuck, Whimsicott,
Jellicent, Heatmor, Beheeyem, Beartic, Stoutland, Leavanny, Sigilyph, and
Bouffalant.

## Rental Master species

The weak range (`209–558`) and strong range (`559–908`) use the same species
set below. Every listed species has four configured builds: two distinct
records in the weak range and two distinct records in the strong range. Its
weak and strong builds can differ in moves, held item, nature, and EV
distribution.

Venusaur, Charizard, Blastoise, Meganium, Typhlosion, Feraligatr, Sceptile,
Blaziken, Swampert, Torterra, Infernape, Empoleon, Serperior, Emboar, Samurott,
Dugtrio, Marowak, Medicham, Quagsire, Granbull, Jynx, Mr. Mime, Lanturn,
Breloom, Forretress, Skarmory, Absol, Whiscash, Hariyama, Vespiquen, Raichu,
Dewgong, Manectric, Staraptor, Gastrodon, Skuntank, Sawk, Throh, Unfezant,
Vileplume, Victreebel, Electrode, Ludicolo, Shiftry, Exploud, Lopunny, Froslass,
Lilligant, Darmanitan, Ambipom, Cofagrigus, Golurk, Durant, Golem, Slowbro,
Weezing, Kangaskhan, Tauros, Spiritomb, Cryogonal, Druddigon, Musharna,
Scrafty, Ferrothorn, Alakazam, Slowking, Miltank, Altaria, Toxicroak,
Gothitelle, Reuniclus, Bisharp, Abomasnow, Nidoqueen, Nidoking, Cradily,
Armaldo, Rampardos, Bastiodon, Floatzel, Mismagius, Carracosta, Escavalier,
Accelgor, Zebstrika, Drifblim, Seismitoad, Poliwrath, Rapidash, Muk, Gengar,
Ampharos, Politoed, Pinsir, Scizor, Heracross, Ursaring, Houndoom, Donphan,
Wailord, Claydol, Bronzong, Drapion, Luxray, Ninetales, Machamp, Shuckle,
Roserade, Honchkrow, Gigalith, Conkeldurr, Excadrill, Krookodile, Steelix,
Weavile, Gliscor, Zoroark, Mandibuzz, Braviary, Tentacruel, Aerodactyl,
Porygon2, Lickilicky, Yanmega, Gardevoir, Gallade, Exeggutor, Starmie, Flygon,
Klinklang, Chandelure, Vaporeon, Jolteon, Flareon, Espeon, Umbreon, Leafeon,
Glaceon, Lucario, Hippowdon, Probopass, Dusknoir, Mienshao, Beartic,
Bouffalant, Aggron, Walrein, Mamoswine, Lapras, Crobat, Magnezone, Rhyperior,
Tangrowth, Porygon-Z, Vanilluxe, Eelektross, Gyarados, Snorlax, Kingdra,
Blissey, Milotic, Electivire, Magmortar, Haxorus, Togekiss, Volcarona,
Arcanine, Archeops, Dragonite, Tyranitar, Salamence, Metagross, Garchomp,
Hydreigon, and Slaking.

The lists above are unique-species summaries in first-appearance order. They
do not collapse the underlying configured records when the game performs its
random selection.

## Reproduction

With the three extracted USA/Europe retail NARCs, regenerate the complete CSV:

```sh
python3 scripts/decode_rental_pokemon.py \
  rom/retail-extracted/a/2/5/7 \
  rom/retail-extracted/a/0/0/2 \
  rom/retail-extracted/a/0/1/6 \
  --output data/rental-pokemon-builds.csv
```

The examined development `/a/2/7/1` can replace the first argument because
its contents are byte-identical. The script reads names from the retail text
archive and normal-ability and gender information from retail personal data;
neither ROM resource is redistributed by this repository.
