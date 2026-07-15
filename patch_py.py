with open("src/ai/action.py", "r") as f:
    content = f.read()

import re

# Add to _collect_booster
booster_handling = """                elif getattr(nearest, "kind", None) == "knockback_booster":
                    self.ball.knockback_booster_timer = 15.0
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
"""
content = re.sub(r'(                elif getattr\(nearest, "kind", None\) == "emp_immunity_booster":)', booster_handling + r'\1', content)

# Add void_panel protection
void_panel_handling = """                    if getattr(hazard, "kind", "") == "void_panel":
                        if getattr(self.ball, "knockback_booster_timer", 0.0) > 0.0:
                            continue
"""
content = re.sub(r'(                    if getattr\(hazard, "kind", ""\) == "void_panel":\n)', void_panel_handling, content, count=1)
content = re.sub(r'(                    if getattr\(hazard, "kind", ""\) == "void_panel":\n)', void_panel_handling, content, count=2) # it happens twice
# wait the first replace might affect the second if we just use string replacement carefully.
# Using string replace is better.
