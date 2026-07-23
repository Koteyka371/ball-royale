import re

file_path = "src/ai/action.py"
with open(file_path, "r") as f:
    content = f.read()

# Add to pullable list
pullable_re = r'pullable = \["event_horizon_trap", "repulsion_zone"'
pullable_replacement = 'pullable = ["deployable_proximity_mud_puddle", "event_horizon_trap", "repulsion_zone"'
content = re.sub(pullable_re, pullable_replacement, content)

# Also need to add pickup logic in action.py
# Look for "deployable_mud_puddle" pickup logic and mirror it
# There are two places. Let's find them
pickup_logic = """                elif getattr(nearest, "kind", None) == "deployable_mud_puddle":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    self.ball.inventory.append("deployable_mud_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)"""

new_pickup_logic = pickup_logic + """
                elif getattr(nearest, "kind", None) == "deployable_proximity_mud_puddle":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    self.ball.inventory.append("deployable_proximity_mud_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)"""

content = content.replace(pickup_logic, new_pickup_logic)

with open(file_path, "w") as f:
    f.write(content)
