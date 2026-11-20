"""
The graphical user interface: the same methods as TerminalUI, drawn with pygame-ce.

Game calls show_event(event) to tell what happened, and a HumanController calls
choose_move, choose_card and choose_mulligan to let the player choose. Game does
not know whether it talks to the terminal or to this window (Strategy pattern,
Gang of Four).

The game itself is not a loop of frames: Game calls a method and waits for the
answer. So each method here runs its own small frame loop until it is done:
show_event plays a short animation, choose_move waits for a click.

Controls: click a card (in the hand or on the board) and then a target. Cards
that can do something glow. Right-click or Esc cancels the choice. Tab opens
and closes the console with everything that has happened.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import sys
import pygame
from event import (MoveEvent, NoticeEvent, CardPlayed, AttackMade, CardSacrificed, StatChanged,
                   CardDied, TurnStarted, TurnEnded, GameWon, GameDrawn)
from gui.assets import ImageLibrary
from gui.layout import Layout, SCREEN_SIZE
from gui.renderer import Renderer, ATTACK_COLOR, HEALTH_COLOR, MAGIC_COLOR, ARMOR_COLOR, TEXT_COLOR
from gui.effects import FloatingText, AttackLine, Banner, FadingImage, ShowCard

# Färger på ramarna när man väljer
PLAYABLE = (90, 220, 110)        # kortet kan göra något
SELECTED = (240, 200, 60)        # kortet man har valt
ENEMY_TARGET = (230, 60, 60)     # ett fiendemål
OWN_TARGET = (90, 220, 110)      # ett eget mål (till exempel SACRIFICE)

# Färgen på siffran som flyger upp när ett värde ändras
STAT_COLORS = {"attack": ATTACK_COLOR, "magic": MAGIC_COLOR, "armor": ARMOR_COLOR}

END_TURN = "end turn"   # det som finns under knappen "End turn"


class PygameUI:
   FPS = 60
   CONSOLE_LINES = 24

   # speed: 1.0 = vanlig fart, 0 = inga pauser (används när datorn spelar mot sig själv i tester)
   def __init__(self, speed=1.0):
      pygame.init()
      # SCALED: vi ritar alltid i 1920 x 1080, och pygame skalar bilden till fönstret
      self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED | pygame.RESIZABLE)
      pygame.display.set_caption("Ritual")
      self.clock = pygame.time.Clock()
      self.images = ImageLibrary()
      self.renderer = Renderer(self.images)
      self.speed = speed
      self.game = None
      self.layout = None
      self.effects = []          # effekter som pågår just nu
      self.history = []          # alla drag (MoveEvent), för listan med senaste drag
      self.log = []              # alla händelser som text, för konsolen
      self.console_open = False
      self.final_text = None     # vem som vann, när spelet är slut
      self.last_rects = {}       # id(sak) -> var saken senast ritades (för effekter och kort som dör)
      self.hit_areas = []        # (ruta, sak) i den ordning de ritades, för klick och hover
      self.highlights = {}       # id(sak) -> färg på ramen runt den
      self.dimmed = set()        # id(kort) i handen som inte går att spela nu
      self.choosing = False      # True medan spelaren väljer drag (då är "End turn" aktiv)
      self.hovered = None        # kortet i handen som är upplyft (musen är över det)

      # Vilken metod som visar vilken sorts händelse. Händelser som inte står här
      # visas efter sin sort (se show_event).
      self.handlers = {
         CardPlayed: self.on_card_played,
         AttackMade: self.on_attack,
         CardSacrificed: self.on_sacrifice,
         StatChanged: self.on_stat_changed,
         CardDied: self.on_card_died,
         TurnStarted: self.on_turn_started,
         TurnEnded: self.on_turn_ended,
         GameWon: self.on_game_over,
         GameDrawn: self.on_game_over,
      }

   # Fönstret behöver veta vilket spel det visar, och vem som sitter vid skärmen
   # (den spelarens sida är nederst och hennes hand syns).
   def attach(self, game, viewer):
      self.game = game
      self.layout = Layout(viewer)


   # Gränssnittets metoder (samma som TerminalUI)

   def show_event(self, event):
      self.log.append(event.describe())
      if isinstance(event, MoveEvent):
         self.history.append(event)
      handler = self.handlers.get(type(event))
      if handler:
         handler(event)
      elif isinstance(event, NoticeEvent):
         self.show_banner(event.describe(), 1.6)
      else:
         self.wait(0.15)   # till exempel "dra ett kort": brädet ritas om, ingen egen effekt än

   def choose_move(self, game, player, moves):
      end_turn = next(move for move in moves if move.ends_turn())
      selected = None   # kortet man har klickat på och som väntar på ett mål
      self.choosing = True
      try:
         while True:
            self.mark_choices(moves, selected)
            for event in self.frame():
               if self.is_cancel(event):
                  selected = None
               elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                  thing = self.thing_at(event.pos)
                  if thing == END_TURN:
                     return end_turn
                  if selected is not None:
                     move = self.move_with_target(moves, selected, thing)
                     if move:
                        return move
                  move, selected = self.pick_source(moves, thing)
                  if move:
                     return move
      finally:
         self.choosing = False
         self.highlights = {}
         self.dimmed = set()

   # Forbidden Codex: välj ett av korten. Man måste välja, så det går inte att ångra.
   def choose_card(self, cards):
      return self.choose_from(cards, "Choose a card to take into your hand", can_cancel=False)

   # Mulligan: klicka på korten du vill byta, och sedan på knappen
   def choose_mulligan(self, cards):
      replace = set()
      while True:
         rects = self.chooser_rects(len(cards))
         button = pygame.Rect(0, 0, 320, 70)
         button.center = (self.layout.BOARD_CENTER_X, rects[0].bottom + 80)
         label = f"Replace {len(replace)}" if replace else "Keep all"

         def overlay():
            self.dim_screen()
            self.renderer.text(self.screen, "Starting hand: click the cards you want to replace",
                               self.renderer.font(36, bold=True), center=(self.layout.BOARD_CENTER_X, 200))
            for card, rect in zip(cards, rects):
               self.renderer.card(self.screen, card, rect, border=ENEMY_TARGET if id(card) in replace else None,
                                  owner_faction=self.faction_of(self.layout.viewer))
               if id(card) in replace:
                  pygame.draw.line(self.screen, ENEMY_TARGET, rect.topleft, rect.bottomright, 8)
                  pygame.draw.line(self.screen, ENEMY_TARGET, rect.topright, rect.bottomleft, 8)
            self.button(button, label, active=True)

         for event in self.frame(overlay):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               if button.collidepoint(event.pos):
                  return [card for card in cards if id(card) in replace]
               for card, rect in zip(cards, rects):
                  if rect.collidepoint(event.pos):
                     replace ^= {id(card)}   # klick igen ångrar


   # Efter matchen: visa vem som vann tills fönstret stängs

   def wait_for_close(self):
      while True:
         self.frame()


   # Händelser

   def on_turn_started(self, event):
      if self.layout.is_viewer(event.player):
         self.show_banner("Your turn", 1.0)
      else:
         self.show_banner(f"{event.player.get_name()}'s turn", 1.0)

   def on_turn_ended(self, event):
      self.wait(0.2)

   # Kortet som spelas visas stort en stund, och en linje visar målet
   def on_card_played(self, event):
      image = self.renderer.card_image(event.card, self.layout.SHOWCASE.size, self.faction_of(event.player))
      self.effects.append(ShowCard(image, self.layout.SHOWCASE, 1.0))
      if event.target is not None and self.rect_of(event.target):
         self.effects.append(AttackLine(self.layout.SHOWCASE.center, self.rect_of(event.target).center,
                                        color=(170, 120, 255), duration=0.6))
      self.wait(1.0 if not self.layout.is_viewer(event.player) else 0.6)

   def on_attack(self, event):
      self.line_between(event.attacker, event.target, (230, 60, 50))
      self.wait(0.45)

   def on_sacrifice(self, event):
      self.line_between(event.card, event.target, OWN_TARGET)
      self.wait(0.45)

   # En siffra flyger upp från kortet: rött när health sjunker, grönt när den stiger
   def on_stat_changed(self, event):
      rect = self.rect_of(event.target)
      if rect:
         change = event.after - event.before
         if event.stat == "health":
            color = HEALTH_COLOR if change < 0 else OWN_TARGET
         else:
            color = STAT_COLORS[event.stat]
         self.effects.append(FloatingText(f"{change:+d}", rect.center, color, self.renderer.font(54, bold=True)))
      self.wait(0.25)

   # Kortet är redan borta från brädet, så porträttet tonar bort där det senast låg
   def on_card_died(self, event):
      rect = self.last_rects.get(id(event.card))
      if rect:
         image = self.renderer.portrait_surface(event.card, rect.size)
         self.effects.append(FadingImage(image, rect))
      self.wait(0.35)

   def on_game_over(self, event):
      self.final_text = event.describe()
      self.wait(0.5)

   def line_between(self, start, end, color):
      if self.rect_of(start) and self.rect_of(end):
         self.effects.append(AttackLine(self.rect_of(start).center, self.rect_of(end).center, color))

   def show_banner(self, text, seconds):
      self.effects.append(Banner(text, self.layout.BANNER, self.renderer.font(48, bold=True), seconds))
      self.wait(seconds)


   # Val

   # Vilka kort som lyser: de som kan göra något, eller (när ett kort är valt) dess mål
   def mark_choices(self, moves, selected):
      self.highlights = {}
      sources = {id(move.get_card()) for move in moves if not move.ends_turn()}
      self.dimmed = {id(card) for card in self.layout.viewer.get_hand() if id(card) not in sources}
      if selected is None:
         for source in sources:
            self.highlights[source] = PLAYABLE
         return
      self.highlights[id(selected)] = SELECTED
      for move in self.moves_for(moves, selected):
         target = move.get_target()
         color = OWN_TARGET if self.belongs_to(self.layout.viewer, target) else ENEMY_TARGET
         self.highlights[id(target)] = color

   # Spelaren klickade på thing utan att ha valt något kort. Returnerar (drag, valt kort):
   # ett färdigt drag om det bara finns ett, annars kortet som nu väntar på ett mål.
   def pick_source(self, moves, thing):
      options = self.moves_for(moves, thing)
      if not options:
         return None, None
      if len(options) == 1:
         return options[0], None   # bara ett möjligt drag: välj det direkt
      targets = [move.get_target() for move in options]
      if not all(self.is_on_board(target) for target in targets):
         # Målen syns inte på brädet (DEVOUR äter ur gravhögen): visa dem att välja bland
         chosen = self.choose_from(targets, f"{thing.get_name()}: choose a card")
         return self.move_with_target(moves, thing, chosen), None
      return None, thing

   # Draget där kortet source gör något med target, eller None
   def move_with_target(self, moves, source, target):
      for move in self.moves_for(moves, source):
         if move.get_target() is target:
            return move
      return None

   def moves_for(self, moves, card):
      return [move for move in moves if not move.ends_turn() and move.get_card() is card]

   # Visar några kort stort i mitten och låter spelaren klicka på ett. Returnerar kortet,
   # eller None om spelaren ångrar sig (högerklick eller Esc) och can_cancel är True.
   def choose_from(self, cards, title, can_cancel=True):
      rects = self.chooser_rects(len(cards))

      def overlay():
         self.dim_screen()
         self.renderer.text(self.screen, title, self.renderer.font(36, bold=True),
                            center=(self.layout.BOARD_CENTER_X, 200))
         mouse = self.mouse_position()
         for card, rect in zip(cards, rects):
            self.renderer.card(self.screen, card, rect, border=SELECTED if rect.collidepoint(mouse) else None,
                               owner_faction=self.faction_of(self.layout.viewer))

      while True:
         for event in self.frame(overlay):
            if can_cancel and self.is_cancel(event):
               return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               for card, rect in zip(cards, rects):
                  if rect.collidepoint(event.pos):
                     return card

   # Rutor för kort som visas stort i mitten (när man väljer bland några kort)
   def chooser_rects(self, count):
      size = (220, 330)
      step = size[0] + 30
      left = self.layout.BOARD_CENTER_X - (size[0] + step * (count - 1)) // 2
      return [pygame.Rect(left + i * step, 300, *size) for i in range(count)]

   def is_cancel(self, event):
      return ((event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
              or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3))


   # Var saker är

   def thing_at(self, position):
      for rect, thing in reversed(self.hit_areas):   # det som ritades sist ligger överst
         if rect.collidepoint(position):
            return thing
      return None

   def rect_of(self, thing):
      return self.last_rects.get(id(thing))

   def belongs_to(self, player, thing):
      return thing is player.get_hero() or any(card is thing for card in player.get_army())

   def is_on_board(self, thing):
      return any(self.belongs_to(player, thing) for player in (self.game.player1, self.game.player2))

   # Kommer ihåg var något ritades: för klick, hover och effekter
   def remember(self, thing, rect):
      self.last_rects[id(thing)] = rect
      self.hit_areas.append((rect, thing))

   def mouse_position(self):
      return pygame.mouse.get_pos()


   # Bildrutor

   # En bildruta: effekterna går vidare, allt ritas, och händelserna (klick, tangenter) returneras.
   # overlay ritas ovanpå allt, till exempel kort att välja bland.
   def frame(self, overlay=None):
      seconds = self.clock.tick(self.FPS) / 1000
      for effect in self.effects:
         effect.update(seconds)
      self.effects = [effect for effect in self.effects if not effect.is_done()]

      events = []
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
         if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.console_open = not self.console_open
            continue
         events.append(event)

      self.draw()
      if overlay:
         overlay()
      if self.console_open:
         self.draw_console()
      pygame.display.flip()
      return events

   # Visar spelet en stund, medan effekterna spelas upp
   def wait(self, seconds):
      waited = 0.0
      while True:
         self.frame()
         waited += self.clock.get_time() / 1000
         if waited >= seconds * self.speed:
            return


   # Ritning

   def draw(self):
      self.hit_areas = []
      background = self.images.get(self.images.board_path(), SCREEN_SIZE)
      if background:
         self.screen.blit(background, (0, 0))
      else:
         self.screen.fill((40, 35, 30))

      viewer = self.layout.viewer
      opponent = self.game.get_opponent_of(viewer)
      for rect in self.layout.card_backs(opponent):
         self.renderer.card_back(self.screen, rect, opponent.get_faction().get_name())
      for player in (opponent, viewer):
         for card, rect in self.layout.board(player):
            self.renderer.board_card(self.screen, card, rect, self.highlights.get(id(card)))
            self.remember(card, rect)
         rect = self.layout.hero(player)
         self.renderer.hero(self.screen, player, rect, self.highlights.get(id(player.get_hero())))
         self.remember(player.get_hero(), rect)

      self.button(self.layout.END_TURN, "End turn" if self.choosing else "Waiting...", self.choosing)
      self.hit_areas.append((self.layout.END_TURN, END_TURN))
      self.draw_history()
      self.draw_hand(viewer)
      for effect in self.effects:
         effect.draw(self.screen)
      self.draw_preview()
      if self.final_text:
         self.renderer.text(self.screen, self.final_text, self.renderer.font(64, bold=True),
                            center=self.layout.BANNER.center)

   # Den egna handen. Kortet under musen lyfts upp och ritas sist, så att det syns helt
   # och vinner när man klickar.
   def draw_hand(self, viewer):
      hand = self.layout.hand(viewer)
      hovered = self.hovered_hand_card(hand)
      placed = []
      for card, rect in hand:
         if card is hovered:
            rect = rect.copy()
            rect.y = self.layout.HAND_RAISED_Y
         placed.append((card, rect))
      placed.sort(key=lambda pair: pair[0] is hovered)   # det lyfta kortet sist, alltså överst
      for card, rect in placed:
         self.renderer.card(self.screen, card, rect, dim=id(card) in self.dimmed,
                            border=self.highlights.get(id(card)), owner_faction=self.faction_of(viewer))
         self.remember(card, rect)
      self.hovered = hovered

   # Kortet i handen som musen är över. Ett kort som redan är lyft får vara kvar uppe
   # så länge musen är över det, annars skulle det hoppa ner när musen når den lyfta delen.
   def hovered_hand_card(self, hand):
      mouse = self.mouse_position()
      previous = self.hovered
      if any(card is previous for card, _ in hand) and self.rect_of(previous).collidepoint(mouse):
         return previous
      hovered = None
      for card, rect in hand:
         if rect.collidepoint(mouse):
            hovered = card   # det sista kortet under musen ligger överst
      return hovered

   # Listan med senaste drag till vänster, nyast överst (som i Hearthstone)
   def draw_history(self):
      recent = list(reversed(self.history[-self.layout.HISTORY_COUNT:]))
      for index, event in enumerate(recent):
         rect = self.layout.history_icon(index)
         card = self.history_card(event)
         side = OWN_TARGET if self.layout.is_viewer(event.player) else ENEMY_TARGET
         pygame.draw.rect(self.screen, side, rect.inflate(6, 6), 3, border_radius=10)
         self.renderer.portrait_image(self.screen, card, rect)
         self.hit_areas.append((rect, event))

   # Kortet som hör till ett drag i listan
   def history_card(self, event):
      if isinstance(event, AttackMade):
         return event.attacker
      return event.card

   # Stort kort när musen är över ett kort på brädet eller i listan med senaste drag
   def draw_preview(self):
      thing = self.thing_at(self.mouse_position())
      if isinstance(thing, MoveEvent):
         self.renderer.card(self.screen, self.history_card(thing), self.layout.PREVIEW,
                            owner_faction=self.faction_of(thing.player))
         self.renderer.text(self.screen, thing.describe(), self.renderer.font(20, kind="sans"),
                            topleft=(self.layout.PREVIEW.x, self.layout.PREVIEW.bottom + 10))
      elif thing is not None and self.is_on_board(thing) and thing not in self.heroes():
         self.renderer.card(self.screen, thing, self.layout.PREVIEW)

   # Spelarens fraktion (för ramen runt kort utan egen fraktion, som Trinket)
   def faction_of(self, player):
      return player.get_faction().get_name()

   def heroes(self):
      return [self.game.player1.get_hero(), self.game.player2.get_hero()]

   def button(self, rect, label, active):
      hover = active and rect.collidepoint(self.mouse_position())
      color = (150, 110, 40) if hover else (110, 80, 35) if active else (60, 55, 50)
      pygame.draw.rect(self.screen, color, rect, border_radius=12)
      pygame.draw.rect(self.screen, (220, 190, 120), rect, 3, border_radius=12)
      self.renderer.text(self.screen, label, self.renderer.font(28, bold=True), center=rect.center)

   def dim_screen(self):
      shade = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
      shade.fill((0, 0, 0, 170))
      self.screen.blit(shade, (0, 0))

   # Konsolen (som i Quake): de senaste raderna av allt som har hänt
   def draw_console(self):
      font = self.renderer.font(20, kind="mono")
      height = (self.CONSOLE_LINES + 1) * font.get_linesize()
      box = pygame.Surface((SCREEN_SIZE[0], height), pygame.SRCALPHA)
      box.fill((0, 0, 0, 215))
      self.screen.blit(box, (0, 0))
      for i, line in enumerate(self.log[-self.CONSOLE_LINES:]):
         self.screen.blit(font.render(line, True, TEXT_COLOR), (16, 8 + i * font.get_linesize()))
