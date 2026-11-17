"""
The Ghouls faction: their cards and the faction object.

Hero: Morrigan Upton. Tough creatures that grow stronger when cards die,
and spells that work through the graveyard.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import copy
from faction import Faction
from card import CreatureCard, RitualCard, SpellCard, Rarity, Special, FactionName
from hero import Hero, HeroAbility


# Tier 1: low stats, no ritual (6 cards x 2 copies = 12)
tier_1 = [
   CreatureCard(FactionName.GHOULS, "Corpse Looter",
                attack_name="Grave Knife",
                attack=2,
                armor=1,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.GHOULS, "Gravedigger",
                attack_name="Rusty Shovel",
                attack=1,
                armor=2,
                magic=0,
                health=1,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.GHOULS, "Changeling Child",
                attack_name="Needle Teeth",
                attack=1,
                armor=1,
                magic=0,
                health=1,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.GHOULS, "Tunnel Scavenger",
                attack_name="Filthy Claws",
                attack=2,
                armor=2,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.GHOULS, "Bone Gnawer",
                attack_name="Gnashing Jaws",
                attack=2,
                armor=1,
                magic=0,
                health=3,
                ritual=0,
                special=Special.DEVOUR,
                rarity=Rarity.COMMON),

   CreatureCard(FactionName.GHOULS, "Mourner in Black",
                attack_name="Funeral Dagger",
                attack=1,
                armor=2,
                magic=0,
                health=2,
                ritual=1,
                special=None,
                rarity=Rarity.COMMON),
]

# Tier 2: medium stats, ritual max 2 (5 cards x 2 copies = 10)
tier_2 = [
   CreatureCard(FactionName.GHOULS, "Grave Eater",
                attack_name="Rending Bite",
                attack=3,
                armor=3,
                magic=0,
                health=2,
                ritual=0,
                special=Special.DEVOUR,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.GHOULS, "Crypt Warden",
                attack_name="Iron Coffin Nail",
                attack=3,
                armor=4,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.GHOULS, "Ossuary Keeper",
                attack_name="Femur Club",
                attack=4,
                armor=3,
                magic=0,
                health=3,
                ritual=0,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.GHOULS, "Hollow-Eyed Stalker",
                attack_name="Ambush from the Dark",
                attack=4,
                armor=4,
                magic=0,
                health=3,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.RARE),

   CreatureCard(FactionName.GHOULS, "Charnel Priest",
                attack_name="Ritual Sickle",
                attack=3,
                armor=3,
                magic=1,
                health=2,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.RARE),
]

# Tier 3: high stats, ritual max 3 (4 cards x 2 copies = 8)
tier_3 = [
   CreatureCard(FactionName.GHOULS, "Bone Crusher",
                attack_name="Skull Maul",
                attack=6,
                armor=4,
                magic=0,
                health=4,
                ritual=1,
                special=Special.TAUNT,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.GHOULS, "Butcher of the Underworld",
                attack_name="Carrion Cleaver",
                attack=5,
                armor=5,
                magic=1,
                health=8,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.GHOULS, "Elder Ghoul",
                attack_name="Ancient Talons",
                attack=6,
                armor=5,
                magic=0,
                health=6,
                ritual=3,
                special=Special.TAUNT,
                rarity=Rarity.EPIC),

   CreatureCard(FactionName.GHOULS, "Catacomb Tyrant",
                attack_name="Tombstone Smash",
                attack=5,
                armor=6,
                magic=0,
                health=6,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.EPIC),
]

# Ritual builders only (5 cards x 1 copy = 5)
ritual_cards = [
   RitualCard(FactionName.GHOULS, "Choir of the Corpse-Eaters",
              armor=0,
              magic=0,
              health=8,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.GHOULS, "The Forbidden Painting",
              armor=0,
              magic=0,
              health=8,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.GHOULS, "Feast of the Dead",
              armor=0,
              magic=0,
              health=10,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.GHOULS, "Rite of Exhumation",
              armor=0,
              magic=0,
              health=10,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard(FactionName.GHOULS, "Altar of Bones",
              armor=0,
              magic=0,
              health=10,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),
]

# Tier 5: dark magic spells (15 cards x 1 copy = 15)
spell_cards = [
   SpellCard(FactionName.GHOULS, "Resurrect",
             magic=0,
             ritual=0,
             special=Special.RESURRECT,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Plague",
             magic=0,
             ritual=0,
             special=Special.PLAGUE,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Infect",
             magic=2,
             ritual=0,
             special=Special.INFECT,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Ruin",
             magic=3,
             ritual=0,
             special=Special.RUIN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Necrotic Bolt",
             magic=3,
             ritual=0,
             special=Special.NECROTIC_BOLT,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Drain Life",
             magic=2,
             ritual=0,
             special=Special.DRAIN_LIFE,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Wither",
             magic=3,
             ritual=0,
             special=Special.WITHER,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Terror",
             magic=2,
             ritual=0,
             special=Special.TERROR,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Bone Ward",
             magic=2,
             ritual=0,
             special=Special.BONE_WARD,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Soul Siphon",
             magic=3,
             ritual=3,
             special=Special.SOUL_SIPHON,
             rarity=Rarity.RARE),

   # Spells that protect ritual
   SpellCard(FactionName.GHOULS, "Veil of Tiamat",
             magic=3,
             ritual=0,
             special=Special.VEIL_OF_TIAMAT,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Scales of Leviathan",
             magic=0,
             ritual=0,
             special=Special.SCALES_OF_LEVIATHAN,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Seal of Apep",
             magic=0,
             ritual=0,
             special=Special.SEAL_OF_APEP,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Kiss of Lilith",
             magic=0,
             ritual=0,
             special=Special.KISS_OF_LILITH,
             rarity=Rarity.RARE),

   SpellCard(FactionName.GHOULS, "Curse of Choronzon",
             magic=0,
             ritual=0,
             special=Special.CURSE_OF_CHORONZON,
             rarity=Rarity.RARE),
]

# Tier 1-3: two copies of each card. ritual and spell one copy each. Total 50 cards.
ghoul_cards = []
for card in tier_1 + tier_2 + tier_3:
   ghoul_cards.append(card)
   ghoul_cards.append(copy.copy(card))
ghoul_cards += ritual_cards
ghoul_cards += spell_cards

morrigan_upton = Hero("Morrigan Upton", ability=HeroAbility.FEAST_OF_GRAVES)

ghouls = Faction(FactionName.GHOULS, morrigan_upton, ritual_goal=15, cards=ghoul_cards)
