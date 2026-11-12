# PWT text members

The USA/Europe retail text NARC `/a/0/0/2` holds the English PWT strings used
by the lobby, the announcer and the opponents. Members 409 and 410 (names and
class labels) are already described in
[`generic-and-rental-records.md`](generic-and-rental-records.md#retail-pwt-names-and-result-fields);
this page records the layout of the two dialogue members so that lines can be
tied to trainer-list rows. Project Pokémon's RawDB renders the same members as
[`msg/406.php`](https://projectpokemon.org/rawdb/black2/msg/406.php) and
[`msg/407.php`](https://projectpokemon.org/rawdb/black2/msg/407.php).

## Member 407: trainer dialogue

1,008 entries in 126 blocks of eight. Within a block:

| Offset | Spoken when |
|---:|---|
| 0 | Before the first-round battle |
| 1 | Before the second-round battle |
| 2 | Before the final |
| 3 | After losing to the player |
| 4 | After beating the player |
| 5 | In the lobby afterwards, having lost to the player (prefixed with the speaker's name) |
| 6 | In the lobby afterwards, having beaten the player (prefixed with the speaker's name) |
| 7 | The announcer's introduction of this trainer |

The three pre-battle entries are variants of one speech that grow with the
round (Chili's third entry opens "The final round of the tournament...",
Maylene's second and third open "Nice to see you again"). This per-round
variation is the behaviour fan wikis describe as the quotes "seeming to vary".

Block order:

| Blocks | Trainer-list rows | Notes |
|---|---|---|
| 0–52 | 0–52 | Same order as the name table: Cheren, Roxie, Burgh, Elesa, Clay, Skyla, Drayden, Marlon, Bianca, Chili, Cress, Cilan, Lenora, Brycen, Blue, Lance, Steven, Wallace, Cynthia, Alder, then the Kanto, Johto, Hoenn and Sinnoh Leaders through Volkner. |
| 53–54 | — | Complete but unused sets for Hilbert and Hilda ("Meet Hilbert, the Trainer some claim to be the strongest of all!"). |
| 55 | — | The player, introduced through `VAR(256, 1)`. |
| 56 | 56 | Second Cheren row (Driftveil event). |
| 57 | 57 | Colress. |
| 58–77 | 58–77 | Type Expert and generic Driftveil trainers (Castor through Destiny). |
| 78–124 | 0–13, 20–52 | Rental/Mix variants of the Unova, Kanto, Johto, Hoenn and Sinnoh rows' lines ("How will he battle with rental Pokémon? Cheren, what will you do?!"), in name-table order. |
| 125 | 53 | Red, whose seven lines are "...", "...!", "...?", "...!!" and "...?!". |

Row 53 (Red) is therefore the only battling row whose dialogue block does not
share its row number. Morty's introduction (block 30, entry 7: "The mystic
seer of the future! What he sees is his victory?!") is the only one that does
not contain the trainer's name.

## Member 406: announcer

33 entries. `VAR(315, 0)` is the tournament name and `VAR(256, n)` a trainer
name.

| Entries | Content |
|---|---|
| 0–4 | Tournament title, "These are the Pokémon Trainers who entered this tournament!", "The … starts now!", "Let's move on to the next battle!", "Which Trainer will win the …?" |
| 5–7 | Round openers: "The first round... A vs. B!", "The second round...", "The final round...". |
| 8–12 | Result calls for a one-sided win ("That was a lopsided battle!", "… was never in any danger."). |
| 13–19 | Result calls for a clear but contested win ("The winner of this thrilling game is …"). |
| 20–24 | Result calls for an even match ("They were evenly matched!", "It was a jaw-dropping seesaw match!"). |
| 25–27 | Result calls styled for the final ("Is this the showdown at the summit?", "This battle will go down in history!"). |
| 28–31 | Come-from-behind calls ("What a come-from-behind victory!", "… turned the tide and won!"). |
| 32 | "The tough Trainer, cool in a pinch but hot as fire, is none other than …!" |

The grouping above is by wording. The code that selects one of entries 8–32
after a battle was not traced, so the thresholds that map a battle's outcome
to a group are not established here.
