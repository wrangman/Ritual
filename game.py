"""
The game itself: starts a match between two players and runs their turns.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


import copy
from card import SpellCard
from move import PlayCard, Attack, EndTurn
from silent_ui import SilentUI


class Game:
   # Så mycket resurs varje spelare får i början av sin tur. Det som inte används sparas.
   RESOURCE_PER_TURN = 1

   # ui visar spelet, till exempel en TerminalUI (eller SilentUI när ingen tittar).
   # Valen gör varje spelares controller (människa eller AI), inte ui.
   # Game vet inte om det är terminal eller grafik, bara att ui har samma metoder.
   def __init__(self, player1, player2, ui):
      self.player1 = player1
      self.player2 = player2
      self.current_player = player1
      self.ui = ui
      self.triggers = []   # effekter som väntar på att något ska hända (Infect, Mirror of Nitocris ...)
      self.turn_count = 0  # hur många turer som har spelats (för statistik i simuleringar)

   def start(self):
      self.player1.draw_cards(5)
      self.player2.draw_cards(5)

   # En tur: spelaren lägger så många kort hen har råd med och anfaller med varje kort
   # som har legat sedan förra turen (en gång var), i valfri ordning.
   # Turen är slut när inget mer går att göra, eller när spelaren passar (för att spara resurs).
   def play_turn(self):
      current_player = self.current_player

      # Ritualen avgörs först, innan något annat händer i turen (före dragning och ny ☩).
      # Spelaren nådde målet tidigare och motståndaren har haft en tur på sig att svara.
      # Når ritualen fortfarande målet vinner spelaren. (Som Felidar Sovereign i Magic.)
      if current_player.reached_ritual():
         current_player.complete_ritual()
         return

      # Buffar som spelaren lade "until your next turn" går ut nu
      self.remove_expired_buffs(this_turn_only=False)

      # Korten som låg kvar sedan förra turen blir redo att anfalla, en gång var
      current_player.ready_army()

      # Triggers som väntar på att en tur börjar (till exempel Infect)
      for trigger in list(self.triggers):
         trigger.at_turn_start(self, current_player)
      self.clear_dead_cards()
      self.remove_used_triggers()
      if self.is_over():
         return

      drawn = current_player.draw_cards(1) #always draw card at your turn
      if not drawn:
         stress = current_player.get_stress()
         self.ui.show_message(f"{current_player.get_name()} has no cards left. "
                              f"Stress {stress}: the hero takes {stress} damage.")
      current_player.refill_resource(self.RESOURCE_PER_TURN)

      # Korten på brädet ger sin ☩ till hjälten. Når man målet vinner man först i början
      # av sin nästa tur, om ritualen fortfarande når målet då.
      current_player.collect_ritual()
      if self.is_over():
         return

      # Spelaren gör ett drag i taget tills hen avslutar turen eller inget mer går att göra.
      # Game räknar ut vilka drag som är lagliga, och spelarens controller (människa eller AI)
      # väljer ett av dem. Då står reglerna bara här, och ingen kan göra ett olagligt drag.
      while True:
         moves = self.get_legal_moves(current_player)
         if len(moves) == 1:
            break   # bara "end turn" kvar: inget mer går att göra

         move = current_player.get_controller().choose_move(self, current_player, moves)
         if move.ends_turn():
            break

         self.ui.show_message(move.describe(current_player))   # så att man ser vad AI:n gör
         move.execute(self)

         if self.is_over():
            break

      # Varning till motståndaren: det här är sista chansen att stoppa ritualen
      if not self.is_over() and current_player.reached_ritual():
         self.ui.show_message(f"☩ The ritual of {current_player.get_name()} is nearly complete! "
                              f"Lower it before their next turn, or it is over.")

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

   def get_ui(self):
      return self.ui

   # Effekter som låter spelaren välja (till exempel Forbidden Codex) frågar spelarens controller
   def choose_card(self, player, cards):
      return player.get_controller().choose_card(self, player, cards)

   def get_opponent(self):
      return self.get_opponent_of(self.current_player)

   def get_opponent_of(self, player):
      return self.player2 if player is self.player1 else self.player1

   def get_triggers(self):
      return list(self.triggers)

   def get_turn_count(self):
      return self.turn_count


   # Lagliga drag

   # Alla drag som player får göra just nu. "End turn" finns alltid med, sist.
   # - Kort i handen som spelaren har råd med. Figurer bara om det finns plats på brädet.
   #   Spells som behöver ett mål blir ett drag per tillåtet mål (effekten säger vilka),
   #   och en spell utan något tillåtet mål kan inte spelas alls (som i Hearthstone).
   # - Anfall: varje kort som får anfalla, mot varje mål som får anfallas.
   def get_legal_moves(self, player):
      moves = []

      for card in player.get_hand():
         if not player.can_afford(card):
            continue
         if isinstance(card, SpellCard):
            effect = card.get_effect()
            if effect and effect.needs_target():
               for target in effect.get_targets(self):
                  moves.append(PlayCard(card, target))
            else:
               moves.append(PlayCard(card))
         elif player.has_room_on_board():
            moves.append(PlayCard(card))

      targets = self.get_opponent_of(player).get_targets()
      for card in player.get_army():
         if card.can_attack():
            for target in targets:
               moves.append(Attack(card, target))

      moves.append(EndTurn())
      return moves

   # Den aktiva spelaren lägger ett kort. Kortet betalas och läggs ut
   # (spells går till döda högen), sedan sker spellens effekt.
   def play_card(self, card, target=None):
      self.current_player.play_card(card)
      if isinstance(card, SpellCard) and card.get_effect():
         card.get_effect().apply(self, card, target)


   # En kopia av hela spelet som AI:n kan prova ett drag på, utan att det riktiga spelet ändras.
   # Kopian får ett gränssnitt som inte visar något, så att inget skrivs ut medan AI:n tänker.
   # Saker som skickas med i others (till exempel draget som ska provas) kopieras tillsammans
   # med spelet, så att de pekar på kopians kort och inte på de riktiga.
   def copy_for_simulation(self, *others):
      memo = {id(self.ui): SilentUI()}   # deepcopy byter ut self.ui mot det tysta gränssnittet
      return copy.deepcopy((self, *others), memo)


   # En figur anfaller och målet slår tillbaka. Triggers får först chansen att ta hand om
   # anfallet (Mirror of Nitocris, då blir det ingen motskada), och efteråt får de reagera
   # på det (Curse of Choronzon).
   def attack(self, attacker, target):
      attacker.mark_attacked()   # kortet har gjort sitt anfall för den här turen
      handled = False
      for trigger in list(self.triggers):
         if trigger.before_attack(self, attacker, target):
            handled = True
            break

      if not handled:
         # Båda gör skada på varandra samtidigt (som i Hearthstone): båda värdena räknas ut
         # innan någon tar skada, så målet slår tillbaka även om det dör.
         damage = attacker.damage_against(target)
         counter_damage = target.counter_damage_against(attacker)
         target.take_damage(damage)
         attacker.take_damage(counter_damage)
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


   # Har player vunnit? Ja om motståndarens hjälte är död (gäller direkt) eller om
   # player:s ritual är klar (avgörs i början av player:s tur, se play_turn).
   def has_won(self, player, opponent):
      return opponent.get_hero().is_dead() or player.is_ritual_complete()

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

   # En hel tur, från början till slut, och sedan är det den andras tur
   def take_turn(self):
      self.play_turn()
      self.remove_expired_buffs(this_turn_only=True)   # "this turn"-buffar går ut
      self.switch_turn()
      self.turn_count += 1

   def run(self):
      self.start()

      while not self.is_over():
         self.take_turn()

      winner = self.determine_winner()
      if winner:
         self.ui.show_winner(winner)
      else:
         self.ui.show_draw()