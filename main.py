from game import Game
import terminal_ui
from player import Player
from factions.ghouls import ghouls
from factions.academics import academics


player1 = Player("Joe", academics)
player2 = Player("Moe", ghouls)

game = Game(player1, player2)
game.start()

game.play_turn(player1)

print("Army:", terminal_ui.show_armfy(player1))
print("Graveyard:", terminal_ui.show_graveyard(player1))

