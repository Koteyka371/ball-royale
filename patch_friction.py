import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

original_friction = """
        if not getattr(self.ball, "is_frictionless", False):
            # Apply friction
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.vx *= 0.95
                self.ball.vy *= 0.95
"""

replacement_friction = """
        if not getattr(self.ball, "is_frictionless", False):
            # Apply friction
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                friction_mult = 0.95
                arena = getattr(self.world, 'arena', None)
                if arena:
                    if getattr(arena, 'is_snowing', False):
                        friction_mult = 0.98  # Very slippery
                    elif getattr(arena, 'is_heatwave', False):
                        friction_mult = 0.90  # Sticky/dry, higher friction

                self.ball.vx *= friction_mult
                self.ball.vy *= friction_mult
"""

if original_friction in content:
    content = content.replace(original_friction, replacement_friction)
    print("Friction patch applied in action.py")
else:
    print("Friction original not found in action.py")

with open("src/ai/action.py", "w") as f:
    f.write(content)
