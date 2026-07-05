import re
with open("src/ai/action.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""        elif strategy in ("use_skill", "use skill", "action_skill", "Действие"):
            if getattr(self.ball, "skill", "") == "flank":
                self.ball.current_action = "flank"
                self._flank(delta)
            else:
                self._use_skill()
        else:
            self._idle(delta)""",
"""        elif strategy in ("use_skill", "use skill", "action_skill", "Действие"):
            if getattr(self.ball, "skill", "") == "flank":
                self.ball.current_action = "flank"
                self._flank(delta)
            else:
                self._use_skill()
        else:
            self._idle(delta)

        if getattr(self.ball, "in_ice_patch", False):
            # Apply momentum and override AI steering with slide
            if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                self.ball.x = old_x + self.ball.vx * delta
                self.ball.y = old_y + self.ball.vy * delta""")

with open("src/ai/action.py", "w") as f:
    f.write(new_code)
