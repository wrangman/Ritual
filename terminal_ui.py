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

import time
from card import SpellCard, RitualCard, FactionName
from move import Attack, Sacrifice
from event import MoveEvent, ChangeEvent, GameWon


RESET = "\033[0m"   # tillbaka till terminalens vanliga färg
DIM = "\033[2m"     # grå, svag text: för kort som inte går att använda just nu

LETTERS = "abcdefghijklmnopqrstuvwxyz"   # korten i armén väljs med bokstäver

# Vad varje sorts drag med ett kort på brädet heter när spelaren ska välja, i den ordning de visas
ARMY_MOVE_KINDS = [(Attack, "attack"), (Sacrifice, "sacrifice")]

RESOURCE_NAME = "Resource"   # vad resursen heter i spelet (namnet är inte bestämt än)

MESSAGE_DELAY = 0.7   # sekunder efter varje meddelande, så att man hinner se datorns drag


# Ger en ANSI-kod som färgar texten efter den, med exakt den här färgen (röd, grön, blå 0–255)
def rgb(red, green, blue):
   return f"\033[38;2;{red};{green};{blue}m"


# Ljusgrå för kortens beskrivning (↳ ...). Ljusare än DIM, så att texten går att läsa,
# men fortfarande svagare än kortet själv. DIM betyder "går inte att använda nu".
TEXT_COLOR = rgb(190, 190, 190)


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

   # Visar spelarens hand som en numrerad lista, en rad per kort.
   # Kostnaden står först inom parentes, till exempel "1. (2) Dark Occultist [...]".
   # Med moves (de lagliga dragen) visas kort som inte går att lägga nu i grått,
   # med skälet efter, så att man direkt ser vad man kan göra.
   def show_hand(self, player, moves=None):
      lines = []
      for card in player.get_hand():
         if moves is None or self.moves_for(card, moves):
            line = f"({card.get_cost()}) {self.colored(card)}"
         else:
            reason = self.why_not_playable(player, card)
            line = f"{DIM}({card.get_cost()}) {card.short()}  – {reason}{RESET}"
         lines.append(line + self.card_text(card))
      return self.numbered(lines)

   # Vad kortet gör (kortets special-text) på en egen rad under kortet, eller ingenting
   def card_text(self, card):
      special = card.get_special()
      if special is None:
         return ""
      return f"\n      {TEXT_COLOR}↳ {special.value}{RESET}"

   # Visar spelarens armé, ett kort per rad. Med moves (den egna armén) får korten
   # bokstäver, och kort som inte kan anfalla nu visas i grått med skälet efter.
   # Utan moves (motståndarens armé) är det bara att titta.
   def show_army(self, player, moves=None):
      lines = []
      for index, card in enumerate(player.get_army()):
         if moves is None:
            lines.append(f"   {self.colored(card)}")
         elif self.moves_for(card, moves):
            # Till exempel "can attack or sacrifice"
            kinds = [kind for kind, _ in self.group_by_kind(self.moves_for(card, moves))]
            can_do = "can " + self.or_list(kinds)
            lines.append(f"{LETTERS[index]}. {self.colored(card)}  – {can_do}")
         else:
            reason = self.why_cannot_attack(card)
            lines.append(f"{LETTERS[index]}. {DIM}{card.short()}  – {reason}{RESET}")
      return "\n".join(lines)

   # Varför går kortet inte att lägga? Game har redan bestämt det (det finns inget drag);
   # här letar terminalen bara upp en förklaring åt spelaren.
   def why_not_playable(self, player, card):
      missing = card.get_cost() - player.get_resource()
      if missing > 0:
         return f"need {missing} more {RESOURCE_NAME}"
      if not isinstance(card, SpellCard) and not player.has_room_on_board():
         return "the board is full"
      return "no valid target"

   # Varför kan kortet inte anfalla just nu?
   def why_cannot_attack(self, card):
      if isinstance(card, RitualCard):
         return "ritual cards never attack"
      if not card.is_ready():
         return "new on the board, can attack next turn"
      if card.has_attacked():
         return "has already attacked this turn"
      return "can't attack (spell effect)"

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

   # Visar en händelse från Game som en rad text. Sorten avgör hur raden ser ut:
   # ett drag får ">>", det som draget ändrade dras in under det, och det man ska
   # lägga märke till (din tur, vinst ...) står för sig. Ett grafiskt gränssnitt
   # har en metod med samma namn som i stället animerar händelsen.
   # En kort paus efter varje rad, annars rusar datorns drag förbi innan man hinner läsa dem.
   def show_event(self, event):
      text = event.describe()
      if isinstance(event, GameWon):
         text = f"WINNER BY A MILE - MAYBE!\n\n {event.player.get_name()}"
      if isinstance(event, MoveEvent):
         print(f"\n>> {text}")
      elif isinstance(event, ChangeEvent):
         print(f"   {text}")
      else:
         print(f"\n{text}")
      time.sleep(MESSAGE_DELAY)


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

      print(f"\nOpponent {opponent.get_name()}:")
      print(self.show_hero(opponent))
      if opponent.get_army():
         print(self.show_army(opponent))
      print("\nYour hero:")
      print(self.show_hero(player))
      if army:
         print("Your army:")
         print(self.show_army(player, moves))

      resource_line = f"\n{RESOURCE_NAME}: {player.get_resource()} of {player.get_max_resource()}"
      if player.get_overload() > 0:
         resource_line += f"  (overload: {player.get_overload()} less next turn)"
      print(resource_line)
      print("Hand (cost):")
      print(self.show_hand(player, moves))

      # Vilka kort går att lägga, och vilka kort får anfalla? Det står i dragen.
      playable = []
      for number, card in enumerate(hand, start=1):
         if self.moves_for(card, moves):
            playable.append(str(number))
      attackers = []
      for index, card in enumerate(army):
         if self.moves_for(card, moves):
            attackers.append(LETTERS[index])

      # Frågan räknar upp exakt de val som går just nu
      options = []
      if playable:
         options.append(f"play {', '.join(playable)}")
      if attackers:
         verb = "attack with"
         if any(isinstance(move, Sacrifice) for move in moves):
            verb = "attack/sacrifice with"
         options.append(f"{verb} {', '.join(attackers)}")
      options.append("0 end turn")
      question = " | ".join(options) + ": "

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
            if card in hand:
               print(f"You can't play {card.get_name()}: {self.why_not_playable(player, card)}.")
            else:
               print(f"{card.get_name()} can't attack: {self.why_cannot_attack(card)}.")
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

   # Delar upp kortets drag efter sort: [("attack", [...]), ("sacrifice", [...])].
   # Bara sorter som kortet faktiskt kan göra kommer med.
   def group_by_kind(self, card_moves):
      groups = []
      for move_class, kind in ARMY_MOVE_KINDS:
         found = [move for move in card_moves if isinstance(move, move_class)]
         if found:
            groups.append((kind, found))
      return groups

   # ["attack", "sacrifice"] -> "attack or sacrifice"; med fler ord: "a, b or c"
   def or_list(self, words):
      if len(words) == 1:
         return words[0]
      return ", ".join(words[:-1]) + " or " + words[-1]

   # Kortet kan göra ett eller flera drag. Kan det göra flera sorter (anfalla, offra sig)
   # frågas först vilken, så att fiender och egna kort inte blandas i samma lista.
   # Har dragen olika mål får spelaren sedan välja mål.
   def choose_move_for_card(self, card_moves):
      groups = self.group_by_kind(card_moves)
      if len(groups) > 1:
         choices = [f"{number}) {kind}" for number, (kind, _) in enumerate(groups, start=1)]
         question = self.or_list(choices) + "? "
         while True:
            answer = input(question).strip()
            if answer.isdigit() and 1 <= int(answer) <= len(groups):
               card_moves = groups[int(answer) - 1][1]
               break
            print("Not a valid choice.")

      if len(card_moves) == 1:
         return card_moves[0]
      targets = []
      for move in card_moves:
         targets.append(move.get_target())
      if isinstance(card_moves[0], Sacrifice):
         target = self.choose_target(targets, "Give its health to which of your cards?")
      else:
         target = self.choose_target(targets)
      for move in card_moves:
         if move.get_target() is target:
            return move

   # Shows the allowed targets and lets the player pick one. Returns the target.
   # The game decides which targets are allowed (Game.get_legal_moves), not the terminal.
   # Targets are shown without color: colored() needs get_faction(), and the hero has no faction.
   def choose_target(self, targets, title="Targets:"):
      lines = []
      for target in targets:
         lines.append(target.short())
      print(title)
      print(self.numbered(lines))

      while True:
         answer = input(f"Choose a target 1-{len(targets)}: ").strip()
         if answer.isdigit() and 1 <= int(answer) <= len(targets):
            return targets[int(answer) - 1]
         print("Not a valid choice.")

   # Mulligan: visar starthanden och frågar vilka kort som ska bytas, till exempel "1 3".
   # Returnerar en lista med korten (tom lista = behåll alla). Ett grafiskt gränssnitt
   # ska ha en metod med samma namn som gör samma sak, till exempel genom att klicka på korten.
   def choose_mulligan(self, cards):
      lines = []
      for card in cards:
         lines.append(f"({card.get_cost()}) {self.colored(card)}{self.card_text(card)}")
      print("Your starting hand:")
      print(self.numbered(lines))

      while True:
         answers = input("Replace which cards? (for example 1 3, or Enter to keep all): ").split()
         if all(answer.isdigit() and 1 <= int(answer) <= len(cards) for answer in answers):
            numbers = sorted(set(int(answer) for answer in answers))   # set: samma kort bara en gång
            return [cards[number - 1] for number in numbers]
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
