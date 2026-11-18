"""
The Academics faction: their cards and the faction object.

Hero: Dr. Henry Armitage. Few, magic creatures that are weak in melee.
Their strength is spells from forbidden books.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import copy
from faction import Faction
from card import CreatureCard, RitualCard, SpellCard, Rarity, Special, FactionName
from hero import Hero, HeroAbility


# The Academics have no tier 1. Their creatures are few, magic and weak in melee:
# low armor, high magic. Their strength is spells from forbidden books.

# Tier 2: scholars of Arkham (5 cards x 2 copies = 10)
tier_2 = [
   CreatureCard(FactionName.ACADEMICS, "Miskatonic Student",
                attack_name="Heavy Textbook",
                attack=3,
                armor=1,
                magic=2,
                health=2,
                ritual=1,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Restricted Stacks Librarian",
                attack_name="Iron-Bound Tome",
                attack=3,
                armor=2,
                magic=2,
                health=2,
                ritual=0,
                special=Special.STUDY,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Dark Occultist",
                attack_name="Ceremonial Athame",
                attack=3,
                armor=1,
                magic=3,
                health=2,
                ritual=1,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Expedition Geologist",
                attack_name="Rock Hammer",
                attack=4,
                armor=2,
                magic=1,
                health=3,
                ritual=0,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.ACADEMICS, "Night Archivist",
                attack_name="Lantern Swing",
                attack=3,
                armor=1,
                magic=3,
                health=3,
                ritual=1,
                special=Special.STUDY,
                rarity=Rarity.RARE),
]

# Tier 3: named characters from Lovecraft's stories (4 cards x 2 copies = 8)
tier_3 = [
   CreatureCard(FactionName.ACADEMICS, "Dr. Francis Morgan",
                attack_name="Hunting Rifle",
                attack=5,
                armor=3,
                magic=3,
                health=6,
                ritual=1,
                special=Special.GUARD,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Herbert West",
                attack_name="Reagent Syringe",
                attack=4,
                armor=2,
                magic=4,
                health=5,
                ritual=1,
                special=None,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Keziah Mason",
                attack_name="Brown Jenkin's Bite",
                attack=4,
                armor=2,
                magic=5,
                health=4,
                ritual=2,
                special=None,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.ACADEMICS, "Wilbur Whateley",
                attack_name="Grasping Tentacles",
                attack=5,
                armor=2,
                magic=5,
                health=5,
                ritual=3,
                special=Special.SUMMON,
                rarity=Rarity.EPIC),
]

# Ritual builders only (5 cards x 1 copy = 5).
# High magic: hard to kill with spells, but weak against melee.
ritual_cards = [
   RitualCard(FactionName.ACADEMICS, "Lectern of the Madman",
              armor=0,
              magic=5,
              health=2,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Sentinel Hill Stone Circle",
              armor=0,
              magic=4,
              health=3,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "The Angled Attic",
              armor=0,
              magic=4,
              health=2,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Circle of Eleven Candles",
              armor=0,
              magic=5,
              health=2,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.ACADEMICS, "Midnight Seminar",
              armor=0,
              magic=3,
              health=3,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),
]

# Basic spells (6 cards x 2 copies = 12)
basic_spells = [
   SpellCard(FactionName.ACADEMICS, "Book of Sorrows",
             magic=3,
             ritual=0,
             special=Special.BOOK_OF_SORROWS,
             rarity=Rarity.UNCOMMON),

   SpellCard(FactionName.ACADEMICS, "Scroll of Rituals",
             magic=0,
             ritual=2,
             special=Special.SCROLL_OF_RITUALS,
             rarity=Rarity.UNCOMMON),

   SpellCard(FactionName.ACADEMICS, "Elder Sign",
             magic=3,
             ritual=0,
             special=Special.ELDER_SIGN,
             rarity=Rarity.UNCOMMON),

   SpellCard(FactionName.ACADEMICS, "Litany of Unmaking",
             magic=3,
             ritual=0,
             special=Special.LITANY_OF_UNMAKING,
             rarity=Rarity.UNCOMMON),

   SpellCard(FactionName.ACADEMICS, "Forbidden Codex",
             magic=0,
             ritual=0,
             special=Special.FORBIDDEN_CODEX,
             rarity=Rarity.UNCOMMON),

   SpellCard(FactionName.ACADEMICS, "Whispered Hex",
             magic=2,
             ritual=0,
             special=Special.WHISPERED_HEX,
             rarity=Rarity.UNCOMMON),
]

# Forbidden books (15 cards x 1 copy = 15). Heavy magic hurts your own cards.
spell_cards = [
   SpellCard(FactionName.ACADEMICS, "Necronomicon",
             magic=7,
             ritual=0,
             special=Special.NECRONOMICON,
             rarity=Rarity.EPIC),

   SpellCard(FactionName.ACADEMICS, "Pnakotic Manuscripts",
             magic=3,
             ritual=0,
             special=Special.PNAKOTIC_MANUSCRIPTS,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Cultes des Goules",
             magic=3,
             ritual=0,
             special=Special.CULTES_DES_GOULES,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Unaussprechlichen Kulten",
             magic=3,
             ritual=0,
             special=Special.UNAUSSPRECHLICHEN_KULTEN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Book of Eibon",
             magic=3,
             ritual=0,
             special=Special.BOOK_OF_EIBON,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "R'lyeh Text",
             magic=0,
             ritual=0,
             special=Special.RLYEH_TEXT,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Scroll of Dzyan",
             magic=2,
             ritual=0,
             special=Special.SCROLL_OF_DZYAN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Rite of the Thirteenth Hour",
             magic=2,
             ritual=0,
             special=Special.RITE_OF_THE_THIRTEENTH_HOUR,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Psalms of the Void",
             magic=2,
             ritual=0,
             special=Special.PSALMS_OF_THE_VOID,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "The King in Yellow",
             magic=0,
             ritual=0,
             special=Special.THE_KING_IN_YELLOW,
             rarity=Rarity.EPIC),

   SpellCard(FactionName.ACADEMICS, "Book of the Nameless Dead",
             magic=0,
             ritual=0,
             special=Special.BOOK_OF_THE_NAMELESS_DEAD,
             rarity=Rarity.RARE),

   # Spells that protect ritual
   SpellCard(FactionName.ACADEMICS, "Seal of the Black Sun",
             magic=0,
             ritual=0,
             special=Special.SEAL_OF_THE_BLACK_SUN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Mirror of Nitocris",
             magic=0,
             ritual=0,
             special=Special.MIRROR_OF_NITOCRIS,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Ward of the Unbegotten",
             magic=3,
             ritual=0,
             special=Special.WARD_OF_THE_UNBEGOTTEN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.ACADEMICS, "Codex of the Eleven Keys",
             magic=3,
             ritual=0,
             special=Special.CODEX_OF_THE_ELEVEN_KEYS,
             rarity=Rarity.RARE),
]

# Tier 2-3 and basic spells: two copies each. Ritual cards and forbidden books: one copy each.
# 10 + 8 + 5 + 12 + 15 = 50 cards, same as the Ghouls.
academic_cards = []
for card in tier_2 + tier_3 + basic_spells:
   academic_cards.append(card)
   academic_cards.append(copy.copy(card))
academic_cards += ritual_cards
academic_cards += spell_cards

henry_armitage = Hero("Dr. Henry Armitage", ability=HeroAbility.ELEVENTH_SEAL)

academics = Faction(FactionName.ACADEMICS, henry_armitage, ritual_goal=15, cards=academic_cards)
