"""
Tests for the budget: every creature, ritual card and spell must fit the budget
for its cost. Spells that give resource are left out (see SpellBudget.OUTSIDE_BUDGET).
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import unittest
from budget import StatBudget, SpellBudget, unique_creatures, unique_cards
from card import SpellCard
from factions.ghouls import ghouls
from factions.academics import academics


class TestBudget(unittest.TestCase):
   # subTest: ett kort som inte håller budgeten syns med namn, och de andra testas ändå
   def assert_fits(self, budget, card):
      with self.subTest(card=card.get_name()):
         self.assertTrue(budget.fits(card),
                         f"{budget.points(card)} poäng, budget {budget.limit(card)}")

   def test_every_creature_and_ritual_card_fits_the_budget(self):
      budget = StatBudget()
      for faction in (ghouls, academics):
         for ritual_cards in (False, True):
            for card in unique_creatures(faction, ritual_cards):
               self.assert_fits(budget, card)

   def test_every_spell_fits_the_budget(self):
      budget = SpellBudget()
      for faction in (ghouls, academics):
         for card in unique_cards(faction, SpellCard):
            if budget.is_measured(card):
               self.assert_fits(budget, card)


if __name__ == "__main__":
   unittest.main()
