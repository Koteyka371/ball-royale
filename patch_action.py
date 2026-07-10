import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Make the breach charge temporarily disable hazards instead of removing them completely.
# Find the exact breach charge logic we added
old_block = """        # Breach Charge logic
        if getattr(self.ball, "breach_charge_active", False):
            if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                hazards_to_remove = []
                for hazard in self.world.arena.hazards:
                    if getattr(hazard, "kind", "") in ["bumper", "breakable_wall"]:
                        dx = hazard.x - self.ball.x
                        dy = hazard.y - self.ball.y
                        dist = math.hypot(dx, dy)
                        if dist < getattr(self.ball, "radius", 10.0) + getattr(hazard, "radius", 10.0) + 10.0:
                            hazards_to_remove.append(hazard)
                if hazards_to_remove:
                    for h in hazards_to_remove:
                        if h in self.world.arena.hazards:
                            self.world.arena.hazards.remove(h)
                    self.ball.breach_charge_active = False # Consume on use
"""

new_block = """        # Breach Charge logic
        if getattr(self.ball, "breach_charge_active", False):
            if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                disabled_any = False
                for hazard in self.world.arena.hazards:
                    if getattr(hazard, "kind", "") in ["bumper", "breakable_wall"]:
                        dx = hazard.x - self.ball.x
                        dy = hazard.y - self.ball.y
                        dist = math.hypot(dx, dy)
                        if dist < getattr(self.ball, "radius", 10.0) + getattr(hazard, "radius", 10.0) + 10.0:
                            hazard.emp_disabled_timer = 15.0 # Temporarily disable
                            disabled_any = True
                if disabled_any:
                    self.ball.breach_charge_active = False # Consume on use
"""

content = content.replace(old_block, new_block)

with open("src/ai/action.py", "w") as f:
    f.write(content)
