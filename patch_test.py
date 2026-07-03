import re

with open('src/ai/game_modes.py', 'r') as f:
    text = f.read()

print("mud_pit 1:", "mud_pit = Hazard" in text[0:20000])
print("mud_pit 2:", "mud_pit = Hazard" in text[20000:])
