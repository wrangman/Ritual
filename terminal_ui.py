"""
Everything to do with the terminal: colors, output and input.

The cards and players know nothing about the terminal. TerminalUI decides
how things look and asks the person at the keyboard what to do.

Game gets a TerminalUI when it is created. A graphical version later
(for example PygameUI) gets the same method names, so Game does not
need to change.
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

   # Visar spelarens armé med bokstäver, med | mellan korten
   def show_army(self, player):
      lines = []
      for index, card in enumerate(player.get_army()):
         lines.append(f"{LETTERS[index]}. {self.colored(card)}")
      return " | ".join(lines)

   # Visar spelarens döda hög i färg, med | mellan korten
   def show_graveyard(self, player):
      lines = []
      for card in player.get_graveyard():
         lines.append(self.colored(card))
      return " | ".join(lines)

   # Visar spelarens hjälte i fraktionens färg. "+" är tangenten som väljer hjälten.
   # Färgen hämtas via spelarens fraktion, eftersom hjälten inte har någon egen fraktion.
   def show_hero(self, player):
      hero = player.get_hero()
      colors = FACTION_COLORS.get(player.get_faction().get_name())
      if colors is None:
         color = ""   # okänd fraktion: ingen färg
      else:
         color = colors[0]   # samma färg som fraktionens figurer
      goal = player.get_faction().get_ritual_goal()
      return f"+. {color}{hero.short()}{RESET}  (ritual goal ☩ {goal})"

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

   # Visar hjälte, hand och armé och frågar vad spelaren vill göra:
   #   siffra = lägg det kortet från handen
   #   bokstav = gör en action med det kortet i armén
   #   0 = passa
   # Returnerar två saker: vad spelaren valde ("card", "action" eller "pass") och vilket kort.
   def choose_move(self, player, can_play, can_act):
      hand = player.get_hand()
      army = player.get_army()

      print(f"\n--- {player.get_name()}'s turn ---")
      print("Hero:")
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

      # Frågan visar bara de val som går just nu
      options = []
      if can_play:
         options.append(f"1-{len(hand)} play a card")
      if can_act:
         options.append(f"a-{LETTERS[len(army) - 1]} act with a card")
      options.append("0) end turn")
      question = ", ".join(options) + ": "

      while True:
         answer = input(question).strip().lower()

         if answer == "0":
            return "pass", None

         if can_play and answer.isdigit() and 1 <= int(answer) <= len(hand):
            card = hand[int(answer) - 1]
            if player.can_afford(card):
               return "card", card
            print(f"Not enough {RESOURCE_NAME} for {card.get_name()} (costs {card.get_cost()}).")
            continue

         if can_act and len(answer) == 1 and answer in LETTERS[:len(army)]:
            card = army[LETTERS.index(answer)]
            if card.can_attack():
               return "action", card
            print(f"{card.get_name()} cannot act.")
            continue

         print("Not a valid choice.")

   # Shows the allowed targets and lets the player pick one. Returns the target.
   # The game decides which targets are allowed (Player.get_targets), not the terminal.
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
