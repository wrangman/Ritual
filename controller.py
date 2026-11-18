"""
Controllers: who makes the choices for a player.

Game asks the player's controller, never the screen directly. A human player
has a HumanController that asks through the user interface (the terminal now,
graphics later). An AI player has an AI controller (see ai.py) that needs no
screen at all. Same idea as PlayerController in Forge (a Magic engine), which
has one version for humans and one for the AI (Strategy pattern, Gang of Four).

A controller only chooses. It never changes the game itself: Game carries out
the move it gets back.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from abc import ABC, abstractmethod


class Controller(ABC):
   # Välj ett av de lagliga dragen. moves kommer från Game.get_legal_moves()
   # och innehåller alltid EndTurn, så det finns alltid något att välja.
   @abstractmethod
   def choose_move(self, game, player, moves):
      pass

   # Välj ett av korten (till exempel Forbidden Codex: ta ett av de översta korten i leken)
   @abstractmethod
   def choose_card(self, game, player, cards):
      pass

   # En controller har inget eget tillstånd som ändras under matchen, så när AI:n
   # kopierar spelet för att prova ett drag kan kopian dela samma controller.
   def __deepcopy__(self, memo):
      return self


# En människa väljer via gränssnittet (TerminalUI nu, PygameUI senare).
# Gränssnittet visar läget och frågar; controllern skickar bara vidare.
class HumanController(Controller):
   def __init__(self, ui):
      self.ui = ui

   def choose_move(self, game, player, moves):
      return self.ui.choose_move(game, player, moves)

   def choose_card(self, game, player, cards):
      return self.ui.choose_card(cards)
