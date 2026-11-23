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

import math
import pygame


# Mjuk start och mjukt slut: 0 -> 1 med en S-kurva i stället för en rak linje
def ease(progress):
   return 0.5 - 0.5 * math.cos(math.pi * progress)


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


# En ruta mitt på skärmen med en text, till exempel "Your turn".
# Den glider in från vänster, stannar en stund och glider ut åt höger.
# lines är texten redan uppdelad i rader. Rutan är minst lika stor som rect,
# men växer så att all text får plats, och har alltid mitten där rect har sin.
class Banner(Effect):
   PADDING = 40   # luft mellan texten och rutans kant

   def __init__(self, lines, rect, font, duration=1.0):
      super().__init__(duration)
      self.images = [font.render(line, True, (240, 225, 190)) for line in lines]
      self.line_height = font.get_linesize()
      text_width = max(image.get_width() for image in self.images)
      text_height = self.line_height * len(self.images)
      width = max(rect.width, text_width + 2 * self.PADDING)
      height = max(rect.height, text_height + 2 * self.PADDING)
      self.rect = pygame.Rect(0, 0, width, height)
      self.rect.center = rect.center

   def draw(self, surface):
      fade = min(1.0, self.progress() * 5, (1 - self.progress()) * 4)
      slide = (1 - ease(min(1.0, self.progress() * 4))) * -120 + ease(max(0.0, self.progress() * 4 - 3)) * 120
      rect = self.rect.move(int(slide), 0)
      box = pygame.Surface(rect.size, pygame.SRCALPHA)
      box.fill((15, 10, 10, int(210 * fade)))
      pygame.draw.rect(box, (170, 140, 90, int(255 * fade)), box.get_rect(), 3, border_radius=12)
      surface.blit(box, rect)
      # Raderna läggs under varandra, och hela textblocket centreras i rutan
      top = rect.centery - self.line_height * len(self.images) / 2
      for i, image in enumerate(self.images):
         image.set_alpha(int(255 * fade))
         center = (rect.centerx, int(top + self.line_height * (i + 0.5)))
         surface.blit(image, image.get_rect(center=center))


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


# Ett kort som visas stort en stund, till exempel kortet som motståndaren just spelade.
# Det poppar upp (växer lite förbi sin storlek och tillbaka) och tonar bort i slutet.
class ShowCard(Effect):
   def __init__(self, image, rect, duration=0.9):
      super().__init__(duration)
      self.image = image   # kortet redan ritat i rätt storlek
      self.rect = rect

   def draw(self, surface):
      fade = min(1.0, self.progress() * 6, (1 - self.progress()) * 5)
      pop = min(1.0, self.progress() * 5)
      scale = 0.8 + 0.2 * pop + 0.06 * math.sin(math.pi * pop)
      image = pygame.transform.rotozoom(self.image, 0, scale)
      image.set_alpha(int(255 * fade))
      surface.blit(image, image.get_rect(center=self.rect.center))


# Rörelser: effekter som inte ritar något själva utan flyttar eller färgar ett kort.
# key säger vilket kort (id(kort) eller id(hjälte)). PygameUI frågar alla rörelser
# för ett kort och lägger ihop dem när kortet ritas.
class Motion(Effect):
   def __init__(self, key, duration):
      super().__init__(duration)
      self.key = key

   def draw(self, surface):
      pass   # en rörelse ritar inget själv

   # Hur långt kortet ska flyttas från sin plats just nu
   def offset(self):
      return pygame.Vector2(0, 0)

   # Hur röd kortet ska blinka just nu (0 = inte alls, 1 = helt)
   def redness(self):
      return 0.0


# Anfallaren rusar fram mot målet och tillbaka. Träffen sker mitt i rörelsen.
class Lunge(Motion):
   def __init__(self, key, direction, duration=0.5):
      super().__init__(key, duration)
      self.direction = pygame.Vector2(direction)   # från anfallaren till målet

   def offset(self):
      # Först en liten rörelse bakåt (tar sats), sedan fort fram och lugnt tillbaka
      p = self.progress()
      if p < 0.15:
         return self.direction * (-0.08 * ease(p / 0.15))
      if p < 0.45:
         return self.direction * (-0.08 + 0.83 * ease((p - 0.15) / 0.3))
      return self.direction * (0.75 * (1 - ease((p - 0.45) / 0.55)))


# Kortet skakar, kraftigast i början
class Shake(Motion):
   def __init__(self, key, strength=10, duration=0.35):
      super().__init__(key, duration)
      self.strength = strength

   def offset(self):
      fade = 1 - self.progress()
      t = self.age * 60
      return pygame.Vector2(math.sin(t) * self.strength * fade, math.cos(t * 1.3) * self.strength * 0.5 * fade)


# Kortet blinkar rött när det tar skada
class Flash(Motion):
   def __init__(self, key, duration=0.35):
      super().__init__(key, duration)

   def redness(self):
      return 1 - self.progress()
