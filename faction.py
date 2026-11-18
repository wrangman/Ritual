"""
A faction: its name, hero, ritual goal and the cards it plays with.

create_cards() gives each player their own copies of the faction's cards.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import copy


class Faction:
   def __init__(self, name, hero, ritual_goal, cards=None):
      self.name = name
      self.hero = hero
      self.ritual_goal = ritual_goal
      if cards:
         self.cards = cards
      else:
         self.cards = []
      
   def get_name(self):
      return self.name
   
   def get_ritual_goal(self):
      return self.ritual_goal
   
   def get_hero(self):
      return self.hero 
   
   # deepcopy och inte copy: varje kort och hjälte har en egen lista med buffar.
   # copy.copy skulle låta kopiorna dela samma lista, så att en buff hamnade på alla kopior.
   def create_hero(self):
      return copy.deepcopy(self.hero)

   def create_cards(self):
      return [copy.deepcopy(card) for card in self.cards]