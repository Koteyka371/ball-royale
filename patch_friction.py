import re
with open("src/ai/action.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""        self.ball.in_anomaly_zone = in_anomaly_zone

        gm = getattr(self.world, "game_mode", None)
        is_zero_gravity = False
        if in_anomaly_zone:
            is_zero_gravity = True""",
"""        self.ball.in_anomaly_zone = in_anomaly_zone

        # Ice patch processing (zero friction, slide fast)
        in_ice_patch = False
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
            for hazard in self.world.arena.hazards:
                if getattr(hazard, "kind", "") == "ice_patch" and getattr(hazard, "active", True):
                    dx = hazard.x - self.ball.x
                    dy = hazard.y - self.ball.y
                    if (dx*dx + dy*dy) <= getattr(hazard, "radius", 0)**2:
                        in_ice_patch = True
                        break
        self.ball.in_ice_patch = in_ice_patch

        gm = getattr(self.world, "game_mode", None)
        is_zero_gravity = False
        if in_anomaly_zone:
            is_zero_gravity = True""")

new_code = new_code.replace(
"""        if is_zero_gravity:
            # Apply friction
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.vx *= (1.0 - 0.5 * delta)
                self.ball.vy *= (1.0 - 0.5 * delta)
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""",
"""        if is_zero_gravity:
            # Apply friction
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.vx *= (1.0 - 0.5 * delta)
                self.ball.vy *= (1.0 - 0.5 * delta)
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta

        if in_ice_patch:
            # Zero friction slide
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""")

new_code = new_code.replace(
"""                bounced = True""",
"""                bounced = True

                in_ice_patch = getattr(self.ball, "in_ice_patch", False)
                if in_ice_patch:
                    knockback_multiplier = 2.0""")

with open("src/ai/action.py", "w") as f:
    f.write(new_code)
