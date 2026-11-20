"""
Moves: the things a player can do during their turn.

Game works out every legal move (Game.get_legal_moves) and the player's
controller picks one of them: a human through the terminal, or an AI. That way
the rules live in one place, and humans and AIs choose from the same list,
like the valid actions in MetaStone (a Hearthstone simulator).

Each move is a small object that knows how to carry itself out (Command
pattern, Gang of Four). A move is complete: it already has its target, so an
AI can try out each move and compare them.

Each move also knows which event tells the user interface about it (see event.py),
so Game does not need to know what kind of move it is.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from event import CardPlayed, AttackMade, CardSacrificed, TurnEnded


class Move:
   def __init__(self, card=None, target=None):
      self.card = card       # kortet som gör något (None för "end turn")
      self.target = target   # vem eller vad det träffar (None om det inte behövs)

   def get_card(self):
      return self.card

   def get_target(self):
      return self.target

   # Avslutar draget turen? Bara EndTurn gör det.
   def ends_turn(self):
      return False

   def execute(self, game):
      raise NotImplementedError("Varje sorts drag måste ha en egen execute()")

   # Händelsen som berättar för gränssnittet om draget, till exempel så att man ser vad AI:n gjorde
   def to_event(self, player):
      raise NotImplementedError("Varje sorts drag måste ha en egen to_event()")


# Lägg ett kort från handen: en figur hamnar på brädet, en spell används direkt.
class PlayCard(Move):
   def execute(self, game):
      game.play_card(self.card, self.target)

   def to_event(self, player):
      return CardPlayed(player, self.card, self.target)


# En figur på brädet anfaller.
class Attack(Move):
   def execute(self, game):
      game.attack(self.card, self.target)

   def to_event(self, player):
      return AttackMade(player, self.card, self.target)


# SACRIFICE: en figur offrar sig i stället för att anfalla. Den dör och ger
# sin ❤️ health till ett annat eget kort (target).
class Sacrifice(Move):
   def execute(self, game):
      game.sacrifice(self.card, self.target)

   def to_event(self, player):
      return CardSacrificed(player, self.card, self.target)


# Spelaren är klar med sin tur (till exempel för att spara resurs till ett dyrt kort).
class EndTurn(Move):
   def ends_turn(self):
      return True

   def execute(self, game):
      pass   # inget händer, Game avslutar turen

   def to_event(self, player):
      return TurnEnded(player)
