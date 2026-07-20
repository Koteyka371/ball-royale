import re

with open('src/ai/game_modes.py', 'r') as f:
    content = f.read()

# Ah, the mode doesn't actually deal damage, it applies a shockwave!
# Let's see how the test is written.
