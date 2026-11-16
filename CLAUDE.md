# Ritual

## Arbetssätt

- Sluta ge snabblösningar. Ge alltid bästa praxis och absolut bästa OOP.
- Basera designförslag på etablerade källor (designmönster, hur riktiga kortspelsmotorer är byggda) och ange källorna. Gissa inte. Skilj tydligt på vad källan faktiskt säger och vad som är din egen tillämpning på projektet.
- Tänk igenom ansvarsfördelning och relationer mellan klasser innan du föreslår kod. Fråga om designbeslut hellre än att gissa.
- Arv bara när beteendet faktiskt skiljer sig. Sammansättning (en spelare *har* en lek, en lek *innehåller* kort) är lika viktig som arv.

## Vad vi bygger

Ett Lovecraft-inspirerat kortspel i Python (kursen Prog2), spelat i terminalen.

Spelare har ingen hälsa. Det som räknas heter ritual: varje fraktion har ett ritualmål, och spelaren samlar ritualpoäng mot det. Motståndaren kan sinka (sänka) ens ritual.

Strategin är att balansera: försvara sin ritual, öka den, och ha både försvarande och anfallande kort.

**Vinstvillkor** (man vinner om något av dessa gäller):
1. Man når sitt ritualmål.
2. Motståndaren är utplånad: inga kort på brädet och inga kort kvar (varken i hand eller lek).
3. Man har byggt upp mer ritual än motståndaren.

Man vinner INTE genom att motståndaren har noll ritual.

### Fraktioner

Beskrivna i `README.md` – läs den innan du frågar om fraktionerna. Hjältebilder finns i `factions/heroes/`.

Varje fraktion har sin egen hjälte, sina egna kort och sina egna skills/förmågor.

- **The Deep Ones**: hjälte The Dagon King. Swarm och förvandling: svaga ensamma, farliga i grupp, kan förvandla mänskliga kort till djupdykare.
- **Ghouls**: hjälte Morrigan Upton. Kyrkogård: blir starkare när pjäser dör, kan äta kort i gravhögen och stjäla deras stats och förmågor.
- **Shoggoths**: hjälte Ur-Shoggothen. Ramp och absorption: dyra, enorma monster som växer och absorberar närliggande pjäser.
- **The Academics**: hjälte Dr. Henry Armitage. Spells och kunskap: drar mycket kort, Discover via förbjudna böcker, tar skada eller tappar förstånd av stark magi.

### Card (`card.py`)

- Fält: `faction`, `name`, `attack`, `armor`, `magic`, `ritual`, `special`, `rarity`.
- Har getters och setters för alla fält. Det är medvetet: kort påverkar varandras stats under spelet, och en magiker ska i framtiden kunna trolla fram påhittade kort, till exempel ett spöke av ett annat kort.
- `__str__` ger full visning med ikoner: ⚔️ attack, 🛡️ armor, 🪄 magic, ☩ ritual.
- `short()` ger kompakt visning för brädet: `Namn [⚔️3 🛡️3 🪄2 ☩3]`.
- Koden använder 3 mellanslags indrag.

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
