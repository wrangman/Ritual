"""
A snapshot of the game: what everything looks like right now.

Game takes a snapshot before and after every move and shows the differences,
for example "Elder Ghoul: ❤️ 6 → 3" or "Night Archivist dies". That way the
player can always see what a move did, without every card or spell having to
describe its own result.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


# Det som går att jämföra för ett kort på brädet eller en hjälte
def card_state(card):
   return {
      "name": card.get_name(),
      "health": card.get_health(),
      "attack": card.get_attack(),
      "armor": card.get_armor(),
      "magic": card.get_magic(),
      "statuses": card.statuses(),
   }


class Snapshot:
   def __init__(self, game):
      self.players = {}
      for player in (game.player1, game.player2):
         hero = player.get_hero()
         self.players[player.get_name()] = {
            "hero": card_state(hero),
            "ritual": hero.get_ritual(),
            "resource": player.get_resource(),
            "deck": len(player.get_deck()),
            "burned": len(player.get_burned()),
            # id(card) skiljer två exemplar av samma kort åt
            "army": {id(card): card_state(card) for card in player.get_army()},
         }

   # Raderna som beskriver vad som har ändrats sedan den här bilden togs
   def changes_until(self, later):
      lines = []
      for name, before in self.players.items():
         after = later.players[name]

         lines += self.stat_changes(before["hero"], after["hero"])
         if before["ritual"] != after["ritual"]:
            lines.append(f"{before['hero']['name']}: ☩ {before['ritual']} → {after['ritual']}")
         if before["resource"] != after["resource"]:
            lines.append(f"{name}: Resource {before['resource']} → {after['resource']}")

         for card_id, card in before["army"].items():
            if card_id not in after["army"]:
               lines.append(f"{card['name']} dies")
            else:
               lines += self.stat_changes(card, after["army"][card_id])
         for card_id, card in after["army"].items():
            if card_id not in before["army"]:
               lines.append(f"{card['name']} enters the board")

         # Kort som dras syns som att leken krymper. Kort som inte fick plats i handen
         # (full hand, 10 kort) försvinner och räknas för sig.
         burned = after["burned"] - before["burned"]
         drawn = before["deck"] - after["deck"] - burned
         if drawn > 0:
            lines.append(f"{name} draws {drawn} card{'s' if drawn > 1 else ''}")
         if burned > 0:
            lines.append(f"{name}'s hand is full: {burned} card{'s' if burned > 1 else ''} burned")
      return lines

   # Ändrade stats och statusar för ett kort eller en hjälte
   def stat_changes(self, before, after):
      lines = []
      icons = {"health": "❤️", "attack": "⚔️", "armor": "🛡️", "magic": "🪄"}
      for stat, icon in icons.items():
         if before[stat] != after[stat]:
            lines.append(f"{before['name']}: {icon} {before[stat]} → {after[stat]}")
      for status in after["statuses"]:
         if status not in before["statuses"]:
            lines.append(f"{before['name']} is now {status}")
      for status in before["statuses"]:
         if status not in after["statuses"]:
            lines.append(f"{before['name']} is no longer {status}")
      return lines
