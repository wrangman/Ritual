from deck import Deck


class Player:
   def __init__(self, name, faction):
      self.name = name
      self.faction = faction
      self.ritual_points = 0
      self.deck = Deck(faction.create_cards())  # nya kortobjekt för just den här spelaren
      self.deck.shuffle()
      self.hand = []
      self.army = []        # korten spelaren har på brädet
      self.graveyard = []   # döda; kastade kort

   def __str__(self):
      return (f"{self.name} ({self.faction.get_name()}) – "
              f"☩ {self.ritual_points}/{self.faction.get_ritual_goal()}, "
              f"hand: {len(self.hand)}, lek: {len(self.deck)}")

   # Handlingar
   def draw_card(self):
      card = self.deck.draw()
      if card is not None:
         return None #FIXME:  just for testing
         # self.hand.append(card)
      return card

   # Flyttar ett kort från handen till armén
   def play_card(self, card):
      self.hand.remove(card)
      self.army.append(card)

   # Ett kort i armén dör och flyttas till döda högen
   def kill_card(self, card):
      self.army.remove(card)
      self.graveyard.append(card)

   def discard(self, card):
      self.hand.remove(card)
      self.graveyard.append(card)

   # Ett dött kort återställs till spelarens hand
   def restore_card(self, card):
      self.graveyard.remove(card)
      self.hand.append(card)
      
   # Ett kort återupplivas tillaka till armén
   def revive_card(self, card):
      self.graveyard.remove(card)
      self.army.append(card)
      
   # Mulligan: "jag vill inte ha det här kortet". Ett nytt kort dras, det gamla läggs sist i leken.
   def mulligan(self, card):
      self.hand.remove(card)
      self.draw_card()
      self.deck.put_on_bottom(card)
      
   # Vinstvillkor som gäller spelaren själv.
   # "Mest ritual" kräver att två spelare jämförs och avgörs därför av spelet, inte här.
   def reached_ritual(self):
      return self.ritual_points >= self.faction.get_ritual_goal()

   # Utplånad: inga kort på brädet, i handen eller i leken
   def is_wiped_out(self):
      return not self.army and not self.hand and len(self.deck) == 0

   # Get methods
   def get_name(self):
      return self.name

   def get_faction(self):
      return self.faction

   def get_ritual_points(self):
      return self.ritual_points

   def get_hand(self):
      return list(self.hand)   # kopia, så att handen bara ändras via Player

   def get_army(self):
      return list(self.army)   # kopia, så att armén bara ändras via Player

   def get_graveyard(self):
      return list(self.graveyard)   # kopia, så att döda högen bara ändras via Player

   def get_deck(self):
      return self.deck

   # Set methods
   def set_ritual_points(self, ritual_points):
      self.ritual_points = ritual_points
