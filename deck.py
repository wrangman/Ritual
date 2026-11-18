"""
A player's deck: draw, shuffle and put cards back.

The top of the deck is the end of the list.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random


class Deck():
   
   def __init__(self, cards=None):
      if cards:
         self.cards = list(cards)
      else:
         self.cards = []

   #räkna kort genom att bara använda len!
   def __len__(self):
      return len(self.cards)
         
   # Drar upp till amount kort från toppen. Returnerar alltid en lista,
  
   def draw(self, amount=1):
      if amount < 0:
         raise ValueError("amount must be non-negative")
      drawn = []
      # se till att inte dra kort om det inte finns kvar. min garanterar att det minsta värdet används.
      for _ in range(min(amount, len(self.cards))):
         drawn.append(self.cards.pop())
      return drawn
      
   def shuffle(self):
      random.shuffle(self.cards)
      
   def add_card(self, card):
      self.cards.append(card)

   # Alla kort i leken, som en kopia (så att leken bara ändras via Deck)
   def get_cards(self):
      return list(self.cards)

   # Tar ut ett visst kort ur leken (SUMMON lägger ett kort ur leken på brädet)
   def remove(self, card):
      self.cards.remove(card)

   # Lägger kortet längst ner i leken (toppen är slutet på listan)
   def put_on_bottom(self, card):
      self.cards.insert(0, card)