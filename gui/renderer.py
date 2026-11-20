"""
Draws the things in the game: a whole card (frame + portrait + text), a
portrait on the board with its stats, a hero, and the back of a card.

A card is a frame (assets/cards) with a portrait (assets/creatures or
assets/spells) inside. On the board only the portrait is shown, with the stats
as small round badges, as in the user's design: the portrait "falls out of the
card" when it is played.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import pygame
from card import CreatureCard, RitualCard, FactionName

# Färger för stats, samma ordning som ikonerna i terminalen (⚔️ ❤️ 🪄 ☩ 🛡️)
ATTACK_COLOR = (215, 150, 30)
HEALTH_COLOR = (175, 35, 35)
MAGIC_COLOR = (55, 100, 215)
RITUAL_COLOR = (130, 55, 165)
ARMOR_COLOR = (140, 140, 150)
COST_COLOR = (45, 90, 200)
TEXT_COLOR = (235, 225, 205)
DAMAGED_COLOR = (255, 120, 110)   # health under max syns i rött

# Fraktionens färg på kortens baksida och på kort utan ram
FACTION_RGB = {
   FactionName.GHOULS: (115, 30, 55),
   FactionName.ACADEMICS: (35, 60, 130),
   FactionName.SHOGGOTHS: (150, 115, 20),
   FactionName.DEEP_ONES: (25, 100, 60),
}
NEUTRAL_RGB = (95, 80, 55)

# Var sakerna sitter i kortramen, som andelar av ramens bredd och höjd (bilden är 1024 x 1536)
FRAME_PORTRAIT = (0.07, 0.05, 0.86, 0.59)
FRAME_NAME = (0.05, 0.655, 0.90, 0.06)
FRAME_TEXT = (0.07, 0.735, 0.86, 0.17)
FRAME_BOTTOM = (0.07, 0.915, 0.86, 0.06)


# En del av en ruta, angiven med andelar: part(ruta, (0.1, 0.2, 0.5, 0.5))
def part(rect, fractions):
   x, y, w, h = fractions
   return pygame.Rect(rect.x + int(rect.width * x), rect.y + int(rect.height * y),
                      int(rect.width * w), int(rect.height * h))


class Renderer:
   def __init__(self, images):
      self.images = images
      self.fonts = {}

   # Ett typsnitt i en viss storlek, sparat så att det bara skapas en gång.
   # SysFont tar en lista med namn och väljer det första som finns på datorn.
   def font(self, size, bold=False, kind="serif"):
      key = (size, bold, kind)
      if key not in self.fonts:
         names = {"serif": "georgia,palatinolinotype,timesnewroman,serif",
                  "sans": "segoeui,arial,helvetica,sans",
                  "mono": "consolas,couriernew,monospace"}[kind]
         self.fonts[key] = pygame.font.SysFont(names, size, bold=bold)
      return self.fonts[key]

   # Det största typsnittet (högst size) där texten får plats i width, till exempel långa kortnamn
   def fitting_font(self, text, size, width, bold=True):
      while size > 8 and self.font(size, bold).size(text)[0] > width:
         size -= 1
      return self.font(size, bold)

   # Skriver text med en mörk skugga, så att den syns mot alla bakgrunder
   def text(self, surface, text, font, color=TEXT_COLOR, center=None, topleft=None):
      image = font.render(text, True, color)
      shadow = font.render(text, True, (0, 0, 0))
      rect = image.get_rect(center=center) if center else image.get_rect(topleft=topleft)
      surface.blit(shadow, rect.move(2, 2))
      surface.blit(image, rect)
      return rect

   # Delar en text i rader som får plats i en viss bredd
   def wrap(self, text, font, width):
      lines = []
      line = ""
      for word in text.split():
         candidate = f"{line} {word}".strip()
         if font.size(candidate)[0] <= width:
            line = candidate
         else:
            lines.append(line)
            line = word
      if line:
         lines.append(line)
      return lines

   # En rund bricka med ett tal, för attack, health, magic, ritual, armor och kostnad
   def badge(self, surface, center, value, color, radius, number_color=TEXT_COLOR):
      pygame.draw.circle(surface, (0, 0, 0), (center[0] + 2, center[1] + 2), radius)
      pygame.draw.circle(surface, color, center, radius)
      pygame.draw.circle(surface, (225, 200, 140), center, radius, 2)
      self.text(surface, str(value), self.font(int(radius * 1.25), bold=True), number_color, center=center)

   # Porträttbilden, eller en mörk ruta med namnet om bilden inte finns än
   def portrait_image(self, surface, card, rect):
      image = self.images.get(self.images.portrait_path(card), rect.size)
      if image:
         surface.blit(image, rect)
      else:
         color = FACTION_RGB.get(card.get_faction(), NEUTRAL_RGB)
         pygame.draw.rect(surface, (20, 15, 15), rect, border_radius=14)
         pygame.draw.rect(surface, color, rect, 4, border_radius=14)
         font = self.font(max(12, rect.width // 9))
         lines = self.wrap(card.get_name(), font, rect.width - 16)
         for i, line in enumerate(lines):
            y = rect.centery + (i - (len(lines) - 1) / 2) * font.get_linesize()
            self.text(surface, line, font, center=(rect.centerx, int(y)))

   # Ett kort på brädet: porträttet med stats i hörnen, som brickor.
   # ⚔️ nere till vänster, ❤️ nere till höger, 🪄 uppe till vänster, ☩ uppe till höger.
   # border: färgen på en ram runt porträttet (till exempel "kan anfalla"), eller None.
   def board_card(self, surface, card, rect, border=None):
      if card.has_guard():
         pygame.draw.rect(surface, (200, 185, 140), rect.inflate(14, 14), 7, border_radius=20)
      if border:
         pygame.draw.rect(surface, border, rect.inflate(8, 8), 5, border_radius=18)
      self.portrait_image(surface, card, rect)
      if not card.can_be_attacked():   # dold (Veil of Tiamat, Void Wraith): halvgenomskinlig slöja
         veil = pygame.Surface(rect.size, pygame.SRCALPHA)
         veil.fill((30, 30, 50, 130))
         surface.blit(veil, rect)

      radius = rect.width // 7
      if not isinstance(card, RitualCard):
         self.badge(surface, (rect.left + radius, rect.bottom - radius), card.get_attack(), ATTACK_COLOR, radius)
      health_color = DAMAGED_COLOR if card.get_health() < card.get_max_health() else TEXT_COLOR
      self.badge(surface, (rect.right - radius, rect.bottom - radius), card.get_health(), HEALTH_COLOR,
                 radius, health_color)
      if card.get_magic() > 0:
         self.badge(surface, (rect.left + radius, rect.top + radius), card.get_magic(), MAGIC_COLOR, radius * 4 // 5)
      if card.get_ritual() > 0:
         self.badge(surface, (rect.right - radius, rect.top + radius), card.get_ritual(), RITUAL_COLOR, radius * 4 // 5)

      statuses = [s for s in card.statuses() if s != "Guard"]   # Guard syns redan som ram
      if statuses:
         self.text(surface, ", ".join(statuses), self.font(16, kind="sans"), center=(rect.centerx, rect.bottom + 16))

   # Ett helt kort: ram, porträtt, namn, text, kostnad och (för figurer) stats.
   # owner_faction: fraktionen hos den som har kortet, för kort utan egen fraktion (Trinket).
   def card(self, surface, card, rect, dim=False, border=None, owner_faction=None):
      if border:
         pygame.draw.rect(surface, border, rect.inflate(10, 10), 5, border_radius=16)
      frame = self.images.get(self.images.frame_path(card, owner_faction), rect.size)
      if frame:
         surface.blit(frame, rect)
      else:
         pygame.draw.rect(surface, (25, 20, 15), rect, border_radius=12)
         pygame.draw.rect(surface, NEUTRAL_RGB, rect, 5, border_radius=12)
      self.portrait_image(surface, card, part(rect, FRAME_PORTRAIT))

      name_rect = part(rect, FRAME_NAME)
      name_font = self.fitting_font(card.get_name(), max(11, rect.width // 13), name_rect.width)
      self.text(surface, card.get_name(), name_font, center=name_rect.center)

      text_rect = part(rect, FRAME_TEXT)
      if card.get_special():
         font = self.font(max(10, rect.width // 15), kind="sans")
         for i, line in enumerate(self.wrap(card.get_special().value, font, text_rect.width)):
            self.text(surface, line, font, topleft=(text_rect.x, text_rect.y + i * font.get_linesize()))

      radius = rect.width // 9
      self.badge(surface, (rect.left + radius, rect.top + radius), card.get_cost(), COST_COLOR, radius)
      if isinstance(card, CreatureCard):
         bottom = part(rect, FRAME_BOTTOM)
         if not isinstance(card, RitualCard):
            self.badge(surface, (bottom.left + radius, bottom.centery), card.get_attack(), ATTACK_COLOR, radius)
         self.badge(surface, (bottom.right - radius, bottom.centery), card.get_health(), HEALTH_COLOR, radius)
         if card.get_magic() > 0:
            self.badge(surface, (bottom.centerx - radius, bottom.centery), card.get_magic(), MAGIC_COLOR, radius * 4 // 5)
         if card.get_ritual() > 0:
            self.badge(surface, (bottom.centerx + radius, bottom.centery), card.get_ritual(), RITUAL_COLOR, radius * 4 // 5)

      if dim:   # kortet går inte att spela nu
         shade = pygame.Surface(rect.size, pygame.SRCALPHA)
         shade.fill((0, 0, 0, 140))
         surface.blit(shade, rect)

   # Ett kort ritat på en egen yta, till exempel för en effekt som visar kortet stort
   def card_image(self, card, size, owner_faction=None):
      image = pygame.Surface(size, pygame.SRCALPHA)
      self.card(image, card, pygame.Rect((0, 0), size), owner_faction=owner_faction)
      return image

   # Ett porträtt ritat på en egen yta (för ett kort som dör och tonar bort)
   def portrait_surface(self, card, size):
      image = pygame.Surface(size, pygame.SRCALPHA)
      self.portrait_image(image, card, pygame.Rect((0, 0), size))
      return image

   # Motståndarens kort syns bara bakifrån, i fraktionens färg
   def card_back(self, surface, rect, faction_name):
      color = FACTION_RGB.get(faction_name, NEUTRAL_RGB)
      pygame.draw.rect(surface, color, rect, border_radius=14)
      pygame.draw.rect(surface, (20, 10, 10), rect, 2, border_radius=14)

   # Hjälten: bilden, ❤️ och 🛡️ som brickor, och ritual och resurs under
   def hero(self, surface, player, rect, border=None):
      hero = player.get_hero()
      if border:
         pygame.draw.rect(surface, border, rect.inflate(10, 10), 5, border_radius=16)
      image = self.images.get(self.images.hero_path(player.get_faction().get_name()), rect.size)
      if image:
         surface.blit(image, rect)
      else:
         pygame.draw.rect(surface, FACTION_RGB.get(player.get_faction().get_name(), NEUTRAL_RGB), rect,
                          border_radius=14)
         self.text(surface, hero.get_name(), self.font(18, bold=True), center=rect.center)

      radius = 26
      health_color = DAMAGED_COLOR if hero.get_health() < hero.get_max_health() else TEXT_COLOR
      self.badge(surface, (rect.right - radius, rect.bottom - radius), hero.get_health(), HEALTH_COLOR,
                 radius, health_color)
      if hero.get_armor() > 0:
         self.badge(surface, (rect.right - 3 * radius, rect.bottom - radius), hero.get_armor(), ARMOR_COLOR, radius)

      font = self.font(22, bold=True)
      goal = player.get_faction().get_ritual_goal()
      lines = [f"{player.get_name()}",
               f"Ritual {hero.get_ritual()} / {goal}",
               f"Resource {player.get_resource()} / {player.get_max_resource()}"]
      if player.get_overload() > 0:
         lines.append(f"Overload {player.get_overload()}")
      if player.get_stress() > 0:
         lines.append(f"Stress {player.get_stress()}")
      for i, line in enumerate(lines):
         self.text(surface, line, font, center=(rect.centerx, rect.bottom + 22 + i * 28))
      statuses = hero.statuses()
      if statuses:
         self.text(surface, ", ".join(statuses), self.font(16, kind="sans"), center=(rect.centerx, rect.top - 14))
