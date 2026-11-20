"""
Where everything is on the screen.

The screen is always 1920 x 1080 (the size of the board image); pygame scales
it to fit the window. Drawing and clicking use the same rectangles from this
class, so what you see is always what you click.

The player at the screen (the viewer) is at the bottom, the opponent at the top,
and the heroes are on the right, as in the user's design sketch.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import math
import pygame
from gui.motion import Placement

SCREEN_SIZE = (1920, 1080)


class Layout:
   BOARD_CENTER_X = 860          # mitten av spelplanen (hjältarna tar plats till höger)

   PORTRAIT = 150                # ett porträtt på brädet är 150 x 150
   PORTRAIT_GAP = 42             # brickorna sticker ut över kanten, så korten behöver luft emellan
   OPPONENT_BOARD_Y = 300
   VIEWER_BOARD_Y = 600

   # Handen är en solfjäder: korten sitter på en cirkel vars mittpunkt ligger under skärmen
   HAND_CARD = (170, 255)        # ett kort i handen
   HAND_RADIUS = 1150            # cirkelns radie
   HAND_PIVOT_Y = 2130           # cirkelns mittpunkt (under skärmen): kortens mitt hamnar vid y = 980
   HAND_ANGLE_STEP = 5.0         # grader mellan korten...
   HAND_MAX_SPREAD = 44.0        # ...men solfjädern blir aldrig bredare än så här
   HOVER_SCALE = 1.35            # kortet under musen växer...
   HOVER_Y = 900                 # ...rätar upp sig och lyfts så att det syns helt
   HOVER_SPREAD = 45             # och korten bredvid glider undan

   HAND_DROP_LINE = 780          # ett kort som släpps ovanför den här linjen spelas ut

   CARD_BACK = (110, 165)        # motståndarens kort syns bara bakifrån, i en solfjäder överst
   CARD_BACK_RADIUS = 900
   CARD_BACK_PIVOT_Y = -890      # mittpunkten ovanför skärmen: kortens mitt hamnar vid y = 10
   CARD_BACK_ANGLE_STEP = 4.0

   HERO = (170, 255)
   OPPONENT_HERO = (1660, 50)
   VIEWER_HERO = (1660, 650)

   END_TURN = pygame.Rect(1640, 470, 210, 66)
   HISTORY_X = 20                # listan med senaste drag, längst till vänster
   HISTORY_Y = 60
   HISTORY_ICON = 72
   HISTORY_COUNT = 10

   PREVIEW = pygame.Rect(110, 300, 260, 390)              # stort kort när musen är över ett kort
   SHOWCASE = pygame.Rect(BOARD_CENTER_X - 130, 290, 260, 390)   # kortet som just spelades
   BANNER = pygame.Rect(BOARD_CENTER_X - 360, 470, 720, 110)

   def __init__(self, viewer):
      self.viewer = viewer   # spelaren vid skärmen: hennes sida är nederst, hennes hand syns

   def is_viewer(self, player):
      return player is self.viewer

   # Porträtten på brädet, i en rad mitt på spelplanen: lista med (kort, ruta)
   def board(self, player):
      army = player.get_army()
      y = self.VIEWER_BOARD_Y if self.is_viewer(player) else self.OPPONENT_BOARD_Y
      return list(zip(army, self.row(len(army), self.PORTRAIT, self.PORTRAIT + self.PORTRAIT_GAP, y,
                                     (self.PORTRAIT, self.PORTRAIT))))

   # Korten i den egna handen som en solfjäder: lista med (kort, placering).
   # hovered: platsen i handen för kortet under musen (det lyfts), eller None.
   def hand(self, player, hovered=None):
      cards = player.get_hand()
      angles = self.fan_angles(len(cards), self.HAND_ANGLE_STEP)
      placements = []
      for index, angle in enumerate(angles):
         x, y = self.on_circle(self.HAND_PIVOT_Y, self.HAND_RADIUS, angle, upward=True)
         placement = Placement((x, y), self.HAND_CARD, -angle)   # kort till höger lutar medurs
         if hovered is not None:
            placement = self.hover_adjusted(placement, index, hovered)
         placements.append(placement)
      return list(zip(cards, placements))

   # Kortet under musen rätar upp sig, växer och lyfts. Korten bredvid glider undan.
   def hover_adjusted(self, placement, index, hovered):
      if index == hovered:
         size = (self.HAND_CARD[0] * self.HOVER_SCALE, self.HAND_CARD[1] * self.HOVER_SCALE)
         return Placement((placement.center.x, self.HOVER_Y), size, 0)
      side = -1 if index < hovered else 1
      return placement.moved((side * self.HOVER_SPREAD, 0))

   # Motståndarens kort, bakifrån, i en spegelvänd solfjäder överst. Korten är vända
   # 180 grader, eftersom motståndaren håller dem mot sig (som i Hearthstone).
   def card_backs(self, player):
      angles = self.fan_angles(len(player.get_hand()), self.CARD_BACK_ANGLE_STEP)
      placements = []
      for angle in angles:
         center = self.on_circle(self.CARD_BACK_PIVOT_Y, self.CARD_BACK_RADIUS, angle, upward=False)
         placements.append(Placement(center, self.CARD_BACK, 180 + angle))
      return placements

   # Vinklarna för count kort i en solfjäder, symmetriskt runt 0
   def fan_angles(self, count, step):
      if count > 1:
         step = min(step, self.HAND_MAX_SPREAD / (count - 1))
      return [(index - (count - 1) / 2) * step for index in range(count)]

   # En punkt på en cirkel runt (spelplanens mitt, pivot_y), angle grader från lodlinjen.
   # upward: punkten ligger ovanför mittpunkten (handen), annars under (motståndarens kort).
   def on_circle(self, pivot_y, radius, angle, upward):
      x = self.BOARD_CENTER_X + radius * math.sin(math.radians(angle))
      dy = radius * math.cos(math.radians(angle))
      return (x, pivot_y - dy if upward else pivot_y + dy)

   def hero(self, player):
      position = self.VIEWER_HERO if self.is_viewer(player) else self.OPPONENT_HERO
      return pygame.Rect(position, self.HERO)

   # Var listan med senaste drag har sin ruta nummer index (0 = överst)
   def history_icon(self, index):
      y = self.HISTORY_Y + index * (self.HISTORY_ICON + 8)
      return pygame.Rect(self.HISTORY_X, y, self.HISTORY_ICON, self.HISTORY_ICON)

   # count rutor bredvid varandra, centrerade kring spelplanens mitt.
   # width är en rutas bredd och step avståndet mellan rutornas vänsterkanter.
   def row(self, count, width, step, y, size):
      total = width + step * (count - 1) if count else 0
      left = self.BOARD_CENTER_X - total // 2
      return [pygame.Rect(left + i * step, y, *size) for i in range(count)]
