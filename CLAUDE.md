# Ritual

## Arbetssätt

- Användaren skriver koden själv. Beskriv steg för steg vad som ska byggas, ett steg i taget, och skriv inte koden åt hen. Hjälp till med kod bara när hen ber om det.
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
1. Man når sitt ritualmål.
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

- `Card` är grundklassen med det som alla kort har: `faction`, `name`, `ritual`, `special`, `rarity`, `cost`. Den skapas inte direkt; `short()` kastar `NotImplementedError`.
- `CreatureCard(Card)` är en figur på brädet. Den lägger till `attack_name`, `attack`, `armor`, `magic`, `health`, `max_health` och `buffs` (en `BuffList`). Getters som `get_attack()` räknar in buffarna; fälten är grundvärdena. Använd alltid getters, inte fälten direkt, när värdet ska visas eller räknas med.
- `RitualCard(CreatureCard)` är ett ritualkort som inte kan anfalla, se Ritual.
- `SpellCard(Card)` är en spell som spelas från handen. Den lägger bara till `magic` (spellens styrka). `special` beskriver vad den gör.
- Alla tre har getters och setters för sina fält. Det är medvetet: kort påverkar varandras stats under spelet, och en magiker ska i framtiden kunna trolla fram påhittade kort, till exempel ett spöke av ett annat kort.
- `FactionName` är en Enum i `card.py` (GHOULS, ACADEMICS, SHOGGOTHS, DEEP_ONES). Kortets `faction` och `Faction.name` är ett `FactionName`, aldrig en sträng. Kortet känner bara till fraktionens namn, inte `Faction`-objektet, så att beroendet bara går åt ett håll (`Faction` → `Card`). Visa texten med `.value`.
- `Rarity` är en Enum i `card.py` (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY). Standard är `Rarity.COMMON`.
- `Special` är en Enum i `card.py`. Namnet (t.ex. `DEVOUR`) säger vilken förmåga det är, värdet är texten spelaren ser. `special=None` betyder ingen förmåga.
- `__str__` ger full visning med ikoner: ⚔️ attack, 🪄 magic, ❤️ health, 🛡️ armor, ☩ ritual.
- `short()` ger kompakt visning för brädet: `Namn [⚔️ 3 ❤️ 4 🛡️ 3 ☩ 3]`. ⚔️ och 🪄 visas bara om värdet är större än 0. Mellanslaget efter ikonen behövs: terminalen i VS Code ritar ⚔️, ❤️ och 🛡️ två rutor breda men räknar dem som en, så utan mellanslag hamnar siffran ovanpå ikonen.
- Koden använder 3 mellanslags indrag.

### Hjälte (`hero.py`)

- `Hero` är en egen klass och inte ett `Card`: den ligger inte i leken, spelas inte och har ingen rarity. (Källa: Fireplace, en Hearthstone-motor i Python, har `Hero` och `Minion` som skilda klasser.)
- Fält: `name`, `health` (30), `max_health`, `armor` och `magic` (0 från början), `ritual` (börjar på 0), `buffs` (en `BuffList`, t.ex. Seal of Apep). Ritualmålet ligger kvar i `Faction`.
- `add_ritual()` och `lose_ritual()` (aldrig under 0, och ingenting händer om ritualen är skyddad).
- Hjälteförmågorna (Feast of Graves, The Eleventh Seal) är **inte byggda** än.
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

- Mål väljs i ordning (`Player.get_targets()`): finns kort med Guard får bara de anfallas. Annars får alla kort i armén anfallas. Hjälten kan bara anfallas när armén är tom. Dolda kort (Veil of Tiamat) räknas inte alls.
- Anfall i `Game.attack(attacker, target)`: triggers får först ta hand om anfallet (Mirror of Nitocris); annars räknar anfallaren skadan (`damage_against`), målet tar den (`take_damage`) och triggers reagerar (Curse of Choronzon). Sist städas döda kort bort på båda sidor.
- Målet slår inte tillbaka (i Hearthstone gör båda korten skada på varandra). *Inte bestämt om det ska ändras.*

### Tur (bestämt)

- Spelare 1 börjar. Slantsingling och mulligan väntar till senare.
- Starthand: 5 kort.
- I varje tur, i valfri ordning: **lägg så många kort du har råd med** (se Resursen) och gör **en action**, till exempel att anfalla med ett kort på brädet. *Om en action per tur ska finnas kvar, eller om alla kort i armén får anfalla en gång var, är inte bestämt.*
- Turen går över när inget mer går att göra, eller när spelaren väljer "0) end turn", till exempel för att spara resurs till ett dyrt kort.
- Finns inget kort som kan göra en action hoppas den över automatiskt.
- Man drar 1 kort i början av sin egen tur, även första turen, som i Hearthstone. Då har man fler val när man spelar.

