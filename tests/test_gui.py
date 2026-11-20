"""
Tests for the graphical interface (PygameUI), run without a screen.

SDL's "dummy" video driver lets pygame draw into memory, so the tests can
click on cards by posting mouse events and check which move they give.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"   # måste sättas innan pygame startar
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
from ai import SmartAI
from game import Game
from player import Player
from move import PlayCard, Attack, EndTurn
from gui.pygame_ui import PygameUI
from factions.ghouls import ghouls
from factions.academics import academics
from tests.helpers import new_game, take_from_deck, take_creatures, put_ready_on_board


# Låtsas att spelaren klickar med vänster musknapp på en viss punkt
def click(position):
   pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=1))


class TestPygameUI(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.ui = PygameUI(speed=0)
      self.game.ui = self.ui
      self.ui.attach(self.game, viewer=self.academics)
      self.game.current_player = self.academics

   def choose(self):
      return self.ui.choose_move(self.game, self.academics, self.game.get_legal_moves(self.academics))

   def test_click_on_a_card_in_the_hand_plays_it(self):
      card = take_from_deck(self.academics, "Novice Scholar")
      self.academics.hand = [card]
      self.academics.resource = 1
      rect = self.ui.layout.hand(self.academics)[0][1]
      click(rect.center)
      move = self.choose()
      self.assertIsInstance(move, PlayCard)
      self.assertIs(move.get_card(), card)

   def test_click_attacker_then_target(self):
      attacker = take_creatures(self.academics, 1)[0]
      put_ready_on_board(self.academics, attacker)
      first, second = take_creatures(self.ghouls, 2)
      put_ready_on_board(self.ghouls, first)
      put_ready_on_board(self.ghouls, second)
      board = dict((id(card), rect) for card, rect in self.ui.layout.board(self.ghouls))
      click(self.ui.layout.board(self.academics)[0][1].center)
      click(board[id(second)].center)
      move = self.choose()
      self.assertIsInstance(move, Attack)
      self.assertIs(move.get_target(), second)

   def test_end_turn_button(self):
      click(self.ui.layout.END_TURN.center)
      self.assertIsInstance(self.choose(), EndTurn)

   def test_a_whole_match_through_the_window(self):
      player1 = Player("Computer", ghouls, SmartAI())
      player2 = Player("Joe", academics, SmartAI())
      game = Game(player1, player2, self.ui)
      self.ui.attach(game, viewer=player2)
      game.run()
      self.assertTrue(game.is_over())
      self.assertIsNotNone(self.ui.final_text)


if __name__ == "__main__":
   unittest.main()
