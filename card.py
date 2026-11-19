"""
Cards in Ritual and the enums that describe them.

Card is the base class. CreatureCard is placed on the board and fights,
RitualCard builds ritual but cannot attack, and SpellCard is played from
the hand and goes straight to the graveyard.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

#TODO: Image!!

from enum import Enum
from buff import BuffList


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
   GUARD = "Enemies must attack this card first"
   SUMMON = "When played: summons a random creature from your deck"

   # Ghouls, figurer
   DEVOUR = "When played: eats a dead creature in your graveyard and gains its attack and health"

   # Academics, figurer
   SACRIFICE = ("When it dies, a random card of yours gets its health and armor. "
                "Instead of attacking, it can sacrifice itself and you choose the card")

   # Ghouls, spells
   RESURRECT = "Returns a random dead creature from your graveyard to the board"
   PLAGUE = "Deals 2 magic damage to all enemy cards on the board"
   INFECT = "Infects an enemy card: it loses 2 health at the start of each of your turns"
   RUIN = "Lowers the opponent's ritual by 3"
   NECROTIC_BOLT = "Deals 3 magic damage to one enemy"
   DRAIN_LIFE = "Deals 2 magic damage to an enemy card and restores 2 health to your hero"
   WITHER = "An enemy card loses 3 attack for good"
   TERROR = "An enemy card cannot attack next turn"
   BONE_WARD = "One of your cards gets +2 armor"
   SOUL_SIPHON = "Steals 3 ritual from the opponent"

   # Ghouls, spells som skyddar ritual
   VEIL_OF_TIAMAT = "One of your ritual cards cannot be attacked until your next turn"
   SCALES_OF_LEVIATHAN = "One of your ritual cards gets +2 armor and +2 magic"
   SEAL_OF_APEP = "Your ritual cannot be lowered or stolen until your next turn"
   KISS_OF_LILITH = "Gives one of your cards Guard until your next turn"
   CURSE_OF_CHORONZON = "The next enemy card that attacks one of your ritual cards takes the same damage"

   STUDY = "Draws a card when played"

   # Academics, spells (förbjudna böcker). Tung magi kostar inte längre de egna korten något.
   # Bara att stjäla ritual (Unaussprechlichen Kulten) och De Vermis Mysteriis skadar den egna hjälten.
   BOOK_OF_SORROWS = "Deals 3 magic damage to one enemy"
   SCROLL_OF_RITUALS = "Adds 2 to your ritual"
   DE_VERMIS_MYSTERIIS = "Gain 2 resource now, but your hero takes 1 damage"
   THE_SILVER_KEY = "Gain 2 resource now. Overload (2): you get 2 less next turn"
   FORBIDDEN_CODEX ="Look at three cards from your deck and put one of them in your hand"
   WHISPERED_HEX = "An enemy card has 2 less attack until your next turn"
   NECRONOMICON = "Deals 7 magic damage to one enemy"
   PNAKOTIC_MANUSCRIPTS = "Deals 3 magic damage to all enemy cards"
   CULTES_DES_GOULES = "Removes all armor from an enemy card"
   UNAUSSPRECHLICHEN_KULTEN = "Steals 3 ritual from the opponent, but your hero takes 1 damage"
   BOOK_OF_EIBON = "Burns away 3 of the opponent's ritual"
   RLYEH_TEXT = "Draw two cards"
   SCROLL_OF_DZYAN = "All your cards get +2 magic until your next turn"
   RITE_OF_THE_THIRTEENTH_HOUR = "All your cards get +2 attack this turn"
   PSALMS_OF_THE_VOID = "Restores 2 health to all your cards"
   THE_KING_IN_YELLOW = "No enemy card can attack next turn"
   BOOK_OF_THE_NAMELESS_DEAD = "Returns a random card from your graveyard to your hand"

   # Academics, spells som skyddar ritual
   SEAL_OF_THE_BLACK_SUN = "Your ritual cards take no melee damage until your next turn"
   MIRROR_OF_NITOCRIS = "The next melee attack on one of your cards hits the attacker instead"
   WARD_OF_THE_UNBEGOTTEN = "One of your cards gets Guard and +3 armor until your next turn"
   CODEX_OF_THE_ELEVEN_KEYS = "One of your ritual cards gets +3 magic and +3 health"


# Magisk skada, för både spells och figurers magiska anfall: styrkan minus målets 🪄 magic,
# minst 0. Armor hjälper inte mot magi. Formeln står bara här, så den är lika överallt.
def magic_damage(strength, target):
   return max(0, strength - target.get_magic())


# Grundklass för alla kort. Innehåller bara det som ALLA kort har.
# Skapa inte Card direkt, använd CreatureCard eller SpellCard.
# ☩ ritual finns inte här: bara kort som ligger på brädet ger ritual (se CreatureCard).
class Card:
   def __init__(self, faction=None, name="Untitled", special=None, rarity=Rarity.COMMON, cost=0):

      # instansvariabler
      self.faction = faction
      self.name = name
      self.special = special
      self.rarity = rarity
      self.cost = cost   # vad kortet kostar att lägga

   # Varje sorts kort bestämmer själv hur det visas på brädet.
   def short(self):
      raise NotImplementedError("Varje sorts kort måste ha en egen short()")


   # Get methods

   def get_faction(self):
      return self.faction

   def get_name(self):
      return self.name

   def get_special(self):
      return self.special

   def get_rarity(self):
      return self.rarity

   def get_cost(self):
      return self.cost


   # Set methods

   def set_faction(self, faction):
      self.faction = faction

   def set_name(self, name):
      self.name = name

   def set_special(self, special):
      self.special = special

   def set_rarity(self, rarity):
      self.rarity = rarity

   def set_cost(self, cost):
      self.cost = cost


# En figur som läggs på brädet, anfaller och kan bli anfallen.
# Figurer slåss alltid med ⚔️ attack, och målets 🛡️ armor tar emot.
class CreatureCard(Card):
   def __init__(self, faction=None, name="Untitled", attack_name=None, attack=0, armor=0, magic=0, health=0, ritual=0, special=None, rarity=Rarity.COMMON, cost=0):
      super().__init__(faction, name, special, rarity, cost)
      self.attack_name = attack_name
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.health = health
      self.ritual = ritual       # ☩ som hjälten får i början av varje egen tur, så länge kortet ligger kvar
      self.max_health = health   # läkning kan aldrig ge mer än så här (som i Hearthstone)
      self.buffs = BuffList()    # tillfälliga ändringar, till exempel från Terror eller Whispered Hex
      self.ready = False              # har legat på brädet sedan förra turen (summoning sickness)
      self.attacked_this_turn = False # varje kort får anfalla en gång per tur

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name}; {self.attack_name or '–'}; "
              f"[ ⚔️ {self.get_attack()}, 🪄 {self.get_magic()}, ❤️ {self.health}, 🛡️ {self.get_armor()}, ☩{self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"CreatureCard(faction={self.faction!r}, name={self.name!r}, attack_name={self.attack_name!r}, "
              f"attack={self.attack!r}, armor={self.armor!r}, "
              f"magic={self.magic!r}, health={self.health!r}, ritual={self.ritual!r}, "
              f"special={self.special!r}, rarity={self.rarity!r}, cost={self.cost!r})")

   # Guard kan komma från kortets förmåga eller från en buff (Kiss of Lilith)
   def has_guard(self):
      return self.special == Special.GUARD or self.buffs.guard()

   # Kan kortet bli anfallet av en figur? Inte om en buff gömmer det (Veil of Tiamat).
   def can_be_attacked(self):
      return not self.buffs.cannot_be_attacked()

   # Tar kortet ingen skada från figurer just nu? (Seal of the Black Sun)
   def is_immune_to_melee(self):
      return self.buffs.no_melee_damage()

   # Buffar

   def add_buff(self, buff):
      self.buffs.add(buff)

   def remove_expired_buffs(self, player, this_turn_only):
      self.buffs.remove_expired(player, this_turn_only)

   # Ett kort som dör eller lämnar brädet tappar alla sina buffar
   def clear_buffs(self):
      self.buffs.clear()

   # Korta ord för kortets status, till exempel ["Guard", "Can't attack"]
   def statuses(self):
      words = []
      if self.has_guard():
         words.append("Guard")
      if self.buffs.cannot_attack():
         words.append("Can't attack")
      if self.buffs.cannot_be_attacked():
         words.append("Veiled")
      if self.buffs.no_melee_damage():
         words.append("Sealed")
      return words

   # Statusorden inom parentes efter kortet, eller ingenting
   def statuses_text(self):
      words = self.statuses()
      if not words:
         return ""
      return f" ({', '.join(words)})"

   def is_dead(self):
      return self.health <= 0
      
   def take_damage(self, amount):
      self.health -= amount

   # Läker, men aldrig över max_health
   def restore_health(self, amount):
      self.health = min(self.health + amount, self.max_health)

   # Ett återupplivat kort kommer tillbaka med full health
   def restore_full_health(self):
      self.health = self.max_health

   # En buff som höjer både health och max_health
   def increase_health(self, amount):
      self.max_health += amount
      self.health += amount

   def increase_magic(self, amount):
      self.magic += amount

   def repair_armor(self, amount):
      self.armor += amount

   # Sänker attack, men aldrig under 0
   def lower_attack(self, amount):
      self.attack = max(0, self.attack - amount)

   # För alltid, till exempel när en ghoul äter ett dött kort (DEVOUR)
   def increase_attack(self, amount):
      self.attack += amount

   def short(self):
      stats = []
      if self.get_attack() > 0:
         stats.append(f"⚔️ {self.get_attack()}")
      if self.get_magic() > 0:
         stats.append(f"🪄 {self.get_magic()}")
      stats.append(f"❤️ {self.health}")
      stats.append(f"🛡️ {self.get_armor()}")
      stats.append(f"☩ {self.ritual}")
      return f"{self.name} [{' '.join(stats)}]{self.statuses_text()}"

   # Vanliga figurer kan anfalla om de har legat på brädet sedan förra turen,
   # inte redan har anfallit den här turen, och ingen buff hindrar dem (Terror, The King in Yellow).
   def can_attack(self):
      return self.ready and not self.attacked_this_turn and not self.buffs.cannot_attack()

   # Summoning sickness (som i Hearthstone): ett kort som kommer ut på brädet
   # (läggs eller återupplivas) måste vänta till sin ägares nästa tur innan det får anfalla.
   def enter_board(self):
      self.ready = False
      self.attacked_this_turn = False

   # I början av ägarens tur: kortet är redo och får anfalla en gång igen
   def ready_for_turn(self):
      self.ready = True
      self.attacked_this_turn = False

   def mark_attacked(self):
      self.attacked_this_turn = True

   # Har kortet legat på brädet sedan förra turen?
   def is_ready(self):
      return self.ready

   def has_attacked(self):
      return self.attacked_this_turn

   # Hur mycket skada figuren gör på target: ⚔️ attack minus målets 🛡️ armor, minst 0.
   # Ett mål som är skyddat mot figurer tar ingen skada alls (Seal of the Black Sun).
   def damage_against(self, target):
      if target.is_immune_to_melee():
         return 0
      return max(0, self.get_attack() - target.get_armor())

   # Hur mycket figuren slår tillbaka när den blir anfallen (som i Hearthstone).
   # Samma formel som ett vanligt anfall: ⚔️ attack minus anfallarens 🛡️ armor.
   # Ritualkort har ⚔️ 0 och slår därför aldrig tillbaka. En buff som Terror hindrar
   # bara kortet från att anfalla, inte från att försvara sig.
   def counter_damage_against(self, attacker):
      return self.damage_against(attacker)

   # Magiskt anfall: en figur med 🪄 magic kan anfalla med magi i stället för med ⚔️.
   # Det är samma anfall för turen, med samma regler för väntetur, Guard och mål.
   def can_magic_attack(self):
      return self.can_attack() and self.get_magic() > 0

   # Magisk skada räknas som för spells, med figurens 🪄 magic som styrka.
   # Skydd mot melee (Seal of the Black Sun) gäller inte.
   def magic_damage_against(self, target):
      return magic_damage(self.get_magic(), target)

   # Målet slår tillbaka på samma sätt som det blev träffat: med magi.
   # Ett kort utan 🪄 kan alltså inte slå tillbaka mot ett magiskt anfall.
   def magic_counter_damage_against(self, attacker):
      return self.magic_damage_against(attacker)


   # Get methods

   def get_attack_name(self):
      return self.attack_name

   # attack, armor och magic räknas med buffarna, men aldrig under 0
   def get_attack(self):
      return max(0, self.attack + self.buffs.attack_bonus())

   def get_armor(self):
      return max(0, self.armor + self.buffs.armor_bonus())

   def get_magic(self):
      return max(0, self.magic + self.buffs.magic_bonus())

   def get_health(self):
      return self.health

   def get_max_health(self):
      return self.max_health

   def get_ritual(self):
      return self.ritual


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

   def set_ritual(self, ritual):
      self.ritual = ritual


# Ett ritualkort ligger på brädet och bygger ritual, men kan aldrig anfalla.
# Det kan bli anfallet, så det har health, armor och magic som andra figurer.
# Bara ritualkort kan skyddas av spells som Veil of Tiamat.
class RitualCard(CreatureCard):
   def __init__(self, faction=None, name="Untitled", armor=0, magic=0, health=0, ritual=0, special=None, rarity=Rarity.COMMON, cost=0):
      super().__init__(faction, name, attack_name=None, attack=0,
                       armor=armor, magic=magic, health=health, ritual=ritual, special=special, rarity=rarity, cost=cost)

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name} (Ritual); "
              f"[ 🪄 {self.get_magic()}, ❤️ {self.health}, 🛡️ {self.get_armor()}, ☩ {self.ritual}], "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"RitualCard(faction={self.faction!r}, name={self.name!r}, armor={self.armor!r}, "
              f"magic={self.magic!r}, health={self.health!r}, ritual={self.ritual!r}, "
              f"special={self.special!r}, rarity={self.rarity!r}, cost={self.cost!r})")

   def short(self):
      stats = []
      if self.get_magic() > 0:
         stats.append(f"🪄 {self.get_magic()}")
      stats.append(f"❤️ {self.health}")
      stats.append(f"🛡️ {self.get_armor()}")
      stats.append(f"☩ {self.ritual}")
      return f"{self.name} (Ritual) [{' '.join(stats)}]{self.statuses_text()}"

   #ritualkort kan inte attackera!
   def can_attack(self):
      return False

   # Ritualkort slåss inte. Mot melee slår de inte tillbaka eftersom de har ⚔️ 0,
   # men många har hög 🪄 magic (den skyddar mot spells), så mot magi måste det sägas här.
   def magic_counter_damage_against(self, attacker):
      return 0


# En spell spelas från handen mot ett mål, verkar direkt och hamnar sedan i gravhögen.
# Den ligger aldrig på brädet, så den har inga stats alls, som i Hearthstone.
# Allt den gör, och hur mycket, står i effekten: DamageOneEnemy(7) gör 7 magisk skada.
# special är texten som visas för spelaren, och den ska nämna samma tal.
class SpellCard(Card):
   def __init__(self, faction=None, name="Untitled", special=None, rarity=Rarity.COMMON, effect=None, cost=0):
      super().__init__(faction, name, special, rarity, cost)
      self.effect = effect

   def __str__(self):
      return (f"{self.faction.value if self.faction else '–'} - {self.name} (Spell); "
              f"SPC: {self.special.value if self.special else '–'}, RAR: {self.rarity.value}")

   def __repr__(self):
      return (f"SpellCard(faction={self.faction!r}, name={self.name!r}, special={self.special!r}, "
              f"rarity={self.rarity!r}, effect={self.effect!r}, cost={self.cost!r})")

   def short(self):
      return f"{self.name} (Spell)"


   # Get methods
   def get_effect(self):
      return self.effect
