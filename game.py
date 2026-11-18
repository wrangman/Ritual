"""
The game itself: starts a match between two players and runs their turns.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


class Game:
   def __init__(self, player1, player2):
      self.player1 = player1
      self.player2 = player2
      self.current_player = player1

   def start(self):
      self.player1.draw_cards(5)
      self.player2.draw_cards(5)

   # En tur: spelaren lägger ett kort och gör en action, i valfri ordning.
   # Turen är slut när båda är gjorda, när inget mer går att göra, eller när spelaren passar.
   def play_turn(self):
      played_card = False
      did_action = False
      current_player = self.current_player

      current_player.draw_cards(1) #always draw card at your turn

      while not (played_card and did_action):
         can_play = not played_card and len(current_player.get_hand()) > 0
         can_act = not did_action and current_player.has_card_that_can_act()

         if not can_play and not can_act:
            break   # inget kvar att göra

         move, card = current_player.choose_move(can_play, can_act)

         if move == "card":
            current_player.play_card(card)
            played_card = True
         elif move == "action":
            print(f"{card.get_name()} acts. (Attacks are not built yet.)")   # anfall byggs i nästa steg
            did_action = True
         else:
            break   # pass

   def switch_turn(self):
      if self.current_player is self.player1:
         self.current_player = self.player2
      else:
         self.current_player = self.player1

   def get_opponent(self):
      return self.player2 if self.current_player is self.player1 else self.player1

   def determine_winner(self):

      #player 1 wins! player 2 has no health or player 1 has reached ritual goal
      #TODO: 3 rounds with ritual goal before win condition!
      if self.player2.get_hero().is_dead() or self.player1.reached_ritual():
         return self.player1

      #player 2 wins!
      elif self.player1.get_hero().is_dead() or self.player2.reached_ritual():
         return self.player2
      
      else:
         return None


   def run(self):
      self.start()   

      while not self.determine_winner():
         self.play_turn()
         self.switch_turn()
