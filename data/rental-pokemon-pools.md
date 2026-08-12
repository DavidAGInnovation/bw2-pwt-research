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

For ordinary Rental, the weak and strong tiers contain different species
sets. For Rental Master, both tiers contain the same 175 species, but the 350
weak records and 350 strong records are different configurations. Therefore,
a species appearing in both Rental Master tiers can still have a weaker or
stronger build.

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
