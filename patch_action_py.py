import re
import sys

def modify_action_py():
    path = "src/ai/action.py"
    with open(path, "r") as f:
        content = f.read()

    orig = """                elif getattr(nearest, "kind", None) == "charging_shockwave_shield_booster":"""
    repl = """                elif getattr(nearest, "kind", None) == "snow_globe_booster":
                    self.ball.freezing_immunity_timer = 15.0
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards") and nearest in self.world.arena.hazards:
                        self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
                elif getattr(nearest, "kind", None) == "umbrella_booster":
                    self.ball.slippery_immunity_timer = 15.0
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards") and nearest in self.world.arena.hazards:
                        self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
                elif getattr(nearest, "kind", None) == "charging_shockwave_shield_booster":"""

    content = content.replace(orig, repl)
    with open(path, "w") as f:
        f.write(content)

modify_action_py()
