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
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.ritual = 0
      self.ability = ability   # ett HeroAbility-värde eller None

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

   def restore_health(self, amount):
      self.health += amount

   def increase_magic(self, amount):
      self.magic += amount

   def repair_armor(self, amount):
      self.armor += amount

   # Get methods

   def get_name(self):
      return self.name

   def get_health(self):
      return self.health
   
   def get_attack(self):
      return self.attack
   
   def get_armor(self):
      return self.armor

   def get_magic(self):
      return self.magic
   
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
      hero_title.append(f"🛡️ {self.armor}")
      hero_title.append(f"☩ {self.ritual}")
      return f"{self.name} [{' '.join(hero_title)}]"