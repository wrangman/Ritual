"""
The Academics faction: their cards and the faction object.

Hero: Dr. Henry Armitage. Few, magic creatures that are weak in melee.
Their strength is spells from forbidden books.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import copy
from effect import (DamageOneEnemy, GainResource, DamageAllEnemyCards,
                    LowerAttack, LowerRitual, StealRitual, GainRitual, HealOwnHero,
                    DrawCards, ReturnRandomToHand, LookAtTopCards, DamageOwnHero, Combined,
                    GiveBuff, ReflectNextAttack, SummonGhost, DrainHealth)
from faction import Faction
from card import CreatureCard, RitualCard, SpellCard, Rarity, Special, FactionName
from hero import Hero, HeroAbility


# The Academics have fewer creatures than the Ghouls and more spells.
# Their creatures have high magic. Their strength is spells from forbidden books.

# Tier 1: novices at Miskatonic University (5 cards x 1 copy = 5).
# Lika starka som Ghouls tier 1, men med lite 🪄 magic, som skyddar mot spells.
tier_1 = [
   CreatureCard(FactionName.ACADEMICS, "Novice Scholar",
                attack_name="Ink-Stained Fist",
                attack=1,
                magic=2,
                health=3,
                ritual=0,
                special=None,
                cost=1,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.ACADEMICS, "Novice Occultist",
                attack_name="Chalk Sigil",
                attack=2,
                magic=2,
                health=2,
                ritual=0,
                special=None,
                cost=1,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.ACADEMICS, "Novice Antiquarian",
                attack_name="Brass Magnifier",
                attack=2,
                magic=1,
                health=2,
                ritual=0,
                special=None,
                cost=1,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.ACADEMICS, "Novice Medium",
                attack_name="Spirit Knock",
                attack=1,
                magic=3,
                health=2,
                ritual=0,
                special=None,
                cost=1,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.ACADEMICS, "Novice Field Researcher",
                attack_name="Survey Pick",
                attack=2,
                magic=0,
                health=3,
                ritual=0,
                special=None,
                cost=1,
                rarity=Rarity.COMMON),
]

# Tier 2: scholars of Arkham (5 cards x 2 copies = 10)
tier_2 = [
   CreatureCard(FactionName.ACADEMICS, "Miskatonic Apprentice",
                attack_name="Heavy Textbook",
                attack=3,
                magic=2,
                health=4,
                ritual=0,
                special=Special.SACRIFICE,
                cost=2,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Restricted Stacks Librarian",
                attack_name="Iron-Bound Tome",
                attack=2,
                magic=2,
                health=3,
                ritual=0,
                special=Special.STUDY,
                cost=2,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Dark Occultist",
                attack_name="Ceremonial Athame",
                attack=2,
                magic=2,
                health=1,
                ritual=1,
                special=Special.SACRIFICE,
                cost=2,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Expedition Geologist",
                attack_name="Rock Hammer",
                attack=4,
                magic=1,
                health=5,
                ritual=0,
                special=None,
                cost=2,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Night Archivist",
                attack_name="Lantern Swing",
                attack=1,
                magic=2,
                health=4,
                ritual=0,
                special=Special.STUDY,
                cost=2,
                rarity=Rarity.RARE),
]

# Tier 3: named characters from Lovecraft's stories (4 cards x 2 copies = 8)
tier_3 = [
   CreatureCard(FactionName.ACADEMICS, "Dr. Francis Morgan",
                attack_name="Hunting Rifle",
                attack=4,
                magic=2,
                health=4,
                ritual=1,
                special=Special.GUARD,
                cost=3,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Herbert West",
                attack_name="Reagent Syringe",
                attack=4,
                magic=4,
                health=5,
                ritual=1,
                special=None,
                cost=3,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Keziah Mason",
                attack_name="Brown Jenkin's Bite",
                attack=4,
                magic=5,
                health=4,
                ritual=1,
                special=None,
                cost=3,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Wilbur Whateley",
                attack_name="Grasping Tentacles",
                attack=4,
                magic=2,
                health=5,
                ritual=0,
                special=Special.SUMMON,
                cost=4,
                rarity=Rarity.EPIC),
]

# Ritual builders only (5 cards x 1 copy = 5).
# High magic: hard to kill with spells, but weak against melee.
# ☩ 2–3 (sänkt från 4–5 2026-11-19): med två ritualkort på brädet nåddes målet 15 på två turer.
# Figurer ger högst ☩ 1, så att ritualkorten är det som bygger ritualen.
ritual_cards = [
   RitualCard(FactionName.ACADEMICS, "Lectern of the Madman",
              magic=4,
              health=6,
              ritual=3,
              special=None,
              cost=4,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Sentinel Hill Stone Circle",
              magic=4,
              health=6,
              ritual=3,
              special=None,
              cost=4,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "The Angled Attic",
              magic=4,
              health=10,
              ritual=2,
              special=None,
              cost=4,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Circle of Eleven Candles",
              magic=4,
              health=10,
              ritual=2,
              special=None,
              cost=4,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Midnight Seminar",
              magic=4,
              health=10,
              ritual=2,
              special=None,
              cost=4,
              rarity=Rarity.LEGENDARY),
]

# Book of Sorrows: Academics enda billiga skada, därför två exemplar (1 card x 2 copies = 2)
book_of_sorrows = SpellCard(FactionName.ACADEMICS, "Book of Sorrows",
                            special=Special.BOOK_OF_SORROWS,
                            cost=1,
                            rarity=Rarity.UNCOMMON,
                            effect=DamageOneEnemy(2))

# The other basic spells (5 cards x 1 copy = 5). Förut två exemplar var;
# de andra platserna gick till tier 1.
basic_spells = [
   SpellCard(FactionName.ACADEMICS, "Scroll of Rituals",
             special=Special.SCROLL_OF_RITUALS,
             cost=1,
             rarity=Rarity.UNCOMMON,
             effect=GainRitual(2)),

   # Ger mer att spendera nu, betalt med blod: den egna hjälten tar skada.
   SpellCard(FactionName.ACADEMICS, "De Vermis Mysteriis",
             special=Special.DE_VERMIS_MYSTERIIS,
             cost=0,
             rarity=Rarity.UNCOMMON,
             effect=GainResource(2, hero_damage=1)),

   # Ger mer att spendera nu, lånat från framtiden: nästa tur får man mindre (overload).
   SpellCard(FactionName.ACADEMICS, "The Silver Key",
             special=Special.THE_SILVER_KEY,
             cost=0,
             rarity=Rarity.UNCOMMON,
             effect=GainResource(2, overload=2)),

   SpellCard(FactionName.ACADEMICS, "Forbidden Codex",
             special=Special.FORBIDDEN_CODEX,
             cost=1,
             rarity=Rarity.UNCOMMON,
             effect=LookAtTopCards(3)),

   SpellCard(FactionName.ACADEMICS, "Whispered Hex",
             special=Special.WHISPERED_HEX,
             cost=1,
             rarity=Rarity.UNCOMMON,
             effect=Combined(GiveBuff(GiveBuff.ENEMY_CARD, attack=-2), DrawCards(1))),
]

# Ghosts: creatures that are not in the deck. Spells summon a new copy each time.
# They give no ritual: they are conjured, not part of the ritual.
the_unbegotten = CreatureCard(FactionName.ACADEMICS, "The Unbegotten",
                              attack_name="Cold Grasp",
                              attack=4,
                              magic=1,
                              health=8,
                              ritual=0,
                              special=Special.GUARD,
                              cost=3,
                              rarity=Rarity.RARE)

void_wraith = CreatureCard(FactionName.ACADEMICS, "Void Wraith",
                           attack_name="Wail from the Void",
                           attack=4,
                           magic=4,
                           health=5,
                           ritual=0,
                           special=None,
                           cost=3,
                           rarity=Rarity.RARE)

# Forbidden books (15 cards x 1 copy = 15).
spell_cards = [
   SpellCard(FactionName.ACADEMICS, "Necronomicon",
             special=Special.NECRONOMICON,
             cost=4,
             rarity=Rarity.EPIC,
             effect=DamageOneEnemy(10)),

   SpellCard(FactionName.ACADEMICS, "Pnakotic Manuscripts",
             special=Special.PNAKOTIC_MANUSCRIPTS,
             cost=3,
             rarity=Rarity.EPIC,
             effect=Combined(DamageAllEnemyCards(3), HealOwnHero(3))),

   SpellCard(FactionName.ACADEMICS, "Cultes des Goules",
             special=Special.CULTES_DES_GOULES,
             cost=1,
             rarity=Rarity.RARE,
             effect=LowerAttack(4)),

   SpellCard(FactionName.ACADEMICS, "Unaussprechlichen Kulten",
             special=Special.UNAUSSPRECHLICHEN_KULTEN,
             cost=2,
             rarity=Rarity.RARE,
             effect=Combined(StealRitual(3), DamageOwnHero(2))),

   SpellCard(FactionName.ACADEMICS, "Book of Eibon",
             special=Special.BOOK_OF_EIBON,
             cost=2,
             rarity=Rarity.RARE,
             effect=LowerRitual(4)),

   SpellCard(FactionName.ACADEMICS, "R'lyeh Text",
             special=Special.RLYEH_TEXT,
             cost=2,
             rarity=Rarity.RARE,
             effect=DrawCards(2)),

   SpellCard(FactionName.ACADEMICS, "Scroll of Dzyan",
             special=Special.SCROLL_OF_DZYAN,
             cost=1,
             rarity=Rarity.RARE,
             effect=Combined(DrawCards(1), GiveBuff(GiveBuff.ALL_OWN_CARDS, magic=2))),

   SpellCard(FactionName.ACADEMICS, "Rite of the Thirteenth Hour",
             special=Special.RITE_OF_THE_THIRTEENTH_HOUR,
             cost=1,
             rarity=Rarity.RARE,
             effect=GiveBuff(GiveBuff.ALL_OWN_CARDS, attack=3, this_turn_only=True)),

   SpellCard(FactionName.ACADEMICS, "Psalms of the Void",
             special=Special.PSALMS_OF_THE_VOID,
             cost=3,
             rarity=Rarity.RARE,
             effect=SummonGhost(void_wraith, hidden=True)),

   SpellCard(FactionName.ACADEMICS, "The King in Yellow",
             special=Special.THE_KING_IN_YELLOW,
             cost=2,
             rarity=Rarity.EPIC,
             effect=Combined(GiveBuff(GiveBuff.ALL_ENEMY_CARDS, cannot_attack=True), DrawCards(1))),

   SpellCard(FactionName.ACADEMICS, "Book of the Nameless Dead",
             special=Special.BOOK_OF_THE_NAMELESS_DEAD,
             cost=1,
             rarity=Rarity.RARE,
             effect=ReturnRandomToHand()),

   # Spells that protect ritual
   SpellCard(FactionName.ACADEMICS, "Seal of the Black Sun",
             special=Special.SEAL_OF_THE_BLACK_SUN,
             cost=1,
             rarity=Rarity.EPIC,
             effect=GiveBuff(GiveBuff.ALL_OWN_RITUAL_CARDS, no_melee_damage=True)),

   SpellCard(FactionName.ACADEMICS, "Mirror of Nitocris",
             special=Special.MIRROR_OF_NITOCRIS,
             cost=2,
             rarity=Rarity.RARE,
             effect=Combined(ReflectNextAttack(), DrawCards(1))),

   SpellCard(FactionName.ACADEMICS, "Ward of the Unbegotten",
             special=Special.WARD_OF_THE_UNBEGOTTEN,
             cost=3,
             rarity=Rarity.RARE,
             effect=SummonGhost(the_unbegotten)),

   SpellCard(FactionName.ACADEMICS, "Codex of the Eleven Keys",
             special=Special.CODEX_OF_THE_ELEVEN_KEYS,
             cost=2,
             rarity=Rarity.RARE,
             effect=DrainHealth(3)),
]

# Tier 2-3 and Book of Sorrows: two copies each.
# Tier 1, the other basic spells, ritual cards and forbidden books: one copy each.
# 5 + 10 + 8 + 2 + 5 + 5 + 15 = 50 cards, same as the Ghouls.
academic_cards = []
for card in tier_2 + tier_3 + [book_of_sorrows]:
   academic_cards.append(card)
   academic_cards.append(copy.copy(card))
academic_cards += tier_1
academic_cards += basic_spells
academic_cards += ritual_cards
academic_cards += spell_cards

henry_armitage = Hero("Dr. Henry Armitage", ability=HeroAbility.ELEVENTH_SEAL)

academics = Faction(FactionName.ACADEMICS, henry_armitage, ritual_goal=15, cards=academic_cards)
