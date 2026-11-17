import terminal_ui
from player import Player
from factions.ghouls import ghouls


player = Player("Joe", ghouls)


player.draw_cards(5)

print(terminal_ui.show_hand(player))

