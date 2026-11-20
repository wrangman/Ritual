"""
A user interface that shows nothing.

Used when no one is watching: in tests, in simulations where AIs play
thousands of matches, and when the AI tries out a move on a copy of the game.
It has the same show method as TerminalUI, but it does nothing.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


class SilentUI:
   def show_event(self, event):
      pass
