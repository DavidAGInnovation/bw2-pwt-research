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

“Weak” and “strong” classify complete configured records, not merely species.
A record includes the species together with its held item, moves, and other
battle parameters. The two records for a species within one tier are distinct.

The complete record-level decode is available as
[`rental-pokemon-builds.csv`](rental-pokemon-builds.csv). It lists all 908
selectable records with their species, form, held item, four moves, nature,
EV allocation, player and opponent IV rules, possible normal abilities,
gender rule, and friendship.

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
| Built-in Rental opponent | Its selected Trainer's `PowerRnd`: `0`, `8`, or `20` in every stat. |
| Built-in Rental Master opponent | `20` in every stat; every eligible built-in Trainer has `PowerRnd = 20`. |

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

## How the `all` tier is assembled

The runtime field called `rental_type` selects the weak, strong, or all branch.
Weak and strong requests draw all entries from their corresponding range. An
all-tier request draws three records from the strong range and any remaining
records from the weak range:

| Requested count | Strong records | Weak records |
|---:|---:|---:|
| 3 | 3 | 0 |
| 4 | 3 | 1 |
| 6 | 3 | 3 |

The number three is the strong portion of the all-tier mix; it does not denote
a Triple Battle. Selection is random within the chosen range. The party
builder always excludes a selected source record and duplicate nonzero held
items; its duplicate-species check follows the regulation-specific rule
described in [`wbt-party-selection.md`](wbt-party-selection.md).

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
set below. Each range independently contains two distinct configured records
per species.

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
