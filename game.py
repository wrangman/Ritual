"""
The game itself: starts a match between two players and runs their turns.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


from card import SpellCard


class Game:
   # Så mycket resurs varje spelare får i början av sin tur. Det som inte används sparas.
   RESOURCE_PER_TURN = 1

   # ui shows the game and asks the players, for example a TerminalUI.
   # Game does not know if it is a terminal or graphics, only that ui has the same methods.
   def __init__(self, player1, player2, ui):
      self.player1 = player1
      self.player2 = player2
      self.current_player = player1
      self.ui = ui
      self.triggers = []   # effekter som väntar på att något ska hända (Infect, Mirror of Nitocris ...)

   def start(self):
      self.player1.draw_cards(5)
      self.player2.draw_cards(5)

   # En tur: spelaren lägger så många kort hen har råd med och gör en action, i valfri ordning.
   # Turen är slut när inget mer går att göra, eller när spelaren passar (för att spara resurs).
   def play_turn(self):
      did_action = False
      current_player = self.current_player

      # Buffar som spelaren lade "until your next turn" går ut nu
      self.remove_expired_buffs(this_turn_only=False)

      # Triggers som väntar på att en tur börjar (till exempel Infect)
      for trigger in list(self.triggers):
         trigger.at_turn_start(self, current_player)
      self.clear_dead_cards()
      self.remove_used_triggers()
      if self.is_over():
         return

      current_player.draw_cards(1) #always draw card at your turn
      current_player.refill_resource(self.RESOURCE_PER_TURN)

      # Korten på brädet ger sin ☩ till hjälten. Når man målet vinner man direkt.
      current_player.collect_ritual()
      if self.is_over():
         return

      while True:
         can_play = current_player.has_affordable_card()
         can_act = not did_action and current_player.has_card_that_can_act()

         if not can_play and not can_act:
            break   # inget kvar att göra

         move, card = self.ui.choose_move(current_player, can_play, can_act)

         if move == "card":
            # är det ett spellcard med en effekt? Då väljs målet först, om effekten behöver ett.
            # Effekten själv säger vilka mål som är tillåtna.
            effect = None
            target = None
            if isinstance(card, SpellCard) and card.get_effect():
               effect = card.get_effect()
               if effect.needs_target():
                  targets = effect.get_targets(self)
                  if not targets:
                     # Som i Hearthstone: en spell utan giltiga mål kan inte spelas
                     self.ui.show_message(f"{card.get_name()} has no valid target.")
                     continue
                  target = self.ui.choose_target(targets)

            # Sedan betalas kortet och läggs ut (spells går till döda högen)
            current_player.play_card(card)

            if effect:
               effect.apply(self, card, target)

         elif move == "action":
            targets = self.get_opponent().get_targets()
            target = self.ui.choose_target(targets)
            self.attack(card, target)
            
            did_action = True

         else:
            break   # pass

         if self.is_over(): break

   def switch_turn(self):
      if self.current_player is self.player1:
         self.current_player = self.player2
      else:
         self.current_player = self.player1

   def get_current_player(self):
      return self.current_player

   # Tar bort buffar som den aktiva spelaren lade och som går ut nu, på båda sidor av brädet.
   # this_turn_only=False: i början av turen ("until your next turn").
   # this_turn_only=True: i slutet av turen ("this turn").
   def remove_expired_buffs(self, this_turn_only):
      self.player1.remove_expired_buffs(self.current_player, this_turn_only)
      self.player2.remove_expired_buffs(self.current_player, this_turn_only)

   # Effekter som låter spelaren välja (till exempel Forbidden Codex) frågar via gränssnittet
   def get_ui(self):
      return self.ui

   def get_opponent(self):
      return self.player2 if self.current_player is self.player1 else self.player1


   # En figur anfaller. Triggers får först chansen att ta hand om anfallet (Mirror of Nitocris),
   # och efteråt får de reagera på det (Curse of Choronzon).
   def attack(self, attacker, target):
      handled = False
      for trigger in list(self.triggers):
         if trigger.before_attack(self, attacker, target):
            handled = True
            break

      if not handled:
         damage = attacker.damage_against(target)
         target.take_damage(damage)
         for trigger in list(self.triggers):
            trigger.after_attack(self, attacker, target, damage)

      self.clear_dead_cards()
      self.remove_used_triggers()


   # Triggers (Observer-mönstret): effekter som väntar på att något ska hända

   def add_trigger(self, trigger):
      self.triggers.append(trigger)

   # Triggers som har gjort sitt jobb tas bort
   def remove_used_triggers(self):
      active = []
      for trigger in self.triggers:
         if not trigger.is_used_up():
            active.append(trigger)
      self.triggers = active

   # Ligger kortet på brädet, hos någon av spelarna?
   def is_on_board(self, card):
      return self.player1.owns_card(card) or self.player2.owns_card(card)

   # Döda kort på båda sidor flyttas till gravhögen (en reflekterad skada kan döda anfallaren)
   def clear_dead_cards(self):
      self.player1.clear_dead_cards()
      self.player2.clear_dead_cards()


   # Har player vunnit? Ja om motståndarens hjälte är död eller om player har nått sitt ritualmål.
   #TODO: 3 rounds with ritual goal before win condition!
   def has_won(self, player, opponent):
      return opponent.get_hero().is_dead() or player.reached_ritual()

   # Matchen är slut när någon har vunnit, eller båda samtidigt (oavgjort).
   def is_over(self):
      return self.has_won(self.player1, self.player2) or self.has_won(self.player2, self.player1)

   # Vem vann? None om ingen har vunnit än, eller om båda vann samtidigt (oavgjort, som i Hearthstone).
   def determine_winner(self):
      player1_won = self.has_won(self.player1, self.player2)
      player2_won = self.has_won(self.player2, self.player1)

      if player1_won and not player2_won:
         return self.player1
      elif player2_won and not player1_won:
         return self.player2
      else:
         return None

   def run(self):
      self.start()

      while not self.is_over():
         self.play_turn()
         self.remove_expired_buffs(this_turn_only=True)   # "this turn"-buffar går ut
         self.switch_turn()

      winner = self.determine_winner()
      if winner:
         self.ui.show_winner(winner)
      else:
         self.ui.show_draw()