### Resursen för att lägga kort (bestämt och byggt)

*Namnet är inte bestämt. "Essence" är bortvalt; det ska låta Darkest Dungeon/Lovecraft (förslag: Dread, Resolve, Devotion, Omen, Ichor). I koden heter den tills vidare `resource` (`Player.resource`, `Game.RESOURCE_PER_TURN`, `RESOURCE_NAME` i `terminal_ui.py`), så den byts lätt.*

- **Overload** (som hos Shaman i Hearthstone): ett kort kan låna resurs från nästa tur. `Player.overload` dras av när resursen fylls på (`refill_resource()`), aldrig under 0.
- Academics har två spells som ger mer att spendera nu (som Innervate i Hearthstone, men med ett pris). De ersatte Elder Sign och Litany of Unmaking, som överlappade Ward of the Unbegotten och Rite of the Thirteenth Hour. Två exemplar var, leken är kvar på 50 kort:
  - **The Silver Key** (kostnad 0): +2 resurs nu, Overload (2). Man lånar från framtiden.
  - **De Vermis Mysteriis** (kostnad 0): +2 resurs nu, den egna hjälten tar 3 skada. Man betalar med blod.
- I koden: `Card.cost`; `Player.refill_resource()`, `gain_resource()`, `add_overload()`, `can_afford()`, `has_affordable_card()`; `Player.play_card()` drar kostnaden (och kastar `ValueError` om man inte har råd). Terminalen visar kostnaden i handen som `(2)` och vägrar kort man inte har råd med.
- Som credits i Android: Netrunner: varje spelare får **+1 av resursen i början av sin tur**, börjar på 0 och har inget tak. Det som inte används **sparas** till nästa tur. Man kan alltså spara ihop till ett dyrt kort, till exempel ett ritualkort tidigt, men gör då mindre under tiden.
- Alla får lika mycket, som mana i Hearthstone: resursen är inte kopplad till health eller ritual. (Ritualen som budget valdes bort: den som leder skulle få fler kort och dra ifrån, en positiv återkopplingsloop.)
- Varje kort har en **kostnad** (`cost`, ett eget fält på `Card`). Man får lägga så många kort man har råd med.
- Startkostnader: figurer kostar sin tier (1–3), ritualkort (tier 4) kostar 4, Academics basic spells kostar 1, övriga spells 2, tunga spells (Necronomicon, Pnakotic Manuscripts) 3. Justeras efter speltest. Kort som behöver vara dyrare (t.ex. Shoggoths stora monster, 6–8) flyttas till högre tier eller får en egen kostnad.
- Samma mekanik för alla fraktioner. Senare kan varje fraktion visa sitt eget namn i spelet, t.ex. Sanity för Academics och Stamina för The Deep Ones.

### Spellkort (bestämt)

