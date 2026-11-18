"""
Let AIs play many matches against each other and print statistics.

Used to test the rules and to balance the factions. Every match gets its own
seed, so a strange match can be played again exactly the same way. The
factions take turns starting, so that the advantage of going first is not
mixed up with the balance between the factions.

Run from the project folder, for example:
   python3 simulate.py                  (100 matches, SmartAI against SmartAI)
   python3 simulate.py 300 --ai random  (300 matches with RandomAI)
   python3 simulate.py 1 --seed 42      (play exactly match number 42 again)
"""

__author__ = "Johan Wrangö"
__version__ = "0.0.1"
__email__ = "johan.wrango@ga.dbgy.se"

import argparse
import random
from collections import Counter

from game import Game
from player import Player
from silent_ui import SilentUI
from ai import SmartAI, RandomAI
from factions.ghouls import ghouls
from factions.academics import academics


AI_TYPES = {"smart": SmartAI, "random": RandomAI}


# Spelar en hel match mellan två AI:er och returnerar resultatet.
# Jämna seeds: första fraktionen börjar. Udda: andra fraktionen börjar.
def play_match(seed, faction_a, faction_b, ai_type):
   random.seed(seed)   # samma seed ger exakt samma match
   if seed % 2 == 0:
      first, second = faction_a, faction_b
   else:
      first, second = faction_b, faction_a

   player1 = Player(first.get_name().value, first, ai_type())
   player2 = Player(second.get_name().value, second, ai_type())
   game = Game(player1, player2, SilentUI())
   game.run()

   winner = game.determine_winner()
   if winner is None:
      how = "draw"
   elif winner.is_ritual_complete():
      how = "ritual"
   else:
      how = "hero killed"

   return {
      "seed": seed,
      "winner": winner.get_name() if winner else None,
      "first": player1.get_name(),
      "how": how,
      "turns": game.get_turn_count(),
   }


def main():
   parser = argparse.ArgumentParser(description="Let AIs play Ritual against each other.")
   parser.add_argument("matches", type=int, nargs="?", default=100, help="number of matches")
   parser.add_argument("--ai", choices=AI_TYPES, default="smart", help="which AI plays")
   parser.add_argument("--seed", type=int, default=0, help="seed of the first match")
   args = parser.parse_args()

   wins = Counter()
   endings = Counter()
   first_player_wins = 0
   turns = []

   for seed in range(args.seed, args.seed + args.matches):
      result = play_match(seed, academics, ghouls, AI_TYPES[args.ai])
      wins[result["winner"] or "draw"] += 1
      endings[result["how"]] += 1
      if result["winner"] == result["first"]:
         first_player_wins += 1
      turns.append(result["turns"])
      if args.matches == 1:
         print(result)

   n = args.matches
   print(f"{n} matches, {args.ai} AI against {args.ai} AI (seeds {args.seed}-{args.seed + n - 1})")
   print("Wins:")
   for name, count in wins.most_common():
      print(f"   {name}: {count} ({100 * count / n:.0f} %)")
   print("How the matches ended:")
   for how, count in endings.most_common():
      print(f"   {how}: {count} ({100 * count / n:.0f} %)")
   print(f"The player who started won {100 * first_player_wins / n:.0f} %")
   print(f"Turns: average {sum(turns) / n:.1f}, shortest {min(turns)}, longest {max(turns)}")


if __name__ == "__main__":
   main()
