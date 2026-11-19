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
      "magic": card.get_magic(),
      "statuses": card.statuses(),
   }


# Hjälten har samma värden som ett kort, och dessutom armor (bara hjälten har armor)
def hero_state(hero):
   state = card_state(hero)
   state["armor"] = hero.get_armor()
   return state


class Snapshot:
   def __init__(self, game):
      self.players = {}
      for player in (game.player1, game.player2):
         hero = player.get_hero()
         self.players[player.get_name()] = {
            "hero": hero_state(hero),
            "ritual": hero.get_ritual(),
            "resource": player.get_resource(),
            "burned": len(player.get_burned()),
            # id(card) skiljer två exemplar av samma kort åt
            "army": {id(card): card_state(card) for card in player.get_army()},
            "deck": {id(card) for card in player.get_deck().get_cards()},
            "hand": {id(card) for card in player.get_hand()},
            "graveyard": {id(card): card.get_name() for card in player.get_graveyard()},
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
               if card_id in before["deck"]:
                  where = " from the deck"            # SUMMON
               elif card_id in before["graveyard"]:
                  where = " from the graveyard"       # Resurrect
               else:
                  where = ""
               lines.append(f"{card['name']} enters the board{where} {self.stats_text(card)}")

         # Kort som lämnade gravhögen utan att komma ut på brädet
         for card_id, card_name in before["graveyard"].items():
            if card_id not in after["graveyard"] and card_id not in after["army"]:
               if card_id in after["hand"]:
                  lines.append(f"{card_name} returns to {name}'s hand")
               else:
                  lines.append(f"{card_name} is eaten")   # DEVOUR

         # Kort som gick från leken till handen är dragna. Kort som inte fick plats
         # i handen (full hand, 10 kort) försvinner och räknas för sig.
         burned = after["burned"] - before["burned"]
         drawn = len(before["deck"] & after["hand"])
         if drawn > 0:
            lines.append(f"{name} draws {drawn} card{'s' if drawn > 1 else ''}")
         if burned > 0:
            lines.append(f"{name}'s hand is full: {burned} card{'s' if burned > 1 else ''} burned")
      return lines

   # Kortets stats inom hakparentes, till exempel [⚔️ 5 ❤️ 4]
   def stats_text(self, card):
      return f"[⚔️ {card['attack']} ❤️ {card['health']}]"

   # Ändrade stats och statusar för ett kort eller en hjälte.
   # Bara hjälten har armor, så den jämförs bara när den finns med.
   def stat_changes(self, before, after):
      lines = []
      icons = {"health": "❤️", "attack": "⚔️", "armor": "🛡️", "magic": "🪄"}
      for stat, icon in icons.items():
         if stat in before and before[stat] != after[stat]:
            lines.append(f"{before['name']}: {icon} {before[stat]} → {after[stat]}")
      for status in after["statuses"]:
         if status not in before["statuses"]:
            lines.append(f"{before['name']} is now {status}")
      for status in before["statuses"]:
         if status not in after["statuses"]:
            lines.append(f"{before['name']} is no longer {status}")
      return lines
