"""
Smooth movement: every card glides to its place instead of jumping there.

Layout says where a card should be. Mover remembers where it is drawn right
now and moves it a little closer every frame. That one idea gives most of the
life in the interface: the hand fans out, cards slide aside when one is
lifted, and a creature that is played shrinks from the size of a card into
its place on the board (the portrait "falls out of the card").

The movement slows down as the card gets close (exponential smoothing), which
is a common way to make interfaces feel soft.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import math
import pygame


# Var och hur något ritas: mittpunkt, storlek och lutning i grader
# (positiv lutning = moturs på skärmen, som i pygame.transform.rotozoom).
class Placement:
   def __init__(self, center, size, angle=0.0):
      self.center = pygame.Vector2(center)
      self.size = pygame.Vector2(size)
      self.angle = angle

   # En placering en bit (amount, 0–1) på vägen mot other
   def toward(self, other, amount):
      return Placement(self.center.lerp(other.center, amount),
                       self.size.lerp(other.size, amount),
                       self.angle + (other.angle - self.angle) * amount)

   def moved(self, offset):
      return Placement(self.center + offset, self.size, self.angle)

   # Rutan utan lutning, till exempel för effekter som ska börja vid kortet
   def rect(self):
      rect = pygame.Rect(0, 0, round(self.size.x), round(self.size.y))
      rect.center = (round(self.center.x), round(self.center.y))
      return rect

   # Är punkten på kortet? Punkten vrids tillbaka åt andra hållet, så att ett lutande
   # kort kan prövas som en vanlig rektangel. Heter som Rect.collidepoint, så att
   # rutor och placeringar kan prövas på samma sätt.
   def collidepoint(self, point):
      local = (pygame.Vector2(point) - self.center).rotate(self.angle)
      return abs(local.x) <= self.size.x / 2 and abs(local.y) <= self.size.y / 2


class Mover:
   SPEED = 12.0   # högre = snabbare (ungefär hur stor del av vägen som går per sekund)

   # instant=True: allt hamnar direkt på sin plats (används i tester, där inget ska glida)
   def __init__(self, instant=False):
      self.placements = {}   # nyckel (oftast id(kort)) -> där saken ritas just nu
      self.instant = instant

   # Flyttar saken en bit mot target och returnerar var den ska ritas nu.
   # start: var en ny sak börjar (annars börjar den direkt på sin plats).
   # speed: en annan fart än SPEED, till exempel snabbare för ett kort som följer musen.
   def follow(self, key, target, seconds, start=None, speed=None):
      if self.instant:
         self.placements[key] = target
         return target
      current = self.placements.get(key)
      if current is None:
         current = start or target
      amount = 1 - math.exp(-(speed or self.SPEED) * seconds)
      current = current.toward(target, amount)
      self.placements[key] = current
      return current

   def knows(self, key):
      return key in self.placements

   # Glömmer saker som inte ritas längre (kort som har dött eller spelats som spell)
   def keep_only(self, keys):
      self.placements = {key: value for key, value in self.placements.items() if key in keys}
