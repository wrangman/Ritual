# Ritual

## Arbetssätt

- Grundnivån av spelet (det som behövdes för kursen) skrev användaren själv. Från 2026-11-18 skriver Claude koden för mer komplicerade saker och grafiken. Eleverna får också använda AI till sådant. Koden ska fortfarande vara lätt att läsa och visa för elever: tydliga namn, svenska kommentarer som förklarar *varför*, och samma stil som resten av projektet.
- Sluta ge snabblösningar. Ge alltid bästa praxis och absolut bästa OOP.
- Basera designförslag på etablerade källor (designmönster, hur riktiga kortspelsmotorer är byggda) och ange källorna. Gissa inte. Skilj tydligt på vad källan faktiskt säger och vad som är din egen tillämpning på projektet.
- Tänk igenom ansvarsfördelning och relationer mellan klasser innan du föreslår kod. Fråga om designbeslut hellre än att gissa.
- Spelinnehåll (kortnamn, specialtexter m.m.) och kod skrivs på engelska. Kommentarer i koden skrivs på svenska, eftersom det är bra för eleverna. Docstrings överst i filerna är på engelska.
- Arv bara när beteendet faktiskt skiljer sig. Sammansättning (en spelare *har* en lek, en lek *innehåller* kort) är lika viktig som arv.

## Vad vi bygger

Ett Lovecraft-inspirerat kortspel i Python (kursen Prog2), spelat i terminalen.

Hjälten är den som utför ritualen. Den har två mätare: ❤️ hälsa (30) och ☩ ritual (mål preliminärt 15, ska provas i spel). Båda ska hållas så höga som möjligt. Motståndaren kan störa på två sätt: sänka ens ritual eller skada hjälten.

Två vägar till seger: bygg klart sin ritual, eller ta sig förbi motståndarens armé och slå ut hjälten (Guard skyddar, som Taunt i Hearthstone). När motståndarens bräde är tomt anfaller man hjälten. Inspiration: Android: Netrunner (agenda points eller flatline) och Hearthstone (hjälte med hälsa, Taunt).

Strategin är att balansera: försvara sin ritual och sin hjälte, öka ritualen, och ha både försvarande och anfallande kort.

**Vinstvillkor** (man vinner om något av dessa gäller):
1. Man har nått sitt ritualmål och har det kvar i början av sin nästa tur, alltså efter att motståndaren har fått svara under sin tur (se Ritual).
2. Motståndarens hjälte har 0 hälsa.
3. Motståndaren är utplånad: inga kort på brädet och inga kort kvar (varken i hand eller lek). *Oklart om detta ska finnas kvar.*
4. Man har byggt upp mer ritual än motståndaren. *Oklart om detta ska finnas kvar.*

Man vinner INTE genom att motståndaren har noll ritual.

Man kan förlora på sin egen effekt, till exempel om De Vermis Mysteriis slår ut den egna hjälten (som Life Tap/Hellfire i Hearthstone). Om båda vinner samtidigt blir det **oavgjort**, som i Hearthstone. I koden: `Game.has_won(player, opponent)`, `is_over()` och `determine_winner()` (ger `None` vid oavgjort).

### Fraktioner

Beskrivna i `README.md` – läs den innan du frågar om fraktionerna. Hjältebilder finns i `factions/heroes/`.

Varje fraktion har sin egen hjälte, sina egna kort och sina egna skills/förmågor.

- **The Deep Ones**: hjälte The Dagon King. Swarm och förvandling: svaga ensamma, farliga i grupp, kan förvandla mänskliga kort till djupdykare.
- **Ghouls**: hjälte Morrigan Upton. Kyrkogård: blir starkare när pjäser dör, kan äta kort i gravhögen och stjäla deras stats och förmågor.
- **Shoggoths**: hjälte Ur-Shoggothen. Ramp och absorption: dyra, enorma monster som växer och absorberar närliggande pjäser.
- **The Academics**: hjälte Dr. Henry Armitage. Spells och kunskap: drar mycket kort, Discover via förbjudna böcker, tar skada eller tappar förstånd av stark magi.
  - Academics identitet är att skydda: deras förmågor ska hålla de sköra figurerna och ritualkorten vid liv. Ghouls tål mycket på brädet, Academics överlever genom magi.
  - Armitages hjälteförmåga är **The Eleventh Seal** (`HeroAbility.ELEVENTH_SEAL` i `hero.py`): "One of your ritual cards cannot be damaged until your next turn, but all your other cards take 2 damage." Namnet bygger på talet 11 i anti-kosmisk satanism, där 11 är porten ut ur kosmos till urkaoset. Effekten är inte byggd än.

### Card (`card.py`)

Fyra klasser, eftersom figurer, ritualkort och spells beter sig olika (figurer stannar på brädet, spells används en gång):

- `Card` är grundklassen med det som alla kort har: `faction`, `name`, `special`, `rarity`, `cost`. `ritual` ligger i `CreatureCard`, eftersom bara kort på brädet ger ☩ (flyttat 2026-11-19). Den skapas inte direkt; `short()` kastar `NotImplementedError`.
- `CreatureCard(Card)` är en figur på brädet. Den lägger till `attack_name`, `attack`, `magic`, `health`, `max_health` och `buffs` (en `BuffList`). Getters som `get_attack()` räknar in buffarna; fälten är grundvärdena. Använd alltid getters, inte fälten direkt, när värdet ska visas eller räknas med.
- `RitualCard(CreatureCard)` är ett ritualkort som inte kan anfalla, se Ritual.
- `SpellCard(Card)` är en spell som spelas från handen. **Spells har inga stats (som i Hearthstone, ändrat 2026-11-19, användarens beslut).** Den lägger bara till `effect`; talet står i effekten (`DamageOneEnemy(7)`) och i texten i `special` ("Deals 7 magic damage to one enemy"). Handen visar bara `(kostnad) Namn (Spell)` och texten.
- Alla tre har getters och setters för sina fält. Det är medvetet: kort påverkar varandras stats under spelet, och en magiker ska i framtiden kunna trolla fram påhittade kort, till exempel ett spöke av ett annat kort.
- `FactionName` är en Enum i `card.py` (GHOULS, ACADEMICS, SHOGGOTHS, DEEP_ONES). Kortets `faction` och `Faction.name` är ett `FactionName`, aldrig en sträng. Kortet känner bara till fraktionens namn, inte `Faction`-objektet, så att beroendet bara går åt ett håll (`Faction` → `Card`). Visa texten med `.value`.
- `Rarity` är en Enum i `card.py` (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY). Standard är `Rarity.COMMON`.
- `Special` är en Enum i `card.py`. Namnet (t.ex. `DEVOUR`) säger vilken förmåga det är, värdet är texten spelaren ser. `special=None` betyder ingen förmåga.
- `__str__` ger full visning med ikoner: ⚔️ attack, 🪄 magic, ❤️ health, ☩ ritual (🛡️ armor bara på hjälten).
- `short()` ger kompakt visning för brädet: `Namn [⚔️ 3 ❤️ 4 ☩ 3]`. ⚔️ och 🪄 visas bara om värdet är större än 0. Mellanslaget efter ikonen behövs: terminalen i VS Code ritar ⚔️, ❤️ och 🛡️ två rutor breda men räknar dem som en, så utan mellanslag hamnar siffran ovanpå ikonen. ☩ har också ett mellanslag (provat utan 2026-11-18, det blev för tätt). Ett mellanslag mellan stats (två provades, det var inte bättre).
- Koden använder 3 mellanslags indrag.

### Hjälte (`hero.py`)

- `Hero` är en egen klass och inte ett `Card`: den ligger inte i leken, spelas inte och har ingen rarity. (Källa: Fireplace, en Hearthstone-motor i Python, har `Hero` och `Minion` som skilda klasser.)
- Fält: `name`, `health` (30), `max_health`, `armor` och `magic` (0 från början), `ritual` (börjar på 0), `buffs` (en `BuffList`, t.ex. Seal of Apep). Ritualmålet ligger kvar i `Faction`.
- `add_ritual()` och `lose_ritual()` (aldrig under 0, och ingenting händer om ritualen är skyddad).
- Hjälteförmågorna (Feast of Graves, The Eleventh Seal) är **inte byggda** än.
- Hjälten har magic så att den kan vara mål för spells precis som ett kort.
- **Bara hjälten har armor (byggt 2026-11-19, användarens beslut),** som i Hearthstone, där figurer inte har armor. Men den fungerar inte som i Hearthstone (där armor är extra health): armor dras av från varje anfall, och **nöts med 1 för varje träff**, även en helt blockerad. 🛡️ 2 och två slag med ⚔️ 3: först 3 − 2 = 1 skada och 🛡️ 1, sedan 3 − 1 = 2 skada och 🛡️ 0. Spells går inte mot armor (🪄 tar emot dem) och nöter den inte. I koden: `Hero.damage_from_attack(attack)`, `Hero.take_hit(damage)` (skada + nötning), `Hero.gain_armor(n)`, effekten `GainArmor(n)`.
  - **Inget tak i koden,** men en designregel för korten: Ghouls spells ger hjälten högst 2 armor, Academics spells högst 3. Ett senare kort får ge mer om vi vill.
  - Bone Ward (Ghouls) ger hjälten 2 armor.
