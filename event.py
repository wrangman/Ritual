"""
Events: what happened in the game, sent from Game to the user interface.

Game does not decide how things look. It only tells the interface what
happened, and the interface decides how to show it (Observer pattern, Gang of
Four). MetaStone, a Hearthstone simulator, works the same way with events such
as TurnStartEvent, PhysicalAttackEvent and DamageEvent.

There are three kinds of events, so that an interface knows what to do with them:
   MoveEvent    - a move a player made (play a card, attack, sacrifice).
                  A graphical interface animates it and adds it to the list of
                  recent moves (like the icons on the left in Hearthstone).
   ChangeEvent  - something that changed because of a move (health, a card dies,
                  a card enters the board). Shown on the board itself.
   NoticeEvent  - something the player must notice (your turn, the ritual is
                  nearly complete, stress, the winner). Shown in a box for a moment.

Every event can describe itself as one line of text. The terminal prints it,
and a console in a graphical interface can show the same line.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


# Ikoner för stats i texten, samma som på korten
STAT_ICONS = {"health": "❤️", "attack": "⚔️", "armor": "🛡️", "magic": "🪄"}


class GameEvent:
   # En rad text om händelsen, för terminalen och en konsol
   def describe(self):
      raise NotImplementedError("Varje sorts händelse måste ha en egen describe()")


class MoveEvent(GameEvent):
   pass


class ChangeEvent(GameEvent):
   pass


class NoticeEvent(GameEvent):
   pass


# Drag

class CardPlayed(MoveEvent):
   def __init__(self, player, card, target=None):
      self.player = player
      self.card = card
      self.target = target   # None om kortet inte har något mål

   def describe(self):
      text = f"{self.player.get_name()} plays {self.card.get_name()}"
      if self.target is not None:
         text += f" on {self.target.get_name()}"
      return text


class AttackMade(MoveEvent):
   def __init__(self, player, attacker, target):
      self.player = player
      self.attacker = attacker
      self.target = target

   def describe(self):
      return f"{self.player.get_name()}: {self.attacker.get_name()} attacks {self.target.get_name()}"


class CardSacrificed(MoveEvent):
   def __init__(self, player, card, target):
      self.player = player
      self.card = card
      self.target = target   # kortet som får styrkan

   def describe(self):
      return f"{self.player.get_name()}: {self.card.get_name()} sacrifices itself for {self.target.get_name()}"


# Ändringar efter ett drag (räknas ut av Snapshot)

# Ett värde på ett kort eller en hjälte ändrades, till exempel ❤️ 6 → 3
class StatChanged(ChangeEvent):
   def __init__(self, target, stat, before, after):
      self.target = target   # kortet eller hjälten
      self.stat = stat       # "health", "attack", "armor" eller "magic"
      self.before = before
      self.after = after

   def describe(self):
      return f"{self.target.get_name()}: {STAT_ICONS[self.stat]} {self.before} → {self.after}"


# Ett kort eller en hjälte fick eller tappade en status, till exempel Guard
class StatusChanged(ChangeEvent):
   def __init__(self, target, status, gained):
      self.target = target
      self.status = status
      self.gained = gained   # True: fick statusen. False: tappade den.

   def describe(self):
      if self.gained:
         return f"{self.target.get_name()} is now {self.status}"
      return f"{self.target.get_name()} is no longer {self.status}"


class RitualChanged(ChangeEvent):
   def __init__(self, player, before, after):
      self.player = player
      self.before = before
      self.after = after

   def describe(self):
      return f"{self.player.get_hero().get_name()}: ☩ {self.before} → {self.after}"


class ResourceChanged(ChangeEvent):
   def __init__(self, player, before, after):
      self.player = player
      self.before = before
      self.after = after

   def describe(self):
      return f"{self.player.get_name()}: Resource {self.before} → {self.after}"


class CardDied(ChangeEvent):
   def __init__(self, player, card):
      self.player = player   # kortets ägare
      self.card = card

   def describe(self):
      return f"{self.card.get_name()} dies"


# Ett kort kom ut på brädet. Varifrån: "hand", "deck" (SUMMON), "graveyard" (Resurrect)
# eller "nowhere" (ett spöke som en spell trollade fram).
class CardEnteredBoard(ChangeEvent):
   WHERE = {"hand": "", "deck": " from the deck", "graveyard": " from the graveyard", "nowhere": ""}

   def __init__(self, player, card, source):
      self.player = player
      self.card = card
      self.source = source
      # Värdena sparas nu, så att texten stämmer även om kortet ändras senare
      self.attack = card.get_attack()
      self.health = card.get_health()

   def describe(self):
      return (f"{self.card.get_name()} enters the board{self.WHERE[self.source]} "
              f"[⚔️ {self.attack} ❤️ {self.health}]")


# Ett kort gick från gravhögen tillbaka till handen (Book of the Nameless Dead)
class CardReturnedToHand(ChangeEvent):
   def __init__(self, player, card):
      self.player = player
      self.card = card

   def describe(self):
      return f"{self.card.get_name()} returns to {self.player.get_name()}'s hand"


# Ett kort i gravhögen åts upp (DEVOUR)
class CardEaten(ChangeEvent):
   def __init__(self, player, card):
      self.player = player
      self.card = card

   def describe(self):
      return f"{self.card.get_name()} is eaten"


class CardsDrawn(ChangeEvent):
   def __init__(self, player, count):
      self.player = player
      self.count = count

   def describe(self):
      return f"{self.player.get_name()} draws {self.count} card{'s' if self.count > 1 else ''}"


# Kort som inte fick plats i handen (full hand, 10 kort) och försvann
class CardsBurned(ChangeEvent):
   def __init__(self, player, count):
      self.player = player
      self.count = count

   def describe(self):
      return (f"{self.player.get_name()}'s hand is full: "
              f"{self.count} card{'s' if self.count > 1 else ''} burned")


# Draget ändrade ingenting, till exempel ett anfall som gjorde 0 skada
class NothingChanged(ChangeEvent):
   def describe(self):
      return "Nothing happened."


# Saker spelaren ska lägga märke till

class GotTrinket(NoticeEvent):
   def __init__(self, player):
      self.player = player   # den som börjar som tvåa

   def describe(self):
      return f"{self.player.get_name()} got the trinket and plays second."


class MulliganDone(NoticeEvent):
   def __init__(self, player, count):
      self.player = player
      self.count = count   # hur många kort som byttes

   def describe(self):
      return f"{self.player.get_name()} replaces {self.count} card(s)."


class TurnStarted(NoticeEvent):
   def __init__(self, player):
      self.player = player

   def describe(self):
      return f"--- {self.player.get_name()}'s turn ---"


class TurnEnded(NoticeEvent):
   def __init__(self, player):
      self.player = player

   def describe(self):
      return f"{self.player.get_name()} ends the turn."


# Leken är tom: hjälten tar skada (Stress, som Fatigue i Hearthstone)
class StressDamage(NoticeEvent):
   def __init__(self, player, amount):
      self.player = player
      self.amount = amount

   def describe(self):
      return (f"{self.player.get_name()} has no cards left. "
              f"Stress {self.amount}: the hero takes {self.amount} damage.")


# Kortet som drogs i början av turen fick inte plats i handen
class DrawBurned(NoticeEvent):
   def __init__(self, player, card):
      self.player = player
      self.card = card

   def describe(self):
      return f"{self.player.get_name()}'s hand is full: {self.card.get_name()} is burned."


# Varning till motståndaren: sista chansen att stoppa ritualen
class RitualNearlyComplete(NoticeEvent):
   def __init__(self, player):
      self.player = player

   def describe(self):
      return (f"☩ The ritual of {self.player.get_name()} is nearly complete! "
              f"Lower it before their next turn, or it is over.")


class GameWon(NoticeEvent):
   def __init__(self, player):
      self.player = player

   def describe(self):
      return f"{self.player.get_name()} wins!"


# Båda vann samtidigt, till exempel om båda hjältarna dog av samma effekt
class GameDrawn(NoticeEvent):
   def describe(self):
      return "Draw! Both rituals ended in madness."
