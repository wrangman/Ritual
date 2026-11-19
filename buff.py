"""
Buffs: temporary changes fastened to a card or a hero.

A buff can change stats (attack, magic) and/or give a status, for
example "cannot attack" or "Guard". The card's own values are never changed:
get_attack() and the others add the buffs on top. When the buff expires it is
simply removed. (Hearthstone calls these enchantments, Fireplace calls them
Buff. Darkest Dungeon has buffs and debuffs with a duration in the same way.)

A buff belongs to the player who cast it. It expires at the start of that
player's next turn, or at the end of the current turn if this_turn_only is True.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"


class Buff:
   def __init__(self, owner, attack=0, magic=0,
                cannot_attack=False, cannot_be_attacked=False, guard=False,
                no_melee_damage=False, ritual_protected=False, this_turn_only=False):
      self.owner = owner                            # spelaren som lade buffen
      self.attack = attack                          # + eller − på attack
      self.magic = magic                            # + eller − på magic
      self.cannot_attack = cannot_attack            # Terror, The King in Yellow
      self.cannot_be_attacked = cannot_be_attacked  # Veil of Tiamat, Void Wraith
      self.guard = guard                            # Kiss of Lilith
      self.no_melee_damage = no_melee_damage        # Seal of the Black Sun
      self.ritual_protected = ritual_protected      # Seal of Apep
      self.this_turn_only = this_turn_only          # True: går ut i slutet av turen

   # Går buffen ut nu? Den går ut när dess ägares tur börjar (eller slutar, för "this turn").
   def expires(self, player, this_turn_only):
      return self.owner is player and self.this_turn_only == this_turn_only


# Listan med buffar som ett kort eller en hjälte har (sammansättning).
# Både CreatureCard och Hero har en BuffList, så logiken står bara här.
class BuffList:
   def __init__(self):
      self.buffs = []

   def add(self, buff):
      self.buffs.append(buff)

   # Tar bort buffarna som går ut för den här spelaren just nu
   def remove_expired(self, player, this_turn_only):
      kept = []
      for buff in self.buffs:
         if not buff.expires(player, this_turn_only):
            kept.append(buff)
      self.buffs = kept

   # Alla buffar försvinner, till exempel när kortet dör
   def clear(self):
      self.buffs = []

   def is_empty(self):
      return not self.buffs


   # Summan av alla buffars stat-ändringar

   def attack_bonus(self):
      total = 0
      for buff in self.buffs:
         total += buff.attack
      return total

   def magic_bonus(self):
      total = 0
      for buff in self.buffs:
         total += buff.magic
      return total


   # Har någon buff den här statusen?

   def cannot_attack(self):
      for buff in self.buffs:
         if buff.cannot_attack:
            return True
      return False

   def cannot_be_attacked(self):
      for buff in self.buffs:
         if buff.cannot_be_attacked:
            return True
      return False

   def guard(self):
      for buff in self.buffs:
         if buff.guard:
            return True
      return False

   def no_melee_damage(self):
      for buff in self.buffs:
         if buff.no_melee_damage:
            return True
      return False

   def ritual_protected(self):
      for buff in self.buffs:
         if buff.ritual_protected:
            return True
      return False
