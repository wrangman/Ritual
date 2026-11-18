"""
Tests for the legal moves (Game.get_legal_moves) and for the terminal
choosing among them.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from buff import Buff
from move import PlayCard, Attack
from player import Player
from terminal_ui import TerminalUI
from tests.helpers import new_game, take_from_deck, take_creatures, put_ready_on_board


# Dragen som ett visst kort kan göra
def moves_for(card, moves):
   return [move for move in moves if move.get_card() is card]


class TestLegalMoves(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.game.current_player = self.ghouls

   def test_end_turn_is_always_last(self):
      moves = self.game.get_legal_moves(self.ghouls)
      self.assertTrue(moves[-1].ends_turn())

   def test_card_you_cannot_afford_is_not_a_move(self):
      card = take_from_deck(self.ghouls, "Elder Ghoul")   # kostar 3
      self.ghouls.hand.append(card)
      self.ghouls.resource = 2
      self.assertEqual(moves_for(card, self.game.get_legal_moves(self.ghouls)), [])
      self.ghouls.resource = 3
      self.assertEqual(len(moves_for(card, self.game.get_legal_moves(self.ghouls))), 1)

   def test_spell_without_target_cannot_be_played(self):
      infect = take_from_deck(self.ghouls, "Infect")   # mål: en fiendefigur
      self.ghouls.hand.append(infect)
      self.ghouls.resource = 5
      self.assertEqual(moves_for(infect, self.game.get_legal_moves(self.ghouls)), [])

   def test_spell_gets_one_move_per_target(self):
      bolt = take_from_deck(self.ghouls, "Necrotic Bolt")   # mål: en fiende, även hjälten
      self.ghouls.hand.append(bolt)
      self.ghouls.resource = 5
      for card in take_creatures(self.academics, 2):
         put_ready_on_board(self.academics, card)
      moves = moves_for(bolt, self.game.get_legal_moves(self.ghouls))
      self.assertEqual(len(moves), 3)   # två figurer och hjälten

   def test_no_creature_when_the_board_is_full(self):
      for card in take_creatures(self.ghouls, Player.MAX_ARMY):
         put_ready_on_board(self.ghouls, card)
      card = take_creatures(self.ghouls, 1)[0]
      self.ghouls.hand.append(card)
      self.ghouls.resource = 5
      self.assertEqual(moves_for(card, self.game.get_legal_moves(self.ghouls)), [])

   def test_guard_must_be_attacked_first(self):
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      put_ready_on_board(self.ghouls, attacker)
      # Vi ger en av Academics figurer Guard med en buff (som Ward of the Unbegotten)
      defender, other = take_creatures(self.academics, 2)
      put_ready_on_board(self.academics, defender)
      put_ready_on_board(self.academics, other)
      defender.add_buff(Buff(self.academics, guard=True))
      targets = [move.get_target() for move in moves_for(attacker, self.game.get_legal_moves(self.ghouls))]
      self.assertEqual(targets, [defender])

   def test_copy_for_simulation_does_not_change_the_real_game(self):
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      put_ready_on_board(self.ghouls, attacker)
      move = Attack(attacker, self.academics.get_hero())
      game_copy, move_copy = self.game.copy_for_simulation(move)
      move_copy.execute(game_copy)
      self.assertEqual(self.academics.get_hero().get_health(), 30)        # det riktiga spelet
      self.assertLess(game_copy.player1.get_hero().get_health(), 30)      # kopian
      self.assertTrue(attacker.can_attack())


class TestTerminalChoosesAmongLegalMoves(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.game.current_player = self.ghouls
      self.ui = TerminalUI()

   # Låtsas att spelaren skriver answers, och dölj det terminalen skriver ut
   def choose(self, answers):
      moves = self.game.get_legal_moves(self.ghouls)
      with patch("builtins.input", side_effect=answers), redirect_stdout(io.StringIO()):
         return self.ui.choose_move(self.game, self.ghouls, moves)

   def test_play_a_card_with_a_number(self):
      self.ghouls.hand = [take_from_deck(self.ghouls, "Gravedigger")]
      self.ghouls.resource = 1
      move = self.choose(["1"])
      self.assertIsInstance(move, PlayCard)

   def test_attack_with_a_letter_then_choose_target(self):
      attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      put_ready_on_board(self.ghouls, attacker)
      first, second = take_creatures(self.academics, 2)
      put_ready_on_board(self.academics, first)
      put_ready_on_board(self.academics, second)
      move = self.choose(["a", "2"])
      self.assertIsInstance(move, Attack)
      self.assertIs(move.get_target(), second)

   def test_invalid_answers_are_asked_again(self):
      self.ghouls.hand = [take_from_deck(self.ghouls, "Elder Ghoul")]   # kostar 3
      self.ghouls.resource = 0
      move = self.choose(["1", "x", "0"])   # kan inte läggas, ogiltigt, avsluta turen
      self.assertTrue(move.ends_turn())


if __name__ == "__main__":
   unittest.main()
