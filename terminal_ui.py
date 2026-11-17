"""
Everything to do with the terminal: colors and output.

The cards know nothing about colors. This module decides how they look.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

# Allt som har med terminalen att göra: färger och utskrift.
# Korten vet inget om färger. De vet bara vad de är, och här bestäms hur de ser ut.

from card import SpellCard, FactionName


RESET = "\033[0m"   # tillbaka till terminalens vanliga färg

LETTERS = "abcdefghijklmnopqrstuvwxyz"   # korten i armén väljs med bokstäver


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


# Väljer färg efter kortets fraktion, och om kortet är en spell eller inte
def color_for(card):
   colors = FACTION_COLORS.get(card.get_faction())
   if colors is None:
      return ""   # okänd fraktion: ingen färg
   creature_color, spell_color = colors
   if isinstance(card, SpellCard):
      return spell_color
   return creature_color


# Kortets korta visning i rätt färg
def colored(card):
   return f"{color_for(card)}{card.short()}{RESET}"


# Visar spelarens hand som en numrerad lista i färg, en rad per kort
def show_hand(player):
   lines = []
   for number, card in enumerate(player.get_hand(), start=1):
      lines.append(f"{number}. {colored(card)}")
   return "\n".join(lines)


# Visar spelarens armé med bokstäver, en rad per kort
def show_army(player):
   lines = []
   for index, card in enumerate(player.get_army()):
      lines.append(f"{LETTERS[index]}. {colored(card)}")
   return " | ".join(lines)


# Visar spelarens döda hög i färg, med | mellan korten
def show_graveyard(player):
   lines = []
   for card in player.get_graveyard():
      lines.append(colored(card))
   return " | ".join(lines)


# Visar spelarens hjälte i fraktionens färg. "+" är tangenten som väljer hjälten.
# Färgen hämtas via spelarens fraktion, eftersom hjälten inte har någon egen fraktion.
def show_hero(player):
   hero = player.get_hero()
   colors = FACTION_COLORS.get(player.get_faction().get_name())
   if colors is None:
      color = ""   # okänd fraktion: ingen färg
   else:
      color = colors[0]   # samma färg som fraktionens figurer
   return f"+. {color}{hero.short()}{RESET}"
