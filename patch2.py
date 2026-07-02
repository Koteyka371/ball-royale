with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

import re

# Update random choice in _trigger_event and tick
old = """            if random.random() < 0.1:
                x = random.uniform(50, self.width - 50)"""
new = """            if random.random() < 0.1:
                x = random.uniform(50, self.width - 50)"""

old2 = """                elif random.random() < 0.10:
                    kind = "sinkhole"
                    damage = 5.0"""
new2 = """                elif random.random() < 0.10:
                    kind = "sinkhole"
                    damage = 5.0
                elif random.random() < 0.10:
                    kind = "shrinking_zone"
                    damage = 15.0"""
content = content.replace(old2, new2)

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
