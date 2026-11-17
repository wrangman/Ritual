"""
Entry point for Ritual, a Lovecraft-inspired card game played in the terminal... for now!

Creates two players with their factions and starts the game.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from game import Game
import terminal_ui
from player import Player
from factions.ghouls import ghouls
from factions.academics import academics


player1 = Player("Joe", academics)
player2 = Player("Moe", ghouls)

game = Game(player1, player2)
game.start()

game.play_turn(player1)

print("Army:", terminal_ui.show_armfy(player1))
print("Graveyard:", terminal_ui.show_graveyard(player1))

