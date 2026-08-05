with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

import re
content = content.replace("class FunnelHazard:\n                    pass\n                f = FunnelHazard()", "class FallbackFunnelHazard:\n                    pass\n                f = type('FunnelHazard', (), {})()")

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
