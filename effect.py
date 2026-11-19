"""
An effect: this class applies effects from spellcards for instance.

apply() can be called to use a spell. Each kind of effect is its own small
class, and the same effect can be reused by many spells (Command/Strategy
pattern, like the actions in Fireplace).

Spells have no stats of their own, as in Hearthstone. How strong an effect
is (how much damage, healing, ritual ...) is given when the effect is created,
for example DamageOneEnemy(7). Magic damage is lowered by the target's 🪄 magic.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import copy
import random
from card import CreatureCard, Special, magic_damage
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

   # En effekt ändras aldrig under matchen (talen sätts när kortet skapas), så när AI:n
   # kopierar spelet för att prova ett drag kan kopian dela samma effekt-objekt.
   # Det gör kopieringen mycket snabbare.
   def __deepcopy__(self, memo):
      return self


# Gör amount magisk skada på en fiende (målets 🪄 magic tar emot, hjältens armor hjälper inte).
# include_hero=False betyder att bara fiendens figurer får väljas, inte hjälten.
class DamageOneEnemy(Effect):
   def __init__(self, amount, include_hero=True):
      self.amount = amount
      self.include_hero = include_hero

   def get_targets(self, game):
      if self.include_hero:
         return game.get_opponent().get_spell_targets()
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      target.take_damage(magic_damage(self.amount, target))
      game.get_opponent().clear_dead_cards()


# Gör amount magisk skada på alla fiendens figurer (inte hjälten).
# own_damage: så mycket skada varje eget kort tar (används inte av något kort just nu).
class DamageAllEnemyCards(Effect):
   def __init__(self, amount, own_damage=0):
      self.amount = amount
      self.own_damage = own_damage

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      opponent = game.get_opponent()
      caster = game.get_current_player()
      for card in opponent.get_army():
         card.take_damage(magic_damage(self.amount, card))
      if self.own_damage > 0:
         for card in caster.get_army():
            card.take_damage(self.own_damage)
      opponent.clear_dead_cards()
      caster.clear_dead_cards()


# Läker den egna hjälten med amount (Drain Life, som i Hearthstone).
class HealOwnHero(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().restore_health(self.amount)


# Läker alla egna kort med amount.
class HealAllOwnCards(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      for card in game.get_current_player().get_army():
         card.restore_health(self.amount)


# Sänker en fientlig figurs ⚔️ attack med amount, för alltid.
class LowerAttack(Effect):
   def __init__(self, amount):
      self.amount = amount

   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      target.lower_attack(self.amount)


# Den egna hjälten får armor (Bone Ward). Bara hjälten kan ha armor, som i Hearthstone.
class GainArmor(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().gain_armor(self.amount)


# Ger ett eget kort mer av en eller flera stats, för alltid. BuffOwnCard(health=3) ger +3 health.
# ritual_only=True betyder att bara egna ritualkort får väljas.
class BuffOwnCard(Effect):
   def __init__(self, magic=0, health=0, ritual_only=False):
      self.magic = magic
      self.health = health
      self.ritual_only = ritual_only

   def get_targets(self, game):
      caster = game.get_current_player()
      if self.ritual_only:
         return caster.get_ritual_cards()
      return caster.get_army()

   def apply(self, game, spell, target):
      if self.magic:
         target.increase_magic(self.magic)
      if self.health:
         target.increase_health(self.health)


# Sänker motståndarens ritual med amount.
class LowerRitual(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_opponent().get_hero().lose_ritual(self.amount)


# Stjäl amount ritual från motståndaren. Man kan inte stjäla mer än motståndaren har.
class StealRitual(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      opponent_hero = game.get_opponent().get_hero()
      if opponent_hero.is_ritual_protected():
         return   # Seal of Apep: inget kan stjälas
      stolen = min(self.amount, opponent_hero.get_ritual())
      opponent_hero.lose_ritual(stolen)
      game.get_current_player().get_hero().add_ritual(stolen)


# Lägger amount till den egna ritualen (Scroll of Rituals).
class GainRitual(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().add_ritual(self.amount)


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


# Trollar fram ett spöke: en figur som inte fanns i leken (en "token", som Mirror Image
# i Hearthstone). ghost är en förlaga; varje gång spellen spelas skapas en ny kopia,
# eftersom spöket kan ändras på brädet (skadas, få buffar).
# hidden=True: spöket kan inte anfallas förrän ens nästa tur (som Stealth i Hearthstone).
# Är brädet fullt händer ingenting, som för Resurrect.
class SummonGhost(Effect):
   def __init__(self, ghost, hidden=False):
      self.ghost = ghost
      self.hidden = hidden

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      if not caster.has_room_on_board():
         return
      ghost = copy.deepcopy(self.ghost)
      caster.summon(ghost)
      if self.hidden:
         ghost.add_buff(Buff(caster, cannot_be_attacked=True))


# Dränerar health från ett fiendekort och ger det till ett slumpat eget kort, för alltid.
# Det är magi, så målets 🪄 magic tar emot som vanligt. Bara det som faktiskt togs ges vidare.
# Spelaren väljer bara ett mål per spell, därför slumpas mottagaren (som SACRIFICE när
# kortet dör). Har man inga kort på brädet läker det i stället den egna hjälten (som Drain Life).
class DrainHealth(Effect):
   def __init__(self, amount):
      self.amount = amount

   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      caster = game.get_current_player()
      drained = min(magic_damage(self.amount, target), target.get_health())
      target.take_damage(drained)
      if drained > 0:
         own_cards = caster.get_army()
         if own_cards:
            random.choice(own_cards).increase_health(drained)
         else:
            caster.get_hero().restore_health(drained)
      game.get_opponent().clear_dead_cards()


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


# Den egna hjälten tar skada: priset för att stjäla ritual (Unaussprechlichen Kulten).
# Priset tas av spelaren själv, aldrig av korten, så att inget kort dör av det.
class DamageOwnHero(Effect):
   def __init__(self, amount):
      self.amount = amount

   def needs_target(self):
      return False

   def apply(self, game, spell, target):
      game.get_current_player().get_hero().take_damage(self.amount)


# Alla egna kort tar lika mycket skada.
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
# Stat-ändringar är tal: attack=-2 betyder 2 mindre attack, magic=2 betyder 2 mer magic.
# Statusar (cannot_attack, guard ...) är True eller False.
class GiveBuff(Effect):
   # Vem som får buffen
   ENEMY_CARD = "enemy card"                       # ett valt fiendekort
   ALL_ENEMY_CARDS = "all enemy cards"
   OWN_CARD = "own card"                           # ett valt eget kort
   OWN_RITUAL_CARD = "own ritual card"             # ett valt eget ritualkort
   ALL_OWN_CARDS = "all own cards"
   ALL_OWN_RITUAL_CARDS = "all own ritual cards"
   OWN_HERO = "own hero"

   def __init__(self, receiver, attack=0, magic=0,
                cannot_attack=False, cannot_be_attacked=False, guard=False,
                no_melee_damage=False, ritual_protected=False, this_turn_only=False):
      self.receiver = receiver
      self.attack = attack
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
      for receiver in self.receivers(game, target):
         buff = Buff(game.get_current_player(),
                     attack=self.attack,
                     magic=self.magic,
                     cannot_attack=self.cannot_attack,
                     cannot_be_attacked=self.cannot_be_attacked,
                     guard=self.guard,
                     no_melee_damage=self.no_melee_damage,
                     ritual_protected=self.ritual_protected,
                     this_turn_only=self.this_turn_only)
         receiver.add_buff(buff)


# Smittar ett fiendekort: det tar amount i skada i början av varje tur
# för den som smittade det, tills det dör (Infect).
class Infect(Effect):
   def __init__(self, amount):
      self.amount = amount

   def get_targets(self, game):
      return game.get_opponent().get_army()

   def apply(self, game, spell, target):
      game.add_trigger(InfectTrigger(game.get_current_player(), target, self.amount))


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


# Figurernas förmågor

# DEVOUR: figuren som läggs äter ett dött kort i den egna gravhögen och får dess
# ⚔️ attack och ❤️ health för alltid. Det ätna kortet försvinner (kan inte återupplivas).
# Värdena är kortets egna utan buffar (buffarna försvann när det dog), men med
# bestående ändringar som Wither.
class Devour(Effect):
   def get_targets(self, game):
      dead_creatures = []
      for card in game.get_current_player().get_graveyard():
         if isinstance(card, CreatureCard):
            dead_creatures.append(card)
      return dead_creatures

   def apply(self, game, card, target):
      card.increase_attack(target.get_attack())
      card.increase_health(target.get_max_health())
      game.get_current_player().eat_from_graveyard(target)


# SUMMON: en slumpad figur ur den egna leken läggs direkt på brädet
# (som Recruit i Hearthstone). Är brädet fullt eller finns ingen figur i leken händer inget.
class SummonRandomFromDeck(Effect):
   def needs_target(self):
      return False

   def apply(self, game, card, target):
      caster = game.get_current_player()
      if not caster.has_room_on_board():
         return
      creatures = []
      for deck_card in caster.get_deck().get_cards():
         if isinstance(deck_card, CreatureCard):
            creatures.append(deck_card)
      if creatures:
         caster.summon_from_deck(random.choice(creatures))


# Vilken effekt en figurs förmåga har när figuren läggs (som Battlecry i Hearthstone).
# Förmågor som inte står här gör inget när kortet läggs (till exempel GUARD, som
# i stället gäller hela tiden kortet ligger på brädet).
CREATURE_ABILITIES = {
   Special.DEVOUR: Devour(),
   Special.STUDY: DrawCards(1),
   Special.SUMMON: SummonRandomFromDeck(),
}

def creature_ability(card):
   return CREATURE_ABILITIES.get(card.get_special())
