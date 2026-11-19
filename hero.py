"""
The hero in play: the one who performs the ritual.

A hero has health and ritual, and can have a faction ability.
"""

"""
HEROES

The Deep Ones:	The Dagon King (Uråldrig jätte som dyrkas av fiskfolket i Innsmouth)	Amfibiska fiskmänniskor från havets djup	Swarm & Förvandling: Svaga ensamma, livsfarliga i grupp. Kan infektera och förvandla mänskliga kort till Djupdykare över tid.

Ghouls: Morrigan Upton  (Konstnär som blev en ghoul och ledare i underjorden)	människomonster. under kyrkogårdar	Kyrkogård: Blir starkare varje gång en pjäs dör på brädet. Kan "äta" kort i gravhögen för att stjäla deras stats och förmågor.

Shoggoths	The Primordial (Amorf, bubblande massa av ögon och tentakler)	Antarktiska urvarelser och deras upproriska slavar	Ramp & Absorption: Dyra, gigantiska monster som växer okontrollerbart och absorberar närliggande pjäser för att få liv och attack.

The academic	Dr. Henry Armitage (Bibliotekarien som faktiskt besegrade monstret i Dunwich)	The Dunwich Horror	Spells & Kunskap: Drar mycket kort och använder "Discover"-mekanik via förbjudna böcker, men tar själv skada eller tappar förstånd vid för stark magi (likt Mage/Warlock).
"""


__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from enum import Enum
from buff import BuffList


# Hero abilities - kind of like specials
class HeroAbility(Enum):
   # Ghouls – Morrigan Upton
   FEAST_OF_GRAVES = "Eat a card in your graveyard: one of your cards gains its attack and health"
   # The Academics – Dr. Henry Armitage
   ELEVENTH_SEAL = "One of your ritual cards cannot be damaged until your next turn, but all your other cards take 2 damage"


class Hero:
   def __init__(self, name="Unnamed Hero", health=30, attack=0, armor=0, magic=0, ability=None):
      self.name = name
      self.health = health
      self.max_health = health   # läkning kan aldrig ge mer än så här
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.ritual = 0
      self.ability = ability   # ett HeroAbility-värde eller None
      self.buffs = BuffList()  # tillfälliga ändringar, till exempel Seal of Apep

   def __str__(self):
      return (f"{self.name} (Hero); "
              f"[ ⚔️ {self.attack}, 🪄 {self.magic}, ❤️ {self.health}, 🛡️ {self.armor}, ☩ {self.ritual}], "
              f"ABL: {self.ability.name if self.ability else '–'}")

   def __repr__(self):
      return (f"Hero(name={self.name!r}, health={self.health!r}, attack={self.attack!r}, "
              f"armor={self.armor!r}, magic={self.magic!r}, ability={self.ability!r})")
   
   
   def is_dead(self):
      return self.health <= 0
      
   def take_damage(self, amount):
      self.health -= amount

   # Läker, men aldrig över max_health
   def restore_health(self, amount):
      self.health = min(self.health + amount, self.max_health)

   def increase_magic(self, amount):
      self.magic += amount

   def repair_armor(self, amount):
      self.armor += amount

   # Hjälten bygger vidare på sin ritual
   def add_ritual(self, amount):
      self.ritual += amount

   # Motståndaren sänker ritualen, men aldrig under 0.
   # Är ritualen skyddad (Seal of Apep) händer ingenting.
   def lose_ritual(self, amount):
      if self.is_ritual_protected():
         return
      self.ritual = max(0, self.ritual - amount)

   # Kan ritualen sänkas eller stjälas just nu?
   def is_ritual_protected(self):
      return self.buffs.ritual_protected()

   # Hjälten kan alltid bli anfallen när armén är tom, och har inget skydd mot figurer.
   # Metoderna finns så att hjälten kan vara mål precis som ett kort.
   def can_be_attacked(self):
      return True

   # Korta ord för hjältens status, som statuses() på korten
   def statuses(self):
      words = []
      if self.is_ritual_protected():
         words.append("Ritual protected")
      return words

   # Hjälten slår inte tillbaka när den blir anfallen (i Hearthstone bara med ett vapen,
   # och hjältarna här har inga vapen). Finns så att hjälten kan vara mål precis som ett kort.
   def counter_damage_against(self, attacker):
      return 0

   # Hjälten slår inte heller tillbaka mot ett magiskt anfall
   def magic_counter_damage_against(self, attacker):
      return 0

   def is_immune_to_melee(self):
      return self.buffs.no_melee_damage()

   # Buffar

   def add_buff(self, buff):
      self.buffs.add(buff)

   def remove_expired_buffs(self, player, this_turn_only):
      self.buffs.remove_expired(player, this_turn_only)

   # Get methods

   def get_name(self):
      return self.name

   def get_health(self):
      return self.health
   
   # attack, armor och magic räknas med buffarna, men aldrig under 0
   def get_attack(self):
      return max(0, self.attack + self.buffs.attack_bonus())

   def get_armor(self):
      return max(0, self.armor + self.buffs.armor_bonus())

   def get_magic(self):
      return max(0, self.magic + self.buffs.magic_bonus())
   
   def get_ritual(self):
      return self.ritual
   
   def get_ability(self):
      return self.ability


   # Set methods

   def set_name(self, name):
      self.name = name

   def set_health(self, health):
      self.health = health

   def set_attack(self, attack):
      self.attack = attack

   def set_armor(self, armor):
      self.armor = armor

   def set_magic(self, magic):
      self.magic = magic

   def set_ritual(self, ritual):
      self.ritual = ritual

   def set_ability(self, ability):
      self.ability = ability

   
   def short(self):
      hero_title = []
      hero_title.append(f"❤️ {self.health}")
      hero_title.append(f"🛡️ {self.get_armor()}")
      hero_title.append(f"☩ {self.ritual}")
      sealed = ""
      if self.is_ritual_protected():
         sealed = " (Ritual sealed)"
      return f"{self.name} [{' '.join(hero_title)}]{sealed}"