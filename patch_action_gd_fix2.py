import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

# I need to properly add "Giant Bouncy Royale": knockback_multiplier = 2.0 to action.gd
# Let's see the current code in action.gd around Pacifist Knockout

text = re.sub(
    r'elif gm_name == "Pacifist Knockout":\n\s*knockback_multiplier = 5\.0\n',
    r'elif gm_name == "Pacifist Knockout":\n\t\t\t\t\tknockback_multiplier = 5.0\n\t\t\t\telif gm_name == "Giant Bouncy Royale":\n\t\t\t\t\tknockback_multiplier = 2.0\n',
    text
)

with open("src/ai/action.gd", "w") as f:
    f.write(text)
