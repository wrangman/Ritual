# Ritual

## Arbetssätt

- Användaren skriver koden själv. Beskriv steg för steg vad som ska byggas, ett steg i taget, och skriv inte koden åt hen. Hjälp till med kod bara när hen ber om det.
- Sluta ge snabblösningar. Ge alltid bästa praxis och absolut bästa OOP.
- Basera designförslag på etablerade källor (designmönster, hur riktiga kortspelsmotorer är byggda) och ange källorna. Gissa inte. Skilj tydligt på vad källan faktiskt säger och vad som är din egen tillämpning på projektet.
- Tänk igenom ansvarsfördelning och relationer mellan klasser innan du föreslår kod. Fråga om designbeslut hellre än att gissa.
- Spelinnehåll (kortnamn, specialtexter m.m.) och kod skrivs på engelska.
- Arv bara när beteendet faktiskt skiljer sig. Sammansättning (en spelare *har* en lek, en lek *innehåller* kort) är lika viktig som arv.

## Vad vi bygger

Ett Lovecraft-inspirerat kortspel i Python (kursen Prog2), spelat i terminalen.

Hjälten är den som utför ritualen. Den har två mätare: ❤️ hälsa (30) och ☩ ritual (mål preliminärt 15, ska provas i spel). Båda ska hållas så höga som möjligt. Motståndaren kan störa på två sätt: sänka ens ritual eller skada hjälten.

Två vägar till seger: bygg klart sin ritual, eller ta sig förbi motståndarens armé och slå ut hjälten (Guard skyddar, som Taunt i Hearthstone). När motståndarens bräde är tomt anfaller man hjälten. Inspiration: Android: Netrunner (agenda points eller flatline) och Hearthstone (hjälte med hälsa, Taunt).

Strategin är att balansera: försvara sin ritual och sin hjälte, öka ritualen, och ha både försvarande och anfallande kort.

**Vinstvillkor** (man vinner om något av dessa gäller):
1. Man når sitt ritualmål.
2. Motståndarens hjälte har 0 hälsa.
3. Motståndaren är utplånad: inga kort på brädet och inga kort kvar (varken i hand eller lek). *Oklart om detta ska finnas kvar.*
4. Man har byggt upp mer ritual än motståndaren. *Oklart om detta ska finnas kvar.*

Man vinner INTE genom att motståndaren har noll ritual.

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

- `Card` är grundklassen med det som alla kort har: `faction`, `name`, `ritual`, `special`, `rarity`. Den skapas inte direkt; `short()` kastar `NotImplementedError`.
- `CreatureCard(Card)` är en figur på brädet. Den lägger till `attack_name`, `attack`, `armor`, `magic` och `health`.
- `RitualCard(CreatureCard)` är ett ritualkort som inte kan anfalla, se Ritual.
- `SpellCard(Card)` är en spell som spelas från handen. Den lägger bara till `magic` (spellens styrka). `special` beskriver vad den gör.
- Alla tre har getters och setters för sina fält. Det är medvetet: kort påverkar varandras stats under spelet, och en magiker ska i framtiden kunna trolla fram påhittade kort, till exempel ett spöke av ett annat kort.
- `FactionName` är en Enum i `card.py` (GHOULS, ACADEMICS, SHOGGOTHS, DEEP_ONES). Kortets `faction` och `Faction.name` är ett `FactionName`, aldrig en sträng. Kortet känner bara till fraktionens namn, inte `Faction`-objektet, så att beroendet bara går åt ett håll (`Faction` → `Card`). Visa texten med `.value`.
- `Rarity` är en Enum i `card.py` (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY). Standard är `Rarity.COMMON`.
- `Special` är en Enum i `card.py`. Namnet (t.ex. `DEVOUR`) säger vilken förmåga det är, värdet är texten spelaren ser. `special=None` betyder ingen förmåga.
- `__str__` ger full visning med ikoner: ⚔️ attack, 🪄 magic, ❤️ health, 🛡️ armor, ☩ ritual.
- `short()` ger kompakt visning för brädet: `Namn [⚔️ 3 ❤️ 4 🛡️ 3 ☩ 3]`. ⚔️ och 🪄 visas bara om värdet är större än 0. Mellanslaget efter ikonen behövs: terminalen i VS Code ritar ⚔️, ❤️ och 🛡️ två rutor breda men räknar dem som en, så utan mellanslag hamnar siffran ovanpå ikonen.
- Koden använder 3 mellanslags indrag.

