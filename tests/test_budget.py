"""
Tests for the stat budget: every creature must fit the budget for its cost.

Ritual cards are left out: they do not fight, so they will get their own budget.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import unittest
from budget import StatBudget, unique_creatures
from factions.ghouls import ghouls
from factions.academics import academics


class TestBudget(unittest.TestCase):
   def test_every_creature_fits_the_budget(self):
      budget = StatBudget()
      for faction in (ghouls, academics):
         for card in unique_creatures(faction, ritual_cards=False):
            # subTest: ett kort som inte håller budgeten syns med namn, och de andra testas ändå
            with self.subTest(card=card.get_name()):
               self.assertTrue(budget.fits(card),
                               f"{budget.points(card)} poäng, budget {budget.limit(card)}")


if __name__ == "__main__":
   unittest.main()
