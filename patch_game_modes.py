import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

# Add math import at top level if not there
if "import math" not in content[:500]:
    content = "import math\n" + content

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
