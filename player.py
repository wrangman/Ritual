"""
A player: their faction, deck, hand, army on the board and graveyard.

Player moves cards between these places and knows the rules about its
own cards. It never talks to the terminal: that is TerminalUI's job.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random
from hero import Hero
from card import SpellCard, RitualCard, Special
from deck import Deck


class Player:
   MAX_ARMY = 7        # högst så många kort på brädet, som i Hearthstone
   MAX_HAND = 10       # högst så många kort i handen, som i Hearthstone
   MAX_RESOURCE = 10   # resursen växer med 1 per tur upp till så här mycket, som mana i Hearthstone

   # controller väljer åt spelaren: en HumanController (via terminalen) eller en AI.
   # Player anropar aldrig controllern själv, det gör Game.
   def __init__(self, name, faction, controller):
      self.name = name
      self.faction = faction
      self.controller = controller
      self.hero = faction.create_hero()
      self.deck = Deck(faction.create_cards())  # nya kortobjekt för just den här spelaren
      self.deck.shuffle()
      self.hand = []
      self.army = []        # korten spelaren har på brädet
      self.graveyard = []   # döda; kastade kort
      self.resource = 0     # betalar för korten man lägger (namnet är inte bestämt än)
      self.max_resource = 0 # så mycket resurs man får varje tur: växer med 1 per tur (mana crystals)
      self.overload = 0     # så mycket mindre resurs man får nästa tur (lånat i förväg)
      self.burned = []      # kort som försvann för att handen var full
      self.stress = 0       # växer varje gång man ska dra ur en tom lek (Fatigue i Hearthstone)
      self.ritual_complete = False   # sant när ritualen höll målet hela motståndarens tur

   def __str__(self):
      return (f"{self.name} ({self.faction.get_name().value}) – "
              f"☩ {self.hero.get_ritual()}/{self.faction.get_ritual_goal()}, "
              f"hand: {len(self.hand)}, lek: {len(self.deck)}, stress: {self.stress}")

   # Handlingar
   # Drar kort från leken till handen. Returnerar de dragna korten,
   # som kan vara färre än amount om leken tar slut.
   # Stress (Fatigue i Hearthstone): för varje kort som saknas ökar stressen med 1,
   # och hjälten tar så mycket skada (1, 2, 3 ...). Då kan spelet aldrig fastna.
   # Är handen full (10 kort) försvinner kortet i stället (som i Hearthstone).
   def draw_cards(self, amount=1):
      drawn = self.deck.draw(amount)
      for card in drawn:
         self.add_to_hand(card)
      missing = amount - len(drawn)
      for _ in range(missing):
         self.stress += 1
         self.hero.take_damage(self.stress)
      return drawn

   # Spelar ett kort från handen och betalar dess kostnad. Figurer hamnar i armén.
   # Spells hamnar aldrig på brädet utan går direkt till döda högen. Effekten sköts av Game.
   def play_card(self, card):
      if not self.can_afford(card):
         raise ValueError(f"Not enough resource to play {card.get_name()}")
      self.resource -= card.get_cost()
      self.hand.remove(card)
      if isinstance(card, SpellCard):
         self.graveyard.append(card)
      else:
         self.army.append(card)
         card.enter_board()   # får inte anfalla förrän nästa tur

   # Ett kort i armén dör och flyttas till döda högen. Buffarna försvinner.
   # Ritualen vilar på korten: när ett kort dör tappar hjälten den ☩ kortet ger just nu.
   # Gäller alla dödsfall, även när man offrar sitt eget kort. Alla dödsfall går igenom
   # den här metoden, så regeln står bara här. Under Seal of Apep gör lose_ritual ingenting.
   def kill_card(self, card):
      self.hero.lose_ritual(card.get_ritual())   # läses innan buffarna tas bort
      self.army.remove(card)
      card.clear_buffs()
      self.graveyard.append(card)

   # Tar bort buffarna som går ut, på alla kort i armén och på hjälten.
   # player är den vars tur börjar (eller slutar, om this_turn_only är True).
   def remove_expired_buffs(self, player, this_turn_only):
      for card in self.army:
         card.remove_expired_buffs(player, this_turn_only)
      self.hero.remove_expired_buffs(player, this_turn_only)

   def discard(self, card):
      self.hand.remove(card)
      self.graveyard.append(card)

   # Ett kort ska till handen. Finns det inte plats (10 kort) försvinner det i stället,
   # som när man drar ett kort med full hand i Hearthstone. Alla kort som ska till handen
   # går igenom den här metoden, så regeln står bara här.
   def add_to_hand(self, card):
      if self.is_hand_full():
         self.burned.append(card)
      else:
         self.hand.append(card)

   def is_hand_full(self):
      return len(self.hand) >= self.MAX_HAND

   # Ett dött kort återställs till spelarens hand. Är handen full stannar det i gravhögen.
   def restore_card(self, card):
      if self.is_hand_full():
         return
      self.graveyard.remove(card)
      self.hand.append(card)
      
   # Ett kort återupplivas tillaka till armén
   def revive_card(self, card):
      self.graveyard.remove(card)
      self.summon(card)   # som i Hearthstone: ett återupplivat kort måste också vänta en tur

   # Ett dött kort äts upp (DEVOUR): det försvinner ur gravhögen för gott,
   # så det kan inte heller återupplivas
   def eat_from_graveyard(self, card):
      self.graveyard.remove(card)

   # Ett kort ur leken läggs direkt på brädet (SUMMON). Det måste vänta en tur, som alla nya kort.
   def summon_from_deck(self, card):
      self.deck.remove(card)
      self.summon(card)

   # En figur kommer ut på brädet utan att spelas från handen: återupplivad, ur leken
   # eller ett spöke som en spell trollar fram. Alla nya kort måste vänta en tur innan de anfaller.
   def summon(self, card):
      self.army.append(card)
      card.enter_board()

   # I början av turen blir alla kort i armén redo att anfalla (en gång var)
   def ready_army(self):
      for card in self.army:
         card.ready_for_turn()
      
   # Tar de översta korten ur leken för att titta på dem (Forbidden Codex).
   # De ligger varken i leken eller i handen förrän take_into_hand eller return_to_deck_bottom anropas.
   def reveal_top_cards(self, amount):
      return self.deck.draw(amount)

   def take_into_hand(self, card):
      self.add_to_hand(card)

   def return_to_deck_bottom(self, card):
      self.deck.put_on_bottom(card)

   # Mulligan (som i Hearthstone): "jag vill inte ha de här korten". Man får byta hur många
   # man vill, en gång. De nya korten dras först och de gamla blandas in efteråt,
   # så att man inte kan få tillbaka samma kort.
   def mulligan(self, cards):
      for card in cards:
         self.hand.remove(card)
      self.draw_cards(len(cards))
      for card in cards:
         self.deck.add_card(card)
      self.deck.shuffle()
      
   # Vinstvillkor som gäller spelaren själv.
   # "Mest ritual" kräver att två spelare jämförs och avgörs därför av spelet, inte här.
   def reached_ritual(self):
      return self.hero.get_ritual() >= self.faction.get_ritual_goal()

   # Ritualen är klar: spelaren nådde målet och hade det kvar efter motståndarens tur.
   # Game avgör när (i början av spelarens tur), Player kommer bara ihåg det.
   def complete_ritual(self):
      self.ritual_complete = True

   def is_ritual_complete(self):
      return self.ritual_complete

   def get_stress(self):
      return self.stress

   # Utplånad: inga kort på brädet, i handen eller i leken
   def is_wiped_out(self):
      return not self.army and not self.hand and len(self.deck) == 0

   # Resursen fylls på i början av turen, som mana i Hearthstone: max_resource växer
   # med 1 varje tur (upp till 10) och resursen fylls upp till max_resource.
   # Det som inte användes förra turen sparas inte. Overload från förra turen dras av,
   # men aldrig under 0.
   def refill_resource(self):
      self.max_resource = min(self.max_resource + 1, self.MAX_RESOURCE)
      self.resource = max(0, self.max_resource - self.overload)
      self.overload = 0

   # Extra resurs mitt i turen, till exempel från en spell
   def gain_resource(self, amount):
      self.resource += amount

   # Lånar från nästa tur: då får man så här mycket mindre
   def add_overload(self, amount):
      self.overload += amount

   # Har spelaren råd att lägga kortet?
   def can_afford(self, card):
      return card.get_cost() <= self.resource

   # Finns det plats för ett kort till på brädet?
   def has_room_on_board(self):
      return len(self.army) < self.MAX_ARMY

   # Finns det något kort i handen som spelaren har råd med?
   def has_affordable_card(self):
      for card in self.hand:
         if self.can_afford(card):
            return True
      return False

   # Finns det något kort i armén som kan anfalla just nu?
   # (Inte ritualkort, inte kort med en buff som Terror, inte kort som lades den här turen
   # och inte kort som redan har anfallit.)
   def has_card_that_can_act(self):
      for card in self.army:
         if card.can_attack():
            return True
      return False

   # I början av turen ger varje kort i armén sin ☩ till hjälten.
   # Ritualen växer bara så länge korten ligger kvar, därför är det viktigt att skydda dem.
   def collect_ritual(self):
      total = 0
      for card in self.get_army():
         total += card.get_ritual()
      self.hero.add_ritual(total)

   # Döda kort tas bort. Sedan sker det som händer när ett kort dör (som Deathrattle i Hearthstone):
   # ett SACRIFICE-kort ger sin styrka till ett slumpat eget kort, oavsett hur det dog.
   # Det sker först när alla döda kort är borta, så att styrkan inte hamnar på ett kort
   # som dog samtidigt (till exempel av Plague). Slumpat, eftersom kortet kan dö under
   # motståndarens tur, och Deathrattle i Hearthstone frågar aldrig efter ett mål.
   def clear_dead_cards(self):
      dead_cards = []
      for card in self.get_army():
         if card.is_dead():
            self.kill_card(card)
            dead_cards.append(card)
      for card in dead_cards:
         if card.get_special() == Special.SACRIFICE and self.army:
            self.pass_on_strength(card, random.choice(self.army))

   # SACRIFICE: det döda kortet ger sin ❤️ max health och sin 🛡️ armor till receiver för alltid.
   # Kortet är redan dött, så buffarna är borta: det ger sina egna värden, inga tillfälliga.
   # Samma regel när kortet offras frivilligt (Game.sacrifice), då väljer spelaren receiver.
   def pass_on_strength(self, card, receiver):
      receiver.increase_health(card.get_max_health())
      receiver.repair_armor(card.get_armor())

   def get_spell_targets(self):
      return self.get_army() + [self.get_hero()]

   # Ligger kortet i spelarens armé?
   def owns_card(self, card):
      return card in self.army

   # Bara ritualkorten i armén (mål för skydds- och buff-spells som Scales of Leviathan)
   def get_ritual_cards(self):
      ritual_cards = []
      for card in self.get_army():
         if isinstance(card, RitualCard):
            ritual_cards.append(card)
      return ritual_cards


   # Vilka mål får en figur anfalla? Kort som en buff gömmer (Veil of Tiamat) räknas inte alls:
   # de kan inte anfallas och skyddar inte heller hjälten.
   def get_targets(self):
      attackable = []
      for card in self.get_army():
         if card.can_be_attacked():
            attackable.append(card)

      valid_targets = []

      for target in attackable:
         if target.has_guard():
            valid_targets.append(target)

      if valid_targets:
         return valid_targets

      else:
         if len(attackable) > 0:
            return attackable
         else:
            return [self.get_hero()] #expects list datatype


   # Get methods
   def get_name(self):
      return self.name

   def get_hero(self):
      return self.hero

   def get_controller(self):
      return self.controller
   
   def get_faction(self):
      return self.faction

   def get_hand(self):
      return list(self.hand)   # kopia, så att handen bara ändras via Player

   def get_army(self):
      return list(self.army)  # kopia, så att armén bara ändras via Player

   def get_graveyard(self):
      return list(self.graveyard)   # kopia, så att döda högen bara ändras via Player

   def get_deck(self):
      return self.deck

   def get_resource(self):
      return self.resource

   def get_max_resource(self):
      return self.max_resource

   def get_burned(self):
      return list(self.burned)

   def get_overload(self):
      return self.overload
