"""
Images for the graphical interface: finds the right file for a card or a hero,
loads it once and keeps scaled copies, so that nothing is loaded twice.

File names follow one pattern, for example
   assets/creatures/Ghouls-Creature-Elder-Ghoul.png
   assets/creatures/Academics-Ritual-Midnight-Seminar.png
   assets/spells/Academics-Spell-Rlyeh-Text.png
A card without an image yet is drawn without one (see renderer.py).
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import os
import pygame
from card import FactionName, RitualCard, SpellCard

# Mappen assets ligger bredvid mappen gui
ASSET_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Hur fraktionens namn skrivs i början av filnamnen
FACTION_PREFIX = {
   FactionName.ACADEMICS: "Academics",
   FactionName.GHOULS: "Ghouls",
   FactionName.SHOGGOTHS: "Shoggoths",
   FactionName.DEEP_ONES: "The-Deep-Ones",
}


# En bild per tier för figurer som inte har en egen bild än: alla figurer i tier 1 använder
# tier 1-bilden, och så vidare (användarens beslut). Tier räknas från kostnaden, högst 3.
TIER_PORTRAITS = {
   FactionName.GHOULS: {
      1: "Ghouls-Creature-Hollow-Eyed-Stalker.png",
      2: "Ghouls-Creature-Crypt-Warden.png",
      3: "Ghouls-Creature-Elder-Ghoul.png",
   },
   FactionName.ACADEMICS: {
      1: "Academics-Creature-Novice-Occultist.png",
      2: "Academics-Creature-Miskatonic-Apprentice.png",
      3: "Academics-Creature-Dr-Francis-Morgan.png",
   },
}
HIGHEST_TIER = 3


# Ett kortnamn som en del av ett filnamn: "Dr. Francis Morgan" -> "Dr-Francis-Morgan",
# "R'lyeh Text" -> "Rlyeh-Text". Tecken som inte får finnas i filnamn tas bort.
def file_name(name):
   cleaned = name.replace("'", "").replace(".", "")
   return "-".join(cleaned.split())


class ImageLibrary:
   def __init__(self):
      self.originals = {}   # sökväg -> bilden som den är i filen (None om filen saknas)
      self.scaled = {}      # (sökväg, storlek) -> skalad bild

   # En bild i en viss storlek, eller None om filen inte finns
   def get(self, path, size):
      if path is None:
         return None
      key = (path, size)
      if key not in self.scaled:
         original = self.load(path)
         self.scaled[key] = None if original is None else pygame.transform.smoothscale(original, size)
      return self.scaled[key]

   # Laddar en bild en gång. convert_alpha behåller genomskinligheten (porträttens rundade hörn).
   def load(self, path):
      if path not in self.originals:
         if os.path.exists(path):
            self.originals[path] = pygame.image.load(path).convert_alpha()
         else:
            self.originals[path] = None
      return self.originals[path]

   # Porträttet till ett kort: figurer och ritualkort i creatures, spells i spells.
   # Kort utan fraktion (Trinket) ligger i cards. En figur utan egen bild får sin tiers bild.
   def portrait_path(self, card):
      if card.get_faction() is None:
         return os.path.join(ASSET_FOLDER, "cards", file_name(card.get_name()).lower() + ".png")
      prefix = FACTION_PREFIX[card.get_faction()]
      if isinstance(card, SpellCard):
         folder, kind = "spells", "Spell"
      elif isinstance(card, RitualCard):
         folder, kind = "creatures", "Ritual"
      else:
         folder, kind = "creatures", "Creature"
      own = os.path.join(ASSET_FOLDER, folder, f"{prefix}-{kind}-{file_name(card.get_name())}.png")
      if os.path.exists(own) or kind != "Creature":
         return own
      return self.tier_portrait_path(card)

   # Bilden för figurens tier, eller None om fraktionen inte har några tierbilder
   def tier_portrait_path(self, card):
      tiers = TIER_PORTRAITS.get(card.get_faction())
      if tiers is None:
         return None
      tier = min(max(card.get_cost(), 1), HIGHEST_TIER)
      return os.path.join(ASSET_FOLDER, "creatures", tiers[tier])

   # Ramen till ett kort, i fraktionens färg. Ett kort utan fraktion (Trinket) får ramen
   # från fraktionen hos den som har kortet (owner_faction), som The Coin i Hearthstone.
   def frame_path(self, card, owner_faction=None):
      faction = card.get_faction() or owner_faction
      if faction is None:
         return None
      name = FACTION_PREFIX[faction].lower()
      return os.path.join(ASSET_FOLDER, "cards", f"card_frame-{name}.png")

   # Hjältens bild: den första filen i hero_portraits som börjar med fraktionens namn
   def hero_path(self, faction_name):
      folder = os.path.join(ASSET_FOLDER, "hero_portraits")
      prefix = FACTION_PREFIX[faction_name] + "-"
      for name in sorted(os.listdir(folder)):
         if name.startswith(prefix):
            return os.path.join(folder, name)
      return None

   def board_path(self):
      return os.path.join(ASSET_FOLDER, "boards", "bg.png")
