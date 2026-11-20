"""
Entry point for Ritual with graphics (pygame-ce): you against the AI.

The terminal version is still main.py. Both use the same Game; only the user
interface differs.

Controls: click a card and then a target. Cards that can do something glow.
Right-click or Esc cancels. Tab opens the console.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from game import Game
from player import Player
from controller import HumanController
from ai import SmartAI
from gui.pygame_ui import PygameUI
from factions.ghouls import ghouls
from factions.academics import academics


ui = PygameUI()

player1 = Player("Computer", ghouls, SmartAI())
player2 = Player("Joe", academics, HumanController(ui))

game = Game(player1, player2, ui)
ui.attach(game, viewer=player2)   # Joe sitter vid skärmen: hans sida är nederst
game.run()
ui.wait_for_close()
