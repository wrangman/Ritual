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

# Var sakerna sitter i kortramen, som andelar av ramens bredd och höjd (bilden är 1024 x 1536).
# Ramens fönster är genomskinligt (mätt: x 0,073–0,927, y 0,07–0,636). Porträttet ritas under
# ramen och lite större än fönstret, så att ramen täcker porträttets egen kant.
FRAME_PORTRAIT = (0.035, 0.04, 0.93, 0.625)
FRAME_NAME = (0.05, 0.655, 0.90, 0.06)
FRAME_TEXT = (0.10, 0.735, 0.80, 0.15)


# Färger för brickornas skuggning: mörkare och ljusare varianter av en färg
def darker(color):
   return tuple(int(c * 0.45) for c in color)


def lighter(color):
   return tuple(int(c + (255 - c) * 0.35) for c in color)


# Blandar två färger: t = 0 ger a, t = 1 ger b
def mix(a, b, t):
   return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


# En del av en ruta, angiven med andelar: part(ruta, (0.1, 0.2, 0.5, 0.5))
def part(rect, fractions):
   x, y, w, h = fractions
   return pygame.Rect(rect.x + int(rect.width * x), rect.y + int(rect.height * y),
                      int(rect.width * w), int(rect.height * h))


class Renderer:
   BOARD_MARGIN = 20      # plats runt ett porträtt på en egen yta, för Guard-ramen och brickorna
   CACHE_LIMIT = 400      # så många färdigritade kort som sparas innan listan töms

   def __init__(self, images):
      self.images = images
      self.fonts = {}
      self.cache = {}   # färdigritade kort, så att de inte ritas om varje bildruta

   # Allt som syns på ett kort och kan ändras under spelet. Ändras något ritas kortet om.
   def card_state(self, card):
      state = (card.get_name(), card.get_cost())
      if isinstance(card, CreatureCard):
         state += (card.get_attack(), card.get_health(), card.get_max_health(), card.get_magic(),
                   card.get_ritual(), card.has_guard(), card.can_be_attacked())
      return state

   # Hämtar en färdigritad yta, eller ritar den med make() och sparar den
   def cached(self, key, make):
      if key not in self.cache:
         if len(self.cache) > self.CACHE_LIMIT:
            self.cache = {}
         self.cache[key] = make()
      return self.cache[key]

   # Ett helt kort på en egen yta (för handen, där korten lutar och växer)
   def card_surface(self, card, size, owner_faction=None, dim=False):
      key = ("card", id(card), size, owner_faction, dim, self.card_state(card))

      def make():
         image = pygame.Surface(size, pygame.SRCALPHA)
         self.card(image, card, pygame.Rect((0, 0), size), dim=dim, owner_faction=owner_faction)
         return image
      return self.cached(key, make)

   # Ett porträtt med stats på en egen yta (för brädet). Ytan är lite större än porträttet
   # (BOARD_MARGIN åt alla håll), så att Guard-ramen får plats.
   def board_surface(self, card, size):
      key = ("board", id(card), size, self.card_state(card))

      def make():
         margin = self.BOARD_MARGIN
         image = pygame.Surface((size[0] + 2 * margin, size[1] + 2 * margin), pygame.SRCALPHA)
         self.board_card(image, card, pygame.Rect((margin, margin), size), show_statuses=False)
         return image
      return self.cached(key, make)

   # Ett typsnitt i en viss storlek, sparat så att det bara skapas en gång.
   # SysFont tar en lista med namn och väljer det första som finns på datorn.
   def font(self, size, bold=False, kind="serif"):
      key = (size, bold, kind)
      if key not in self.fonts:
         names = {"serif": "georgia,palatinolinotype,timesnewroman,serif",
                  # Verdana är ritad för att vara lättläst på skärm i små storlekar
                  "sans": "verdana,tahoma,segoeui,arial,helvetica,sans",
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

   # En rund bricka med ett tal, för attack, health, magic, ritual, armor och kostnad.
   # Den ritas färdig en gång (badge_surface) och sätts sedan in med mitten på center.
   def badge(self, surface, center, value, color, radius, number_color=TEXT_COLOR):
      image = self.badge_surface(value, color, radius, number_color)
      surface.blit(image, image.get_rect(center=center))

   # Brickan ritas fyra gånger större och skalas ner (supersampling), så att kanterna blir mjuka.
   # Den har skugga, mörk kant, guldkant och en färg som går från mörk nedtill till ljus upptill,
   # som en slipad sten. Siffran får en svart kontur, så att den syns mot alla färger.
   def badge_surface(self, value, color, radius, number_color=TEXT_COLOR):
      key = ("badge", value, color, radius, number_color)

      def make():
         scale = 4
         size = 2 * radius + 8
         big = pygame.Surface((size * scale, size * scale), pygame.SRCALPHA)
         middle = pygame.Vector2(size * scale / 2, size * scale / 2)
         outer = radius * scale
         pygame.draw.circle(big, (0, 0, 0, 110), middle + (2 * scale, 3 * scale), outer)   # skugga
         pygame.draw.circle(big, (25, 18, 10), middle, outer)                               # mörk kant
         pygame.draw.circle(big, (205, 170, 95), middle, outer - 1 * scale)                 # guldkant
         pygame.draw.circle(big, (90, 65, 30), middle, outer - 3 * scale)                   # mörk ring innanför
         inner = outer - 4 * scale
         steps = 24
         for step in range(steps):   # färgen: ringar som blir ljusare och flyttar uppåt
            t = step / (steps - 1)
            shade = mix(darker(color), lighter(color), t)
            center = middle - (0, inner * 0.35 * t)
            pygame.draw.circle(big, shade, center, inner * (1 - 0.75 * t))
         image = pygame.transform.smoothscale(big, (size, size))
         self.outlined_text(image, str(value), self.font(int(radius * 1.25), bold=True),
                            number_color, (size / 2, size / 2))
         return image
      return self.cached(key, make)

   # Text med svart kontur runt om (för siffror på brickor)
   def outlined_text(self, surface, text, font, color, center):
      image = font.render(text, True, color)
      outline = font.render(text, True, (0, 0, 0))
      # Den renderade bilden har plats för bokstäver som går under raden (g, p, y) och
      # över den (accenter). Siffror använder inte den platsen, så om hela bilden
      # centreras hamnar siffran för högt. Därför centreras de synliga pixlarna
      # (get_bounding_rect) i stället.
      ink = image.get_bounding_rect()
      x = round(center[0] - ink.centerx)
      y = round(center[1] - ink.centery)
      for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
         surface.blit(outline, (x + dx, y + dy))
      surface.blit(image, (x, y))

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

   # Ett kort på brädet: porträttet med det som behövs hela tiden, som brickor på hörnen:
   # ⚔️ nere till vänster, ❤️ nere till höger, ☩ uppe till höger (om kortet ger ritual).
   # 🪄 skyddar bara mot spells och visas på hela kortet (musen över porträttet), inte här.
   # Brickorna sitter med mitten nära hörnet och sticker ut lite över kanten, som i Hearthstone.
   # border: färgen på en ram runt porträttet (till exempel "kan anfalla"), eller None.
   # show_statuses: skriv statusorden (Veiled, Can't attack ...) under porträttet.
   def board_card(self, surface, card, rect, border=None, show_statuses=True):
      if card.has_guard():
         pygame.draw.rect(surface, (200, 185, 140), rect.inflate(14, 14), 7, border_radius=20)
      if border:
         pygame.draw.rect(surface, border, rect.inflate(8, 8), 5, border_radius=18)
      self.portrait_image(surface, card, rect)
      if not card.can_be_attacked():   # dold (Veil of Tiamat, Void Wraith): halvgenomskinlig slöja
         veil = pygame.Surface(rect.size, pygame.SRCALPHA)
         veil.fill((30, 30, 50, 130))
         surface.blit(veil, rect)

      radius = round(rect.width * 0.15)
      inset = round(rect.width * 0.07)   # hur långt in från kanten brickans mitt sitter
      if not isinstance(card, RitualCard):
         self.badge(surface, (rect.left + inset, rect.bottom - inset), card.get_attack(), ATTACK_COLOR, radius)
      self.badge(surface, (rect.right - inset, rect.bottom - inset), card.get_health(), HEALTH_COLOR,
                 radius, self.health_color(card))
      if card.get_ritual() > 0:
         self.badge(surface, (rect.right - inset, rect.top + inset), card.get_ritual(), RITUAL_COLOR,
                    round(radius * 0.8))

      if show_statuses:
         self.statuses(surface, card, rect)

   # Health under max syns i rött, så att man ser vilka kort som är skadade
   def health_color(self, thing):
      return DAMAGED_COLOR if thing.get_health() < thing.get_max_health() else TEXT_COLOR

   # Korttexten i textrutan, så stor som möjligt men aldrig större än att den får plats
   def card_text(self, surface, text, box):
      size = max(10, box.width // 11)
      while True:
         font = self.font(size, kind="sans")
         lines = self.wrap(text, font, box.width)
         if len(lines) * font.get_linesize() <= box.height or size <= 9:
            break
         size -= 1
      top = box.y + (box.height - len(lines) * font.get_linesize()) // 2   # mitt i rutan
      for i, line in enumerate(lines):
         self.text(surface, line, font, center=(box.centerx, top + i * font.get_linesize() + font.get_linesize() // 2))

   # Statusorden under ett porträtt. Guard syns redan som ram, så den skrivs inte.
   def statuses(self, surface, card, rect):
      words = [status for status in card.statuses() if status != "Guard"]
      if words:
         self.text(surface, ", ".join(words), self.font(16, kind="sans"), center=(rect.centerx, rect.bottom + 16))

   # Ett helt kort: ram, porträtt, namn, text, kostnad och (för figurer) stats.
   # owner_faction: fraktionen hos den som har kortet, för kort utan egen fraktion (Trinket).
   def card(self, surface, card, rect, dim=False, border=None, owner_faction=None):
      if border:
         pygame.draw.rect(surface, border, rect.inflate(10, 10), 5, border_radius=16)
      # Porträttet först och ramen ovanpå (ramens fönster är genomskinligt)
      self.portrait_image(surface, card, part(rect, FRAME_PORTRAIT))
      frame = self.images.get(self.images.frame_path(card, owner_faction), rect.size)
      if frame:
         surface.blit(frame, rect)
      else:
         pygame.draw.rect(surface, NEUTRAL_RGB, rect, 5, border_radius=12)

      name_rect = part(rect, FRAME_NAME)
      name_font = self.fitting_font(card.get_name(), max(11, rect.width // 13), name_rect.width)
      self.text(surface, card.get_name(), name_font, center=name_rect.center)

      if card.get_special():
         self.card_text(surface, card.get_special().value, part(rect, FRAME_TEXT))

      # Brickorna på kortets hörn: kostnad uppe till vänster, ☩ uppe till höger,
      # ⚔️ nere till vänster, ❤️ nere till höger, och 🪄 som en mindre bricka mitt nedtill.
      radius = round(rect.width * 0.12)
      inset = radius + 2   # hela brickan får plats på kortet
      self.badge(surface, (rect.left + inset, rect.top + inset), card.get_cost(), COST_COLOR, radius)
      if isinstance(card, CreatureCard):
         bottom = rect.bottom - inset
         if not isinstance(card, RitualCard):
            self.badge(surface, (rect.left + inset, bottom), card.get_attack(), ATTACK_COLOR, radius)
         self.badge(surface, (rect.right - inset, bottom), card.get_health(), HEALTH_COLOR,
                    radius, self.health_color(card))
         if card.get_ritual() > 0:
            self.badge(surface, (rect.right - inset, rect.top + inset), card.get_ritual(), RITUAL_COLOR, radius)
         if card.get_magic() > 0:
            self.badge(surface, (rect.centerx, bottom), card.get_magic(), MAGIC_COLOR, round(radius * 0.8))

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

   # Motståndarens kort syns bara bakifrån: fraktionens baksida, eller fraktionens färg
   # om bilden saknas
   def card_back(self, surface, rect, faction_name):
      image = self.images.get(self.images.back_path(faction_name), rect.size)
      if image:
         surface.blit(image, rect)
         return
      color = FACTION_RGB.get(faction_name, NEUTRAL_RGB)
      pygame.draw.rect(surface, color, rect, border_radius=14)
      pygame.draw.rect(surface, (20, 10, 10), rect, 2, border_radius=14)

   # Bilden på fraktionens hjälte, eller en ruta i fraktionens färg med hjältens namn om
   # bilden saknas. Används både i matchen och när man väljer fraktion (då finns ingen spelare än).
   def hero_image(self, surface, faction, rect):
      image = self.images.get(self.images.hero_path(faction.get_name()), rect.size)
      if image:
         surface.blit(image, rect)
      else:
         pygame.draw.rect(surface, FACTION_RGB.get(faction.get_name(), NEUTRAL_RGB), rect, border_radius=14)
         self.text(surface, faction.get_hero().get_name(), self.font(18, bold=True), center=rect.center)

   # Hjälten: bilden, ❤️ och 🛡️ som brickor, och ritual och resurs under
   def hero(self, surface, player, rect, border=None):
      hero = player.get_hero()
      if border:
         pygame.draw.rect(surface, border, rect.inflate(10, 10), 5, border_radius=16)
      self.hero_image(surface, player.get_faction(), rect)

      # ❤️ på hörnet nere till höger, 🛡️ (om hjälten har armor) ovanför den
      radius = 28
      inset = 12
      self.badge(surface, (rect.right - inset, rect.bottom - inset), hero.get_health(), HEALTH_COLOR,
                 radius, self.health_color(hero))
      if hero.get_armor() > 0:
         self.badge(surface, (rect.right - inset, rect.bottom - inset - 2 * radius - 4), hero.get_armor(),
                    ARMOR_COLOR, round(radius * 0.85))

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
