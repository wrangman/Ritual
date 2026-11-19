"""
The budget: how strong a card may be for its cost.

Every card gets the same number of points per cost, whatever its faction.
A creature's stats and ability cost points, and so does a spell's effect.
A card above the budget is too strong for its cost, a card below is too weak.
This is the idea behind the "vanilla test" in Hearthstone: compare a card with
a card without an ability for the same cost, and let an ability cost some of
the stats ("text tax"). For spells, Hearthstone players compare with known
benchmark cards, for example Fireball (4 mana, 6 damage).

The point values are our own choice and are tested with simulate.py. When the
balance is wrong, change the values here, not one card at a time.

Run from the project folder:
   python3 budget.py
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

from card import CreatureCard, RitualCard, SpellCard, Special
from effect import (DamageOneEnemy, DamageAllEnemyCards, HealOwnHero, HealAllOwnCards,
                    LowerAttack, GainArmor, BuffOwnCard, LowerRitual, StealRitual, GainRitual,
                    DrawCards, ReviveRandom, ReturnRandomToHand, LookAtTopCards, DamageOwnHero,
                    GiveBuff, Infect, ReflectNextAttack, CurseRitualAttacker, Combined,
                    GainResource, SummonGhost, DrainHealth)
from factions.ghouls import ghouls
from factions.academics import academics


# Gemensamt för figurer och spells: budgeten för en kostnad, och jämförelsen med den.
# Varje underklass räknar ut points() på sitt eget sätt (polymorfism).
class Budget:
   POINTS_PER_COST = 5   # ett kort får 5 poäng per kostnad: kostnad 1 = 5, kostnad 3 = 15
   TOLERANCE = 0.5       # ett kort får ligga högst så här mycket under budgeten (🪄 ger halva poäng)

   def points(self, card):
      raise NotImplementedError("Varje sorts budget måste ha en egen points()")

   # Hur många poäng kortet får för sin kostnad
   def limit(self, card):
      return self.POINTS_PER_COST * card.get_cost()

   # Positivt: kortet är för starkt. Negativt: kortet är för svagt.
   def difference(self, card):
      return self.points(card) - self.limit(card)

   # Håller kortet budgeten? Aldrig över, och högst TOLERANCE under.
   def fits(self, card):
      return -self.TOLERANCE <= self.difference(card) <= 0


class StatBudget(Budget):
   # Vad varje stat kostar i poäng
   STAT_POINTS = {
      "attack": 1,    # ⚔️
      "health": 1,    # ❤️
      "magic": 0.5,   # 🪄 skyddar bara mot spells, så den är värd mindre
      "ritual": 2,    # ☩ ger ritual varje tur kortet ligger kvar
   }

   # Vad en förmåga kostar ("text tax" i Hearthstone)
   ABILITY_POINTS = {
      Special.GUARD: 2,
      Special.STUDY: 2,
      Special.SACRIFICE: 2,
      Special.DEVOUR: 5,   # kortet växer för alltid med ett dött korts ⚔️ och ❤️, ofta +4/+5
      Special.SUMMON: 3,
   }

   # Hur många poäng kortets stats och förmåga är värda
   def points(self, card):
      total = (self.STAT_POINTS["attack"] * card.get_attack()
               + self.STAT_POINTS["health"] * card.get_max_health()
               + self.STAT_POINTS["magic"] * card.get_magic()
               + self.STAT_POINTS["ritual"] * card.get_ritual())
      return total + self.ability_points(card)

   # En förmåga som inte finns i tabellen ska synas, inte bli gratis i tysthet
   def ability_points(self, card):
      special = card.get_special()
      if special is None:
         return 0
      if special not in self.ABILITY_POINTS:
         raise ValueError(f"{card.get_name()}: förmågan {special.name} har inget pris i ABILITY_POINTS")
      return self.ABILITY_POINTS[special]


# En spell är värd det dess effekt gör. Varje sorts effekt har ett eget pris nedan.
# Priserna ligger här och inte i effect.py: effekterna sköter spelet, budgeten sköter balansen.
class SpellBudget(Budget):
   # Härlett ur figurbudgeten: en figur för kostnad C har 5C poäng, ungefär hälften ❤️ (2,5C).
   # Att döda den kräver alltså 2,5C skada, så 1 skada på ett mål är värd 2 poäng.
   DAMAGE = 2

   # Uppskattningar, att prova med simulate.py:
   HEALTH = 1             # 1 ❤️ till ett eget kort eller hjälten, samma som på en figur
   CARD = 4               # ett kort till handen (Hearthstone: att dra ett kort är värt ungefär 1 mana)
   RITUAL = 2             # 1 ☩ en gång, samma som ☩ på en figur
   ATTACK = 1             # 1 ⚔️ mer eller mindre för alltid, samma som på en figur
   MAGIC = 0.5            # 1 🪄 mer för alltid, samma som på en figur
   TEMPORARY = 0.5        # en ändring som bara varar en tur är värd hälften
   BOARD = 2              # så många kort som ligger på en sida i snitt (mätt: 1,8–2,2)
   CREATURE = 10          # en slumpad figur ur gravhögen: en figur för kostnad 2 i snitt
   INFECT_TURNS = 2       # Infect hinner skada ungefär två gånger innan kortet dör

   # Statusar för ett kort under en tur
   STATUS_POINTS = {
      "cannot_attack": 3,       # ett fiendekort kan inte anfalla (Terror)
      "cannot_be_attacked": 3,  # ett eget kort kan inte anfallas (Veil of Tiamat)
      "guard": 2,               # samma som GUARD på en figur
      "no_melee_damage": 3,     # Seal of the Black Sun
      "ritual_protected": 4,    # Seal of Apep
   }
   MIRROR = 6    # ett helt anfall träffar anfallaren i stället
   CURSE = 4     # nästa anfall mot ett ritualkort slår tillbaka

   def __init__(self):
      self.creature_budget = StatBudget()   # spöken räknas som figurer
      # Varje sorts effekt -> metoden som räknar ut dess värde
      self.prices = {
         DamageOneEnemy: self.damage_one_enemy,
         DamageAllEnemyCards: self.damage_all_enemy_cards,
         HealOwnHero: lambda e: self.HEALTH * e.amount,
         HealAllOwnCards: lambda e: self.HEALTH * e.amount * self.BOARD,
         LowerAttack: lambda e: self.ATTACK * e.amount,
         GainArmor: self.gain_armor,
         BuffOwnCard: lambda e: self.MAGIC * e.magic + self.HEALTH * e.health,
         LowerRitual: lambda e: self.RITUAL * e.amount,
         StealRitual: lambda e: 2 * self.RITUAL * e.amount,   # motståndaren tappar, jag får
         GainRitual: lambda e: self.RITUAL * e.amount,
         DrawCards: lambda e: self.CARD * e.amount,
         LookAtTopCards: lambda e: self.CARD + 1,   # ett kort, och man får välja bland flera
         ReturnRandomToHand: lambda e: self.CARD,
         ReviveRandom: lambda e: self.CREATURE,
         DamageOwnHero: lambda e: -self.HEALTH * e.amount,
         GiveBuff: self.give_buff,
         Infect: lambda e: self.DAMAGE * e.amount * self.INFECT_TURNS,
         ReflectNextAttack: lambda e: self.MIRROR,
         CurseRitualAttacker: lambda e: self.CURSE,
         Combined: lambda e: sum(self.effect_points(part) for part in e.effects),
         GainResource: self.gain_resource,
         SummonGhost: self.summon_ghost,
         DrainHealth: lambda e: self.DAMAGE * e.amount + self.HEALTH * e.amount,
      }

   def points(self, card):
      return self.effect_points(card.get_effect())

   # En effekt som inte har något pris ska synas, inte bli gratis i tysthet
   def effect_points(self, effect):
      price = self.prices.get(type(effect))
      if price is None:
         raise ValueError(f"{type(effect).__name__} har inget pris i SpellBudget")
      return price(effect)

   def damage_one_enemy(self, effect):
      return self.DAMAGE * effect.amount

   def damage_all_enemy_cards(self, effect):
      return self.DAMAGE * effect.amount * self.BOARD - self.DAMAGE * effect.own_damage * self.BOARD

   # Hjältens armor nöts med 1 per träff, så 🛡️ 2 tar högst 2 + 1 = 3 skada
   def gain_armor(self, effect):
      return self.HEALTH * effect.amount * (effect.amount + 1) / 2

   # Resurs nu är värd som kostnad, minus det man betalar med overload och blod
   def gain_resource(self, effect):
      return (self.POINTS_PER_COST * (effect.amount - effect.overload)
              - self.HEALTH * effect.hero_damage)

   # Ett spöke är värt som en figur enligt figurbudgeten, plus att det inte kan anfallas en tur
   def summon_ghost(self, effect):
      value = self.creature_budget.points(effect.ghost)
      if effect.hidden:
         value += self.STATUS_POINTS["cannot_be_attacked"]
      return value

   # En buff: stat-ändringar och statusar, gånger hur många kort som får den.
   # Buffar varar bara en tur, så stat-ändringar räknas till hälften (TEMPORARY).
   def give_buff(self, effect):
      value = (self.ATTACK * abs(effect.attack) + self.MAGIC * abs(effect.magic)) * self.TEMPORARY
      for status, status_value in self.STATUS_POINTS.items():
         if getattr(effect, status):
            value += status_value
      return value * self.receiver_count(effect)

   # Hur många kort en buff träffar i snitt
   def receiver_count(self, effect):
      if effect.receiver in (GiveBuff.ALL_ENEMY_CARDS, GiveBuff.ALL_OWN_CARDS):
         return self.BOARD
      return 1   # ett valt kort, hjälten, eller alla ritualkort (oftast bara ett)


# Fraktionens kort av en sort, ett av varje (leken har ofta två exemplar av samma kort)
def unique_cards(faction, kind):
   seen = set()
   cards = []
   for card in faction.create_cards():
      if type(card) is not kind or card.get_name() in seen:
         continue
      seen.add(card.get_name())
      cards.append(card)
   return sorted(cards, key=lambda card: card.get_cost())


# Fraktionens figurer (eller ritualkort), ett av varje
def unique_creatures(faction, ritual_cards):
   return unique_cards(faction, RitualCard if ritual_cards else CreatureCard)


# Ett tal utan ".0" när det är ett heltal: 12 i stället för 12.0, men 12.5 som det är
def number(value):
   if value == int(value):
      return str(int(value))
   return str(value)


def budget_text(budget, card):
   diff = budget.difference(card)
   sign = "+" if diff > 0 else ""
   return f"{number(budget.points(card)):>4s} / {budget.limit(card):<3d} {sign}{number(diff)}"


def print_creatures(budget, cards, title):
   print(title)
   for card in cards:
      special = card.get_special().name if card.get_special() else ""
      print(f"   ({card.get_cost()}) {card.get_name():28s} "
            f"⚔️ {card.get_attack()} 🪄 {card.get_magic()} ❤️ {card.get_max_health()} ☩ {card.get_ritual()} "
            f"{special:10s} {budget_text(budget, card)}")


def print_spells(budget, cards, title):
   print(title)
   for card in cards:
      print(f"   ({card.get_cost()}) {card.get_name():28s} {budget_text(budget, card)}")


def main():
   creature_budget = StatBudget()
   spell_budget = SpellBudget()
   print("Poäng / budget, och skillnaden (+ = för starkt, − = för svagt)\n")
   for faction in (ghouls, academics):
      name = faction.get_name().value
      print_creatures(creature_budget, unique_creatures(faction, ritual_cards=False), f"{name}, figurer:")
      print_creatures(creature_budget, unique_creatures(faction, ritual_cards=True), f"{name}, ritualkort:")
      print_spells(spell_budget, unique_cards(faction, SpellCard), f"{name}, spells:")
      print()


if __name__ == "__main__":
   main()
