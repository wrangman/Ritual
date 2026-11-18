"""
Tests for the rules: ritual, Stress, attacks and retaliation.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import unittest
from buff import Buff
from tests.helpers import (new_game, take_from_deck, take_ritual_card, take_creatures,
                           put_ready_on_board)


# Ett gränssnitt som sparar meddelandena, så att testet kan se vad spelet skrev
class RecordingUI:
   def __init__(self):
      self.messages = []

   def show_message(self, text):
      self.messages.append(text)

   def show_winner(self, player):
      pass

   def show_draw(self):
      pass


class TestRitualWhenCardDies(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.card = take_ritual_card(self.academics)
      put_ready_on_board(self.academics, self.card)

   def kill(self, card):
      card.take_damage(999)
      self.academics.clear_dead_cards()

   def test_ritual_drops_by_the_cards_ritual(self):
      self.academics.get_hero().add_ritual(10)
      self.kill(self.card)
      self.assertEqual(self.academics.get_hero().get_ritual(), 10 - self.card.get_ritual())
      self.assertIn(self.card, self.academics.get_graveyard())

   def test_ritual_never_below_zero(self):
      self.academics.get_hero().add_ritual(1)
      self.kill(self.card)
      self.assertEqual(self.academics.get_hero().get_ritual(), 0)

   def test_seal_of_apep_protects(self):
      self.academics.get_hero().add_ritual(10)
      self.academics.get_hero().add_buff(Buff(self.academics, ritual_protected=True))
      self.kill(self.card)
      self.assertEqual(self.academics.get_hero().get_ritual(), 10)


class TestRitualIsDecidedAfterOpponentsTurn(unittest.TestCase):
   def test_reaching_the_goal_does_not_win_at_once(self):
      game, academics, ghouls = new_game()
      academics.get_hero().add_ritual(15)
      self.assertFalse(game.is_over())

   def test_no_win_if_opponent_lowered_it(self):
      game, academics, ghouls = new_game()
      academics.get_hero().add_ritual(15)
      academics.get_hero().lose_ritual(3)   # motståndaren svarade under sin tur
      game.play_turn()
      self.assertFalse(game.is_over())

   def test_win_at_start_of_own_turn_before_drawing(self):
      game, academics, ghouls = new_game()
      academics.get_hero().add_ritual(15)
      deck_before = len(academics.get_deck())
      game.play_turn()
      self.assertIs(game.determine_winner(), academics)
      self.assertEqual(len(academics.get_deck()), deck_before)

   def test_warning_when_goal_is_reached(self):
      game, academics, ghouls = new_game()
      game.ui = RecordingUI()
      academics.get_hero().add_ritual(14)
      put_ready_on_board(academics, take_ritual_card(academics))   # ger ☩ i början av turen
      game.play_turn()
      self.assertTrue(any("nearly complete" in text for text in game.ui.messages))
      self.assertFalse(game.is_over())


class TestStress(unittest.TestCase):
   def test_stress_grows_and_hurts_the_hero(self):
      game, academics, ghouls = new_game()
      academics.deck.cards = []
      health = academics.get_hero().get_health()
      academics.draw_cards(1)
      academics.draw_cards(2)
      self.assertEqual(academics.get_stress(), 3)
      self.assertEqual(health - academics.get_hero().get_health(), 1 + 2 + 3)

   def test_game_ends_when_everyone_is_out_of_cards(self):
      game, academics, ghouls = new_game()
      for player in (academics, ghouls):
         player.deck.cards = []
         player.hand = []
      turns = 0
      while not game.is_over() and turns < 100:
         game.take_turn()
         turns += 1
      self.assertTrue(game.is_over())


class TestAttacks(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.academics.resource = 10

   def test_new_card_must_wait_a_turn(self):
      card = take_creatures(self.academics, 1)[0]
      self.academics.hand.append(card)
      self.academics.play_card(card)
      self.assertFalse(card.can_attack())
      self.academics.ready_army()   # början av nästa egna tur
      self.assertTrue(card.can_attack())

   def test_each_card_attacks_once_per_turn(self):
      first, second = take_creatures(self.academics, 2)
      put_ready_on_board(self.academics, first)
      put_ready_on_board(self.academics, second)
      self.game.attack(first, self.ghouls.get_hero())
      self.assertFalse(first.can_attack())
      self.assertTrue(second.can_attack())
      self.academics.ready_army()
      self.assertTrue(first.can_attack())

   def test_revived_card_must_wait_a_turn(self):
      card = take_creatures(self.academics, 1)[0]
      self.academics.graveyard.append(card)
      self.academics.revive_card(card)
      self.assertFalse(card.can_attack())


class TestRetaliation(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()

   def ghoul(self, name):
      return take_from_deck(self.ghouls, name)

   def test_target_hits_back(self):
      # Grave Eater ⚔️3 🛡️3 ❤️2 mot Ossuary Keeper ⚔️4 🛡️3 ❤️3
      eater, keeper = self.ghoul("Grave Eater"), self.ghoul("Ossuary Keeper")
      self.game.attack(eater, keeper)
      self.assertEqual(keeper.get_health(), 3)   # 3 - 3 = 0 skada
      self.assertEqual(eater.get_health(), 1)    # 4 - 3 = 1 i motskada

   def test_target_hits_back_even_if_it_dies(self):
      # Bone Crusher ⚔️6 🛡️4 ❤️4 dödar Keeper, som slår tillbaka med 4 - 4 = 0
      crusher, keeper = self.ghoul("Bone Crusher"), self.ghoul("Ossuary Keeper")
      self.game.attack(crusher, keeper)
      self.assertTrue(keeper.is_dead())
      self.assertEqual(crusher.get_health(), 4)

   def test_both_can_die(self):
      first, second = self.ghoul("Ossuary Keeper"), self.ghoul("Ossuary Keeper")
      first.set_health(1)
      second.set_health(1)
      self.game.attack(first, second)
      self.assertTrue(first.is_dead())
      self.assertTrue(second.is_dead())

   def test_hero_and_ritual_card_do_not_hit_back(self):
      crusher = self.ghoul("Bone Crusher")
      self.game.attack(crusher, self.academics.get_hero())
      self.assertEqual(crusher.get_health(), 4)
      crusher = self.ghoul("Bone Crusher")
      self.game.attack(crusher, take_ritual_card(self.academics))
      self.assertEqual(crusher.get_health(), 4)


if __name__ == "__main__":
   unittest.main()
