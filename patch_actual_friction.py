import re
with open("src/ai/action.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""        if in_ice_patch:
            # Zero friction slide
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""",
"""        if in_ice_patch:
            # Zero friction slide
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""")

new_code = new_code.replace(
"""            self.ball.vx = dx / delta
            self.ball.vy = dy / delta

            if hasattr(self.ball, "_reflection_vx"):""",
"""            self.ball.vx = dx / delta
            self.ball.vy = dy / delta

            if getattr(self.ball, "in_ice_patch", False):
                # When in ice patch, we do not want the new position (dx/delta) to override the velocity if they are just sliding
                # Actually, the sliding is self.ball.x += vx * delta. Then old_x to x is exactly vx * delta.
                # BUT when they use a skill or move normally, we override vx.
                # We need to maintain velocity momentum rather than decaying it.
                pass

            if hasattr(self.ball, "_reflection_vx"):""")

with open("src/ai/action.py", "w") as f:
    f.write(new_code)
