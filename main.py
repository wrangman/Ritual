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

print("Army:", [card.short() for card in player1.get_army()])
print("Graveyard:", [card.short() for card in player1.get_graveyard()])

