class Game:
   def __init__(self, player1, player2):
      self.player1 = player1
      self.player2 = player2

   def start(self):
      self.player1.draw_cards(5)
      self.player2.draw_cards(5)

   # En tur: spelaren lägger ett kort och gör en action, i valfri ordning.
   # Turen är slut när båda är gjorda, när inget mer går att göra, eller när spelaren passar.
   def play_turn(self, player):
      played_card = False
      did_action = False

      while not (played_card and did_action):
         can_play = not played_card and len(player.get_hand()) > 0
         can_act = not did_action and player.has_card_that_can_act()

         if not can_play and not can_act:
            break   # inget kvar att göra

         move, card = player.choose_move(can_play, can_act)

         if move == "card":
            player.play_card(card)
            player.draw_cards(1)   # regel: efter att man lagt sitt kort drar man ett nytt
            played_card = True
         elif move == "action":
            print(f"{card.get_name()} acts. (Attacks are not built yet.)")   # anfall byggs i nästa steg
            did_action = True
         else:
            break   # pass
