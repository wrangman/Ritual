"""
The graphical user interface: the same methods as TerminalUI, drawn with pygame-ce.

Game calls show_event(event) to tell what happened, and a HumanController calls
choose_move, choose_card and choose_mulligan to let the player choose. Game does
not know whether it talks to the terminal or to this window (Strategy pattern,
Gang of Four).

The game itself is not a loop of frames: Game calls a method and waits for the
answer. So each method here runs its own small frame loop until it is done:
show_event plays a short animation, choose_move waits for a click.

Everything glides to its place (see motion.py): the hand is a fan, a lifted
card straightens up and the others slide aside, and a creature that is played
shrinks from a card into its portrait on the board.

Controls: click a card (in the hand or on the board) and then a target. Cards
that can do something glow. Right-click or Esc cancels the choice. Tab opens
and closes the console with everything that has happened.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import math
import os
import sys

# Windows kan förstora fönster när skärmen är skalad (till exempel 125 %), och då blir
# bilden suddig och fönstret större än skärmen. Den här inställningen till SDL (som pygame
# bygger på) säger att programmet sköter skalningen själv. Den måste sättas innan pygame startar.
os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")

import pygame
from card import CreatureCard
from event import (MoveEvent, NoticeEvent, CardPlayed, AttackMade, CardSacrificed, StatChanged,
                   CardDied, TurnStarted, TurnEnded, GameWon, GameDrawn)
from gui.assets import ImageLibrary
from gui.layout import Layout, SCREEN_SIZE
from gui.motion import Mover, Placement
from gui.renderer import Renderer, ATTACK_COLOR, HEALTH_COLOR, MAGIC_COLOR, ARMOR_COLOR, TEXT_COLOR
from gui.effects import (FloatingText, AttackLine, Banner, FadingImage, ShowCard, Motion, Lunge,
                         Shake, Flash)

# Färger på ramarna när man väljer
PLAYABLE = (90, 220, 110)        # kortet kan göra något
SELECTED = (240, 200, 60)        # kortet man har valt
ENEMY_TARGET = (230, 60, 60)     # ett fiendemål
OWN_TARGET = (90, 220, 110)      # ett eget mål (till exempel SACRIFICE)

# Färgen på siffran som flyger upp när ett värde ändras
STAT_COLORS = {"attack": ATTACK_COLOR, "magic": MAGIC_COLOR, "armor": ARMOR_COLOR}

END_TURN = "end turn"   # det som finns under knappen "End turn"


# En dragning med musen, som i Hearthstone. Ett kort utan mål följer musen och spelas
# när det släpps på spelplanen. Ett kort med mål (en spell, eller en figur som anfaller)
# stannar kvar, och en pil följer musen i stället; man släpper på målet.
class Drag:
   THRESHOLD = 12   # så många punkter musen måste röra sig innan ett klick blir en dragning

   def __init__(self, card, start, aiming):
      self.card = card
      self.start = pygame.Vector2(start)
      self.aiming = aiming   # True: en pil visar målet. False: kortet följer musen.
      self.active = False    # blir True när musen har rört sig tillräckligt

   def move_to(self, position):
      if (pygame.Vector2(position) - self.start).length() > self.THRESHOLD:
         self.active = True


class PygameUI:
   FPS = 60
   CONSOLE_LINES = 24
   MAX_FRAME_SECONDS = 0.05   # en lång paus (till exempel medan AI:n tänker) blir inget hopp

   PULSES = 3          # så många gånger ramarna pulserar i början av turen, sedan lyser de stilla
   PULSE_SPEED = 5     # hur fort de pulserar (radianer per sekund; en puls tar 2π / 5 ≈ 1,3 sekunder)

   WINDOW_SHARE = 0.9  # fönstret tar högst så här stor del av skärmen (plats för aktivitetsfältet)
   FACTION_CHOICE = (340, 510)   # hjältebilden när man väljer fraktion (samma form som HERO i Layout)

   # speed: 1.0 = vanlig fart, 0 = inga pauser (används när datorn spelar mot sig själv i tester)
   # window_size: fönstrets storlek, eller None för så stort som får plats på skärmen
   def __init__(self, speed=1.0, window_size=None):
      pygame.init()
      # Allt ritas på en bild i 1920 x 1080 (self.screen), som sedan skalas till fönstret
      # (present). Då kan fönstret ha vilken storlek som helst, och resten av koden märker inget.
      self.window = pygame.display.set_mode(window_size or self.fitting_window_size(), pygame.RESIZABLE)
      self.screen = pygame.Surface(SCREEN_SIZE)
      self.view_scale = 1.0         # hur mycket bilden är skalad i fönstret
      self.view_offset = (0, 0)     # var bilden börjar i fönstret (svarta kanter runt om)
      pygame.display.set_caption("Ritual")
      self.clock = pygame.time.Clock()
      self.images = ImageLibrary()
      self.renderer = Renderer(self.images)
      self.speed = speed
      self.console_open = False
      self.seconds = 0.0         # hur lång den senaste bildrutan var
      self.time = 0.0            # sekunder sedan fönstret öppnades (för pulserande ramar)
      self.last_mouse = (0, 0)   # musens plats förra bildrutan (ett draget kort lutar åt rörelsen)
      self.game = None
      self.layout = None
      self.start_match_state()

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
   # (den spelarens sida är nederst och hennes hand syns). Varje ny match börjar ren.
   def attach(self, game, viewer):
      self.game = game
      self.layout = Layout(viewer)
      self.start_match_state()

   # Allt som hör till en match och ska vara tomt när en ny match börjar
   def start_match_state(self):
      self.mover = Mover(instant=self.speed == 0)   # var varje kort ritas just nu (det glider mot sin plats)
      self.effects = []          # effekter och rörelser som pågår just nu
      self.history = []          # alla drag (MoveEvent), för listan med senaste drag
      self.log = []              # alla händelser som text, för konsolen
      self.final_text = None     # vem som vann, när spelet är slut
      self.last_rects = {}       # id(sak) -> var saken senast ritades (för effekter och kort som dör)
      self.hit_areas = []        # (form, sak) i den ordning de ritades, för klick och hover
      self.highlights = {}       # id(sak) -> färg på ramen runt den
      self.dimmed = set()        # id(kort) i handen som inte går att spela nu
      self.choosing = False      # True medan spelaren väljer drag (då är "End turn" aktiv)
      self.hovered = None        # kortet i handen som är upplyft (musen är över det)
      self.drag = None           # en pågående dragning med musen (se Drag), eller None
      self.moves = []            # de lagliga dragen medan spelaren väljer (för pilens färg)
      self.pulse_start = None    # när ramarna började pulsera denna tur (None: när spelaren får välja)


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
         self.wait(0.15)   # till exempel "dra ett kort": kortet glider in i handen av sig självt

   # Två sätt att välja, och båda fungerar hela tiden:
   #   klicka på ett kort och sedan på ett mål, eller
   #   dra kortet (eller en pil från det) och släpp det på spelplanen eller på målet.
   # Ett klick och en dragning börjar likadant (musknappen trycks ner på ett kort).
   # Först när knappen släpps vet vi vilket det var.
   def choose_move(self, game, player, moves):
      end_turn = next(move for move in moves if move.ends_turn())
      selected = None   # kortet man har klickat på och som väntar på ett mål
      self.choosing = True
      if self.pulse_start is None:   # första valet denna tur: nu ska ramarna pulsera
         self.pulse_start = self.time
      self.moves = moves
      try:
         while True:
            focus = self.drag.card if self.drag and self.drag.active else selected
            self.mark_choices(moves, focus)
            for event in self.frame():
               if self.is_cancel(event):
                  selected = None
                  self.drag = None
               elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                  thing = self.thing_at(event.pos)
                  if thing == END_TURN:
                     return end_turn
                  if selected is not None:
                     move = self.move_with_target(moves, selected, thing)
                     if move:
                        return move
                  selected = None
                  if self.moves_for(moves, thing):
                     self.drag = Drag(thing, event.pos, self.aims(moves, thing))
               elif event.type == pygame.MOUSEMOTION and self.drag:
                  self.drag.move_to(event.pos)
               elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag:
                  drag, self.drag = self.drag, None
                  if drag.active:
                     move = self.drop(moves, drag, event.pos)
                  else:
                     move, selected = self.pick_source(moves, drag.card)   # det var ett klick
                  if move:
                     return move
      finally:
         self.choosing = False
         self.highlights = {}
         self.dimmed = set()
         self.drag = None
         self.moves = []

   # Behöver kortet ett mål på brädet? Då visar en pil målet när man drar.
   def aims(self, moves, card):
      return any(move.get_target() is not None and self.is_on_board(move.get_target())
                 for move in self.moves_for(moves, card))

   # Kortet släpptes efter en dragning. Returnerar draget, eller None om inget ska hända
   # (kortet släpptes bredvid ett mål eller tillbaka i handen, och glider då tillbaka).
   def drop(self, moves, drag, position):
      target = self.thing_at(position, ignore=drag.card)
      if target is not None:
         move = self.move_with_target(moves, drag.card, target)
         if move:
            return move
      if drag.aiming or position[1] > self.layout.HAND_DROP_LINE:
         return None
      move, _ = self.pick_source(moves, drag.card)   # släppt på spelplanen: som ett klick på kortet
      return move

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


   # Menyer före och efter matchen. De är inte en del av gränssnittet som Game använder:
   # main_gui.py frågar innan spelet skapas och mellan matcherna.

   # Före matchen: fraktionernas hjältar visas stora bredvid varandra, och spelaren
   # klickar på en. Returnerar fraktionen.
   def choose_faction(self, factions):
      center_x = SCREEN_SIZE[0] // 2   # ingen match än, så hela skärmen används (inte brädets mitt)
      spacing = self.FACTION_CHOICE[0] + 120
      rects = []
      for index in range(len(factions)):
         rect = pygame.Rect((0, 0), self.FACTION_CHOICE)
         rect.center = (round(center_x + (index - (len(factions) - 1) / 2) * spacing), 560)
         rects.append(rect)

      def overlay():
         self.dim_screen()
         self.renderer.text(self.screen, "Choose your faction", self.renderer.font(56, bold=True),
                            center=(center_x, 170))
         mouse = self.mouse_position()
         for faction, rect in zip(factions, rects):
            if rect.collidepoint(mouse):
               self.glow(rect, SELECTED)
            self.renderer.hero_image(self.screen, faction, rect)
            self.renderer.text(self.screen, faction.get_name().value, self.renderer.font(40, bold=True),
                               center=(rect.centerx, rect.top - 40))
            self.renderer.text(self.screen, faction.get_hero().get_name(), self.renderer.font(26, kind="sans"),
                               center=(rect.centerx, rect.bottom + 36))

      while True:
         for event in self.frame(overlay):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               for faction, rect in zip(factions, rects):
                  if rect.collidepoint(event.pos):
                     return faction

   # Efter matchen: visa vem som vann och fråga om spelaren vill spela igen.
   # Returnerar True för "Play again" och False för "Quit".
   def ask_play_again(self):
      play_again = pygame.Rect(0, 0, 300, 76)
      quit_game = pygame.Rect(0, 0, 300, 76)
      play_again.center = (self.layout.BOARD_CENTER_X - 180, 640)
      quit_game.center = (self.layout.BOARD_CENTER_X + 180, 640)

      def overlay():
         self.dim_screen()
         self.renderer.text(self.screen, self.final_text or "", self.renderer.font(72, bold=True),
                            center=(self.layout.BOARD_CENTER_X, 480))
         self.button(play_again, "Play again", active=True)
         self.button(quit_game, "Quit", active=True)

      while True:
         for event in self.frame(overlay):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               if play_again.collidepoint(event.pos):
                  return True
               if quit_game.collidepoint(event.pos):
                  return False

   def close(self):
      pygame.quit()


   # Händelser

   def on_turn_started(self, event):
      self.pulse_start = None   # ramarna pulserar igen när spelaren får välja i den nya turen
      if self.layout.is_viewer(event.player):
         self.show_banner("Your turn", 1.0)
      else:
         self.show_banner(f"{event.player.get_name()}'s turn", 1.0)

   def on_turn_ended(self, event):
      self.wait(0.2)

   # Kortet som spelas visas stort en stund, och en linje visar målet. När man själv
   # lägger en figur behövs det inte: porträttet glider direkt från handen till brädet.
   def on_card_played(self, event):
      own_creature = self.layout.is_viewer(event.player) and isinstance(event.card, CreatureCard)
      if own_creature:
         self.wait(0.05)
         return
      image = self.renderer.card_image(event.card, self.layout.SHOWCASE.size, self.faction_of(event.player))
      self.effects.append(ShowCard(image, self.layout.SHOWCASE, 1.0))
      if event.target is not None and self.rect_of(event.target):
         self.effects.append(AttackLine(self.layout.SHOWCASE.center, self.rect_of(event.target).center,
                                        color=(170, 120, 255), duration=0.6))
      self.wait(1.0 if not self.layout.is_viewer(event.player) else 0.6)

   # Anfallaren tar sats och rusar fram mot målet. Skadan (StatChanged) kommer i träffen,
   # och då skakar målet. Rörelsen tillbaka fortsätter medan siffrorna flyger.
   def on_attack(self, event):
      start, end = self.rect_of(event.attacker), self.rect_of(event.target)
      if start and end:
         direction = pygame.Vector2(end.center) - pygame.Vector2(start.center)
         self.effects.append(Lunge(id(event.attacker), direction))
      self.wait(0.25)

   def on_sacrifice(self, event):
      self.line_between(event.card, event.target, OWN_TARGET)
      self.wait(0.45)

   # En siffra flyger upp från kortet: rött när health sjunker, grönt när den stiger.
   # Tar kortet skada skakar det och blinkar rött.
   def on_stat_changed(self, event):
      rect = self.rect_of(event.target)
      change = event.after - event.before
      if event.stat == "health":
         color = HEALTH_COLOR if change < 0 else OWN_TARGET
         if change < 0:
            self.effects.append(Shake(id(event.target), strength=min(18, 6 - change * 2)))
            self.effects.append(Flash(id(event.target)))
      else:
         color = STAT_COLORS[event.stat]
      if rect:
         self.effects.append(FloatingText(f"{change:+d}", rect.center, color, self.renderer.font(54, bold=True)))
      self.wait(0.2)

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
      font = self.renderer.font(48, bold=True)
      # Långa texter delas i rader, så att rutan aldrig blir bredare än BANNER_MAX_WIDTH
      lines = self.renderer.wrap(text, font, self.layout.BANNER_MAX_WIDTH - 2 * Banner.PADDING)
      self.effects.append(Banner(lines, self.layout.BANNER, font, seconds))
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

   # Det som ligger överst på en punkt. ignore: något som inte räknas, till exempel kortet
   # man drar (det ligger ju alltid under musen).
   def thing_at(self, position, ignore=None):
      for shape, thing in reversed(self.hit_areas):   # det som ritades sist ligger överst
         if thing is not ignore and shape.collidepoint(position):
            return thing
      return None

   def rect_of(self, thing):
      return self.last_rects.get(id(thing))

   def belongs_to(self, player, thing):
      return thing is player.get_hero() or any(card is thing for card in player.get_army())

   def is_on_board(self, thing):
      return any(self.belongs_to(player, thing) for player in (self.game.player1, self.game.player2))

   # Kommer ihåg var något ritades: för klick, hover och effekter.
   # shape är en Rect eller en Placement (ett lutande kort i handen); båda har collidepoint.
   def remember(self, thing, shape, rect):
      self.last_rects[id(thing)] = rect
      self.hit_areas.append((shape, thing))

   def mouse_position(self):
      return self.to_screen(pygame.mouse.get_pos())

   # Hur långt rörelserna (Lunge, Shake) flyttar en sak just nu
   def offset(self, key):
      total = pygame.Vector2(0, 0)
      for effect in self.effects:
         if isinstance(effect, Motion) and effect.key == key:
            total += effect.offset()
      return total

   # Hur röd en sak blinkar just nu (Flash)
   def redness(self, key):
      return max([effect.redness() for effect in self.effects
                  if isinstance(effect, Motion) and effect.key == key], default=0.0)


   # Bildrutor

   # En bildruta: effekterna går vidare, allt ritas, och händelserna (klick, tangenter) returneras.
   # overlay ritas ovanpå allt, till exempel kort att välja bland.
   def frame(self, overlay=None):
      self.seconds = min(self.clock.tick(self.FPS) / 1000, self.MAX_FRAME_SECONDS)
      self.time += self.seconds
      for effect in self.effects:
         effect.update(self.seconds)
      self.effects = [effect for effect in self.effects if not effect.is_done()]

      events = []
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
         if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.console_open = not self.console_open
            continue
         if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            # Musen anges i fönstrets punkter; spelet räknar i 1920 x 1080
            event = pygame.event.Event(event.type, {**event.dict, "pos": self.to_screen(event.pos)})
         events.append(event)

      self.draw()
      if overlay:
         overlay()
      if self.console_open:
         self.draw_console()
      self.present()
      return events

   # Så stort fönster som får plats på skärmen, med samma form som spelet (16:9)
   def fitting_window_size(self):
      desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
      scale = min(desktop_width * self.WINDOW_SHARE / SCREEN_SIZE[0],
                  desktop_height * self.WINDOW_SHARE / SCREEN_SIZE[1], 1.0)
      return (int(SCREEN_SIZE[0] * scale), int(SCREEN_SIZE[1] * scale))

   # Visar bilden i fönstret: skalad så att den får plats, med svarta kanter om formen
   # inte stämmer (letterboxing), så att proportionerna behålls.
   def present(self):
      self.window = pygame.display.get_surface()   # fönstret kan ha bytt storlek
      window_width, window_height = self.window.get_size()
      self.view_scale = min(window_width / SCREEN_SIZE[0], window_height / SCREEN_SIZE[1])
      size = (round(SCREEN_SIZE[0] * self.view_scale), round(SCREEN_SIZE[1] * self.view_scale))
      self.view_offset = ((window_width - size[0]) // 2, (window_height - size[1]) // 2)
      self.window.fill((0, 0, 0))
      if size == SCREEN_SIZE:
         self.window.blit(self.screen, self.view_offset)
      else:
         self.window.blit(pygame.transform.smoothscale(self.screen, size), self.view_offset)
      pygame.display.flip()

   # En punkt i fönstret som en punkt i spelets 1920 x 1080
   def to_screen(self, position):
      return ((position[0] - self.view_offset[0]) / self.view_scale,
              (position[1] - self.view_offset[1]) / self.view_scale)

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
      self.draw_background()
      if self.game is None:   # före första matchen (till exempel när man väljer fraktion)
         return

      viewer = self.layout.viewer
      opponent = self.game.get_opponent_of(viewer)
      drawn = set()   # nycklarna för allt som har en rörelse, så att Mover kan glömma resten
      drawn |= self.draw_card_backs(opponent)
      for player in (opponent, viewer):
         for card, rect in self.layout.board(player):
            self.draw_board_card(card, rect)
            drawn.add(id(card))
         self.draw_hero(player)

      self.button(self.layout.END_TURN, "End turn" if self.choosing else "Waiting...", self.choosing)
      self.hit_areas.append((self.layout.END_TURN, END_TURN))
      self.draw_history()
      drawn |= self.draw_hand(viewer)
      self.draw_aim()
      for effect in self.effects:
         effect.draw(self.screen)
      if not (self.drag and self.drag.active):
         self.draw_preview()
      self.last_mouse = self.mouse_position()
      if self.final_text:
         self.renderer.text(self.screen, self.final_text, self.renderer.font(64, bold=True),
                            center=self.layout.BANNER.center)
      self.mover.keep_only(drawn)

   def draw_background(self):
      background = self.images.get(self.images.board_path(), SCREEN_SIZE)
      if background:
         self.screen.blit(background, (0, 0))
      else:
         self.screen.fill((40, 35, 30))

   # Ett porträtt på brädet. Det glider mot sin plats; ett nytt kort börjar där det
   # senast var (i handen, som ett kort) eller där spelade kort visas, och krymper in.
   def draw_board_card(self, card, rect):
      target = Placement(rect.center, rect.size)
      start = None if self.mover.knows(id(card)) else Placement(self.layout.SHOWCASE.center,
                                                                (self.layout.SHOWCASE.width,) * 2)
      placement = self.mover.follow(id(card), target, self.seconds, start).moved(self.offset(id(card)))
      shown = placement.rect()

      color = self.highlights.get(id(card))
      if color:
         self.glow(shown, color)
      image = self.renderer.board_surface(card, rect.size)
      scale = placement.size.x / rect.width
      if abs(scale - 1) > 0.01 or abs(placement.angle) > 0.5:
         image = pygame.transform.rotozoom(image, placement.angle, scale)
      self.screen.blit(image, image.get_rect(center=shown.center))
      self.red_flash(card, shown)
      self.renderer.statuses(self.screen, card, shown)
      self.remember(card, shown, shown)

   def draw_hero(self, player):
      hero = player.get_hero()
      rect = self.layout.hero(player).move(self.offset(id(hero)))
      color = self.highlights.get(id(hero))
      if color:
         self.glow(rect, color)
      self.renderer.hero(self.screen, player, rect, self.layout.hero_info(player))
      self.red_flash(hero, rect)
      self.remember(hero, rect, rect)

   # Den egna handen som en solfjäder. Kortet under musen rätar upp sig, växer och lyfts,
   # och ritas sist, så att det syns helt och vinner när man klickar. Returnerar nycklarna.
   def draw_hand(self, viewer):
      cards = viewer.get_hand()
      hovered = self.hovered_index(cards)
      self.hovered = cards[hovered] if hovered is not None else None
      placed = []
      for card, target in self.layout.hand(viewer, hovered):
         speed = None
         if self.is_carried(card):   # kortet följer musen och lutar åt det håll det dras
            mouse = pygame.Vector2(self.mouse_position())
            tilt = max(-15.0, min(15.0, (self.last_mouse[0] - mouse.x) * 0.8))
            target = Placement(mouse, self.layout.HAND_CARD, tilt)
            speed = 30
         start = Placement((self.layout.BOARD_CENTER_X + 700, 1300), self.layout.HAND_CARD, -30)   # nytt kort glider in
         placed.append((card, self.mover.follow(id(card), target, self.seconds, start, speed)))
      # Det lyfta eller dragna kortet ritas sist, alltså överst
      placed.sort(key=lambda pair: pair[0] is self.hovered or self.is_carried(pair[0]))

      base_size = self.layout.HAND_CARD
      for card, placement in placed:
         scale = placement.size.x / base_size[0]
         color = self.highlights.get(id(card))
         if color:
            self.glow(placement.rect(), color, placement.angle)
         image = self.renderer.card_surface(card, base_size, self.faction_of(viewer), dim=id(card) in self.dimmed)
         image = pygame.transform.rotozoom(image, placement.angle, scale)
         self.screen.blit(image, image.get_rect(center=placement.center))
         self.remember(card, placement, placement.rect())
      return {id(card) for card in cards}

   # Platsen i handen för kortet under musen, eller None. Ett kort som redan är lyft får
   # vara kvar uppe så länge musen är över det, annars skulle det hoppa ner igen.
   def hovered_index(self, cards):
      if self.drag and self.drag.active:
         # Under en dragning: ett kort som siktar med en pil stannar upplyft, annars lyfts inget
         for index, card in enumerate(cards):
            if card is self.drag.card and self.drag.aiming:
               return index
         return None
      mouse = self.mouse_position()
      for index, card in enumerate(cards):
         placement = self.mover.placements.get(id(card))
         if card is self.hovered and placement and placement.collidepoint(mouse):
            return index
      for index in reversed(range(len(cards))):   # korten till höger ligger överst
         placement = self.mover.placements.get(id(cards[index]))
         if placement and placement.collidepoint(mouse):
            return index
      return None

   # Motståndarens kort, bakifrån, i en solfjäder överst. Returnerar nycklarna.
   def draw_card_backs(self, opponent):
      keys = set()
      back = self.renderer.cached(("back", self.faction_of(opponent)), lambda: self.card_back_surface(opponent))
      for index, target in enumerate(self.layout.card_backs(opponent)):
         key = ("back", index)
         start = Placement((self.layout.BOARD_CENTER_X, -150), self.layout.CARD_BACK, 180)
         placement = self.mover.follow(key, target, self.seconds, start)
         image = pygame.transform.rotozoom(back, placement.angle, 1)
         self.screen.blit(image, image.get_rect(center=placement.center))
         keys.add(key)
      return keys

   def card_back_surface(self, player):
      image = pygame.Surface(self.layout.CARD_BACK, pygame.SRCALPHA)
      self.renderer.card_back(image, image.get_rect(), self.faction_of(player))
      return image

   # Följer kortet musen just nu? (En dragning av ett kort utan mål.)
   def is_carried(self, card):
      return self.drag is not None and self.drag.active and not self.drag.aiming and card is self.drag.card

   # Under en dragning med mål: en pil från kortet till musen. Pilen är röd över ett
   # fiendemål, grön över ett eget mål och grå annars, och målet under den får en vit ram.
   def draw_aim(self):
      if not (self.drag and self.drag.active and self.drag.aiming):
         return
      start = self.rect_of(self.drag.card)
      if start is None:
         return
      mouse = self.mouse_position()
      target = self.thing_at(mouse, ignore=self.drag.card)
      color = (170, 160, 150)
      if target is not None and self.move_with_target(self.moves, self.drag.card, target):
         color = self.highlights.get(id(target), ENEMY_TARGET)
         pygame.draw.rect(self.screen, (255, 245, 220), self.rect_of(target).inflate(18, 18), 4, border_radius=20)
      self.draw_arrow(start.center, mouse, color)

   # En böjd, prickad pil (som i Hearthstone): prickar längs en kurva som blir större
   # mot spetsen, och en triangel längst fram
   def draw_arrow(self, start, end, color):
      start, end = pygame.Vector2(start), pygame.Vector2(end)
      bend = pygame.Vector2(0, -min(220, start.distance_to(end) * 0.35))
      control = (start + end) / 2 + bend
      points = []
      steps = 18
      for step in range(steps + 1):
         t = step / steps
         points.append(start * (1 - t) ** 2 + control * 2 * (1 - t) * t + end * t ** 2)
      for index, point in enumerate(points[1:-2]):
         radius = 5 + 4 * index / steps
         pygame.draw.circle(self.screen, (0, 0, 0), point, radius + 2)
         pygame.draw.circle(self.screen, color, point, radius)
      direction = end - points[-3]
      if direction.length() > 0:
         direction = direction.normalize()
         side = pygame.Vector2(-direction.y, direction.x)
         tip = [end, end - direction * 34 + side * 20, end - direction * 34 - side * 20]
         pygame.draw.polygon(self.screen, (0, 0, 0), [p + direction * 2 for p in tip])
         pygame.draw.polygon(self.screen, color, tip)

   # En lysande ram runt något som går att välja. Grön och röd pulserar några gånger
   # i början av turen och lyser sedan stilla; gul (vald) står alltid still.
   def glow(self, rect, color, angle=0.0):
      strength = 1.0 if color == SELECTED else self.pulse_strength()
      size = (rect.width + 20, rect.height + 20)
      ring = pygame.Surface(size, pygame.SRCALPHA)
      pygame.draw.rect(ring, (*color, int(90 * strength)), ring.get_rect(), border_radius=20)
      pygame.draw.rect(ring, (*color, int(255 * strength)), ring.get_rect(), 6, border_radius=20)
      if angle:
         ring = pygame.transform.rotozoom(ring, angle, 1)
      self.screen.blit(ring, ring.get_rect(center=rect.center))

   # Hur starkt ramarna lyser just nu (0,2 till 1,0). Cosinus börjar och slutar på 1,0,
   # så efter sista pulsen går ramen över i stilla ljus utan att hoppa.
   def pulse_strength(self):
      if self.pulse_start is None:
         return 1.0
      phase = (self.time - self.pulse_start) * self.PULSE_SPEED
      if phase >= self.PULSES * 2 * math.pi:
         return 1.0
      return 0.6 + 0.4 * math.cos(phase)

   # Ett rött sken över en sak som just tog skada
   def red_flash(self, thing, rect):
      redness = self.redness(id(thing))
      if redness > 0:
         shade = pygame.Surface(rect.size, pygame.SRCALPHA)
         pygame.draw.rect(shade, (220, 30, 30, int(150 * redness)), shade.get_rect(), border_radius=16)
         self.screen.blit(shade, rect)

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
