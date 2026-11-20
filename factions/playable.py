"""
The factions you can play with right now.

Shoggoths and The Deep Ones are added to the list when they are built.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from factions.academics import academics
from factions.ghouls import ghouls

# Listan finns på ett ställe, så att både main.py och main_gui.py (och menyn där
# man väljer fraktion) alltid visar samma fraktioner.
PLAYABLE_FACTIONS = [academics, ghouls]