- Spells spelas som i Hearthstone: välj kortet från handen, välj mål, och effekten sker direkt. Kortet hamnar aldrig på brädet.
- **Guard skyddar inte mot spells** (som Taunt i Hearthstone). Annars har Academics ingen chans. `Player.get_spell_targets()` ger hela armén plus hjälten.
- Varje effekt avgör själv vilka mål den får välja (`get_targets`), som i Hearthstone där kortets text styr (Fireplace: play requirements som `REQ_ENEMY_TARGET`). Se "Mål" nedan.
- **Effekter är egna objekt (sammansättning).** `SpellCard` *har* en effekt, till exempel `DamageOneEnemy`, som gör jobbet med `apply(...)`. Samma effekt kan återanvändas av flera spells. Källa: Fireplace (`play = Hit(TARGET, 6)`) och Forge (`DealDamage`); mönstret Command/Strategy (Gang of Four). Ingen lång `if/elif` över `Special`.
- **Styrkan i en effekt är spellens 🪄 magic** (skada, läkning, buff, hur mycket ritual som sänks eller stjäls). Undantag: Scroll of Rituals använder sin ☩. Plague och Scales of Leviathan hade 🪄 0 och fick 🪄 2.
- En effekt svarar på `needs_target()` och `get_targets(game)`: effekten själv säger vilka mål som är tillåtna. Har en spell inga giltiga mål kan den inte spelas (den betalas inte).
- Byggda effekter i `effect.py` (grupp A, omedelbara): `DamageOneEnemy(include_hero)`, `DamageAllEnemyCards(own_damage)`, `HealOwnHero`, `HealAllOwnCards`, `LowerAttack`, `RemoveArmor`, `BuffOwnCard(armor, magic, health, ritual_only)`, `LowerRitual`, `StealRitual`, `GainRitual`, `DrawCards(n)`, `ReviveRandom`, `ReturnRandomToHand`, `LookAtTopCards(n)`, `PayWithBlood(n)`, `GainResource(...)` och `Combined(...)` (flera effekter i samma spell, Composite-mönstret; bara den första får ett mål).
- Läkning går aldrig över `max_health` (både kort och hjälte), som i Hearthstone. Återupplivade kort kommer tillbaka med full health.
- **Buffar (grupp B, byggt):** effekter som varar "until your next turn" eller "this turn" är `Buff`-objekt (`buff.py`) som fästs på ett kort eller en hjälte, som enchantments i Hearthstone, `Buff` i Fireplace och buffar/debuffar i Darkest Dungeon. Kortets egna värden ändras aldrig: `get_attack()`, `get_armor()`, `get_magic()`, `can_attack()`, `has_guard()` osv. räknar in buffarna. När buffen går ut tas den bara bort. (Command-mönstret med `undo` valdes bort: `undo` blir fel när ett värde stannat på 0.)
  - `CreatureCard` och `Hero` *har* en `BuffList` (sammansättning), så logiken står på ett ställe.
  - En buff tillhör spelaren som lade den. "Until your next turn" går ut i början av den spelarens nästa tur, "this turn" i slutet av turen (`Game.remove_expired_buffs`). Kort som dör tappar sina buffar.
  - Effekten `GiveBuff(receiver, ...)` ger buffar: Terror, Veil of Tiamat, Seal of Apep, Kiss of Lilith, Whispered Hex, Scroll of Dzyan, Rite of the Thirteenth Hour, The King in Yellow, Seal of the Black Sun, Ward of the Unbegotten.
  - Ett kort som är dolt (Veil of Tiamat) kan inte anfallas av figurer och skyddar inte heller hjälten. Spells kan fortfarande träffa det.
  - `Faction` skapar kort och hjältar med `copy.deepcopy`, så att varje kopia har en egen lista med buffar.
- **Triggers (grupp C, byggt):** effekter som väntar på att något ska hända är `Trigger`-objekt (`trigger.py`), Observer-mönstret (Gang of Four), som Secrets och gift i Hearthstone och event-lyssnare i Fireplace. `Game` har en lista med triggers och meddelar dem `before_attack` (kan ta hand om anfallet), `after_attack` och `at_turn_start`. En trigger som har gjort sitt markerar sig som förbrukad och tas bort.
  - **Infect:** fiendekortet tar 🪄 magic i skada i början av varje tur för den som smittade det, tills kortet dör eller lämnar brädet.
  - **Mirror of Nitocris:** nästa melee-anfall mot det valda egna kortet träffar anfallaren i stället (engångs).
  - **Curse of Choronzon:** nästa fiendekort som anfaller ett av dina ritualkort tar samma skada som det gjorde (engångs).
  - Triggers gäller bara melee-anfall (`Game.attack`), inte spells.
- **Alla spells har en effekt.** Det tillfälliga blocket som bytte ut spells utan effekt är borttaget.
- Man kan ångra medan man väljer (kort eller mål). När man har bekräftat är spellen kastad och kan inte tas tillbaka. *Ångra är inte byggt: i dag går det inte att backa ur målvalet.*
- Exempel: tier 5 hos Ghouls (Resurrect, Plague, Infect, Ruin m.fl.).
- **Tung dark magic kostar health.** Academics tyngsta spells skadar de egna korten i stället för att använda en egen stat för förstånd. Exempel: Necronomicon gör 3 skada på ett av de egna korten.
- **Mål (bestämt, som i Hearthstone):** spelaren väljer högst **ett** mål per spell. Allt annat sker automatiskt eller slumpat.
  - "One enemy" (fiendens figur eller hjälte): Book of Sorrows, Necrotic Bolt, Necronomicon. Texterna ska säga "one enemy".
  - Bara fiendens figurer: Infect, Drain Life, Wither, Terror, Whispered Hex, Cultes des Goules. Area-spells (Plague, Pnakotic Manuscripts) träffar bara figurer, inte hjälten.
  - Eget kort: Bone Ward, Kiss of Lilith, Ward of the Unbegotten, Mirror of Nitocris. Eget ritualkort: Veil of Tiamat, Scales of Leviathan, Codex of the Eleven Keys.
  - Inget mål: resten (gäller alla kort, spelaren eller ritualen).
  - Drain Life läker automatiskt den egna hjälten (som Drain Life i Hearthstone).
  - Resurrect och Book of the Nameless Dead hämtar ett **slumpat** kort ur gravhögen (som Resurrect i Hearthstone).
  - Forbidden Codex: titta på tre kort i leken och ta ett (som Tracking i Hearthstone).
