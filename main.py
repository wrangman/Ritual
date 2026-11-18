"""
Entry point for Ritual, a Lovecraft-inspired card game played in the terminal... for now!

Creates two players with their factions and starts the game: you against the AI.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import os
import subprocess
from game import Game
from player import Player
from terminal_ui import TerminalUI
from controller import HumanController
from ai import SmartAI
from factions.ghouls import ghouls
from factions.academics import academics


subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

ui = TerminalUI()

player1 = Player("Joe", academics, HumanController(ui))
player2 = Player("Computer", ghouls, SmartAI())

game = Game(player1, player2, ui)
game.run()
