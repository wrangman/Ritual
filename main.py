"""
Entry point for Ritual, a Lovecraft-inspired card game played in the terminal... for now!

You choose your faction, the AI gets a random one, and the game starts.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import os
import random
import subprocess
from game import Game, random_order
from player import Player
from terminal_ui import TerminalUI
from controller import HumanController
from ai import SmartAI
from factions.playable import PLAYABLE_FACTIONS


subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

ui = TerminalUI()

# Datorn kan få samma fraktion som spelaren. Det går bra: varje spelare får egna kopior av korten.
human = Player("Joe", ui.choose_faction(PLAYABLE_FACTIONS), HumanController(ui))
computer = Player("Computer", random.choice(PLAYABLE_FACTIONS), SmartAI())
player1, player2 = random_order(human, computer)   # slantsingling: vem börjar?

game = Game(player1, player2, ui)
game.run()
