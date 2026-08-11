import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

text = re.sub(
    r'elif "name" in self\.world\.game_mode and self\.world\.game_mode\.name == "Pacifist Knockout":\n(\s+)knockback_multiplier = 5\.0\n',
    r'elif "name" in self.world.game_mode and self.world.game_mode.name == "Pacifist Knockout":\n\1knockback_multiplier = 5.0\n\t\t\t\telif "name" in self.world.game_mode and self.world.game_mode.name == "Giant Bouncy Royale":\n\t\t\t\t\tknockback_multiplier = 2.0\n',
    text
)

with open("src/ai/action.gd", "w") as f:
    f.write(text)
