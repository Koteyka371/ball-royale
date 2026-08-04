import sys
sys.path.append("src")
from ai.game_modes import GAME_MODES
print("Mutator exists:", "silent_world_mutator" in GAME_MODES)
