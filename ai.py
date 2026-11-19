"""
AI players: controllers that choose moves without asking a human.

RandomAI picks any legal move. It plays badly, but it is useful as a baseline
and for finding crashes, since it tries everything.

SmartAI tries every legal move on a copy of the game and scores the result
with an evaluation function, then picks the move with the best score. This is
the idea behind GreedyOptimizeMove in MetaStone (a Hearthstone simulator).
New cards need no new AI code: the AI just sees what each move leads to.

The weights in the evaluation decide what the AI cares about. Changing them
gives the AI another style, for example more aggressive or more ritual-minded.
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import random
from controller import Controller


# Hittar "end turn" bland dragen (det finns alltid ett)
def find_end_turn(moves):
   for move in moves:
      if move.ends_turn():
         return move


# Väljer helt slumpvis bland de lagliga dragen, och avslutar turen ibland.
class RandomAI(Controller):
   def __init__(self, end_turn_chance=0.1):
      self.end_turn_chance = end_turn_chance   # chansen att avsluta turen i stället för att göra något

   def choose_move(self, game, player, moves):
      other_moves = []
      for move in moves:
         if not move.ends_turn():
            other_moves.append(move)
      if not other_moves or random.random() < self.end_turn_chance:
         return find_end_turn(moves)
      return random.choice(other_moves)

   def choose_card(self, game, player, cards):
      return random.choice(cards)

   # Byter varje kort med 50 % chans
   def choose_mulligan(self, game, player, cards):
      replace = []
      for card in cards:
         if random.random() < 0.5:
            replace.append(card)
      return replace


# Provar varje drag på en kopia av spelet och väljer det som ger bäst läge efteråt.
# AI:n tittar bara ett drag framåt: den gör det bästa draget, sedan det bästa igen,
# tills inget drag gör läget bättre. Då avslutar den turen.
class SmartAI(Controller):
   # Hur mycket AI:n bryr sig om olika saker. Värdena är gissningar att börja med.
   # Samma vikter används för båda sidor: det som är bra för mig är dåligt för motståndaren.
   WEIGHTS = {
      "win": 1000,                  # vunnen match (förlust ger lika mycket minus)
      "hero_health": 1.0,           # per ❤️ på hjälten
      "ritual": 1.5,                # per ☩ på hjälten (upp till målet)
      "ritual_income": 3.0,         # per ☩ på korten på brädet (ger ritual varje tur de ligger kvar)
      "own_ritual_reached": 50,     # jag har nått målet: vinner nästa tur om ingen stoppar mig
      "enemy_ritual_reached": 300,  # motståndaren har nått målet: vinner i början av sin tur!
      "attack": 1.0,                # per ⚔️ på ett kort på brädet
      "health": 0.5,                # per ❤️ på ett kort på brädet
      "armor": 0.5,                 # per 🛡️ på ett kort på brädet
      "magic": 0.3,                 # per 🪄 på ett kort på brädet
      "guard": 1.5,                 # ett kort med Guard skyddar resten
      "hidden": 1.5,                # ett kort som inte kan anfallas (Veil of Tiamat)
      "hand_card": 1.0,             # per kort i handen
      "resource": 0.1,              # per resurs kvar (försvinner när turen är slut, så värd lite)
      "overload": 0.5,              # per resurs som är lånad från nästa tur
      "trigger": 2.0,               # per trigger som väntar (Infect, Mirror, Curse)
      "ritual_protection": 3.0,     # ritualen kan inte sänkas (Seal of Apep)
      "exposed_hero": 0.5,          # per skada motståndarens armé kan göra när min hjälte saknar skydd
   }

   # Ett drag måste göra läget minst så här mycket bättre, annars avslutar AI:n turen.
   # Då gör den inga meningslösa drag (till exempel ett anfall som gör 0 skada).
   MIN_GAIN = 0.01

   # Kort som kostar mer än så här byts bort i mulligan. En gissning, som vikterna.
   MULLIGAN_MAX_COST = 3

   def __init__(self, weights=None):
      self.weights = dict(self.WEIGHTS)
      if weights:
         self.weights.update(weights)   # ändra bara de vikter man skickar med

   def choose_move(self, game, player, moves):
      best_move = find_end_turn(moves)
      best_score = self.evaluate(game, player) + self.MIN_GAIN   # läget om AI:n inte gör något

      for move in moves:
         if move.ends_turn():
            continue
         score = self.score_move(game, move)
         if score > best_score:
            best_move = move
            best_score = score

      return best_move

   # Provar draget på en kopia av spelet och betygsätter läget efteråt.
   # Det riktiga spelet ändras inte. Slumpade effekter (till exempel Resurrect)
   # provas en gång, så betyget blir en uppskattning.
   def score_move(self, game, move):
      game_copy, move_copy = game.copy_for_simulation(move)
      player = game_copy.get_current_player()
      resource_before = player.get_resource()
      move_copy.execute(game_copy)
      score = self.evaluate(game_copy, player)

      # Ett drag som ger resurs (Trinket, The Silver Key) är inte värt något i sig,
      # utan värt det man kan göra med resursen. Med bara ett drag framåt skulle AI:n
      # aldrig spela sådana kort. Därför tittar den ett drag till och tar det bästa.
      if player.get_resource() > resource_before and not game_copy.is_over():
         for next_move in game_copy.get_legal_moves(player):
            if not next_move.ends_turn():
               score = max(score, self.score_move(game_copy, next_move))

      return score

   # Forbidden Codex: ta det dyraste kortet (dyra kort är oftast starkast)
   def choose_card(self, game, player, cards):
      return max(cards, key=lambda card: card.get_cost())

   # Mulligan: byt kort som är för dyra för de första turerna (resursen är 1, 2, 3 ...).
   # Utan billiga kort gör man ingenting i början. Det är ett vanligt råd i Hearthstone
   # ("mulligan for a curve").
   def choose_mulligan(self, game, player, cards):
      replace = []
      for card in cards:
         if card.get_cost() > self.MULLIGAN_MAX_COST:
            replace.append(card)
      return replace


   # Betygsättning

   # Hur bra är läget för player? Högre är bättre.
   def evaluate(self, game, player):
      w = self.weights
      opponent = game.get_opponent_of(player)

      i_won = game.has_won(player, opponent)
      they_won = game.has_won(opponent, player)
      if i_won and they_won:
         return 0   # oavgjort
      if i_won:
         return w["win"]
      if they_won:
         return -w["win"]

      score = self.side_value(game, player) - self.side_value(game, opponent)

      # Ritualen avgörs i början av ägarens tur. Har motståndaren nått målet nu,
      # mitt i min tur, vinner hen när hens tur börjar om jag inte sänker den.
      if opponent.reached_ritual():
         score -= w["enemy_ritual_reached"]
      if player.reached_ritual():
         score += w["own_ritual_reached"]

      # Kan min hjälte anfallas direkt (inga kort som skyddar)? Då är motståndarens armé ett hot.
      # Varje kort räknar själv ut sitt bästa anfall (⚔️ eller 🪄), så AI:n behöver
      # inte veta vilken sorts kort det är (polymorfism).
      hero = player.get_hero()
      if hero in player.get_targets():
         threat = 0
         for card in opponent.get_army():
            threat += card.threat_against(hero)
         score -= w["exposed_hero"] * threat

      return score

   # Värdet av allt på en spelares sida: hjälten, ritualen, korten och handen
   def side_value(self, game, player):
      w = self.weights
      hero = player.get_hero()
      goal = player.get_faction().get_ritual_goal()

      value = w["hero_health"] * hero.get_health()
      value += w["ritual"] * min(hero.get_ritual(), goal)   # mer än målet är inte värt mer
      value += w["hand_card"] * len(player.get_hand())
      value += w["resource"] * player.get_resource()
      value -= w["overload"] * player.get_overload()

      for card in player.get_army():
         value += self.board_value(card)

      for trigger in game.get_triggers():
         if trigger.get_owner() is player:
            value += w["trigger"]

      if hero.is_ritual_protected():
         value += w["ritual_protection"]

      return value

   # Värdet av ett kort på brädet: dess stats och den ☩ det ger varje tur
   def board_value(self, card):
      return self.card_value(card) + self.weights["ritual_income"] * card.get_ritual()

   # Värdet av ett korts stats. Getters räknar in buffarna (Bone Ward, Terror ...).
   def card_value(self, card):
      w = self.weights
      value = (w["attack"] * card.get_attack()
               + w["health"] * card.get_health()
               + w["armor"] * card.get_armor()
               + w["magic"] * card.get_magic())
      if card.has_guard():
         value += w["guard"]
      if not card.can_be_attacked():
         value += w["hidden"]
      return value