- Varje spelare har en egen hjälte (sammansättning: `Player` har en `Hero`), eftersom hjältens värden ändras under spelet.
- Hjälteförmågor är enumen `HeroAbility` i `hero.py`, skild från kortens `Special`. Samma mönster: namnet säger vilken förmåga, värdet är texten.
- Morrigan Upton (Ghouls): **Feast of Graves** – "Eat a card in your graveyard: one of your cards gains its attack and health".

### Terminalen (`terminal_ui.py`)

- All visning och inmatning i terminalen ligger i klassen `TerminalUI` i `terminal_ui.py`. Korten och spelarna vet inget om terminalen (separation of concerns, som i Model-View-Controller). `Player` gör aldrig `print` eller `input`.
- `Game` får sitt gränssnitt utifrån: `Game(player1, player2, ui)`. `Game` använder `ui` bara för att **visa**, med en enda metod: `show_event(event)`. **Valen** görs av spelarens controller (se AI och controllers). En mänsklig spelares `HumanController` frågar via `TerminalUI` (`choose_move(game, player, moves)`, `choose_card`, `choose_mulligan`).
- **Gränssnittets metoder (stabil lista, 2026-11-20):** `show_event`, `choose_move`, `choose_card`, `choose_mulligan`. Ett `PygameUI` ska ha exakt dessa.
- **Händelser (byggt 2026-11-20, `event.py`):** `Game` berättar vad som hände med händelseobjekt, och gränssnittet bestämmer hur det visas (Observer-mönstret, Gang of Four; MetaStone har händelser som `TurnStartEvent`, `PhysicalAttackEvent`, `DamageEvent`). Tre sorter, så att ett grafiskt gränssnitt vet vad det ska göra:
  - `MoveEvent` – ett drag: `CardPlayed`, `AttackMade`, `CardSacrificed`. Animeras och hamnar i listan över senaste drag (som ikonlistan till vänster i Hearthstone).
  - `ChangeEvent` – vad draget ändrade: `StatChanged`, `StatusChanged`, `RitualChanged`, `ResourceChanged`, `CardDied`, `CardEnteredBoard` (varifrån: hand, deck, graveyard, nowhere), `CardReturnedToHand`, `CardEaten`, `CardsDrawn`, `CardsBurned`, `NothingChanged`. Ren grafik: siffrorna på porträttet ändras efter smällen.
  - `NoticeEvent` – sådant man ska lägga märke till: `TurnStarted`, `TurnEnded`, `GotTrinket`, `MulliganDone`, `StressDamage`, `DrawBurned`, `RitualNearlyComplete`, `GameWon`, `GameDrawn`. Visas i en ruta en stund.
  - Alla händelser har `describe()` (en textrad). Terminalen skriver den; en konsol (som i Quake) i grafiken kan visa samma rader. Händelserna har de riktiga kort- och hjälteobjekten, så att grafiken vet vilket porträtt som ska animeras.
  - Varje drag skapar sin händelse själv (`Move.to_event(player)`, polymorfism), så `Game` behöver inte veta vilken sorts drag det är. Varje tur slutar med draget `EndTurn` och händelsen `TurnEnded`, även när "end turn" är det enda som återstår.
  - `Snapshot` jämför spelet före och efter ett drag och ger `ChangeEvent`s (förut textrader).
  - `TerminalUI.show_event` skriver drag med `>>`, ändringar indragna under, och övrigt för sig. "--- Joe's turn ---" kommer nu en gång per tur (`TurnStarted`), inte efter varje drag. Spelet görs för terminalen först, sedan grafik: en grafisk version (t.ex. `PygameUI`) ska ha samma metodnamn, så att `Game` inte behöver ändras (Strategy-mönstret, Gang of Four).
- **Grundspelet ska alltid gå att spela i terminalen** (användaren vill kunna visa det), även när grafiken finns. Terminalen behöver inte alla finesser.
- `TerminalUI.choose_move` kollar inga regler själv: den visar motståndarens hjälte och armé, den egna sidan, och väljer bland de lagliga dragen från `Game` (siffra = kort i handen, bokstav = anfall, 0 = avsluta turen; har kortet flera mål frågas målet efteråt).
- **Vad som hände (byggt 2026-11-18):** efter varje drag (både spelarens och AI:ns) visar `Game` draget (`>> Joe plays Book of Sorrows on Morrigan Upton`) och sedan exakt vad som ändrades: ❤️/⚔️/🛡️/🪄 före → efter, döda kort, nya kort på brädet, ☩, resurs, dragna kort och statusar (Guard, Veiled ...). `Snapshot` (`snapshot.py`) tar en bild av spelet före och efter draget och jämför. Då behöver ingen effekt beskriva sitt eget resultat. Hjälten har `statuses()` som korten.
- **Handen** visar vad varje kort gör (kortets `special`-text) på raden under. Kort som inte går att spela är grå med skälet efter (för lite resurs, fullt bräde, inget mål). Den egna armén visar för varje kort om det kan anfalla, och annars varför. Frågan räknar upp exakt vilka val som går. Har ett drag bara ett möjligt mål väljs det automatiskt (användaren vill ha det så).
- Alla figurförmågor är byggda. (Medan några inte var det visades de med "(NOT IN THE GAME YET: does nothing)"; `Special.is_built()` togs bort när SACRIFICE byggdes. Lägg tillbaka en sådan märkning om en förmåga läggs på kort innan den är byggd, så att kortet inte lovar något som inte händer.)
- Ett kort i armén som kan göra flera sorters drag får frågan "1) attack or 2) sacrifice?" (bara de sorter kortet kan, `ARMY_MOVE_KINDS`) innan målet väljs, så att fiender och egna kort inte blandas i samma lista.
- `SilentUI` (`silent_ui.py`) visar ingenting. Används i tester, simuleringar och när AI:n provar drag på en kopia.
- Färg per fraktion: figurer får en färg och spells en ljusare ton av samma färg. Ghouls är mörkröda, The Academics blå, Shoggoths gyllengula och The Deep Ones gröna.
- Färgerna är 24-bitars ANSI-koder (`rgb()`). Nycklarna i `FACTION_COLORS` är `FactionName`-värden.

### AI och controllers (byggt 2026-11-18)

- **Vem som väljer är skilt från vad som visas.** Varje `Player` *har* en controller (sammansättning), `Player(name, faction, controller)`. `Player` anropar den aldrig själv, det gör `Game`. Källa: Forge (motor för Magic) har `PlayerController` med `PlayerControllerHuman` och `PlayerControllerAi`.
- `controller.py`: `Controller` är en abstrakt basklass (`abc`) med `choose_move(game, player, moves)`, `choose_card(game, player, cards)` och `choose_mulligan(game, player, cards)`. `HumanController(ui)` skickar vidare till gränssnittet.
- **Lagliga drag:** `Game.get_legal_moves(player)` räknar ut alla drag; controllern väljer ett. Källa: MetaStone (Hearthstone-simulator) ger `validActions` till spelarens `Behaviour`. Då ligger reglerna på ett ställe, och människor och AI väljer ur samma lista. Dragen är objekt i `move.py` (Command-mönstret): `PlayCard(card, target)`, `Attack(card, target)`, `EndTurn()`, med `execute(game)` och `describe(player)`. Ett drag är komplett (målet ingår), så att AI:n kan prova varje drag. En spell utan tillåtet mål blir inget drag. Figurer blir inget drag när brädet är fullt.
- **Max 7 kort på brädet (byggt):** `Player.MAX_ARMY = 7`, `has_room_on_board()`. Resurrect (`ReviveRandom`) gör ingenting när brädet är fullt, som i Hearthstone.
- `Game` visar varje drag med `show_event(move.to_event(player))`, så att man ser vad AI:n gör.
- `ai.py`:
  - `RandomAI`: slumpar bland de lagliga dragen (avslutar turen med 10 % chans). Jämförelse och krasch-sökning.
  - `SmartAI`: provar varje drag på en kopia av spelet (`Game.copy_for_simulation(move)`, `copy.deepcopy` med `SilentUI`) och betygsätter läget med `evaluate()`. Väljer bästa draget, tills inget drag gör läget bättre (`MIN_GAIN`), då avslutas turen. Principen bakom `GreedyOptimizeMove` i MetaStone. Nya kort kräver ingen ny AI-kod.
  - Betyget bygger på vikterna i `SmartAI.WEIGHTS` (hjältens hälsa, ritual, ☩ på brädet, figurernas stats, Guard, kort i handen, triggers, Seal of Apep, om ens hjälte saknar skydd m.m.). Har motståndaren nått ritualmålet ger det −300: hen vinner i början av sin tur. Vikterna är gissningar; andra vikter ger en annan spelstil (`SmartAI(weights={...})`).
  - Resurs som blir kvar är värd lite (`resource` 0.1), eftersom den försvinner när turen är slut. (Det fanns en sparregel, `saving`, när resursen sparades mellan turer. Den togs bort när resursen blev som mana i Hearthstone.)
  - Efter ett drag som ger resurs (Trinket, The Silver Key, De Vermis Mysteriis) tittar den ett drag till, eftersom resursen bara är värd det den gör möjligt. Utan det spelades Trinket aldrig. (MetaStones `GreedyOptimizeTurn` söker igenom hela turen; detta är en mindre variant.)
  - Hotet mot den egna hjälten frågas varje fiendekort om (`CreatureCard.threat_against()`: skadan det kan göra, 0 om Terror hindrar det och 0 för ritualkort).
  - Begränsningar: tittar annars bara ett drag framåt; slumpade effekter provas en gång; spells räknas inte som något att spara till.
