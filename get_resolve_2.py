import re

with open("src/ai/action.py", "r") as f:
    data = f.read()

start = data.find("def _resolve_collisions")
print(data.find("for hazard in self.world.arena.hazards:", start))
