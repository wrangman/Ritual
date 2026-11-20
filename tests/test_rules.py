"""
Tests for the rules: ritual, Stress, attacks and retaliation.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import unittest
from buff import Buff
from move import Sacrifice
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

   # Testerna räknar med kortens ⚔️ i stället för fasta tal, så att de håller när stats ändras.
   # Figurer har ingen armor: båda gör hela sin ⚔️ i skada på varandra.
   def test_target_hits_back(self):
      eater, keeper = self.ghoul("Grave Eater"), self.ghoul("Ossuary Keeper")
      eater.set_health(10)
      keeper.set_health(10)
      self.game.attack(eater, keeper)
      self.assertEqual(keeper.get_health(), 10 - eater.get_attack())
      self.assertEqual(eater.get_health(), 10 - keeper.get_attack())

   def test_target_hits_back_even_if_it_dies(self):
      crusher, keeper = self.ghoul("Bone Crusher"), self.ghoul("Ossuary Keeper")
      crusher.set_health(10)
      keeper.set_health(1)
      self.game.attack(crusher, keeper)
      self.assertTrue(keeper.is_dead())
      self.assertEqual(crusher.get_health(), 10 - keeper.get_attack())

   def test_both_can_die(self):
      first, second = self.ghoul("Ossuary Keeper"), self.ghoul("Ossuary Keeper")
      first.set_health(1)
      second.set_health(1)
      self.game.attack(first, second)
      self.assertTrue(first.is_dead())
      self.assertTrue(second.is_dead())

   def test_hero_and_ritual_card_do_not_hit_back(self):
      crusher = self.ghoul("Bone Crusher")
      health = crusher.get_health()
      self.game.attack(crusher, self.academics.get_hero())
      self.assertEqual(crusher.get_health(), health)
      crusher = self.ghoul("Bone Crusher")
      self.game.attack(crusher, take_ritual_card(self.academics))
      self.assertEqual(crusher.get_health(), health)


class TestHeroArmor(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.hero = self.academics.get_hero()
      self.attacker = take_from_deck(self.ghouls, "Ossuary Keeper")
      self.attacker.set_attack(3)

   def test_armor_wears_down_one_per_hit(self):
      # 🛡️ 2 och två slag med ⚔️ 3: först 3 - 2 = 1 skada, sedan 3 - 1 = 2
      self.hero.gain_armor(2)
      self.game.attack(self.attacker, self.hero)
      self.assertEqual((self.hero.get_health(), self.hero.get_armor()), (30 - 1, 1))
      self.game.attack(self.attacker, self.hero)
      self.assertEqual((self.hero.get_health(), self.hero.get_armor()), (30 - 1 - 2, 0))

   def test_fully_blocked_hit_still_wears_the_armor(self):
      self.hero.gain_armor(2)
      self.attacker.set_attack(1)
      self.game.attack(self.attacker, self.hero)
      self.assertEqual((self.hero.get_health(), self.hero.get_armor()), (30, 1))

   def test_spells_ignore_armor_and_do_not_wear_it(self):
      self.hero.gain_armor(2)
      self.game.current_player = self.ghouls
      self.ghouls.resource = 10
      bolt = take_from_deck(self.ghouls, "Necrotic Bolt")   # magisk skada på en fiende
      damage = bolt.get_effect().amount
      self.ghouls.hand.append(bolt)
      self.game.play_card(bolt, self.hero)
      self.assertEqual((self.hero.get_health(), self.hero.get_armor()), (30 - damage, 2))

   def test_bone_ward_gives_the_hero_armor(self):
      self.game.current_player = self.ghouls
      self.ghouls.resource = 10
      ward = take_from_deck(self.ghouls, "Bone Ward")
      self.ghouls.hand.append(ward)
      self.game.play_card(ward)
      self.assertEqual(self.ghouls.get_hero().get_armor(), 2)


class TestSpells(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.game.current_player = self.academics
      self.academics.resource = 10

   # Lägger spellen från handen, som när spelaren väljer den
   def cast(self, name, target=None):
      spell = take_from_deck(self.academics, name)
      self.academics.hand.append(spell)
      self.game.play_card(spell, target)
      return spell

   def test_spell_shows_no_stats(self):
      spell = take_from_deck(self.academics, "Necronomicon")
      self.assertEqual(spell.short(), "Necronomicon (Spell)")

   def test_magic_damage_is_lowered_by_the_targets_magic(self):
      west = take_from_deck(self.academics, "Herbert West")   # som mål
      west.set_magic(4)
      west.set_health(20)
      put_ready_on_board(self.ghouls, west)
      spell = self.cast("Necronomicon", west)
      self.assertEqual(west.get_health(), 20 - (spell.get_effect().amount - 4))

   def test_card_without_magic_takes_all_spell_damage(self):
      elder = take_from_deck(self.ghouls, "Elder Ghoul")
      elder.set_magic(0)
      elder.set_health(20)
      put_ready_on_board(self.ghouls, elder)
      spell = self.cast("Book of Sorrows", elder)
      self.assertEqual(elder.get_health(), 20 - spell.get_effect().amount)

   def test_scroll_of_rituals_adds_two(self):
      self.cast("Scroll of Rituals")
      self.assertEqual(self.academics.get_hero().get_ritual(), 2)


class TestCreatureAbilities(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.game.current_player = self.ghouls
      self.ghouls.resource = 10

   def test_devour_eats_a_dead_card_and_gains_its_stats(self):
      dead = take_from_deck(self.ghouls, "Ossuary Keeper")
      self.ghouls.graveyard.append(dead)
      eater = take_from_deck(self.ghouls, "Catacomb Tyrant")  # DEVOUR
      self.ghouls.hand.append(eater)
      attack, health = eater.get_attack(), eater.get_health()
      moves = [m for m in self.game.get_legal_moves(self.ghouls) if m.get_card() is eater]
      self.assertEqual([m.get_target() for m in moves], [dead])
      moves[0].execute(self.game)
      self.assertEqual(eater.get_attack(), attack + dead.get_attack())
      self.assertEqual(eater.get_health(), health + dead.get_max_health())
      self.assertNotIn(dead, self.ghouls.get_graveyard())   # uppäten, kan inte återupplivas

   def test_devour_with_empty_graveyard_still_plays_the_card(self):
      eater = take_from_deck(self.ghouls, "Catacomb Tyrant")
      self.ghouls.hand.append(eater)
      attack = eater.get_attack()
      moves = [m for m in self.game.get_legal_moves(self.ghouls) if m.get_card() is eater]
      self.assertEqual(len(moves), 1)
      moves[0].execute(self.game)
      self.assertIn(eater, self.ghouls.get_army())
      self.assertEqual(eater.get_attack(), attack)   # inget att äta, så inget växer

   def test_study_draws_a_card(self):
      self.game.current_player = self.academics
      self.academics.resource = 10
      student = take_from_deck(self.academics, "Night Archivist")   # STUDY
      self.academics.hand.append(student)
      hand_before = len(self.academics.get_hand())
      self.game.play_card(student)
      self.assertEqual(len(self.academics.get_hand()), hand_before - 1 + 1)

   def test_summon_puts_a_random_creature_from_the_deck_on_the_board(self):
      self.game.current_player = self.academics
      self.academics.resource = 10
      wilbur = take_from_deck(self.academics, "Wilbur Whateley")   # SUMMON
      self.academics.hand.append(wilbur)
      deck_before = len(self.academics.get_deck())
      self.game.play_card(wilbur)
      self.assertEqual(len(self.academics.get_army()), 2)
      self.assertEqual(len(self.academics.get_deck()), deck_before - 1)
      self.assertFalse(self.academics.get_army()[1].can_attack())   # nytt kort väntar en tur


class TestSacrifice(unittest.TestCase):
   def setUp(self):
      self.game, self.academics, self.ghouls = new_game()
      self.apprentice = take_from_deck(self.academics, "Miskatonic Apprentice")
      self.ritual_card = take_ritual_card(self.academics)
      put_ready_on_board(self.academics, self.apprentice)
      put_ready_on_board(self.academics, self.ritual_card)

   def sacrifice_moves(self):
      return [m for m in self.game.get_legal_moves(self.academics) if isinstance(m, Sacrifice)]

   def test_sacrifice_gives_health_and_costs_ritual(self):
      self.academics.get_hero().add_ritual(5)
      health = self.ritual_card.get_health()
      gift = self.apprentice.get_max_health()
      lost_ritual = self.apprentice.get_ritual()   # kortet dör, så dess ☩ försvinner
      move = self.sacrifice_moves()[0]
      self.assertIs(move.get_target(), self.ritual_card)
      move.execute(self.game)
      self.assertNotIn(self.apprentice, self.academics.get_army())
      self.assertEqual(self.ritual_card.get_health(), health + gift)
      self.assertEqual(self.academics.get_hero().get_ritual(), 5 - lost_ritual)

   def test_new_card_cannot_sacrifice(self):
      self.apprentice.enter_board()   # som om den lades den här turen
      self.assertEqual(self.sacrifice_moves(), [])

   def test_damaged_card_still_gives_its_max_health(self):
      gift = self.apprentice.get_max_health()
      self.apprentice.set_health(1)
      health = self.ritual_card.get_health()
      self.game.sacrifice(self.apprentice, self.ritual_card)
      self.assertEqual(self.ritual_card.get_health(), health + gift)

   def test_killed_in_an_attack_still_gives_its_strength(self):
      # En ghoul dödar lärlingen. Ritualkortet är det enda kortet kvar och får styrkan.
      health = self.ritual_card.get_health()
      gift = self.apprentice.get_max_health()
      self.apprentice.set_health(1)
      keeper = take_from_deck(self.ghouls, "Ossuary Keeper")
      self.game.attack(keeper, self.apprentice)
      self.assertNotIn(self.apprentice, self.academics.get_army())
      self.assertEqual(self.ritual_card.get_health(), health + gift)

   def test_strength_never_goes_to_a_card_that_died_at_the_same_time(self):
      other_apprentice = take_from_deck(self.academics, "Miskatonic Apprentice")
      put_ready_on_board(self.academics, other_apprentice)
      health = self.ritual_card.get_health()
      gift = self.apprentice.get_max_health()
      self.apprentice.set_health(0)
      other_apprentice.set_health(0)          # båda dör samtidigt, som av Plague
      self.academics.clear_dead_cards()
      self.assertEqual(self.ritual_card.get_health(), health + gift + gift)

   def test_dying_with_no_other_card_does_nothing(self):
      self.academics.kill_card(self.ritual_card)
      self.apprentice.set_health(0)
      self.academics.clear_dead_cards()   # ingen att ge till, och ingen krasch
      self.assertEqual(self.academics.get_army(), [])


if __name__ == "__main__":
   unittest.main()