- För att kopieringen ska gå snabbt delas sådant som inte ändras under en match mellan kopiorna (`__deepcopy__` returnerar `self`): effekter, fraktioner och controllers. En SmartAI-match tar ungefär 0,2 sekunder.
- **Bara människa mot AI (beslutat 2026-11-18).** Människa mot människa är borttaget och ska inte gå längre. `main.py` startar alltid spelaren (`HumanController`) mot `SmartAI`.

### Tester och simulering (byggt 2026-11-18)

- `python3 -m unittest` i projektmappen kör alla tester i `tests/` (57 st, ungefär tio sekunder): regler (`test_rules.py`), lagliga drag och terminalens val (`test_moves.py`, med `unittest.mock.patch` på `input`), AI:ns val och hela matcher (`test_ai.py`), att alla figurer och spells håller budgeten (`test_budget.py`), och grafiken utan skärm (`test_gui.py`). Testerna läser kortens värden med getters i stället för fasta tal, så att de håller när stats ändras. Gemensamma hjälpfunktioner i `tests/helpers.py`.
- `python3 simulate.py [antal] [--ai smart|random] [--seed N]` låter AI spela mot AI och skriver ut vinster per fraktion, hur matcherna slutade, hur ofta den som började vann, och antal turer. Varje match har en egen seed (samma seed = exakt samma match). Fraktionerna turas om att börja.

### Strid (bestämt)

- Korttypen avgör hur ett kort gör skada:
  - Figurer (`CreatureCard`): skada = hela ⚔️ attack (figurer har ingen armor). Mot hjälten: ⚔️ − hjältens 🛡️, se Hjälte.
  - Spells (`SpellCard`): skada = effektens tal − målets 🪄 magic.
- Skadan är minst 0 och dras från målets ❤️ health. Kortet dör vid 0.
- **Varje stat har en uppgift (bestämt 2026-11-19, användarens beslut):** ⚔️ är strid (anfall och motskada), 🪄 skyddar mot spells, 🛡️ finns bara på hjälten och skyddar mot ⚔️. 🪄 används inte i strid. Formeln för magisk skada står på ett ställe: `magic_damage(strength, target)` i `card.py`.
- **Magiskt anfall är borttaget (2026-11-19, samma dag som det byggdes).** En figur med 🪄 kunde anfalla med 🪄 mot 🪄. Ghouls har nästan ingen 🪄 (snitt 0,1), så Academics gick förbi Ghouls armor och fick ingen motskada: de bytte kort gratis och vann 68 %. Utan magiska anfall: 30 %. Hearthstone har bara ett värde för strid (Attack), och striden är alltid symmetrisk; magi hör till spells. Academics behöver i stället fler figurer. Koden finns i git-historiken om idén ska tas upp igen.
- **Academics tier 1 (byggt 2026-11-19, användarens beslut):** 5 olika Novices (kostnad 1, ett exemplar var): Novice Scholar, Novice Occultist, Novice Antiquarian, Novice Medium och Novice Field Researcher. Ungefär lika starka som Ghouls tier 1 (cirka 5 i ⚔️ + 🛡️ + ❤️), men med mindre armor och lite 🪄. De ersatte andra exemplaret av fem grundspells (Book of Sorrows har kvar två). Leken: 23 figurer, 22 spells, 5 ritualkort (Ghouls: 30, 15, 5). Användaren vill att Academics har många spells. Rangerna heter Novice, Apprentice och Master. Resultat: Academics 28 % (30 % före), alltså ingen skillnad.
- I koden räknar varje klass ut sin egen skada med `damage_against(target)` (polymorfism). Spelet frågar bara kortet och behöver inte kolla vilken sorts kort det är.
- Det finns inget `attack_type`-fält. Det togs bort för att klassen redan avgör sortens skada (YAGNI).
- **Armor togs bort från figurer 2026-11-19 (användarens beslut).** Mätning före: Ghouls dödade 994 kort och Academics 590; de som dödade mest var Ghouls figurer för kostnad 3 med 🛡️ 4–6, som Academics (⚔️ 4–5) inte kunde skada alls, medan Ghouls slog tillbaka. Med ⚔️ minus 🛡️ blir små skillnader enorma (⚔️ 5 mot 🛡️ 4 ger 1, mot 🛡️ 5 ger 0). Att sänka Ghouls armor ett steg hjälpte inte (26 %). Utan armor på figurer: Academics 50 %, Ghouls 50 % (200 matcher), 22 turer i snitt, ritualseger 59 %.
- **Budget per kostnad (byggt 2026-11-19, användarens beslut), som "vanilla test" i Hearthstone:** varje figur får 5 poäng per kostnad (5, 10, 15) och får ligga på budgeten eller högst ½ under, aldrig över. ⚔️ 1 poäng, ❤️ 1, 🪄 ½, ☩ 2, förmåga 2 (GUARD, STUDY, SACRIFICE) eller 3 (DEVOUR, SUMMON). Idén (budget per kostnad, förmågor kostar stats, "text tax") kommer från Hearthstone-communityns vanilla test, där Attack + Health ≈ 2 × kostnad + 1; poängvärdena är våra egna och ändras i `budget.py`, inte kort för kort. `python3 budget.py` visar alla figurer mot budgeten; `tests/test_budget.py` kontrollerar att alla håller den. Ritualkort är inte med (de slåss inte) och ska få en egen budget. Alla figurer fick nya stats efter budgeten.
  - Resultat: Academics 35 %, Ghouls 65 % (200 matcher). Troliga orsaker: DEVOUR är för billig i budgeten (Catacomb Tyrant och Butcher dödar mest, eftersom de växer för alltid), Ghouls har fler figurer (30 mot 23), och spells har ingen budget än.
  - **Steg 1, DEVOUR 3 → 5 poäng:** Catacomb Tyrant blev ⚔️ 4 ❤️ 4, Butcher of the Underworld ⚔️ 3 🪄 1 ❤️ 4. Academics 37 % (inom slumpens marginal).
  - **Steg 2, experiment (inte ändrat i projektet):** Academics med 30 figurer, 15 spells och 5 ritualkort (7 spells bytta mot extra exemplar av Novices, Expedition Geologist och Restricted Stacks Librarian) vann **56 %** i stället för 37 %. En figur som håller budgeten är alltså mer värd än en genomsnittlig spell för samma plats i leken.
  - Om att göra kort dyrare (användarens idé, kostnaden behöver inte följa tier): med budgeten följer stats med kostnaden, så ett dyrare kort blir större, inte svagare. Det ändrar när kortet kan spelas. Att sänka kostnaden passar för spells med små effekter.
