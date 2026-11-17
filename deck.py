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

   # Lägger kortet längst ner i leken (toppen är slutet på listan)
   def put_on_bottom(self, card):
      self.cards.insert(0, card)