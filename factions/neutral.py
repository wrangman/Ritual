"""
Cards that belong to no faction.

The Trinket is given to the player who starts second, to make up for
the first player's head start (like The Coin in Hearthstone).
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from effect import GainResource
from card import SpellCard, Special


# En funktion och inte ett färdigt kort: varje match ska få ett nytt kortobjekt,
# eftersom kort kan ändras under spelet (samma skäl som att Faction kopierar sina kort).
# faction=None: kortet hör inte till någon fraktion, så terminalen visar det utan färg.
def make_trinket():
   return SpellCard(None, "Trinket",
                    special=Special.TRINKET,
                    cost=0,
                    effect=GainResource(1))
