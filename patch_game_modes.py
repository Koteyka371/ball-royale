import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

if "from ai.ball_types_mirror import Mirror" not in content:
    content = content.replace("from ai.ball_types_templar import Templar", "from ai.ball_types_templar import Templar\nfrom ai.ball_types_mirror import Mirror")

if "Mirror" not in content and "'mirror'" not in content:
    print("Wait, Mirror is not in game_modes.py")