- **Budget för spells (byggt 2026-11-19, användarens beslut):** `SpellBudget` i `budget.py` ger varje sorts effekt ett pris; spellen får samma budget som en figur (5 per kostnad). `StatBudget` och `SpellBudget` ärver från `Budget` (gemensam `limit`, `difference`, `fits`). Priserna ligger i `budget.py`, inte i `effect.py`: effekterna sköter spelet, budgeten sköter balansen. En effekt utan pris ger ett fel, så inget blir gratis i tysthet.
  - **Härlett:** 1 skada på ett mål = 2 poäng (en figur för kostnad C har cirka 2,5C ❤️, så att döda den kräver 2,5C skada, värt 5C poäng).
  - **Uppskattat (prova med simulate.py):** 1 ❤️ = 1, ett kort till handen = 4 (Hearthstone: ett kort ≈ 1 mana), 1 ☩ = 2, 1 ⚔️ för alltid = 1, 1 🪄 = ½, ändringar som varar en tur räknas till hälften, statusar per kort 2–4 (Terror 3, Veil 3, Guard 2, Seal of the Black Sun 3, Seal of Apep 4), snittbräde 2 kort, en återupplivad figur 10, Infect två turer, Mirror 6, Curse 4. Resurs nu = 5 per resurs minus overload och blod. Hjältens armor n = n(n+1)/2 (nöts 1 per träff). Ett spöke = figurens poäng (+3 om det inte kan anfallas en tur).
  - **Resultat:** nästan alla spells ligger under budgeten, i båda fraktionerna. Academics: över De Vermis Mysteriis (+9), Book of Sorrows (+1), Unaussprechlichen Kulten (+1); långt under Seal of the Black Sun (3/20), The King in Yellow (6/20), Scroll of Dzyan (1/10), Rite of the Thirteenth Hour (2/10), Cultes des Goules (3/10), Necronomicon (14/20), spökena Ward of the Unbegotten (9,5/15) och Psalms of the Void (9/15). Ghouls: över bara Soul Siphon (+2), Resurrect på budgeten, resten 2–8 under. Academics har 22 spells och Ghouls 15, så svaga spells fäller Academics mest. Det stämmer med experimentet ovan.
  - **Alla spells lyfta till budgeten (gjort 2026-11-20, användarens beslut).** Regel för spells: på budgeten eller högst 2 poäng under (`SpellBudget.TOLERANCE = 2`, eftersom ett steg i skada redan är 2 poäng). Resurs-spells (De Vermis Mysteriis, The Silver Key, Trinket) är utanför budgeten (`OUTSIDE_BUDGET`): budgeten mäter värde per resurs, och de korten ändrar måttstocken. `tests/test_budget.py` kontrollerar nu även spells. Ändringar:
    - Ghouls: Ruin −4 ritual; Necrotic Bolt 5 skada; Drain Life 3 skada och läker 3; Soul Siphon stjäl 2 (var över budgeten). Kostnad 2 → 1: Wither (nu −4 attack), Terror, Bone Ward, Veil of Tiamat, Scales of Leviathan, Seal of Apep, Curse of Choronzon och Kiss of Lilith (nu Guard och +2 health).
    - Academics: Book of Sorrows 2 skada (var över budgeten); Whispered Hex drar också ett kort; Necronomicon 10 skada; Pnakotic Manuscripts läker också hjälten 3; Unaussprechlichen Kulten kostar hjälten 2; Book of Eibon −4 ritual; Mirror of Nitocris drar ett kort. Kostnad → 1: Cultes des Goules (−4 attack), Scroll of Dzyan (drar också ett kort), Rite of the Thirteenth Hour (+3 attack), Book of the Nameless Dead, Seal of the Black Sun (var 4). The King in Yellow kostar 2 (var 4) och drar ett kort. Spökena: The Unbegotten [⚔️ 4 🪄 1 ❤️ 8, Guard], Void Wraith [⚔️ 4 🪄 4 ❤️ 5].
    - Flera Academics-spells drar nu ett kort, vilket passar fraktionen ("drar mycket kort" i README).
    - **Resultat: Academics 50 %, Ghouls 50 %** (200 matcher, seed 1); med seeds 1000–1199: Academics 48 %, Ghouls 52 %. 23 turer i snitt, ritualseger 57–60 %, den som började vann 41–44 %.
  - **STUDY, SUMMON och ☩ rättade (2026-11-20, användarens beslut).** Gemensamma värden står i basklassen `Budget`, så att figurer och spells aldrig ger samma sak olika pris: `CARD = 4`, `CREATURE = 10`, `RITUAL_ONCE = 2`, `TURNS_ON_BOARD = 2`. STUDY = `CARD` (4, var 2), SUMMON = `CREATURE` (10, var 3). ☩ på ett kort ges varje tur, ungefär två gånger: `RITUAL_ONCE × TURNS_ON_BOARD` = 4 (var 2); ☩ från en spell = 2. Ritualkorten räknas nu med samma budget som figurerna (5 per kostnad), och testet kontrollerar dem.
    - Nya värden: Mourner in Black kostar 2 [⚔️ 2 ❤️ 4 ☩ 1]; Stalker 3/3, Charnel Priest 2/3, Bone Crusher 5/4, Elder Ghoul 4/5; Butcher och Catacomb Tyrant tappade ☩ (3/6 och 4/6). Ghouls ritualkort: ☩ 2 → ❤️ 12, ☩ 3 → ❤️ 8. Academics: Novice Occultist 2/2 🪄 2 utan ☩; Miskatonic Apprentice 3/4 utan ☩; Dark Occultist 2/1 🪄 2 ☩ 1; Librarian 2/3; Night Archivist 1/4 utan ☩; Morgan 4/4, West 4/5, Keziah 4/4; **Wilbur Whateley kostar 4** [⚔️ 4 🪄 2 ❤️ 5], utan ☩. Academics ritualkort: 🪄 4 och ☩ 3 → ❤️ 6, ☩ 2 → ❤️ 10.
    - Resultat: **Academics 40 % och 34 %** (seed 1 och 1000).
    - **Fynd: 🪄 är för dyr i budgeten.** Experiment (inte ändrat): all 🪄 hos Academics byttes mot ❤️ (2 🪄 = 1 ❤️, samma poäng) → Academics 53 % och 47 %. 🪄 skyddar bara mot spells, och Ghouls dödar mest med anfall, så 🪄 är nästan inget värd mot dem. Ghouls har nästan ingen 🪄 och betalar därför inget. Värdet av 🪄 beror på hur många skadespells motståndaren har. Inte bestämt: sänka priset på 🪄, eller ta bort det mesta av 🪄 på Academics figurer.
- Gammal notering: The Academics figurer var inte svaga i stats (snitt ⚔️ 3,8 ❤️ 3,6 mot Ghouls ⚔️ 3,2 ❤️ 3,1), men färre (18 mot 30) och med lägre armor (1,8 mot 3,1). De har svårt mot till exempel Ghouls i tier 2–3, som har hög armor. Academics styrka är spells: magisk skada räknas mot målets 🪄 magic, inte mot 🛡️ armor, så spells går igenom armor.

### Anfall (bestämt)

- Mål väljs i ordning (`Player.get_targets()`): finns kort med Guard får bara de anfallas. Annars får alla kort i armén anfallas. Hjälten kan bara anfallas när armén är tom. Dolda kort (Veil of Tiamat) räknas inte alls.
- Anfall i `Game.attack(attacker, target)`: triggers får först ta hand om anfallet (Mirror of Nitocris); annars räknar anfallaren skadan (`damage_against`), målet tar den (`take_damage`) och triggers reagerar (Curse of Choronzon). Sist städas döda kort bort på båda sidor.
- **Målet slår tillbaka (byggt 2026-11-18),** som i Hearthstone: båda gör skada på varandra samtidigt, så målet slår tillbaka även om det dör, och båda kan dö. Motskadan räknas med samma formel (målets hela ⚔️). Målet räknar själv ut sin motskada med `counter_damage_against(attacker)` (polymorfism): figurer använder `damage_against`, hjälten ger alltid 0 (inga vapen). Ritualkort har ⚔️ 0 och slår därför aldrig tillbaka. Terror hindrar inte motskada (som frysta figurer i Hearthstone). Mirror of Nitocris tar hand om hela anfallet, så då blir det ingen motskada. Spells får aldrig motskada.
- **Summoning sickness och ett anfall per kort (byggt 2026-11-18):** ett kort som läggs eller återupplivas får inte anfalla samma tur, det måste vänta till ägarens nästa tur, precis som i Hearthstone. Varje redo kort får anfalla en gång per tur. I koden: `CreatureCard.ready` och `attacked_this_turn`; `enter_board()` (från `Player.play_card()` och `revive_card()`), `ready_for_turn()` (via `Player.ready_army()` i början av turen) och `mark_attacked()` (i `Game.attack()`). `can_attack()` räknar in allt detta, så `TerminalUI` och `has_card_that_can_act()` behövde inte ändras.
  - *Notering, senare:* Academics ska få en spell som låter ett kort anfalla samma tur som det läggs (som Charge i Hearthstone). Väntar tills vi rättar till och lägger till spells.
- **Max 7 kort på brädet (byggt 2026-11-18),** som i Hearthstone. Se AI och controllers.

### Tur (bestämt)

