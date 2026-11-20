"""
Short animations: a number that flies up when a card takes damage, a line from
attacker to target, a banner with text, a card that fades away when it dies.

Every effect has a lifetime. PygameUI calls update(seconds) and draw(surface)
once per frame and removes the effect when it is done. Each effect knows how
to draw itself (polymorphism), so PygameUI just loops over them.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import pygame


class Effect:
   def __init__(self, duration):
      self.duration = duration   # sekunder
      self.age = 0.0

   def update(self, seconds):
      self.age += seconds

   def is_done(self):
      return self.age >= self.duration

   # Hur långt effekten har kommit: 0.0 i början, 1.0 när den är klar
   def progress(self):
      return min(1.0, self.age / self.duration)

   def draw(self, surface):
      raise NotImplementedError("Varje sorts effekt måste ha en egen draw()")


# En text (till exempel "-3") som stiger uppåt och tonar bort
class FloatingText(Effect):
   def __init__(self, text, center, color, font, duration=0.9):
      super().__init__(duration)
      self.image = font.render(text, True, color)
      self.outline = font.render(text, True, (0, 0, 0))
      self.center = center

   def draw(self, surface):
      x, y = self.center
      y -= int(60 * self.progress())   # stiger 60 punkter
      alpha = int(255 * (1 - self.progress() ** 2))
      for image, offset in ((self.outline, 3), (self.image, 0)):
         image.set_alpha(alpha)
         rect = image.get_rect(center=(x + offset, y + offset))
         surface.blit(image, rect)


# En linje från anfallaren till målet som växer fram, med en blixt där den träffar
class AttackLine(Effect):
   def __init__(self, start, end, color=(230, 60, 50), duration=0.45):
      super().__init__(duration)
      self.start = pygame.Vector2(start)
      self.end = pygame.Vector2(end)
      self.color = color

   def draw(self, surface):
      tip = self.start.lerp(self.end, min(1.0, self.progress() * 1.6))   # linjen hinner fram först
      pygame.draw.line(surface, (0, 0, 0), self.start, tip, 12)
      pygame.draw.line(surface, self.color, self.start, tip, 7)
      if self.progress() > 0.6:
         pygame.draw.circle(surface, (255, 220, 120), self.end, int(40 * self.progress()), 6)


# En ruta mitt på skärmen med en text, till exempel "Your turn"
class Banner(Effect):
   def __init__(self, text, rect, font, duration=1.0):
      super().__init__(duration)
      self.rect = rect
      self.image = font.render(text, True, (240, 225, 190))

   def draw(self, surface):
      # Tonar in snabbt och ut i slutet
      fade = min(1.0, self.progress() * 5, (1 - self.progress()) * 4)
      box = pygame.Surface(self.rect.size, pygame.SRCALPHA)
      box.fill((15, 10, 10, int(210 * fade)))
      pygame.draw.rect(box, (170, 140, 90, int(255 * fade)), box.get_rect(), 3, border_radius=12)
      surface.blit(box, self.rect)
      self.image.set_alpha(int(255 * fade))
      surface.blit(self.image, self.image.get_rect(center=self.rect.center))


# En bild som tonar bort och krymper, till exempel porträttet av ett kort som dör
class FadingImage(Effect):
   def __init__(self, image, rect, duration=0.6):
      super().__init__(duration)
      self.image = image
      self.rect = rect

   def draw(self, surface):
      scale = 1 - 0.3 * self.progress()
      size = (int(self.rect.width * scale), int(self.rect.height * scale))
      image = pygame.transform.smoothscale(self.image, size)
      image.set_alpha(int(255 * (1 - self.progress())))
      surface.blit(image, image.get_rect(center=self.rect.center))


# Ett kort som visas stort en stund, till exempel kortet som motståndaren just spelade
class ShowCard(Effect):
   def __init__(self, image, rect, duration=0.9):
      super().__init__(duration)
      self.image = image   # kortet redan ritat i rätt storlek
      self.rect = rect

   def draw(self, surface):
      fade = min(1.0, self.progress() * 6, (1 - self.progress()) * 5)
      self.image.set_alpha(int(255 * fade))
      surface.blit(self.image, self.rect)
