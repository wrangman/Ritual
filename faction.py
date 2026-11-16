from card import Card


class Faction:
   def __init__(self, name, hero, ritual_goal, cards=None, abilities=None):
      self.name = name
      self.hero = hero
      self.ritual_goal = ritual_goal
      if cards:
         self.cards = cards
      else:
         self.cards = []
         
      if abilities:   
         self.abilities = abilities
      else:
         self.abilities = []
      
   def get_name(self):
      return self.name
   
   def get_ritual_goal(self):
      return self.get_ritual_goal
   
   def create_cards(self):
      ghoul_cards = []
      
      for idx in range(10):
         ghoul_cards.append(Card("Ghouls", attack=1, armor=1, magic=0, ritual=0))
         
         
      ghouls = Faction("Ghouls", "Morrigan Upton", ritual_goal=30, ghoul_cards)
         