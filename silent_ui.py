"""
A user interface that shows nothing.

Used when no one is watching: in tests, in simulations where AIs play
thousands of matches, and when the AI tries out a move on a copy of the game.
It has the same show methods as TerminalUI, but they do nothing.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


class SilentUI:
   def show_message(self, text):
      pass

   def show_winner(self, player):
      pass

   def show_draw(self):
      pass
