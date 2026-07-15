import re
with open("src/ai/game_modes.py", "r") as f:
    content = f.read()
for m in re.finditer(r'class \w+Mode\b', content):
    if "BlackHole" in m.group() or "SafeZone" in m.group():
        print(m.group())
