#TODO: Image!!

from enum import Enum


class AttackType(Enum):
   MELEE = "melee"   # anfaller med attack, stoppas av armor
   MAGIC = "magic"   # anfaller med magic, stoppas av magic


class Rarity(Enum):
   COMMON = "Common"
   UNCOMMON = "Uncommon"
   RARE = "Rare"
   EPIC = "Epic"
   LEGENDARY = "Legendary"


# Namnet säger VILKEN förmåga det är, värdet är texten som visas för spelaren.
class Special(Enum):
   # Alla fraktioner
   TAUNT = "Enemies must attack this card first"

   # Ghouls, figurer
   DEVOUR = "Devours dead cards to gain their stats"
   SACRIFICE = "Sacrifices itself to boost another card"
   SUMMON = "Summons a card of your choice from your deck"

   # Ghouls, spells
   RESURRECT = "Returns a dead card from your graveyard to the board"
   PLAGUE = "Deals magic damage to all enemy cards on the board"
   INFECT = "Infects an enemy card, which loses health every turn"
   RUIN = "Lowers the opponent's ritual"
   NECROTIC_BOLT = "Deals magic damage to one enemy card"
   DRAIN_LIFE = "Deals magic damage to an enemy card and heals one of your cards"
   WITHER = "Lowers an enemy card's attack"
   TERROR = "An enemy card cannot attack next turn"
   BONE_WARD = "Gives one of your cards extra armor"
   SOUL_SIPHON = "Steals ritual points from the opponent"

   # Ghouls, spells som skyddar ritual
   VEIL_OF_TIAMAT = "One of your ritual cards cannot be attacked until your next turn"
   SCALES_OF_LEVIATHAN = "Gives one of your ritual cards extra armor and magic"
   SEAL_OF_APEP = "Your ritual cannot be lowered or stolen until your next turn"
   KISS_OF_LILITH = "Gives one of your cards Taunt until your next turn"
   CURSE_OF_CHORONZON = "The next enemy card that attacks one of your ritual cards takes the same damage"


# Grundklass för alla kort. Innehåller bara det som ALLA kort har.
# Skapa inte Card direkt, använd CreatureCard eller SpellCard.
class Card:
   def __init__(self, faction=None, name="Untitled", ritual=0, special=None, rarity=Rarity.COMMON):

      # instansvariabler
      self.faction = faction
      self.name = name
      self.ritual = ritual
      self.special = special
      self.rarity = rarity

   # Varje sorts kort bestämmer själv hur det visas på brädet.
   def short(self):
      raise NotImplementedError("Varje sorts kort måste ha en egen short()")


   # Get methods

   def get_faction(self):
      return self.faction

   def get_name(self):
      return self.name

   def get_ritual(self):
      return self.ritual

   def get_special(self):
      return self.special

   def get_rarity(self):
      return self.rarity


   # Set methods

   def set_faction(self, faction):
      self.faction = faction

   def set_name(self, name):
      self.name = name

   def set_ritual(self, ritual):
      self.ritual = ritual

   def set_special(self, special):
      self.special = special

   def set_rarity(self, rarity):
      self.rarity = rarity


