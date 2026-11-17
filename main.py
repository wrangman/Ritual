"""
Entry point for Ritual, a Lovecraft-inspired card game played in the terminal... for now!

Creates two players with their factions and starts the game.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import os
import subprocess
from game import Game
import terminal_ui
from player import Player
from factions.ghouls import ghouls
from factions.academics import academics


subprocess.run("cls" if os.name == "nt" else "clear", shell=True) 

player1 = Player("Joe", academics)
player2 = Player("Moe", ghouls)

game = Game(player1, player2)
game.start()

game.play_turn(player1)

print("Hero:", terminal_ui.show_hero(player1))
print("Army:", terminal_ui.show_army(player1))
print("Graveyard:", terminal_ui.show_graveyard(player1))
game.play_turn(player2)

print("Hero:", terminal_ui.show_hero(player2))
print("Army:", terminal_ui.show_army(player2))
print("Graveyard:", terminal_ui.show_graveyard(player2))