### Hjälte (`hero.py`) – byggs nu

- `Hero` är en egen klass och inte ett `Card`: den ligger inte i leken, spelas inte och har ingen rarity. (Källa: Fireplace, en Hearthstone-motor i Python, har `Hero` och `Minion` som skilda klasser.)
- Fält: `name`, `health` (30), `armor` och `magic` (0 från början), `ritual` (börjar på 0). Ritualmålet ligger kvar i `Faction`.
- Hjälten har armor och magic så att den kan vara mål för `damage_against(target)` precis som ett kort.
- Varje spelare har en egen hjälte (sammansättning: `Player` har en `Hero`), eftersom hjältens värden ändras under spelet.
- Hjälteförmågor är enumen `HeroAbility` i `hero.py`, skild från kortens `Special`. Samma mönster: namnet säger vilken förmåga, värdet är texten.
- Morrigan Upton (Ghouls): **Feast of Graves** – "Eat a card in your graveyard: one of your cards gains its attack and health".

### Terminalen (`terminal_ui.py`)

- All visning och inmatning i terminalen ligger i klassen `TerminalUI` i `terminal_ui.py`. Korten och spelarna vet inget om terminalen (separation of concerns, som i Model-View-Controller). `Player` gör aldrig `print` eller `input`.
- `Game` får sitt gränssnitt utifrån: `Game(player1, player2, TerminalUI())`, och anropar bara `self.ui.choose_move(...)`, `self.ui.choose_target(...)` osv. Spelet görs för terminalen först, sedan grafik: en grafisk version (t.ex. `PygameUI`) ska ha samma metodnamn, så att `Game` inte behöver ändras (Strategy-mönstret, Gang of Four).
- Färg per fraktion: figurer får en färg och spells en ljusare ton av samma färg. Ghouls är mörkröda, The Academics blå, Shoggoths gyllengula och The Deep Ones gröna.
- Färgerna är 24-bitars ANSI-koder (`rgb()`). Nycklarna i `FACTION_COLORS` är `FactionName`-värden.

### Strid (bestämt)

- Korttypen avgör hur ett kort gör skada:
  - Figurer (`CreatureCard`): skada = ⚔️ attack − målets 🛡️ armor.
  - Spells (`SpellCard`): skada = 🪄 magic − målets 🪄 magic.
- Skadan är minst 0 och dras från målets ❤️ health. Kortet dör vid 0.
- `magic` är alltså både spellens styrka och figurernas försvar mot magi.
- I koden räknar varje klass ut sin egen skada med `damage_against(target)` (polymorfism). Spelet frågar bara kortet och behöver inte kolla vilken sorts kort det är.
- Det finns inget `attack_type`-fält. Det togs bort för att klassen redan avgör sortens skada (YAGNI).
- The Academics: alla deras figurer är ganska svaga. De har svårt mot till exempel Ghouls i tier 2–3, som har hög armor. Academics styrka är spells: magisk skada räknas mot målets 🪄 magic, inte mot 🛡️ armor, så spells går igenom armor.

### Anfall (bestämt)

- Mål väljs i ordning: finns kort med Guard får bara de anfallas. Annars får alla kort i armén anfallas. Hjälten kan bara anfallas när armén är tom.
- Anfall i `Game.attack(attacker, target)`: anfallaren räknar skadan (`damage_against`), målet tar den (`take_damage`), motståndaren städar sin armé (`clear_dead_cards`).