# En figur som läggs på brädet, anfaller och kan bli anfallen.
class CreatureCard(Card):
   def __init__(self, faction=None, name="Untitled", attack_name=None, attack_type=AttackType.MELEE, attack=0, armor=0, magic=0, health=0, ritual=0, special=None, rarity=Rarity.COMMON):
      super().__init__(faction, name, ritual, special, rarity)
      self.attack_name = attack_name
      self.attack_type = attack_type
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.health = health

   def __str__(self):
      return (f"{self.faction or '–'} - {self.name}; {self.attack_name or '–'} ({self.attack_type.value}); "
              f"[ ⚔️ {self.attack}, 🪄 {self.magic}, ❤️ {self.health}, 🛡️ {self.armor}, ☩ {self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"CreatureCard(faction={self.faction!r}, name={self.name!r}, attack_name={self.attack_name!r}, "
              f"attack_type={self.attack_type!r}, attack={self.attack!r}, armor={self.armor!r}, "
              f"magic={self.magic!r}, health={self.health!r}, ritual={self.ritual!r}, "
              f"special={self.special!r}, rarity={self.rarity!r})")

   def short(self):
      stats = []
      if self.attack > 0:
         stats.append(f"⚔️ {self.attack}")
      if self.magic > 0:
         stats.append(f"🪄 {self.magic}")
      stats.append(f"❤️ {self.health}")
      stats.append(f"🛡️ {self.armor}")
      stats.append(f"☩ {self.ritual}")
      return f"{self.name} [{' '.join(stats)}]"

   # Vanliga figurer kan anfalla. RitualCard svarar annorlunda.
   def can_attack(self):
      return True


   # Get methods

   def get_attack_name(self):
      return self.attack_name

   def get_attack_type(self):
      return self.attack_type

   def get_attack(self):
      return self.attack

   def get_armor(self):
      return self.armor

   def get_magic(self):
      return self.magic

   def get_health(self):
      return self.health


   # Set methods

   def set_attack_name(self, attack_name):
      self.attack_name = attack_name

   def set_attack_type(self, attack_type):
      self.attack_type = attack_type

   def set_attack(self, attack):
      self.attack = attack

   def set_armor(self, armor):
      self.armor = armor

   def set_magic(self, magic):
      self.magic = magic

   def set_health(self, health):
      self.health = health


# Ett ritualkort ligger på brädet och bygger ritual, men kan aldrig anfalla.
# Det kan bli anfallet, så det har health, armor och magic som andra figurer.
# Bara ritualkort kan skyddas av spells som Veil of Tiamat.
class RitualCard(CreatureCard):
   def __init__(self, faction=None, name="Untitled", armor=0, magic=0, health=0, ritual=0, special=None, rarity=Rarity.COMMON):
      super().__init__(faction, name, attack_name=None, attack_type=AttackType.MELEE, attack=0,
                       armor=armor, magic=magic, health=health, ritual=ritual, special=special, rarity=rarity)

   def __str__(self):
      return (f"{self.faction or '–'} - {self.name} (Ritual); "
              f"[ 🪄 {self.magic}, ❤️ {self.health}, 🛡️ {self.armor}, ☩ {self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"RitualCard(faction={self.faction!r}, name={self.name!r}, armor={self.armor!r}, "
              f"magic={self.magic!r}, health={self.health!r}, ritual={self.ritual!r}, "
              f"special={self.special!r}, rarity={self.rarity!r})")

   def short(self):
      stats = []
      if self.magic > 0:
         stats.append(f"🪄 {self.magic}")
      stats.append(f"❤️ {self.health}")
      stats.append(f"🛡️ {self.armor}")
      stats.append(f"☩ {self.ritual}")
      return f"{self.name} (Ritual) [{' '.join(stats)}]"

   def can_attack(self):
      return False


# En spell spelas från handen mot ett mål, verkar direkt och hamnar sedan i gravhögen.
# Den ligger aldrig på brädet, så den har ingen health, armor eller attack.
# magic är spellens styrka. special beskriver vad den gör.
class SpellCard(Card):
   def __init__(self, faction=None, name="Untitled", magic=0, ritual=0, special=None, rarity=Rarity.COMMON):
      super().__init__(faction, name, ritual, special, rarity)
      self.magic = magic

   def __str__(self):
      return (f"{self.faction or '–'} - {self.name} (Spell); "
              f"[ 🪄 {self.magic}, ☩ {self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"SpellCard(faction={self.faction!r}, name={self.name!r}, magic={self.magic!r}, "
              f"ritual={self.ritual!r}, special={self.special!r}, rarity={self.rarity!r})")

   def short(self):
      stats = []
      if self.magic > 0:
         stats.append(f"🪄 {self.magic}")
      stats.append(f"☩ {self.ritual}")
      return f"{self.name} (Spell) [{' '.join(stats)}]"


   # Get methods

   def get_magic(self):
      return self.magic


   # Set methods

   def set_magic(self, magic):
      self.magic = magic
