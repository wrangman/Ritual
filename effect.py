"""
An effect: this class applies effects from spellcards for instance.

apply() can be called to use a spell. Each kind of effect is its own small
class, and the same effect can be reused by many spells (Command/Strategy
pattern, like the actions in Fireplace).

The strength of an effect is the spell's 🪄 magic, unless the card says
otherwise (Scroll of Rituals uses its ☩ ritual).
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random
from card import CreatureCard
from buff import Buff
from trigger import InfectTrigger, MirrorTrigger, CurseTrigger


class Effect:
   def __init__(self):
      pass

   def apply(self, game, spell, target):
      raise NotImplementedError("Varje sorts effekt måste ha en egen apply()")

   # Behöver effekten ett mål? De flesta gör det. Effekter som inte gör det svarar False,
   # och då frågar spelet inte efter något mål (target blir None).
   def needs_target(self):
      return True

   # Vilka mål får spelaren välja mellan? Standard: en fiende (figur eller hjälte).
   # Effekter som ska träffa något annat skriver en egen get_targets().
   # (Som "play requirements" i Fireplace: kortets text styr vilka mål som är tillåtna.)
   def get_targets(self, game):
      return game.get_opponent().get_spell_targets()

   # En effekt har inget eget tillstånd (styrkan kommer från spellen), så när AI:n
   # kopierar spelet för att prova ett drag kan kopian dela samma effekt-objekt.
   # Det gör kopieringen mycket snabbare.
   def __deepcopy__(self, memo):
      return self


# Skadar en fiende med spellens 🪄 magic.
# Samma tre steg som Game.attack, men det är spellen som slår.
# include_hero=False betyder att bara fiendens figurer får väljas, inte hjälten.
class DamageOneEnemy(Effect):
   def __init__(self, include_hero=True):
      self.include_hero = include_hero

   def get_targets(self, game):
      if self.include_hero:
         return game.get_opponent().get_spell_targets()
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      damage = spell.damage_against(target)
      target.take_damage(damage)
      game.get_opponent().clear_dead_cards()


# Skadar alla fiendens figurer (inte hjälten) med spellens 🪄 magic.
# own_damage: så mycket skada varje eget kort tar (Pnakotic Manuscripts).
class DamageAllEnemyCards(Effect):
   def __init__(self, own_damage=0):
      self.own_damage = own_damage

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      opponent = game.get_opponent()
      caster = game.get_current_player()
      for card in opponent.get_army():
         card.take_damage(spell.damage_against(card))
      if self.own_damage > 0:
         for card in caster.get_army():
            card.take_damage(self.own_damage)
      opponent.clear_dead_cards()
      caster.clear_dead_cards()


# Läker den egna hjälten med spellens 🪄 magic (Drain Life, som i Hearthstone).
class HealOwnHero(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().restore_health(spell.get_magic())


# Läker alla egna kort med spellens 🪄 magic.
class HealAllOwnCards(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      for card in game.get_current_player().get_army():
         card.restore_health(spell.get_magic())


# Sänker en fientlig figurs ⚔️ attack med spellens 🪄 magic, för alltid.
class LowerAttack(Effect):
   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      target.lower_attack(spell.get_magic())


# Tar bort all 🛡️ armor från en fientlig figur.
class RemoveArmor(Effect):
   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      target.set_armor(0)


# Ger ett eget kort mer av en eller flera stats, lika mycket som spellens 🪄 magic.
# ritual_only=True betyder att bara egna ritualkort får väljas.
class BuffOwnCard(Effect):
   def __init__(self, armor=False, magic=False, health=False, ritual_only=False):
      self.armor = armor
      self.magic = magic
      self.health = health
      self.ritual_only = ritual_only

   def get_targets(self, game):
      caster = game.get_current_player()
      if self.ritual_only:
         return caster.get_ritual_cards()
      return caster.get_army()

   def apply(self, game, spell, target):
      amount = spell.get_magic()
      if self.armor:
         target.repair_armor(amount)
      if self.magic:
         target.increase_magic(amount)
      if self.health:
         target.increase_health(amount)


# Sänker motståndarens ritual med spellens 🪄 magic.
class LowerRitual(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_opponent().get_hero().lose_ritual(spell.get_magic())


# Stjäl ritual från motståndaren, lika mycket som spellens 🪄 magic.
# Man kan inte stjäla mer än motståndaren har.
class StealRitual(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      opponent_hero = game.get_opponent().get_hero()
      if opponent_hero.is_ritual_protected():
         return   # Seal of Apep: inget kan stjälas
      stolen = min(spell.get_magic(), opponent_hero.get_ritual())
      opponent_hero.lose_ritual(stolen)
      game.get_current_player().get_hero().add_ritual(stolen)


# Lägger spellens ☩ ritual till den egna ritualen (Scroll of Rituals).
class GainRitual(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().add_ritual(spell.get_ritual())


# Den som spelar drar kort.
class DrawCards(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().draw_cards(self.amount)


# Ett slumpat dött kort i den egna gravhögen kommer tillbaka till brädet med full health
# (Resurrect, som i Hearthstone). Bara figurer kan komma tillbaka till brädet.
class ReviveRandom(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      if not caster.has_room_on_board():
         return   # brädet är fullt (7 kort), som i Hearthstone händer då ingenting
      dead_cards = []
      for card in caster.get_graveyard():
         if isinstance(card, CreatureCard):
            dead_cards.append(card)
      if not dead_cards:
         return   # inget att återuppliva
      card = random.choice(dead_cards)
      card.restore_full_health()
      caster.revive_card(card)


# Ett slumpat kort i den egna gravhögen kommer tillbaka till handen.
# Spellen själv ligger redan i gravhögen, så den räknas inte.
class ReturnRandomToHand(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      cards = []
      for card in caster.get_graveyard():
         if card is not spell:
            cards.append(card)
      if not cards:
         return   # inget att hämta
      card = random.choice(cards)
      if isinstance(card, CreatureCard):
         card.restore_full_health()
      caster.restore_card(card)


# Titta på de översta korten i leken och ta ett till handen. Resten läggs sist i leken.
# (Som Tracking i Hearthstone.) Spelaren väljer själv, därför frågas gränssnittet.
class LookAtTopCards(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      cards = caster.reveal_top_cards(self.amount)
      if not cards:
         return   # leken är tom
      chosen = game.choose_card(caster, cards)   # människa eller AI väljer
      caster.take_into_hand(chosen)
      for card in cards:
         if card is not chosen:
            caster.return_to_deck_bottom(card)


# Priset för tung magi: ett slumpat eget kort som har minst lika mycket health som priset
# tar skadan (kortet får dö). Finns inget sådant kort tar den egna hjälten skadan.
class PayWithBlood(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      can_pay = []
      for card in caster.get_army():
         if card.get_health() >= self.amount:
            can_pay.append(card)
      if can_pay:
         random.choice(can_pay).take_damage(self.amount)
         caster.clear_dead_cards()
      else:
         caster.get_hero().take_damage(self.amount)


# Alla egna kort tar lika mycket skada (Rite of the Thirteenth Hour).
class DamageAllOwnCards(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      for card in caster.get_army():
         card.take_damage(self.amount)
      caster.clear_dead_cards()


# Fäster en buff (en tillfällig ändring) på ett eller flera mål.
# Buffen tillhör den som spelar spellen och går ut i början av hens nästa tur,
# eller i slutet av den här turen om this_turn_only är True.
# Stat-ändringar räknas i spellens 🪄 magic: attack=-1 betyder "−🪄 magic attack",
# armor=1 betyder "+🪄 magic armor". Statusar (cannot_attack, guard ...) är True eller False.
class GiveBuff(Effect):
   # Vem som får buffen
   ENEMY_CARD = "enemy card"                       # ett valt fiendekort
   ALL_ENEMY_CARDS = "all enemy cards"
   OWN_CARD = "own card"                           # ett valt eget kort
   OWN_RITUAL_CARD = "own ritual card"             # ett valt eget ritualkort
   ALL_OWN_CARDS = "all own cards"
   ALL_OWN_RITUAL_CARDS = "all own ritual cards"
   OWN_HERO = "own hero"

   def __init__(self, receiver, attack=0, armor=0, magic=0,
                cannot_attack=False, cannot_be_attacked=False, guard=False,
                no_melee_damage=False, ritual_protected=False, this_turn_only=False):
      self.receiver = receiver
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.cannot_attack = cannot_attack
      self.cannot_be_attacked = cannot_be_attacked
      self.guard = guard
      self.no_melee_damage = no_melee_damage
      self.ritual_protected = ritual_protected
      self.this_turn_only = this_turn_only

   # Bara när buffen ges till ETT kort väljer spelaren vilket
   def needs_target(self):
      return self.receiver in (self.ENEMY_CARD, self.OWN_CARD, self.OWN_RITUAL_CARD)

   def get_targets(self, game):
      if self.receiver == self.ENEMY_CARD:
         return game.get_opponent().get_army()
      if self.receiver == self.OWN_RITUAL_CARD:
         return game.get_current_player().get_ritual_cards()
      return game.get_current_player().get_army()

   # Vilka som får buffen: det valda målet, eller alla av en sort
   def receivers(self, game, target):
      if target is not None:
         return [target]
      caster = game.get_current_player()
      if self.receiver == self.ALL_ENEMY_CARDS:
         return game.get_opponent().get_army()
      if self.receiver == self.ALL_OWN_CARDS:
         return caster.get_army()
      if self.receiver == self.ALL_OWN_RITUAL_CARDS:
         return caster.get_ritual_cards()
      if self.receiver == self.OWN_HERO:
         return [caster.get_hero()]
      return []

   def apply(self, game, spell, target):
      amount = spell.get_magic()
      for receiver in self.receivers(game, target):
         buff = Buff(game.get_current_player(),
                     attack=self.attack * amount,
                     armor=self.armor * amount,
                     magic=self.magic * amount,
                     cannot_attack=self.cannot_attack,
                     cannot_be_attacked=self.cannot_be_attacked,
                     guard=self.guard,
                     no_melee_damage=self.no_melee_damage,
                     ritual_protected=self.ritual_protected,
                     this_turn_only=self.this_turn_only)
         receiver.add_buff(buff)


# Smittar ett fiendekort: det tar spellens 🪄 magic i skada i början av varje tur
# för den som smittade det, tills det dör (Infect).
class Infect(Effect):
   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      game.add_trigger(InfectTrigger(game.get_current_player(), target, spell.get_magic()))


# Nästa melee-anfall mot ett valt eget kort träffar anfallaren i stället (Mirror of Nitocris).
class ReflectNextAttack(Effect):
   def get_targets(self, game):
      return game.get_current_player().get_army()

   def apply(self, game, spell, target):
      game.add_trigger(MirrorTrigger(game.get_current_player(), target))


# Nästa fiendekort som anfaller ett av dina ritualkort tar samma skada (Curse of Choronzon).
class CurseRitualAttacker(Effect):
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.add_trigger(CurseTrigger(game.get_current_player()))


# Flera effekter i samma spell, till exempel "skada en fiende, men ett eget kort tar 3 skada".
# Bara den första effekten får ett mål. De andra sker automatiskt.
# (Composite-mönstret, Gang of Four. Fireplace skriver flera actions efter varandra på samma sätt.)
class Combined(Effect):
   def __init__(self, *effects):
      self.effects = effects

   def needs_target(self):
      return self.effects[0].needs_target()

   def get_targets(self, game):
      return self.effects[0].get_targets(game)

   def apply(self, game, spell, target):
      for effect in self.effects:
         effect.apply(game, spell, target)


# Ger den som spelar spellen mer resurs att spendera nu.
# Priset betalas med overload (mindre resurs nästa tur, som Overload hos Shaman i Hearthstone)
# och/eller med skada på den egna hjälten (tung magi kostar health).
class GainResource(Effect):
   def __init__(self, amount, overload=0, hero_damage=0):
      self.amount = amount
      self.overload = overload
      self.hero_damage = hero_damage

   # Ingen behöver väljas: effekten gäller alltid den som spelar.
   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      caster.gain_resource(self.amount)
      caster.add_overload(self.overload)
      caster.get_hero().take_damage(self.hero_damage)
