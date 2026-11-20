"""
Entry point for Ritual with graphics (pygame-ce): you against the AI.

The terminal version is still main.py. Both use the same Game; only the user
interface differs.

Before each match you choose your faction; the AI gets a random one.
Who starts is decided by a coin flip. After a match you can play again.

Controls: click or drag a card. Cards that can do something glow.
Right-click or Esc cancels. Tab opens the console.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random
from game import Game, random_order
from player import Player
from controller import HumanController
from ai import SmartAI
from gui.pygame_ui import PygameUI
from factions.playable import PLAYABLE_FACTIONS


ui = PygameUI()

# En match i taget, tills spelaren väljer "Quit". Varje match får nya spelare,
# och därmed nya lekar och hjältar.
while True:
   # Datorn kan få samma fraktion som spelaren. Det går bra: varje spelare får egna kopior av korten.
   human = Player("Joe", ui.choose_faction(PLAYABLE_FACTIONS), HumanController(ui))
   computer = Player("Computer", random.choice(PLAYABLE_FACTIONS), SmartAI())
   first, second = random_order(human, computer)   # slantsingling: vem börjar?

   game = Game(first, second, ui)
   ui.attach(game, viewer=human)   # Joe sitter vid skärmen: hans sida är nederst
   game.run()

   if not ui.ask_play_again():
      break

ui.close()
