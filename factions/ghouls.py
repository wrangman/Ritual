import copy
from faction import Faction
from card import CreatureCard, RitualCard, SpellCard, Rarity, Special


# Tier 1: low stats, no ritual (6 cards x 2 copies = 12)
tier_1 = [
   CreatureCard("Ghouls", "Corpse Looter",
                attack_name="Grave Knife",
                attack=2,
                armor=1,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard("Ghouls", "Gravedigger",
                attack_name="Rusty Shovel",
                attack=1,
                armor=2,
                magic=0,
                health=1,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard("Ghouls", "Changeling Child",
                attack_name="Needle Teeth",
                attack=1,
                armor=1,
                magic=0,
                health=1,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard("Ghouls", "Tunnel Scavenger",
                attack_name="Filthy Claws",
                attack=2,
                armor=2,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.COMMON),

   CreatureCard("Ghouls", "Bone Gnawer",
                attack_name="Gnashing Jaws",
                attack=2,
                armor=1,
                magic=0,
                health=3,
                ritual=0,
                special=Special.DEVOUR,
                rarity=Rarity.COMMON),

   CreatureCard("Ghouls", "Mourner in Black",
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
   CreatureCard("Ghouls", "Grave Eater",
                attack_name="Rending Bite",
                attack=3,
                armor=3,
                magic=0,
                health=2,
                ritual=0,
                special=Special.DEVOUR,
                rarity=Rarity.RARE),

   CreatureCard("Ghouls", "Crypt Warden",
                attack_name="Iron Coffin Nail",
                attack=3,
                armor=4,
                magic=0,
                health=2,
                ritual=0,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard("Ghouls", "Ossuary Keeper",
                attack_name="Femur Club",
                attack=4,
                armor=3,
                magic=0,
                health=3,
                ritual=0,
                special=None,
                rarity=Rarity.RARE),

   CreatureCard("Ghouls", "Hollow-Eyed Stalker",
                attack_name="Ambush from the Dark",
                attack=4,
                armor=4,
                magic=0,
                health=3,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.RARE),

   CreatureCard("Ghouls", "Charnel Priest",
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
   CreatureCard("Ghouls", "Bone Crusher",
                attack_name="Skull Maul",
                attack=6,
                armor=4,
                magic=0,
                health=4,
                ritual=1,
                special=Special.TAUNT,
                rarity=Rarity.EPIC),

   CreatureCard("Ghouls", "Butcher of the Underworld",
                attack_name="Carrion Cleaver",
                attack=5,
                armor=5,
                magic=1,
                health=8,
                ritual=1,
                special=Special.DEVOUR,
                rarity=Rarity.EPIC),

   CreatureCard("Ghouls", "Elder Ghoul",
                attack_name="Ancient Talons",
                attack=6,
                armor=5,
                magic=0,
                health=6,
                ritual=3,
                special=Special.TAUNT,
                rarity=Rarity.EPIC),

   CreatureCard("Ghouls", "Catacomb Tyrant",
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
   RitualCard("Ghouls", "Choir of the Corpse-Eaters",
              armor=0,
              magic=0,
              health=8,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard("Ghouls", "The Forbidden Painting",
              armor=0,
              magic=0,
              health=8,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard("Ghouls", "Feast of the Dead",
              armor=0,
              magic=0,
              health=10,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard("Ghouls", "Rite of Exhumation",
              armor=0,
              magic=0,
              health=10,
              ritual=4,
              special=None,
              rarity=Rarity.LEGENDARY),

   RitualCard("Ghouls", "Altar of Bones",
              armor=0,
              magic=0,
              health=10,
              ritual=5,
              special=None,
              rarity=Rarity.LEGENDARY),
]

# Tier 5: dark magic spells (15 cards x 1 copy = 15)
spell_cards = [
   SpellCard("Ghouls", "Resurrect",
             magic=0,
             ritual=0,
             special=Special.RESURRECT,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Plague",
             magic=0,
             ritual=0,
             special=Special.PLAGUE,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Infect",
             magic=2,
             ritual=0,
             special=Special.INFECT,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Ruin",
             magic=3,
             ritual=0,
             special=Special.RUIN,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Necrotic Bolt",
             magic=3,
             ritual=0,
             special=Special.NECROTIC_BOLT,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Drain Life",
             magic=2,
             ritual=0,
             special=Special.DRAIN_LIFE,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Wither",
             magic=3,
             ritual=0,
             special=Special.WITHER,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Terror",
             magic=2,
             ritual=0,
             special=Special.TERROR,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Bone Ward",
             magic=2,
             ritual=0,
             special=Special.BONE_WARD,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Soul Siphon",
             magic=3,
             ritual=3,
             special=Special.SOUL_SIPHON,
             rarity=Rarity.RARE),

   # Spells that protect ritual
   SpellCard("Ghouls", "Veil of Tiamat",
             magic=3,
             ritual=0,
             special=Special.VEIL_OF_TIAMAT,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Scales of Leviathan",
             magic=0,
             ritual=0,
             special=Special.SCALES_OF_LEVIATHAN,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Seal of Apep",
             magic=0,
             ritual=0,
             special=Special.SEAL_OF_APEP,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Kiss of Lilith",
             magic=0,
             ritual=0,
             special=Special.KISS_OF_LILITH,
             rarity=Rarity.RARE),

   SpellCard("Ghouls", "Curse of Choronzon",
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

ghouls = Faction("Ghouls", "Morrigan Upton", ritual_goal=30, cards=ghoul_cards)
