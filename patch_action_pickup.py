import re

with open("src/ai/action.py", "r") as f:
    text = f.read()

pickup_code = """
                elif getattr(nearest, "kind", None) == "deployable_acid_puddle":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    self.ball.inventory.append("deployable_acid_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
                elif getattr(nearest, "kind", None) == "deployable_shockwave_mine":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    self.ball.inventory.append("deployable_shockwave_mine")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
"""

text = re.sub(r'(\s+)elif getattr\(nearest, "kind", None\) == "deployable_acid_puddle":\s+if not hasattr.*?self\.world\.boosters\.remove\(nearest\)', pickup_code, text, count=1, flags=re.DOTALL)

with open("src/ai/action.py", "w") as f:
    f.write(text)