- **Priset för tung magi** (Necronomicon, Unaussprechlichen Kulten, R'lyeh Text): skadan tas automatiskt av ett slumpat eget kort som har **minst lika mycket health som priset** (kortet får dö, men ett kort med 2 health väljs aldrig för ett pris på 3). Finns inget sådant kort tar den egna hjälten skadan, och dör hjälten förlorar man (oavgjort om motståndarens hjälte dör samtidigt). (Ersätter den gamla regeln att tung magi inte fungerar utan eget kort.)

### Ritual (bestämt)

- **Ritualkort** är bara tier 4-korten: de finns till för att bygga ritual och kan inte slåss (⚔️ 0). Andra kort kan också ha lite ☩, men räknas inte som ritualkort.
- I koden är ritualkort klassen `RitualCard(CreatureCard)` i `card.py`. Den är en egen klass eftersom beteendet skiljer sig: `can_attack()` ger `False` (för `CreatureCard` ger den `True`), och bara ritualkort kan få skydds-spells. Spelet känner igen dem med `isinstance(card, RitualCard)`.
- **När ☩ räknas (bestämt):** i början av sin tur får hjälten ☩ från alla egna kort på brädet (`Player.collect_ritual()` → `Hero.add_ritual()`), så länge korten ligger kvar. Därför är det viktigt att skydda ritualkorten. Når man målet vinner man direkt. Målet 15 kan behöva höjas.
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

- Ska alla lekar för en fraktion vara identiska, eller ska spelaren kunna välja kort?
- Vem bygger leken när ett spel startar: spelaren, spelet eller en meny?
- När en ghoul äter ett kort, får den kortets grundvärden eller värdena kortet hade när det dog?
- En action per tur, eller får alla kort i armén anfalla en gång var (som i Hearthstone)?
- Ska målet slå tillbaka vid anfall (som i Hearthstone)?
- Ska ett nytt kort få anfalla samma tur som det läggs ("summoning sickness" i Hearthstone)?
- Ska armén ha ett max antal kort (Hearthstone: 7)?
- Vad heter resursen? (Dread, Resolve, Devotion, Omen, Ichor …)
- Idé: måste man hålla ritualmålet i 3 rundor för att vinna? Provas när spelet går att balansera (TODO i `Game.has_won`).
- Ritualmålet 15 och `RESOURCE_PER_TURN = 1` ska provas i spel.

## Läget (2026-11-18)

**Fungerar:** en hel match i terminalen mellan Academics och Ghouls (`main.py`). Dra kort, resurs med sparande och overload, lägga kort, anfall med Guard, ritual som växer varje tur, vinst/förlust/oavgjort. Alla 36 spells har effekter (omedelbara, buffar och triggers). `TerminalUI` är utbytbart mot ett grafiskt gränssnitt.

**Kontrollerat:** alla moduler importeras; 300 matcher med slumpbotar utan krascher, alla spells spelades; tio regelkontroller (buffar som går ut, Seal of Apep, Mirror, Curse, Infect, Veil, blodpris, läkningstak, overload) stämde. Med slumpbotar vann Academics 39 % och Ghouls 61 % (före spelleffekterna: Academics 20 % med en enklare bot). Testskripten låg i scratchpad och finns inte i projektet.

**Inte byggt än:**
- Figurernas förmågor (`Special` på figurer): DEVOUR, SACRIFICE, STUDY, SUMMON. Bara GUARD fungerar.
- Hjälteförmågorna Feast of Graves och The Eleventh Seal.
- Visa i terminalen att ett kort är smittat (Infect) eller att Mirror/Curse väntar.
- Visa motståndarens bräde under ens egen tur, och en text efter anfall (hur mycket skada, vilket kort som dog).
- Spelet kan hänga sig om båda spelarna har slut på kort och ingen kan anfalla.
- Mulligan och slantsingling.
- Shoggoths och The Deep Ones (bara Academics och Ghouls är byggda).

**Förslag på nästa steg:** commit, sedan speltesta själv; därefter balans (en smartare bot för jämförelser) och de öppna frågorna ovan.