- Spelare 1 börjar. Slantsingling väntar till senare.
- Starthand: 3 kort, 4 för den som börjar som tvåa (`Game.STARTING_HAND`), som i Hearthstone. (5 kort till 2026-11-19, ändrat när mulligan byggdes.)
- **Mulligan (byggt 2026-11-19, användarens beslut, förberett för grafik):** som i Hearthstone ser man sin starthand och byter hur många kort man vill, en gång. De nya korten dras först och de gamla blandas in i leken efteråt, så att man inte får tillbaka samma kort (`Player.mulligan(cards)`). Ordning i `Game.start()`: meddelandet om Trinket → starthänder → mulligan för båda (`Game.mulligan(player)`) → Trinket i handen (efter mulligan, så den inte kan bytas bort).
  - Valet görs av controllern: `Controller.choose_mulligan(game, player, cards)` returnerar korten som ska bytas. `HumanController` skickar vidare till `ui.choose_mulligan(cards)`; ett `PygameUI` behöver bara en metod med samma namn (till exempel klicka på korten). `TerminalUI` frågar "Replace which cards? (for example 1 3, or Enter to keep all)".
  - `SmartAI` byter kort som kostar mer än `MULLIGAN_MAX_COST = 3` ("mulligan for a curve", vanligt råd i Hearthstone; gränsen är en gissning). `RandomAI` byter varje kort med 50 % chans.
- **Trinket (byggt 2026-11-19):** den som börjar som tvåa "got the trinket": ett extra kort i starthanden och kortet Trinket (kostnad 0, +1 resurs en gång, `make_trinket()` i `factions/neutral.py`, ingen fraktion). Källa: The Coin i Hearthstone. Bonusen hör till turordningen, inte fraktionen. Den som började vann 74 % före, 53 % efter (med 5 kort i starthanden), 44 % med 3/4 kort och mulligan.
- I varje tur, i valfri ordning: **lägg så många kort du har råd med** (se Resursen) och **anfall med varje kort som har legat på brädet sedan förra turen, en gång var** (som i Hearthstone; byggt 2026-11-18). Den gamla regeln "en action per tur" är borttagen.
- Turen går över när inget mer går att göra, eller när spelaren väljer "0) end turn", till exempel för att spara resurs till ett dyrt kort.
- Finns inget kort som kan göra en action hoppas den över automatiskt.
- Man drar 1 kort i början av sin egen tur, även första turen, som i Hearthstone. Då har man fler val när man spelar.
- **Stress (byggt):** Fatigue från Hearthstone med namnet Stress (ordet kommer från Darkest Dungeon, men mekaniken är Hearthstones). Varje gång man ska dra ett kort ur en tom lek ökar `Player.stress` med 1 och hjälten tar så mycket skada (1, 2, 3 …). Gäller alla dragningar (även spells som DrawCards), men inte att titta på kort (`reveal_top_cards`, Forbidden Codex). Logiken ligger i `Player.draw_cards()`. Man kan förlora på sin egen stress. Löser att spelet hänger sig när båda har slut på kort. Stressen visas i statusraden (`show_hero`, när den är större än 0), och `Game` visar ett meddelande när dragningen i början av turen ger stress.

### Resursen för att lägga kort (bestämt och byggt)

*Namnet är inte bestämt. "Essence" är bortvalt; det ska låta Darkest Dungeon/Lovecraft (förslag: Dread, Resolve, Devotion, Omen, Ichor). I koden heter den tills vidare `resource` (`Player.resource`, `Player.max_resource`, `RESOURCE_NAME` i `terminal_ui.py`), så den byts lätt.*

- **Overload** (som hos Shaman i Hearthstone): ett kort kan låna resurs från nästa tur. `Player.overload` dras av när resursen fylls på (`refill_resource()`), aldrig under 0.
- Academics har två spells som ger mer att spendera nu (som Innervate i Hearthstone, men med ett pris). De ersatte Elder Sign och Litany of Unmaking, som överlappade Ward of the Unbegotten och Rite of the Thirteenth Hour. Två exemplar var, leken är kvar på 50 kort:
  - **The Silver Key** (kostnad 0): +2 resurs nu, Overload (2). Man lånar från framtiden.
  - **De Vermis Mysteriis** (kostnad 0): +2 resurs nu, den egna hjälten tar 3 skada. Man betalar med blod.
- I koden: `Card.cost`; `Player.refill_resource()`, `gain_resource()`, `add_overload()`, `can_afford()`, `has_affordable_card()`; `Player.play_card()` drar kostnaden (och kastar `ValueError` om man inte har råd). Terminalen visar kostnaden i handen som `(2)` och vägrar kort man inte har råd med.
- **Som mana i Hearthstone (ändrat 2026-11-18):** `max_resource` växer med 1 i början av varje egen tur, upp till `Player.MAX_RESOURCE = 10`, och resursen fylls upp till `max_resource` (minus overload). Det som inte används **försvinner** när turen är slut, det sparas inte. Första turen: 1, andra: 2 osv. Terminalen visar "Resource: 2 of 3". *(Tidigare: +1 per tur som sparades, som credits i Android: Netrunner. Det var för segt: med 1 per tur och ungefär 12 egna turer kunde man nästan bara lägga ett billigt kort per tur, handen växte, och ritualkort för 4 spelades nästan aldrig.)*
- **Max 10 kort i handen (2026-11-18),** som i Hearthstone: `Player.MAX_HAND`. Alla kort som ska till handen går genom `Player.add_to_hand()`. Är handen full försvinner kortet (`Player.burned`), som när man drar med full hand i Hearthstone. Ett kort som ska tillbaka från gravhögen (Book of the Nameless Dead) stannar där.
- Alla får lika mycket, som mana i Hearthstone: resursen är inte kopplad till health eller ritual. (Ritualen som budget valdes bort: den som leder skulle få fler kort och dra ifrån, en positiv återkopplingsloop.)
- Varje kort har en **kostnad** (`cost`, ett eget fält på `Card`). Man får lägga så många kort man har råd med.
- Startkostnader: figurer kostar sin tier (1–3), ritualkort (tier 4) kostar 4, Academics basic spells kostar 1, övriga spells 2, tunga spells (Necronomicon, Pnakotic Manuscripts) 3. Justeras efter speltest. Kort som behöver vara dyrare (t.ex. Shoggoths stora monster, 6–8) flyttas till högre tier eller får en egen kostnad.
- Samma mekanik för alla fraktioner. Senare kan varje fraktion visa sitt eget namn i spelet, t.ex. Sanity för Academics och Stamina för The Deep Ones.

### Spellkort (bestämt)

- Spells spelas som i Hearthstone: välj kortet från handen, välj mål, och effekten sker direkt. Kortet hamnar aldrig på brädet.
- **Guard skyddar inte mot spells** (som Taunt i Hearthstone). Annars har Academics ingen chans. `Player.get_spell_targets()` ger hela armén plus hjälten.
- Varje effekt avgör själv vilka mål den får välja (`get_targets`), som i Hearthstone där kortets text styr (Fireplace: play requirements som `REQ_ENEMY_TARGET`). Se "Mål" nedan.
- **Effekter är egna objekt (sammansättning).** `SpellCard` *har* en effekt, till exempel `DamageOneEnemy`, som gör jobbet med `apply(...)`. Samma effekt kan återanvändas av flera spells. Källa: Fireplace (`play = Hit(TARGET, 6)`) och Forge (`DealDamage`); mönstret Command/Strategy (Gang of Four). Ingen lång `if/elif` över `Special`.
- **Styrkan i en effekt anges när effekten skapas** (som `Hit(TARGET, 6)` i Fireplace): `DamageOneEnemy(7)`, `DamageAllEnemyCards(3)`, `HealOwnHero(2)`, `HealAllOwnCards(2)`, `LowerAttack(3)`, `LowerRitual(3)`, `StealRitual(3)`, `GainRitual(2)`, `Infect(2)`, `BuffOwnCard(health=3, magic=2)`, `GainArmor(2)` och `GiveBuff(..., attack=-2)`. Talen är desamma som spellernas gamla 🪄 (Scroll of Rituals: gamla ☩). Ändrar man ett tal ska texten i `Special` ändras också. *(Förut, till 2026-11-19: spells hade 🪄 och ☩, och effekten läste spellens 🪄. Flera spells visade då 🪄 som inte användes, till exempel Terror, Veil of Tiamat och Cultes des Goules.)*
- En effekt svarar på `needs_target()` och `get_targets(game)`: effekten själv säger vilka mål som är tillåtna. Har en spell inga giltiga mål kan den inte spelas (den betalas inte).
- Byggda effekter i `effect.py` (grupp A, omedelbara): `DamageOneEnemy(include_hero)`, `DamageAllEnemyCards(own_damage)`, `HealOwnHero`, `HealAllOwnCards`, `LowerAttack`, `GainArmor(n)` (den egna hjälten), `BuffOwnCard(magic, health, ritual_only)`, `LowerRitual`, `StealRitual`, `GainRitual`, `DrawCards(n)`, `ReviveRandom`, `ReturnRandomToHand`, `LookAtTopCards(n)`, `PayWithBlood(n)`, `GainResource(...)`, `SummonGhost(ghost, hidden)`, `DrainHealth(n)` och `Combined(...)` (flera effekter i samma spell, Composite-mönstret; bara den första får ett mål).
- Läkning går aldrig över `max_health` (både kort och hjälte), som i Hearthstone. Återupplivade kort kommer tillbaka med full health.
- **Buffar (grupp B, byggt):** effekter som varar "until your next turn" eller "this turn" är `Buff`-objekt (`buff.py`) som fästs på ett kort eller en hjälte, som enchantments i Hearthstone, `Buff` i Fireplace och buffar/debuffar i Darkest Dungeon. Kortets egna värden ändras aldrig: `get_attack()`, `get_magic()`, `can_attack()`, `has_guard()` osv. räknar in buffarna. När buffen går ut tas den bara bort. (Command-mönstret med `undo` valdes bort: `undo` blir fel när ett värde stannat på 0.)
  - `CreatureCard` och `Hero` *har* en `BuffList` (sammansättning), så logiken står på ett ställe.
  - En buff tillhör spelaren som lade den. "Until your next turn" går ut i början av den spelarens nästa tur, "this turn" i slutet av turen (`Game.remove_expired_buffs`). Kort som dör tappar sina buffar.
  - Effekten `GiveBuff(receiver, ...)` ger buffar: Terror, Veil of Tiamat, Seal of Apep, Kiss of Lilith, Whispered Hex, Scroll of Dzyan, Rite of the Thirteenth Hour, The King in Yellow, Seal of the Black Sun.
  - Ett kort som är dolt (Veil of Tiamat) kan inte anfallas av figurer och skyddar inte heller hjälten. Spells kan fortfarande träffa det.
  - `Faction` skapar kort och hjältar med `copy.deepcopy`, så att varje kopia har en egen lista med buffar.
