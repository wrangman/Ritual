import copy

from card import Card
from faction import Faction


EAT_DEAD = "Devours dead cards to gain their stats"

# Tier 1: low stats, no ritual (6 cards x 2 copies = 12)
tier_1 = [
   Card("Ghouls", "Corpse Looter",              attack=2, armor=1, magic=0, ritual=0, special=EAT_DEAD, rarity="Common"),
   Card("Ghouls", "Gravedigger",                attack=1, armor=2, magic=0, ritual=0, special=EAT_DEAD, rarity="Common"),
   Card("Ghouls", "Changeling Child",           attack=1, armor=1, magic=0, ritual=0, special=EAT_DEAD, rarity="Common"),
   Card("Ghouls", "Tunnel Scavenger",           attack=2, armor=2, magic=0, ritual=0, special=EAT_DEAD, rarity="Common"),
   Card("Ghouls", "Bone Gnawer",                attack=2, armor=1, magic=0, ritual=0, special=EAT_DEAD, rarity="Common"),
   Card("Ghouls", "Mourner in Black",           attack=1, armor=2, magic=0, ritual=1, special=EAT_DEAD, rarity="Common"),
]

# Tier 2: medium stats, ritual max 2 (5 cards x 2 copies = 10)
tier_2 = [
   Card("Ghouls", "Grave Eater",                attack=3, armor=3, magic=0, ritual=0, special=EAT_DEAD, rarity="Rare"),
   Card("Ghouls", "Crypt Warden",               attack=3, armor=4, magic=0, ritual=0, special=EAT_DEAD, rarity="Rare"),
   Card("Ghouls", "Ossuary Keeper",             attack=4, armor=3, magic=0, ritual=0, special=EAT_DEAD, rarity="Rare"),
   Card("Ghouls", "Hollow-Eyed Stalker",        attack=4, armor=4, magic=0, ritual=1, special=EAT_DEAD, rarity="Rare"),
   Card("Ghouls", "Charnel Priest",             attack=3, armor=3, magic=1, ritual=1, special=EAT_DEAD, rarity="Rare"),
]

# Tier 3: high stats, ritual max 3 (4 cards x 2 copies = 8)
tier_3 = [
   Card("Ghouls", "Bone Crusher",               attack=6, armor=4, magic=0, ritual=1, special=EAT_DEAD, rarity="Epic"),
   Card("Ghouls", "Butcher of the Underworld",  attack=5, armor=5, magic=1, ritual=1, special=EAT_DEAD, rarity="Epic"),
   Card("Ghouls", "Elder Ghoul",                attack=6, armor=5, magic=0, ritual=3, special=EAT_DEAD, rarity="Epic"),
   Card("Ghouls", "Catacomb Tyrant",            attack=5, armor=6, magic=0, ritual=1, special=EAT_DEAD, rarity="Epic"),
]

# Tier 4: ritual builders only (5 cards x 1 copy = 5)
tier_4 = [
   Card("Ghouls", "Choir of the Corpse-Eaters", attack=0, armor=0, magic=0, ritual=4, rarity="Legendary"),
   Card("Ghouls", "The Forbidden Painting",     attack=0, armor=0, magic=0, ritual=5, rarity="Legendary"),
   Card("Ghouls", "Feast of the Dead",          attack=0, armor=0, magic=0, ritual=4, rarity="Legendary"),
   Card("Ghouls", "Midnight Exhumation",        attack=0, armor=0, magic=0, ritual=4, rarity="Legendary"),
   Card("Ghouls", "Altar of Bones",             attack=0, armor=0, magic=0, ritual=5, rarity="Legendary"),
]

# Tier 1-3: two copies of each card. Tier 4: one copy each. Total 35 cards.
ghoul_cards = []
for card in tier_1 + tier_2 + tier_3:
   ghoul_cards.append(card)
   ghoul_cards.append(copy.copy(card))
ghoul_cards += tier_4

ghouls = Faction("Ghouls", "Morrigan Upton", ritual_goal=30, cards=ghoul_cards)
