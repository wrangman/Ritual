"""
A snapshot of the game: what everything looks like right now.

Game takes a snapshot before and after every move and turns the differences
into events (see event.py), for example StatChanged(Elder Ghoul, health, 6, 3)
or CardDied(Night Archivist). That way the player can always see what a move
did, without every card or spell having to describe its own result.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from event import (StatChanged, StatusChanged, RitualChanged, ResourceChanged, CardDied,
                   CardEnteredBoard, CardReturnedToHand, CardEaten, CardsDrawn, CardsBurned)


# Värdena som jämförs för ett kort på brädet
def card_state(card):
   return {
      "health": card.get_health(),
      "attack": card.get_attack(),
      "magic": card.get_magic(),
      "statuses": card.statuses(),
   }


# Hjälten har samma värden som ett kort, och dessutom armor (bara hjälten har armor)
def hero_state(hero):
   state = card_state(hero)
   state["armor"] = hero.get_armor()
   return state


# Det som syns av en spelares sida i ett visst ögonblick.
# id(card) skiljer två exemplar av samma kort åt.
class PlayerState:
   def __init__(self, player):
      hero = player.get_hero()
      self.player = player
      self.hero = hero_state(hero)
      self.ritual = hero.get_ritual()
      self.resource = player.get_resource()
      self.burned = len(player.get_burned())
      self.army = {id(card): (card, card_state(card)) for card in player.get_army()}
      self.deck = {id(card) for card in player.get_deck().get_cards()}
      self.hand = {id(card) for card in player.get_hand()}
      self.graveyard = {id(card): card for card in player.get_graveyard()}


class Snapshot:
   def __init__(self, game):
      self.sides = [PlayerState(game.player1), PlayerState(game.player2)]

   # Händelserna som beskriver vad som har ändrats sedan den här bilden togs
   def changes_until(self, later):
      events = []
      for before, after in zip(self.sides, later.sides):
         events += self.side_changes(before, after)
      return events

   def side_changes(self, before, after):
      player = before.player
      events = self.stat_changes(player.get_hero(), before.hero, after.hero)
      if before.ritual != after.ritual:
         events.append(RitualChanged(player, before.ritual, after.ritual))
      if before.resource != after.resource:
         events.append(ResourceChanged(player, before.resource, after.resource))

      for card_id, (card, state) in before.army.items():
         if card_id not in after.army:
            events.append(CardDied(player, card))
         else:
            events += self.stat_changes(card, state, after.army[card_id][1])

      for card_id, (card, state) in after.army.items():
         if card_id not in before.army:
            events.append(CardEnteredBoard(player, card, self.came_from(card_id, before)))

      # Kort som lämnade gravhögen utan att komma ut på brädet
      for card_id, card in before.graveyard.items():
         if card_id not in after.graveyard and card_id not in after.army:
            if card_id in after.hand:
               events.append(CardReturnedToHand(player, card))
            else:
               events.append(CardEaten(player, card))   # DEVOUR

      # Kort som gick från leken till handen är dragna. Kort som inte fick plats
      # i handen (full hand, 10 kort) försvinner och räknas för sig.
      drawn = len(before.deck & after.hand)
      if drawn > 0:
         events.append(CardsDrawn(player, drawn))
      burned = after.burned - before.burned
      if burned > 0:
         events.append(CardsBurned(player, burned))
      return events

   # Varifrån kom ett nytt kort på brädet?
   def came_from(self, card_id, before):
      if card_id in before.hand:
         return "hand"
      if card_id in before.deck:
         return "deck"        # SUMMON
      if card_id in before.graveyard:
         return "graveyard"   # Resurrect
      return "nowhere"        # ett spöke som en spell trollade fram

   # Ändrade värden och statusar för ett kort eller en hjälte.
   # Bara hjälten har armor, så den jämförs bara när den finns med.
   def stat_changes(self, target, before, after):
      events = []
      for stat in ("health", "attack", "armor", "magic"):
         if stat in before and before[stat] != after[stat]:
            events.append(StatChanged(target, stat, before[stat], after[stat]))
      for status in after["statuses"]:
         if status not in before["statuses"]:
            events.append(StatusChanged(target, status, gained=True))
      for status in before["statuses"]:
         if status not in after["statuses"]:
            events.append(StatusChanged(target, status, gained=False))
      return events
