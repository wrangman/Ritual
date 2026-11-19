"""
Shared helpers for the tests: build a game and pick out cards to test with.

The tests sometimes put cards straight into a player's hand, army or
graveyard. That is fine in a test: it sets up exactly the situation we want
to check, without playing a whole match to get there.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random
from game import Game
from player import Player
from silent_ui import SilentUI
from controller import Controller
from card import CreatureCard, RitualCard
from factions.ghouls import ghouls
from factions.academics import academics


# En controller som alltid avslutar turen direkt. Då händer inget annat i turen
# än det testet vill kontrollera.
class EndTurnController(Controller):
   def choose_move(self, game, player, moves):
      for move in moves:
         if move.ends_turn():
            return move

   def choose_card(self, game, player, cards):
      return cards[0]

   def choose_mulligan(self, game, player, cards):
      return []   # behåller alltid starthanden


# Academics (spelare 1) mot Ghouls (spelare 2). Samma seed varje gång,
# så att testerna blir likadana varje körning.
def new_game(controller1=None, controller2=None):
   random.seed(1)
   player1 = Player("A", academics, controller1 or EndTurnController())
   player2 = Player("G", ghouls, controller2 or EndTurnController())
   return Game(player1, player2, SilentUI()), player1, player2


# Tar ett kort med det namnet ur spelarens lek
def take_from_deck(player, name):
   for card in player.deck.cards:
      if card.get_name() == name:
         player.deck.cards.remove(card)
         return card
   raise ValueError(f"{name} finns inte i leken")


# Tar ett ritualkort ur spelarens lek
def take_ritual_card(player):
   for card in player.deck.cards:
      if isinstance(card, RitualCard):
         player.deck.cards.remove(card)
         return card


# Tar n vanliga figurer (inte ritualkort) ur spelarens lek
def take_creatures(player, n):
   found = []
   for card in player.deck.cards:
      if isinstance(card, CreatureCard) and not isinstance(card, RitualCard):
         found.append(card)
      if len(found) == n:
         break
   for card in found:
      player.deck.cards.remove(card)
   return found


# Lägger kortet på brädet som om det hade legat där sedan förra turen
def put_ready_on_board(player, card):
   player.army.append(card)
   card.enter_board()
   card.ready_for_turn()
