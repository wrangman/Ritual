"""
Triggers: effects that wait for something to happen and then react.

Game tells all active triggers when an attack is about to happen, when it has
happened, and when a turn starts (Observer pattern). Each trigger only writes
the methods it needs. A trigger that has done its job marks itself as used up
and Game removes it. (Hearthstone has Secrets and poison that work like this;
Fireplace builds them as event listeners.)
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from card import RitualCard


class Trigger:
   def __init__(self, owner):
      self.owner = owner       # spelaren som lade triggern
      self.used_up = False     # True när triggern har gjort sitt och ska tas bort

   # Precis innan en figur anfaller. Returnera True om triggern tar hand om anfallet,
   # så att det vanliga anfallet inte sker (Mirror of Nitocris).
   def before_attack(self, game, attacker, target):
      return False

   # Efter att en figur har anfallit och gjort damage i skada (Curse of Choronzon)
   def after_attack(self, game, attacker, target, damage):
      pass

   # I början av en spelares tur (Infect)
   def at_turn_start(self, game, player):
      pass

   def is_used_up(self):
      return self.used_up


# Infect: det smittade kortet tar skada i början av varje tur för den som smittade det,
# tills kortet dör eller lämnar brädet.
class InfectTrigger(Trigger):
   def __init__(self, owner, card, amount):
      super().__init__(owner)
      self.card = card
      self.amount = amount

   def at_turn_start(self, game, player):
      if not game.is_on_board(self.card):
         self.used_up = True   # kortet är borta, smittan också
         return
      if player is self.owner:
         self.card.take_damage(self.amount)


# Mirror of Nitocris: nästa melee-anfall mot det skyddade kortet träffar anfallaren i stället.
class MirrorTrigger(Trigger):
   def __init__(self, owner, card):
      super().__init__(owner)
      self.card = card

   def before_attack(self, game, attacker, target):
      if target is not self.card:
         return False
      damage = attacker.damage_against(target)
      attacker.take_damage(damage)
      self.used_up = True
      return True


# Curse of Choronzon: nästa fiendekort som anfaller ett av ägarens ritualkort tar samma skada.
class CurseTrigger(Trigger):
   def after_attack(self, game, attacker, target, damage):
      if isinstance(target, RitualCard) and self.owner.owns_card(target):
         attacker.take_damage(damage)
         self.used_up = True
