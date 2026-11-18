"""
A player: their faction, deck, hand, army on the board and graveyard.

Player moves cards between these places and knows the rules about its
own cards. It never talks to the terminal: that is TerminalUI's job.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from hero import Hero
from card import SpellCard
from deck import Deck


class Player:
   def __init__(self, name, faction):
      self.name = name
      self.faction = faction
      self.hero = faction.create_hero()
      self.deck = Deck(faction.create_cards())  # nya kortobjekt för just den här spelaren
      self.deck.shuffle()
      self.hand = []
      self.army = []        # korten spelaren har på brädet
      self.graveyard = []   # döda; kastade kort

   def __str__(self):
      return (f"{self.name} ({self.faction.get_name().value}) – "
              f"☩ {self.hero.get_ritual()}/{self.faction.get_ritual_goal()}, "
              f"hand: {len(self.hand)}, lek: {len(self.deck)}")

   # Handlingar
   # Drar kort från leken till handen. Returnerar de dragna korten,
   # som kan vara färre än amount om leken tar slut.
   def draw_cards(self, amount=1):
      drawn = self.deck.draw(amount)
      self.hand.extend(drawn)
      return drawn

   # Spelar ett kort från handen. Figurer hamnar i armén.
   # Spells hamnar aldrig på brädet utan går direkt till döda högen (effekten byggs senare).
   def play_card(self, card):
      self.hand.remove(card)
      if isinstance(card, SpellCard):
         self.graveyard.append(card)
      else:
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
   #FIXME: ska kunna slänga alla kort eller bara två?
   def mulligan(self, card):
      self.hand.remove(card)
      self.draw_cards()
      self.deck.put_on_bottom(card)
      
   # Vinstvillkor som gäller spelaren själv.
   # "Mest ritual" kräver att två spelare jämförs och avgörs därför av spelet, inte här.
   def reached_ritual(self):
      return self.hero.get_ritual() >= self.faction.get_ritual_goal()

   # Utplånad: inga kort på brädet, i handen eller i leken
   def is_wiped_out(self):
      return not self.army and not self.hand and len(self.deck) == 0

   # Finns det något kort i armén som kan göra en action? (Ritualkort kan inte anfalla.)
   def has_card_that_can_act(self):
      for card in self.army:
         if card.can_attack():
            return True
      return False

   def clear_dead_cards(self):
      for card in self.get_army():
         if card.is_dead(): 
            self.kill_card(card)


   def get_targets(self):
      valid_targets = []

      for target in self.get_army():
         if target.has_guard():
            valid_targets.append(target)

      if valid_targets:
         return valid_targets
      
      else:
         if len(self.get_army()) > 0:
            return self.get_army()
         else:
            return [self.get_hero()] #expects list datatype 


   # Get methods
   def get_name(self):
      return self.name

   def get_hero(self):
      return self.hero
   
   def get_faction(self):
      return self.faction

   def get_hand(self):
      return list(self.hand)   # kopia, så att handen bara ändras via Player

   def get_army(self):
      return list(self.army)  # kopia, så att armén bara ändras via Player

   def get_graveyard(self):
      return list(self.graveyard)   # kopia, så att döda högen bara ändras via Player

   def get_deck(self):
      return self.deck
