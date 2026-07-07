import sys

with open("src/ai/game_modes.py", 'r') as f:
    text = f.read()

# Let's search if game_modes are calling check_winner
