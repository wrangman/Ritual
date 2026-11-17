#TODO: Image!!

from enum import Enum


# Vilken fraktion ett kort tillhör. Namnet används i koden, värdet är texten som visas för spelaren.
class FactionName(Enum):
   GHOULS = "Ghouls"
   ACADEMICS = "The Academics"
   SHOGGOTHS = "Shoggoths"
   DEEP_ONES = "The Deep Ones"


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
   SUMMON = "Summons a card of your choice from your deck"

   # Ghouls, figurer
   DEVOUR = "Devours dead cards to gain their stats"
   SACRIFICE = "Sacrifices itself to boost another card"

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

   # Academics, figurer
   STUDY = "Draws a card when played"

   # Academics, spells (förbjudna böcker). Tung magi skadar de egna korten.
   BOOK_OF_SORROWS = "Strikes one enemy card with magic damage"
   SCROLL_OF_RITUALS ="Adds this spell's ritual to yours"
   ELDER_SIGN = "One of your cards gets extra armor until your next turn"
   LITANY_OF_UNMAKING = "One of your cards gets extra attack this turn"
   FORBIDDEN_CODEX ="Look at three cards from your deck and put one of them in your hand"
   WHISPERED_HEX = "An enemy card loses attack until your next turn"
   NECRONOMICON = "Deals heavy magic damage to one enemy card, but one of your cards takes 3 damage"
   PNAKOTIC_MANUSCRIPTS = "Deals magic damage to all enemy cards, but your own cards take 1 damage"
   CULTES_DES_GOULES = "Removes armor from an enemy card"
   UNAUSSPRECHLICHEN_KULTEN = "Steals ritual from the opponent, but one of your cards takes 2 damage"
   BOOK_OF_EIBON = "Burns away part of the opponent's ritual"
   RLYEH_TEXT = "Draw two cards, but one of your cards takes 2 damage"
   SCROLL_OF_DZYAN ="All your cards get extra magic until your next turn"
   RITE_OF_THE_THIRTEENTH_HOUR = "All your cards get extra attack this turn, but each of them takes 1 damage"
   PSALMS_OF_THE_VOID = "Heals all your cards"
   THE_KING_IN_YELLOW = "No enemy card can attack next turn, but one of your cards takes 2 damage"
   BOOK_OF_THE_NAMELESS_DEAD = "Returns one of your dead cards to your hand"

   # Academics, spells som skyddar ritual
   SEAL_OF_THE_BLACK_SUN = "Your ritual cards take no melee damage until your next turn"
   MIRROR_OF_NITOCRIS = "The next melee attack on one of your cards hits the attacker instead"
   WARD_OF_THE_UNBEGOTTEN = "One of your cards gets Taunt and extra armor until your next turn"
   CODEX_OF_THE_ELEVEN_KEYS = "One of your ritual cards gets extra magic and health"


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
# Figurer slåss alltid med ⚔️ attack, och målets 🛡️ armor tar emot.
class CreatureCard(Card):
   def __init__(self, faction=None, name="Untitled", attack_name=None, attack=0, armor=0, magic=0, health=0, ritual=0, special=None, rarity=Rarity.COMMON):
      super().__init__(faction, name, ritual, special, rarity)
      self.attack_name = attack_name
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.health = health

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name}; {self.attack_name or '–'}; "
              f"[ ⚔️ {self.attack}, 🪄 {self.magic}, ❤️ {self.health}, 🛡️ {self.armor}, ☩{self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"CreatureCard(faction={self.faction!r}, name={self.name!r}, attack_name={self.attack_name!r}, "
              f"attack={self.attack!r}, armor={self.armor!r}, "
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

   # Vanliga figurer kan anfalla.
   def can_attack(self):
      return True

   # Hur mycket skada figuren gör på target: ⚔️ attack minus målets 🛡️ armor, minst 0.
   def damage_against(self, target):
      return max(0, self.attack - target.get_armor())


   # Get methods

   def get_attack_name(self):
      return self.attack_name

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
      super().__init__(faction, name, attack_name=None, attack=0,
                       armor=armor, magic=magic, health=health, ritual=ritual, special=special, rarity=rarity)

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name} (Ritual); "
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

   #ritualkort kan inte attackera!
   def can_attack(self):
      return False


# En spell spelas från handen mot ett mål, verkar direkt och hamnar sedan i gravhögen.
# Den ligger aldrig på brädet, så den har ingen health, armor eller attack.
# magic är spellens styrka. special beskriver vad den gör.
# Spells slåss alltid med 🪄 magic, och målets 🪄 magic tar emot. Därför går de igenom armor.
class SpellCard(Card):
   def __init__(self, faction=None, name="Untitled", magic=0, ritual=0, special=None, rarity=Rarity.COMMON):
      super().__init__(faction, name, ritual, special, rarity)
      self.magic = magic

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name} (Spell); "
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

   # Hur mycket skada spellen gör på target: 🪄 magic minus målets 🪄 magic, minst 0.
   def damage_against(self, target):
      return max(0, self.magic - target.get_magic())


   # Get methods

   def get_magic(self):
      return self.magic


   # Set methods

   def set_magic(self, magic):
      self.magic = magic
