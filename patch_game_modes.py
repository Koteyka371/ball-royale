import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

new_mode = '''class CursedBoosterMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Cursed Boosters"
        self.description = "All boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect."

'''

# Ensure we don't insert multiple times
if "CursedBoosterMode" not in content:
    match = re.search(r'GAME_MODES\s*=\s*{', content)
    idx = match.start()

    content = content[:idx] + new_mode + content[idx:]

    target_reg = 'GAME_MODES = {'
    replace_reg = 'GAME_MODES = {\n    "cursed_boosters": CursedBoosterMode(),'
    content = content.replace(target_reg, replace_reg)

    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
