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

import pygame

SCREEN_SIZE = (1920, 1080)


class Layout:
   BOARD_CENTER_X = 860          # mitten av spelplanen (hjältarna tar plats till höger)

   PORTRAIT = 150                # ett porträtt på brädet är 150 x 150
   PORTRAIT_GAP = 24
   OPPONENT_BOARD_Y = 300
   VIEWER_BOARD_Y = 600

   HAND_CARD = (170, 255)        # ett kort i handen
   HAND_STEP = 135               # korten överlappar lite
   HAND_Y = 870                  # bara överdelen syns...
   HAND_RAISED_Y = 815           # ...tills musen är över kortet

   CARD_BACK = (110, 165)        # motståndarens kort syns bara bakifrån
   CARD_BACK_STEP = 62
   CARD_BACK_Y = -70

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

   # Korten i den egna handen, nederst och lite överlappande: lista med (kort, ruta)
   def hand(self, player):
      cards = player.get_hand()
      return list(zip(cards, self.row(len(cards), self.HAND_CARD[0], self.HAND_STEP, self.HAND_Y,
                                      self.HAND_CARD)))

   # Motståndarens kort, överst och bakifrån
   def card_backs(self, player):
      count = len(player.get_hand())
      return self.row(count, self.CARD_BACK[0], self.CARD_BACK_STEP, self.CARD_BACK_Y, self.CARD_BACK)

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
