"""
Tests for the AI: it makes sensible choices in clear situations, and whole
matches between AIs finish without crashing.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import unittest
from ai import SmartAI, RandomAI
from move import Attack, PlayCard
from simulate import play_match
from factions.ghouls import ghouls
from factions.academics import academics
from tests.helpers import new_game, take_from_deck, take_ritual_card, put_ready_on_board


class TestSmartAIChoices(unittest.TestCase):
   def setUp(self):
      self.ai = SmartAI()
      self.game, self.academics, self.ghouls = new_game()
      self.game.current_player = self.ghouls

   def choose(self):
      moves = self.game.get_legal_moves(self.ghouls)
      return self.ai.choose_move(self.game, self.ghouls, moves)

   def test_takes_the_win_when_it_can(self):
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")   # ⚔️ 4
      put_ready_on_board(self.ghouls, attacker)
      self.academics.get_hero().set_health(3)
      move = self.choose()
      self.assertIsInstance(move, Attack)
      self.assertIs(move.get_target(), self.academics.get_hero())

   def test_stops_the_enemy_ritual(self):
      # Academics har nått målet och vinner i början av sin tur om inget händer
      self.academics.get_hero().add_ritual(15)
      ruin = take_from_deck(self.ghouls, "Ruin")   # sänker motståndarens ritual med 3
      self.ghouls.hand.append(ruin)
      self.ghouls.resource = 2
      move = self.choose()
      self.assertIsInstance(move, PlayCard)
      self.assertIs(move.get_card(), ruin)

   def test_kills_a_ritual_card_to_stop_the_ritual(self):
      # Ritualkortets ☩ försvinner när det dör, så att döda det räddar matchen
      ritual_card = take_ritual_card(self.academics)
      put_ready_on_board(self.academics, ritual_card)
      self.academics.get_hero().add_ritual(15 + ritual_card.get_ritual() - 1)
      ritual_card.set_health(1)
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      put_ready_on_board(self.ghouls, attacker)
      move = self.choose()
      self.assertIsInstance(move, Attack)
      self.assertIs(move.get_target(), ritual_card)

   def test_does_not_change_the_real_game_while_thinking(self):
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      put_ready_on_board(self.ghouls, attacker)
      self.choose()
      self.assertEqual(self.academics.get_hero().get_health(), 30)
      self.assertTrue(attacker.can_attack())


class TestWholeMatches(unittest.TestCase):
   def test_smart_ai_matches_finish(self):
      for seed in range(6):
         result = play_match(seed, academics, ghouls, SmartAI)
         self.assertGreater(result["turns"], 0)

   def test_random_ai_matches_finish(self):
      for seed in range(30):
         result = play_match(seed, academics, ghouls, RandomAI)
         self.assertGreater(result["turns"], 0)


if __name__ == "__main__":
   unittest.main()
