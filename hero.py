"""
The hero in play: the one who performs the ritual.

A hero has health and ritual, and can have a faction ability.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

"""
The Deep Ones:	The Dagon King (Uråldrig jätte som dyrkas av fiskfolket i Innsmouth)	Amfibiska fiskmänniskor från havets djup	Swarm & Förvandling: Svaga ensamma, livsfarliga i grupp. Kan infektera och förvandla mänskliga kort till Djupdykare över tid.

Ghouls: Morrigan Upton  (Konstnär som blev en ghoul och ledare i underjorden)	människomonster. under kyrkogårdar	Kyrkogård: Blir starkare varje gång en pjäs dör på brädet. Kan "äta" kort i gravhögen för att stjäla deras stats och förmågor.

Shoggother	Ur-Shoggothen (Amorf, bubblande massa av ögon och tentakler)	Antarktiska urvarelser och deras upproriska slavar	Ramp & Absorption: Dyra, gigantiska monster som växer okontrollerbart och absorberar närliggande pjäser för att få liv och attack.

The academic	Dr. Henry Armitage (Bibliotekarien som faktiskt besegrade monstret i Dunwich)	The Dunwich Horror	Spells & Kunskap: Drar mycket kort och använder "Discover"-mekanik via förbjudna böcker, men tar själv skada eller tappar förstånd vid för stark magi (likt Mage/Warlock).
"""

class Hero:
   def __init__(self, name, health, ritual, ability=None):
      self.name = name
      self.health = health
      self.ritual = ritual
      self.ability = ability
      
   
   def __str__(self):
      pass
   
   def __repr__(self):
      pass
   
   
   
      
   