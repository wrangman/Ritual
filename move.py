"""
Moves: the things a player can do during their turn.

Game works out every legal move (Game.get_legal_moves) and the player's
controller picks one of them: a human through the terminal, or an AI. That way
the rules live in one place, and humans and AIs choose from the same list,
like the valid actions in MetaStone (a Hearthstone simulator).

Each move is a small object that knows how to carry itself out (Command
pattern, Gang of Four). A move is complete: it already has its target, so an
AI can try out each move and compare them.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


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

   # Kort text om draget, till exempel så att man ser vad AI:n gjorde
   def describe(self, player):
      raise NotImplementedError("Varje sorts drag måste ha en egen describe()")


# Lägg ett kort från handen: en figur hamnar på brädet, en spell används direkt.
class PlayCard(Move):
   def execute(self, game):
      game.play_card(self.card, self.target)

   def describe(self, player):
      text = f"{player.get_name()} plays {self.card.get_name()}"
      if self.target is not None:
         text += f" on {self.target.get_name()}"
      return text


# En figur på brädet anfaller.
class Attack(Move):
   def execute(self, game):
      game.attack(self.card, self.target)

   def describe(self, player):
      return f"{player.get_name()}: {self.card.get_name()} attacks {self.target.get_name()}"


# SACRIFICE: en figur offrar sig i stället för att anfalla. Den dör och ger
# sin ❤️ health till ett annat eget kort (target).
class Sacrifice(Move):
   def execute(self, game):
      game.sacrifice(self.card, self.target)

   def describe(self, player):
      return f"{player.get_name()}: {self.card.get_name()} sacrifices itself for {self.target.get_name()}"


# Spelaren är klar med sin tur (till exempel för att spara resurs till ett dyrt kort).
class EndTurn(Move):
   def ends_turn(self):
      return True

   def execute(self, game):
      pass   # inget händer, Game avslutar turen

   def describe(self, player):
      return f"{player.get_name()} ends the turn"
