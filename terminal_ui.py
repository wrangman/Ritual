"""
Everything to do with the terminal: colors, output and input.

The cards and players know nothing about the terminal. TerminalUI decides
how things look and asks the person at the keyboard what to do.

Game gets a TerminalUI when it is created and uses it to show what happens.
A human player's HumanController uses it to ask for choices. A graphical
version later (for example PygameUI) gets the same method names, so Game
does not need to change.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from card import SpellCard, FactionName


RESET = "\033[0m"   # tillbaka till terminalens vanliga färg

LETTERS = "abcdefghijklmnopqrstuvwxyz"   # korten i armén väljs med bokstäver

RESOURCE_NAME = "Resource"   # vad resursen heter i spelet (namnet är inte bestämt än)


# Ger en ANSI-kod som färgar texten efter den, med exakt den här färgen (röd, grön, blå 0–255)
def rgb(red, green, blue):
   return f"\033[38;2;{red};{green};{blue}m"


# Fraktion -> (färg för figurer, färg för spells)
FACTION_COLORS = {
   FactionName.GHOULS:    (rgb(150, 0, 0),   rgb(230, 60, 80)),    # mörkröd, ljusare blodröd
   FactionName.ACADEMICS: (rgb(40, 90, 210), rgb(120, 180, 255)),  # blå, ljusblå
   FactionName.SHOGGOTHS: (rgb(200, 150, 0), rgb(255, 215, 80)),   # gyllengul, ljus guld
   FactionName.DEEP_ONES: (rgb(20, 130, 60), rgb(100, 220, 150)),  # grön, ljusgrön
}


class TerminalUI:

   # Hjälpmetoder

   # Väljer färg efter kortets fraktion, och om kortet är en spell eller inte
   def color_for(self, card):
      colors = FACTION_COLORS.get(card.get_faction())
      if colors is None:
         return ""   # okänd fraktion: ingen färg
      creature_color, spell_color = colors
      if isinstance(card, SpellCard):
         return spell_color
      return creature_color

   # Kortets korta visning i rätt färg
   def colored(self, card):
      return f"{self.color_for(card)}{card.short()}{RESET}"

   # Numbers finished lines of text: "1. ...", "2. ..." and so on, one per line
   def numbered(self, lines):
      numbered_lines = []
      for number, line in enumerate(lines, start=1):
         numbered_lines.append(f"{number}. {line}")
      return "\n".join(numbered_lines)


   # Visning

   # Visar spelarens hand som en numrerad lista i färg, en rad per kort.
   # Kostnaden står först inom parentes, till exempel "1. (2) Dark Occultist [...]".
   def show_hand(self, player):
      lines = []
      for card in player.get_hand():
         lines.append(f"({card.get_cost()}) {self.colored(card)}")
      return self.numbered(lines)

   # Visar spelarens armé med | mellan korten. Med bokstäver när spelaren ska kunna välja
   # ett kort (den egna armén), utan när det bara är att titta (motståndarens).
   def show_army(self, player, with_letters=True):
      lines = []
      for index, card in enumerate(player.get_army()):
         if with_letters:
            lines.append(f"{LETTERS[index]}. {self.colored(card)}")
         else:
            lines.append(self.colored(card))
      return " | ".join(lines)

   # Visar spelarens döda hög i färg, med | mellan korten
   def show_graveyard(self, player):
      lines = []
      for card in player.get_graveyard():
         lines.append(self.colored(card))
      return " | ".join(lines)

   # Visar spelarens hjälte i fraktionens färg.
   # Färgen hämtas via spelarens fraktion, eftersom hjälten inte har någon egen fraktion.
   def show_hero(self, player):
      hero = player.get_hero()
      colors = FACTION_COLORS.get(player.get_faction().get_name())
      if colors is None:
         color = ""   # okänd fraktion: ingen färg
      else:
         color = colors[0]   # samma färg som fraktionens figurer
      goal = player.get_faction().get_ritual_goal()
      text = f"{color}{hero.short()}{RESET}  (ritual goal ☩ {goal}, deck: {len(player.get_deck())}"
      # Stressen visas först när leken är slut och den har börjat växa
      if player.get_stress() > 0:
         text += f", stress {player.get_stress()}"
      return text + ")"

   # Shows who won. Game decides the winner, the terminal only shows it.
   def show_winner(self, player):
      print(f"WINNER BY A MILE - MAYBE!\n\n {player.get_name()}")

   # Ett kort meddelande till spelaren
   def show_message(self, text):
      print(text)

   # Båda vann samtidigt, till exempel om båda hjältarna dog av samma effekt
   def show_draw(self):
      print("DRAW! Both rituals ended in madness.")


   # Val

   # Visar motståndarens sida, sedan den egna hjälten, handen och armén,
   # och frågar vad spelaren vill göra:
   #   siffra = lägg det kortet från handen
   #   bokstav = anfall med det kortet i armén
   #   0 = avsluta turen
   # moves är de lagliga dragen från Game. Terminalen kollar inga regler själv:
   # den visar bara de val som finns i listan och returnerar draget spelaren valde.
   # Behöver kortet ett mål frågas det efteråt (två steg, så att listan inte blir för lång).
   def choose_move(self, game, player, moves):
      hand = player.get_hand()
      army = player.get_army()
      opponent = game.get_opponent_of(player)

      print(f"\n--- {player.get_name()}'s turn ---")
      print(f"Opponent {opponent.get_name()}:")
      print(self.show_hero(opponent))
      if opponent.get_army():
         print(self.show_army(opponent, with_letters=False))
      print("Your hero:")
      print(self.show_hero(player))
      resource_line = f"{RESOURCE_NAME}: {player.get_resource()}"
      if player.get_overload() > 0:
         resource_line += f"  (overload: {player.get_overload()} less next turn)"
      print(resource_line)
      print("Hand (cost):")
      print(self.show_hand(player))
      if army:
         print("Army:")
         print(self.show_army(player))

      # Vilka kort går att lägga, och vilka kort får anfalla? Det står i dragen.
      can_play = any(self.moves_for(card, moves) for card in hand)
      can_attack = any(self.moves_for(card, moves) for card in army)

      # Frågan visar bara de val som går just nu
      options = []
      if can_play:
         options.append(f"1-{len(hand)} play a card")
      if can_attack:
         options.append(f"a-{LETTERS[len(army) - 1]} attack")
      options.append("0) end turn")
      question = ", ".join(options) + ": "

      while True:
         answer = input(question).strip().lower()

         if answer == "0":
            return self.end_turn_move(moves)

         card = None
         if answer.isdigit() and 1 <= int(answer) <= len(hand):
            card = hand[int(answer) - 1]
         elif len(answer) == 1 and answer in LETTERS[:len(army)]:
            card = army[LETTERS.index(answer)]

         if card is None:
            print("Not a valid choice.")
            continue

         card_moves = self.moves_for(card, moves)
         if not card_moves:
            print(f"{card.get_name()} can't do anything right now.")
            continue

         return self.choose_move_for_card(card_moves)

   # Dragen som ett visst kort kan göra (att lägga det, eller att anfalla med det)
   def moves_for(self, card, moves):
      found = []
      for move in moves:
         if move.get_card() is card:
            found.append(move)
      return found

   def end_turn_move(self, moves):
      for move in moves:
         if move.ends_turn():
            return move

   # Kortet kan göra ett eller flera drag. Har dragen olika mål får spelaren välja mål.
   def choose_move_for_card(self, card_moves):
      if len(card_moves) == 1:
         return card_moves[0]
      targets = []
      for move in card_moves:
         targets.append(move.get_target())
      target = self.choose_target(targets)
      for move in card_moves:
         if move.get_target() is target:
            return move

   # Shows the allowed targets and lets the player pick one. Returns the target.
   # The game decides which targets are allowed (Game.get_legal_moves), not the terminal.
   # Targets are shown without color: colored() needs get_faction(), and the hero has no faction.
   def choose_target(self, targets):
      lines = []
      for target in targets:
         lines.append(target.short())
      print("Targets:")
      print(self.numbered(lines))

      while True:
         answer = input(f"Choose a target 1-{len(targets)}: ").strip()
         if answer.isdigit() and 1 <= int(answer) <= len(targets):
            return targets[int(answer) - 1]
         print("Not a valid choice.")

   # Visar några kort (till exempel de översta i leken) och låter spelaren ta ett. Returnerar kortet.
   def choose_card(self, cards):
      lines = []
      for card in cards:
         lines.append(f"({card.get_cost()}) {self.colored(card)}")
      print("Choose a card to take into your hand:")
      print(self.numbered(lines))

      while True:
         answer = input(f"Choose a card 1-{len(cards)}: ").strip()
         if answer.isdigit() and 1 <= int(answer) <= len(cards):
            return cards[int(answer) - 1]
         print("Not a valid choice.")
