import sys
from ai.game_modes import GAME_MODES

# print some lines of check_winner implementations
with open("src/ai/game_modes.py", "r") as f:
    lines = f.readlines()
    for i in range(1228, 1240):
        print(lines[i-1].rstrip())
