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
   
   def create_hero(self):
      return copy.copy(self.hero)
   
   def create_cards(self):
      return [copy.copy(card) for card in self.cards]