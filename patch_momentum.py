import re
with open("src/ai/action.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""        if in_ice_patch:
            # Zero friction slide
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""",
"""        # Wait, if we just want them to slide without friction... the problem is standard movement commands (like chase, attack, idle) normally move the ball towards a target. Then at the end dx/delta becomes vx.
        # So "friction" in a kinematic system is just not storing velocity. To "slide continuously", they should keep moving in the direction of their last velocity instead of fully following the new AI command, or blending them.
        if in_ice_patch:
            # Apply momentum (slide continuously)
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x += self.ball.vx * delta
                self.ball.y += self.ball.vy * delta""")

with open("src/ai/action.py", "w") as f:
    f.write(new_code)

with open("src/ai/action.gd", "r") as f:
    code = f.read()

new_code = code.replace(
"""    if in_ice_patch:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta""",
"""    if in_ice_patch:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta""")

with open("src/ai/action.gd", "w") as f:
    f.write(new_code)
