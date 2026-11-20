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
from gui.layout import SCREEN_SIZE
from factions.ghouls import ghouls
from factions.academics import academics
from tests.helpers import new_game, take_from_deck, take_creatures, put_ready_on_board


# Låtsas att spelaren klickar med vänster musknapp på en viss punkt (trycker ner och släpper)
def click(position):
   pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=1))
   pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=position, button=1))


# Låtsas att spelaren drar med musen från en punkt till en annan och släpper där
def drag(start, end):
   pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=start, button=1))
   pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=end, rel=(0, 0), buttons=(1, 0, 0)))
   pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=end, button=1))


class TestPygameUI(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.ui = PygameUI(speed=0, window_size=SCREEN_SIZE)   # fönstret lika stort som spelet
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

   def test_drag_a_card_from_the_hand_onto_the_board(self):
      card = take_from_deck(self.academics, "Novice Scholar")
      self.academics.hand = [card]
      self.academics.resource = 1
      start = self.ui.layout.hand(self.academics)[0][1].center
      drag(start, (self.ui.layout.BOARD_CENTER_X, 520))
      move = self.choose()
      self.assertIsInstance(move, PlayCard)
      self.assertIs(move.get_card(), card)

   def test_a_card_dropped_back_in_the_hand_is_not_played(self):
      card = take_from_deck(self.academics, "Novice Scholar")
      self.academics.hand = [card]
      self.academics.resource = 1
      start = self.ui.layout.hand(self.academics)[0][1].center
      drag(start, (start.x + 60, 1050))          # släpps längst ner, i handen
      click(self.ui.layout.END_TURN.center)      # sedan avslutas turen
      self.assertIsInstance(self.choose(), EndTurn)

   def test_drag_an_arrow_from_attacker_to_target(self):
      attacker = take_creatures(self.academics, 1)[0]
      put_ready_on_board(self.academics, attacker)
      enemy = take_creatures(self.ghouls, 1)[0]
      put_ready_on_board(self.ghouls, enemy)
      start = self.ui.layout.board(self.academics)[0][1].center
      end = self.ui.layout.board(self.ghouls)[0][1].center
      drag(start, end)
      move = self.choose()
      self.assertIsInstance(move, Attack)
      self.assertIs(move.get_target(), enemy)

   def test_click_in_a_smaller_window_hits_the_right_card(self):
      # Fönstret är hälften så stort som spelet: punkten i fönstret räknas om till spelets punkt
      self.ui = PygameUI(speed=0, window_size=(960, 540))
      self.game.ui = self.ui
      self.ui.attach(self.game, viewer=self.academics)
      self.ui.frame()   # en bildruta, så att fönstrets skala är räknad
      card = take_from_deck(self.academics, "Novice Scholar")
      self.academics.hand = [card]
      self.academics.resource = 1
      center = self.ui.layout.hand(self.academics)[0][1].center
      click((center.x / 2, center.y / 2))
      self.assertIs(self.choose().get_card(), card)

   def test_end_turn_button(self):
      click(self.ui.layout.END_TURN.center)
      self.assertIsInstance(self.choose(), EndTurn)

   def test_play_again_or_quit_after_the_match(self):
      center_x = self.ui.layout.BOARD_CENTER_X
      click((center_x - 180, 640))   # "Play again"
      self.assertTrue(self.ui.ask_play_again())
      click((center_x + 180, 640))   # "Quit"
      self.assertFalse(self.ui.ask_play_again())

   def test_a_new_match_starts_with_an_empty_history(self):
      self.ui.history.append("ett gammalt drag")
      self.ui.attach(self.game, viewer=self.academics)
      self.assertEqual(self.ui.history, [])

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