- **Triggers (grupp C, byggt):** effekter som väntar på att något ska hända är `Trigger`-objekt (`trigger.py`), Observer-mönstret (Gang of Four), som Secrets och gift i Hearthstone och event-lyssnare i Fireplace. `Game` har en lista med triggers och meddelar dem `before_attack` (kan ta hand om anfallet), `after_attack` och `at_turn_start`. En trigger som har gjort sitt markerar sig som förbrukad och tas bort.
  - **Infect:** fiendekortet tar 🪄 magic i skada i början av varje tur för den som smittade det, tills kortet dör eller lämnar brädet.
  - **Mirror of Nitocris:** nästa melee-anfall mot det valda egna kortet träffar anfallaren i stället (engångs).
  - **Curse of Choronzon:** nästa fiendekort som anfaller ett av dina ritualkort tar samma skada som det gjorde (engångs).
  - Triggers gäller bara melee-anfall (`Game.attack`), inte spells.
- **Spöken och dränering (byggt 2026-11-19, användarens idé):** Academics ska kännas som magiker med många spells av tre sorter: spells som skapar spöken, spells som anfaller och spells som dränerar. Tre skydds-spells gjordes om:
  - **Ward of the Unbegotten** (3): skapar spöket *The Unbegotten* [⚔️ 2 🪄 1 ❤️ 5, Guard].
  - **Psalms of the Void** (3): skapar *Void Wraith* [⚔️ 1 🪄 4 ❤️ 3], som inte kan anfallas förrän ens nästa tur (som Stealth i Hearthstone, samma buff som Veil of Tiamat).
  - **Codex of the Eleven Keys** (2): dränerar 3 health (magi, 🪄 tar emot) från ett fiendekort och ger det för alltid till ett slumpat eget kort, eller läker hjälten om brädet är tomt.
  - Spöken är *tokens* (som Mirror Image i Hearthstone): förlagorna ligger i `academics.py` men inte i leken, och `SummonGhost` skapar en ny kopia varje gång. De ger ingen ☩. Ett spöke med Guard får inte samtidigt vara dolt, eftersom dolda kort inte skyddar.
  - `Player.summon(card)` lägger en figur på brädet utan att den spelas från handen (används av återupplivning, SUMMON och spöken).
- **Alla spells har en effekt.** Det tillfälliga blocket som bytte ut spells utan effekt är borttaget.
- Man kan ångra medan man väljer (kort eller mål). När man har bekräftat är spellen kastad och kan inte tas tillbaka. *Ångra är inte byggt: i dag går det inte att backa ur målvalet.*
- Exempel: tier 5 hos Ghouls (Resurrect, Plague, Infect, Ruin m.fl.).
- **Tung dark magic kostar inte längre något (ändrat 2026-11-18, användarens beslut).** Förut skadade Academics tyngsta spells de egna korten. Tillsammans med regeln att ritualen sjunker när ett kort dör straffades Academics då dubbelt för sin egen magi (kortet dog *och* ☩ försvann), och de vann bara drygt 20 % av AI-matcherna. Nu:
  - **Unaussprechlichen Kulten** (stjäl ritual): **hjälten** tar 1 skada (`DamageOwnHero(1)`), aldrig ett kort. Att stjäla ritual ska kosta spelaren själv.
  - **Necronomicon, R'lyeh Text, The King in Yellow, Pnakotic Manuscripts, Rite of the Thirteenth Hour:** inget pris alls.
  - **De Vermis Mysteriis** (+2 resurs, hjälten tar 1, sänkt från 3) **behåller sitt pris** (användarens beslut): utan det vore den gratis +2 resurs, bättre än The Silver Key.
  - `PayWithBlood` och `DamageAllOwnCards` finns kvar i `effect.py` men används inte av något kort just nu.
- **Mål (bestämt, som i Hearthstone):** spelaren väljer högst **ett** mål per spell. Allt annat sker automatiskt eller slumpat.
  - "One enemy" (fiendens figur eller hjälte): Book of Sorrows, Necrotic Bolt, Necronomicon. Texterna ska säga "one enemy".
  - Bara fiendens figurer: Infect, Drain Life, Wither, Terror, Whispered Hex, Cultes des Goules. Area-spells (Plague, Pnakotic Manuscripts) träffar bara figurer, inte hjälten.
  - Bara fiendens figurer gäller också Codex of the Eleven Keys (dränerar).
  - Eget kort: Bone Ward, Kiss of Lilith, Mirror of Nitocris. Eget ritualkort: Veil of Tiamat, Scales of Leviathan.
  - Inget mål: resten (gäller alla kort, spelaren eller ritualen).
  - Drain Life läker automatiskt den egna hjälten (som Drain Life i Hearthstone).
  - Resurrect och Book of the Nameless Dead hämtar ett **slumpat** kort ur gravhögen (som Resurrect i Hearthstone).
  - Forbidden Codex: titta på tre kort i leken och ta ett (som Tracking i Hearthstone).
- *(Gammal regel, används inte av något kort sedan 2026-11-18:)* **Priset för tung magi** (`PayWithBlood`): skadan tas automatiskt av ett slumpat eget kort som har **minst lika mycket health som priset** (kortet får dö, men ett kort med 2 health väljs aldrig för ett pris på 3). Finns inget sådant kort tar den egna hjälten skadan, och dör hjälten förlorar man (oavgjort om motståndarens hjälte dör samtidigt). (Ersätter den gamla regeln att tung magi inte fungerar utan eget kort.)

### Ritual (bestämt)

