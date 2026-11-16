from random import shuffle


class Deck():
   def __init__(self, cards=None):
      if cards:
         self.cards = list(cards)
      else:
         self.cards = []

   #räkna kort genom att bara använda len!
   def __len__(self):
      return len(self.cards)
         
   def draw(self):
      if self.cards:
         return self.cards.pop()
      return None
      
   def shuffle_deck(self):
      shuffle(self.cards)
      
   def add_card(self, card):
      self.cards.append(card)

   # Lägger kortet längst ner i leken (toppen är slutet på listan)
   def put_on_bottom(self, card):
      self.cards.insert(0, card)