### Tur (bestämt)

- Spelare 1 börjar. Slantsingling och mulligan väntar till senare.
- Starthand: 5 kort.
- I varje tur gör man två saker, i valfri ordning: **lägga ett kort** och **en action**, till exempel att anfalla med ett kort på brädet. När båda är gjorda går turen över.
- Finns inget kort som kan göra en action hoppas den över automatiskt.
- Att kunna välja "pass" kommer senare, inte i första versionen.
- Att spela en spell räknas som att lägga kortet för turen.
- Man drar 1 kort i början av sin egen tur, även första turen, som i Hearthstone. Då har man fler val när man spelar.

### Spellkort (bestämt)

- Spells spelas som i Hearthstone: välj kortet från handen, välj mål, och effekten sker direkt. Kortet hamnar aldrig på brädet.
- Man kan ångra medan man väljer (kort eller mål). När man har bekräftat är spellen kastad och kan inte tas tillbaka.
- Exempel: tier 5 hos Ghouls (Resurrect, Plague, Infect, Ruin m.fl.).
- **Tung dark magic kostar health.** Academics tyngsta spells skadar de egna korten i stället för att använda en egen stat för förstånd. Exempel: Necronomicon gör 3 skada på ett av de egna korten.
- **Utan eget kort på brädet fungerar inte tung magi.** Man får fortfarande spela spellen, men den gör ingenting. Spelet ska varna innan man bekräftar. Detta är inte byggt än.

### Ritual (bestämt)

- **Ritualkort** är bara tier 4-korten: de finns till för att bygga ritual och kan inte slåss (⚔️ 0). Andra kort kan också ha lite ☩, men räknas inte som ritualkort.
- I koden är ritualkort klassen `RitualCard(CreatureCard)` i `card.py`. Den är en egen klass eftersom beteendet skiljer sig: `can_attack()` ger `False` (för `CreatureCard` ger den `True`), och bara ritualkort kan få skydds-spells. Spelet känner igen dem med `isinstance(card, RitualCard)`.
- Sätt att bygga ritual: ritualkort (snabbt, men oskyddat), vanliga kort med lite ☩ (långsamt men säkrare) och spells.
- Ritual kan stjälas, men bara av fraktioner med dark magic: Ghouls och Academics.
- Ritualkort skyddas med `GUARD` på starka melee-kort (fienden måste anfalla dem först, som Taunt i Hearthstone; namnet Guard kommer från The Elder Scrolls: Legends) och med skydds-spells (Ghouls: Veil of Tiamat, Scales of Leviathan, Seal of Apep, Kiss of Lilith, Curse of Choronzon).
- Skydds-spellernas namn har anti-kosmisk inspiration: gamla kaosväsen och antigudar (Tiamat, Leviathan, Apep, Lilith, Choronzon).

### Deck (`deck.py`) – under diskussion, inte bestämt

Riktning som diskuterats:

- `Deck` hanterar bara högen: blanda, dra, räkna. Den får färdiga kort och vet inget om fraktioner.
- Fraktionen, eller en skaparfunktion för den, bygger fraktionens kort. Varje lek ska få nya kortobjekt, eftersom korten kan ändras under spelet.
- Spelaren har sin fraktion och sin lek.
- Ingen arvshierarki för lekar (som `GhoulDeck`). Lekarna fungerar likadant, och skillnaden ligger i korten.

### Öppna frågor

- Är hjälten ett kort i leken eller separat, som en spelarfigur?
- Ska alla lekar för en fraktion vara identiska, eller ska spelaren kunna välja kort?
- Vem bygger leken när ett spel startar: spelaren, spelet eller en meny?
- När en ghoul äter ett kort, får den kortets grundvärden eller värdena kortet hade när det dog?
- Är tier 4 hos Ghouls (rena ritualkort med ❤️ 0) figurer eller spells?
- `Player.play_card()` lägger alla kort i armén. Spells ska i stället verka och sedan hamna i gravhögen.