- **Ritualkort** är bara tier 4-korten: de finns till för att bygga ritual och kan inte slåss (⚔️ 0). Andra kort kan också ha lite ☩, men räknas inte som ritualkort.
- **☩ på korten (ändrat 2026-11-19, användarens beslut):** ritualkort ger ☩ 2 eller 3 (förut 4 eller 5), figurer högst ☩ 1 (Elder Ghoul och Wilbur Whateley hade 3, Keziah Mason 2). Förut nåddes målet 15 på två turer med två ritualkort på brädet. Samma värden i båda fraktionerna. Resultat: matcherna blev längre (19 turer i stället för 17) och ritualseger sjönk från 84 % till 66 %, men Academics vann fortfarande bara 26 %.
- I koden är ritualkort klassen `RitualCard(CreatureCard)` i `card.py`. Den är en egen klass eftersom beteendet skiljer sig: `can_attack()` ger `False` (för `CreatureCard` ger den `True`), och bara ritualkort kan få skydds-spells. Spelet känner igen dem med `isinstance(card, RitualCard)`.
- **När ☩ räknas (bestämt):** i början av sin tur får hjälten ☩ från alla egna kort på brädet (`Player.collect_ritual()` → `Hero.add_ritual()`), så länge korten ligger kvar. Därför är det viktigt att skydda ritualkorten. Målet 15 kan behöva höjas.
- **När ritualen avgörs (byggt):** man vinner inte direkt när man når målet. Motståndaren får en tur att svara (sänka ritualen, döda ritualkort, slå ut hjälten). I början av ens nästa tur, **före** allt annat (buffar, triggers, dragning, `collect_ritual()`), vinner man om ritualen fortfarande når målet. Källa: Magic: The Gathering, Felidar Sovereign ("At the beginning of your upkeep, if you have 40 or more life, you win the game"). I koden: `play_turn()` kollar `reached_ritual()` först och anropar då `Player.complete_ritual()`. `Game.has_won()` frågar `is_ritual_complete()` (och hjältedöd, som gäller direkt). Spelet visar "The ritual of … is nearly complete!" i slutet av turen när målet är nått, så att motståndaren vet att det är sista chansen. Att hålla målet i 3 rundor är bortvalt: ritualen fortsätter växa, så det blir nästan samma sak som ett högre mål.
- **När ett kort dör sjunker ritualen (byggt):** hjälten tappar kortets ☩ just nu (`card.get_ritual()`, ett kort med ☩ 3 ger −3), en gång. Inte allt kortet bidragit med under spelet. Gäller **alla** dödsfall: anfall, spells, blodpris, Infect och eget offer (SACRIFICE, DEVOUR). Att offra ett kort med ☩ blir då ett strategiskt val. Byggs i `Player.kill_card()` (alla dödsfall går igenom den) med `hero.lose_ritual()`, och ☩ läses innan `clear_buffs()`. Kort som återupplivas (Resurrect) ger ingen ☩ direkt, bara i början av nästa tur som vanligt.
- **Seal of Apep skyddar även mot detta** ("Your ritual cannot be lowered or stolen"): under Seal tappar man ingen ☩ när kort dör, inte heller vid eget offer. Ska provas i spel, den kan bli för stark i sista turen före vinsten.
- Sätt att bygga ritual: ritualkort (snabbt, men oskyddat), vanliga kort med lite ☩ (långsamt men säkrare) och spells.
- Ritual kan stjälas, men bara av fraktioner med dark magic: Ghouls och Academics.
- Ritualkort skyddas med `GUARD` på starka melee-kort (fienden måste anfalla dem först, som Taunt i Hearthstone; namnet Guard kommer från The Elder Scrolls: Legends) och med skydds-spells (Ghouls: Veil of Tiamat, Scales of Leviathan, Seal of Apep, Kiss of Lilith, Curse of Choronzon).
- Skydds-spellernas namn har anti-kosmisk inspiration: gamla kaosväsen och antigudar (Tiamat, Leviathan, Apep, Lilith, Choronzon).

### Figurernas förmågor (byggt 2026-11-18, utom ABSORB)

GUARD gäller hela tiden kortet ligger på brädet. DEVOUR, STUDY och SUMMON händer **när kortet läggs** (som Battlecry i Hearthstone). De är vanliga `Effect`-objekt i `effect.py`, precis som spellernas, och `CREATURE_ABILITIES` / `creature_ability(card)` säger vilken effekt en förmåga har. `Game.get_legal_moves()` ger ett drag per mål när förmågan behöver ett mål, och `Game.play_card()` kör förmågan när figuren läggs. Mål, AI och terminal fungerar därför som för spells. SACRIFICE är i stället ett eget drag (se nedan).

- **DEVOUR (Ghouls, byggt):** bara på de stora korten i tier 3, **Butcher of the Underworld** och **Catacomb Tyrant** (4 kort i leken). Bone Gnawer, Grave Eater, Hollow-Eyed Stalker och Charnel Priest hade också DEVOUR men fick `special=None` 2026-11-18: 12 kort med DEVOUR var på tok för starkt, eftersom Ghouls redan var starkast. Förmågan: när kortet läggs väljer spelaren ett dött kort (figur) i den **egna** gravhögen. Figuren får dess ⚔️ attack och ❤️ max health för alltid (`Devour`, `increase_attack`, `increase_health`). Värdena är det döda kortets egna utan buffar (buffarna försvann när det dog) men med bestående ändringar som Wither. **Det ätna kortet försvinner ur gravhögen** (`Player.eat_from_graveyard`), så det kan inte återupplivas (beslutat av användaren). Är gravhögen tom läggs kortet ändå, utan att äta. Att äta ur motståndarens gravhög väntar; det passar kanske bättre för en helt annan fraktion senare. *Öppet:* hur ska hjälteförmågan Feast of Graves skilja sig från DEVOUR? (Förslag: Feast låter hjälten ge ett kort som redan ligger på brädet ett dött korts stats.)
- **SACRIFICE (Academics, byggt):** finns på **Miskatonic Apprentice** (hette Miskatonic Student till 2026-11-19) och **Dark Occultist** (beslutat av användaren). I stället för att anfalla offrar kortet sig: det dör och ger sin ❤️ max health till ett annat eget kort för alltid (förut också 🛡️ armor, borttaget med armor på figurer). **Även när kortet dör på annat sätt (anfall, spell, Infect) ger det sin styrka (ändrat 2026-11-19, användarens beslut),** som Deathrattle i Hearthstone: då får ett **slumpat** eget kort den (Deathrattle frågar aldrig efter mål, eftersom kortet kan dö under motståndarens tur). Vid frivilligt offer väljer spelaren. Det ges bara en gång. Värdena är kortets egna utan buffar: ❤️ max health (inte den health som är kvar, den är 0 när kortet dött). Dör flera kort samtidigt går styrkan bara till kort som överlevde. I koden: `Player.clear_dead_cards()` (alla dödsfall) och `Player.pass_on_strength()`; `Game.sacrifice()` anropar `kill_card()` direkt så att styrkan inte ges två gånger. Samma regler som för anfall: kortet måste ha legat sedan förra turen, och Terror hindrar det. Kortet dör som vanligt, så dess ☩ försvinner från ritualen (båda har ☩ 1). Passar Academics identitet att skydda: offra en skör figur för att hålla t.ex. ett ritualkort (❤️ 2–3, 🛡️ 0) vid liv. I koden: draget `Sacrifice(card, target)` i `move.py`, `Game.sacrifice()`, och `Game.get_legal_moves()` ger ett drag per annat eget kort.
- **ABSORB (Shoggoths), notering, väntar:** Shoggoths absorberar närliggande pjäser för att få liv och attack (se `README.md`). Det ska heta Absorb, inte Sacrifice. Byggs när Shoggoths byggs.
- **SUMMON (Wilbur Whateley, byggt):** när kortet läggs hamnar en **slumpad** figur ur den egna leken direkt på brädet (`SummonRandomFromDeck`, `Player.summon_from_deck`, `Deck.remove`), som Recruit i Hearthstone (Kobolds & Catacombs). Den nya figuren måste vänta en tur innan den får anfalla. Är brädet fullt eller finns ingen figur i leken händer inget.
- **STUDY (Academics, byggt):** drar ett kort när kortet läggs (`DrawCards(1)`, som Battlecry: Draw a card i Hearthstone).
- Rapporten efter draget visar förmågorna: "enters the board [⚔️ 7 ❤️ 5]", "Ossuary Keeper is eaten", "enters the board from the deck", "draws 1 card" (`snapshot.py` håller reda på vilka kort som finns i lek, hand, bräde och gravhög).

### Deck (`deck.py`) – under diskussion, inte bestämt

Riktning som diskuterats:

- `Deck` hanterar bara högen: blanda, dra, räkna. Den får färdiga kort och vet inget om fraktioner.
- Fraktionen, eller en skaparfunktion för den, bygger fraktionens kort. Varje lek ska få nya kortobjekt, eftersom korten kan ändras under spelet.
- Spelaren har sin fraktion och sin lek.
- Ingen arvshierarki för lekar (som `GhoulDeck`). Lekarna fungerar likadant, och skillnaden ligger i korten.

### Öppna frågor

- Ska alla lekar för en fraktion vara identiska, eller ska spelaren kunna välja kort?
- Vem bygger leken när ett spel startar: spelaren, spelet eller en meny?
- När en ghoul äter ett kort, får den kortets grundvärden eller värdena kortet hade när det dog?
- Vad heter resursen? (Dread, Resolve, Devotion, Omen, Ichor …)
- Är Seal of Apep för stark nu när den också skyddar mot ☩-förlust när kort dör?
- Ritualmålet 15 ska provas i spel, nu när resursen växer som i Hearthstone (ritualkort blir lättare att lägga, så målet kan behöva höjas).

## Läget (2026-11-18)

**Fungerar:** en hel match i terminalen mellan Academics och Ghouls (`main.py`). Dra kort, resurs med sparande och overload, lägga kort, anfall med Guard, ritual som växer varje tur, vinst/förlust/oavgjort. Alla 36 spells har effekter (omedelbara, buffar och triggers). `TerminalUI` är utbytbart mot ett grafiskt gränssnitt.

**Kontrollerat:** alla moduler importeras; 300 matcher med slumpbotar utan krascher, alla spells spelades; tio regelkontroller (buffar som går ut, Seal of Apep, Mirror, Curse, Infect, Veil, blodpris, läkningstak, overload) stämde. Med slumpbotar vann Academics 39 % och Ghouls 61 % (före spelleffekterna: Academics 20 % med en enklare bot). Testskripten låg i scratchpad och finns inte i projektet.

