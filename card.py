

class Card:
   def __init__(self, faction=None, name="Unknown", attack=0, armor=0, magic=0, ritual=0, special=None, rarity="Common"):
      self.faction = faction
      self.name = name
      self.attack = attack
      self.armor = armor
      self.magic = magic
      self.ritual = ritual
      self.special = special
      self.rarity = rarity
      
      
   def __str__(self):
      return f"{self.faction or '–'} - {self.name}; [ ⚔️ {self.attack}, 🛡️ {self.armor}, 🪄 {self.magic}, ☩ {self.ritual}], SPC: {self.special or '–'}, RAR: {self.rarity}"
   
   def __repr__(self):
      return (f"Card(faction={self.faction!r}, name={self.name!r}, attack={self.attack!r}, "
              f"armor={self.armor!r}, magic={self.magic!r}, ritual={self.ritual!r}, "
              f"special={self.special!r}, rarity={self.rarity!r})")

   def short(self):
      return f"{self.name} [⚔️{self.attack} 🛡️{self.armor} 🪄{self.magic} ☩{self.ritual}]"

   # --- Getters ---
   def get_faction(self):
      return self.faction

   def get_name(self):
      return self.name

   def get_attack(self):
      return self.attack

   def get_armor(self):
      return self.armor

   def get_magic(self):
      return self.magic

   def get_ritual(self):
      return self.ritual

   def get_special(self):
      return self.special

   def get_rarity(self):
      return self.rarity

   # --- Setters ---
   def set_faction(self, faction):
      self.faction = faction

   def set_name(self, name):
      self.name = name

   def set_attack(self, attack):
      self.attack = attack

   def set_armor(self, armor):
      self.armor = armor

   def set_magic(self, magic):
      self.magic = magic

   def set_ritual(self, ritual):
      self.ritual = ritual

   def set_special(self, special):
      self.special = special

   def set_rarity(self, rarity):
      self.rarity = rarity

   