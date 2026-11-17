# Allt som har med terminalen att göra: färger och utskrift.
# Korten vet inget om färger. De vet bara vad de är, och här bestäms hur de ser ut.

from card import SpellCard


RESET = "\033[0m"   # tillbaka till terminalens vanliga färg


# Ger en ANSI-kod som färgar texten efter den, med exakt den här färgen (röd, grön, blå 0–255)
def rgb(red, green, blue):
   return f"\033[38;2;{red};{green};{blue}m"


# Fraktion -> (färg för figurer, färg för spells)
FACTION_COLORS = {
   "Ghouls":        (rgb(150, 0, 0),   rgb(230, 60, 80)),    # mörkröd, ljusare blodröd
   "The Academics": (rgb(40, 90, 210), rgb(120, 180, 255)),  # blå, ljusblå
   "Shoggoths":     (rgb(200, 150, 0), rgb(255, 215, 80)),   # gyllengul, ljus guld
   "The Deep Ones": (rgb(20, 130, 60), rgb(100, 220, 150)),  # grön, ljusgrön
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