**Inte byggt än:**
- ABSORB (Shoggoths). GUARD, DEVOUR, STUDY, SUMMON och SACRIFICE är byggda.
- Hjälteförmågorna Feast of Graves och The Eleventh Seal.
- Visa i terminalen att ett kort är smittat (Infect) eller att Mirror/Curse väntar.
- Visa motståndarens bräde under ens egen tur, och en text efter anfall (hur mycket skada, vilket kort som dog).
- Slantsingling (mulligan är byggd 2026-11-19).
- Shoggoths och The Deep Ones (bara Academics och Ghouls är byggda).

**Byggt 2026-11-18:** ☩ sjunker när ett kort dör, ritualen avgörs efter motståndarens svar, Stress. Kontrollerat med 300 matcher med slumpbotar (inga krascher, inget hängde sig; ritualseger 231, hjälte dödad 69; Academics 102, Ghouls 198) och 13 riktade regelkontroller. Stress uppstår inte i vanliga matcher (leken på 50 kort tar inte slut), bara i specialfallet med tomma lekar, där spelet nu tar slut. Testskripten ligger i scratchpad och finns inte i projektet.

**Byggt 2026-11-18, senare:** alla redo kort anfaller en gång per tur, med summoning sickness. 300 matcher med slumpbotar: ritualseger 92, hjälte dödad 208 (före: 231/69); Academics 82, Ghouls 218; i genomsnitt 26 turer (före: 35). Anfall har alltså blivit mycket starkare än ritualen, och Ghouls vinner nästan 3 av 4. Slumpbotar säger lite om riktig balans.

**Motskada byggd 2026-11-18.** 300 matcher: ritualseger 53, hjälte dödad 247; Academics 79, Ghouls 221; 26 turer i snitt. Motskadan gjorde alltså inte anfall svagare, tvärtom: figurerna dör fortare, armén töms, och hjälten kan bara anfallas när armén är tom. Academics (svaga figurer) straffas hårdast. **Balans görs inte på slumpbotar:** först AI-motståndaren, sedan balans med den.

**AI byggd 2026-11-18.** SmartAI slår RandomAI i 56 av 60 matcher som Academics och 59 av 60 som Ghouls. 100 matcher SmartAI mot SmartAI (`simulate.py 100`): Ghouls 78 %, Academics 22 %; ritualseger 56 %, hjälte dödad 44 %; den som började vann 54 %; i snitt 21 turer. **Fynd om ekonomin (inte beslutat):** med +1 resurs per tur och ungefär 10–13 egna turer per match kostar ett ritualkort (4) en tredjedel av all resurs man får. Ritualkort spelades därför nästan aldrig, inte ens av SmartAI som sparade. **Löst samma dag:** resursen växer nu som mana i Hearthstone, och handen har max 10 kort. Siffrorna ovan gäller den gamla ekonomin.

**Mekanik före grafik.** Grafiken (t.ex. `PygameUI`) väntar tills listan med gränssnittsmetoder är stabil: varje ny metod (motståndarens bräde, text efter anfall, Stress, "ritualen är nästan klar") måste annars skrivas i både `TerminalUI` och `PygameUI`.

**AI-motståndare före grafik (beslutat 2026-11-18).** Användaren vill inte bygga om gränssnittet efteråt. Idag frågar `Game` samma `ui` om valen för båda spelarna, så en AI kräver att "vem som väljer" skiljs från "vad som visas".

**Väntar till grafiken (beslutat 2026-11-18):** *(mulligan stod här, men byggdes 2026-11-19 i terminalen och förbereddes för grafik, användarens beslut.)* Tre visningsfel som syntes i speltest: (1) ⚔️ döljs när den är 0, så en figur vars attack sänkts till 0 (Wither) ser ut att sakna värdet; figurer ska alltid visa ⚔️, bara ritualkort ska dölja den. (2) Rapporten efter ett anfall säger inte när skadan blev 0 (den visar bara det som ändrades); den ska säga skada åt båda håll, t.ex. "deals 0 damage (⚔️ 0 vs 🛡️ 1), hits back for 1". (3) ~~"--- Joe's turn ---" skrivs ut efter varje drag~~ (löst 2026-11-20 med händelsen `TurnStarted`).

### Grafik (första versionen byggd 2026-11-20)

- **Start:** `python3 main_gui.py` (grafik) eller `python3 main.py` (terminal). **Terminalversionen ska finnas kvar** (användaren visar eleverna hur spelet såg ut före grafiken). Båda använder samma `Game`.
- **`gui/`**, en fil per ansvar: `assets.py` (`ImageLibrary`: hittar och laddar bilder en gång, sparar skalade kopior), `layout.py` (`Layout`: var allt ligger i 1920 × 1080; samma rutor används för att rita och för klick), `renderer.py` (`Renderer`: ritar kort, porträtt med stats som brickor, hjältar, kortens baksida), `effects.py` (`Effect` med `FloatingText`, `AttackLine`, `Banner`, `FadingImage`, `ShowCard`; varje effekt ritar sig själv), `pygame_ui.py` (`PygameUI`).
- `PygameUI` har gränssnittets fyra metoder plus `attach(game, viewer)` (vilket spel och vem som sitter vid skärmen) och `wait_for_close()`. `Game` är synkront, så varje metod kör en egen liten loop med bildrutor: `show_event` spelar en kort effekt, `choose_move` väntar på klick. Vilken effekt en händelse får står i `self.handlers` (händelsens klass → metod); andra visas efter sin sort (`NoticeEvent` som ruta).
- **Spela:** klicka på ett kort (i handen eller på brädet) och sedan på ett mål. Kort som kan göra något lyser grönt, valt kort gult, mål rött (fiende) eller grönt (eget). Högerklick eller Esc ångrar valet. Har ett drag bara ett möjligt mål väljs det direkt. Mål som inte ligger på brädet (DEVOUR äter ur gravhögen) visas stort att välja bland. Tab öppnar konsolen.
- Ikonlista med senaste drag till vänster (nyast överst, grön kant = egna drag, röd = motståndarens; musen över en ikon visar kortet och vad som hände). Musen över ett kort på brädet visar hela kortet stort.
- Kort utan egen fraktion (Trinket) får ramen från fraktionen hos den som har kortet, som The Coin i Hearthstone.
- **En bild per tier (användarens beslut):** en figur utan egen bild får bilden för sin tier (`TIER_PORTRAITS` i `gui/assets.py`; tier = kostnad, högst 3). Ghouls: tier 1 Hollow-Eyed Stalker, tier 2 Crypt Warden, tier 3 Elder Ghoul. Academics: tier 1 Novice Occultist, tier 2 Miskatonic Apprentice, tier 3 Dr. Francis Morgan. Ett kort med egen bild (rätt filnamn) använder alltid den. Spells utan egen bild (ungefär 20) visas än så länge som en mörk ruta med namnet.
- Testas utan skärm med SDL:s dummy-drivrutin (`tests/test_gui.py`: klick blir rätt drag, en hel match genom fönstret).

### Grafik (planerad, användarens beslut 2026-11-20)

- **pygame-ce** (Community Edition, underhålls aktivt, `pip install pygame-ce`, man skriver fortfarande `import pygame`). `PygameUI` får samma metoder som `TerminalUI` (se Terminalen), så `Game` ändras inte. `choose_move` väntar på klick i stället för tangentbordet.
- **Brädet visar porträtt, inte hela kort.** Ett kort är en ram (`assets/cards/card_frame-<fraktion>.png`, 1024×1536) plus ett porträtt (`assets/creatures/`, `assets/spells/`, cirka 1263×1246, rundad ruta med genomskinlig bakgrund). När kortet spelas "faller porträttet ur kortet" och läggs på brädet med stats synliga. Hjältarna har hela kort (`assets/hero_portraits/`). Bakgrund: `assets/boards/bg.png` (1920×1080). Användarens demo: motståndarens hand överst, hjältarna till höger, egen hand nederst.
- Filnamn: `<Fraktion>-<Creature|Ritual|Spell>-<Namn-med-bindestreck>.png`. Inte alla kort har bild än; kort utan bild visas med namn och stats.
- **Planerat:** lista med ikoner för senaste drag till vänster (som Hearthstone, byggs av `MoveEvent`), en konsol som i Quake (alla `describe()`-rader, behöver inte byggas direkt), en ruta som visas en stund vid `NoticeEvent` (till exempel "Din tur"), animationer och effekter vid anfall (`AttackMade` följt av `StatChanged`/`CardDied`). Ångra i målvalet: inte nu. *(Text efter anfall stod här först, men det gick inte att förstå spelet utan den, så den är byggd, se Terminalen.)*
