import re

def apply_patch():
    # 1. Decrement pinball_projectile_timer in action.py
    with open("src/ai/action.py", "r") as f:
        content = f.read()

    target_py = """        if hasattr(self.ball, "pull_booster_timer") and self.ball.pull_booster_timer > 0:"""
    replacement_py = """        if hasattr(self.ball, "pinball_projectile_timer") and self.ball.pinball_projectile_timer > 0:
            self.ball.pinball_projectile_timer -= delta
            if self.ball.pinball_projectile_timer < 0:
                self.ball.pinball_projectile_timer = 0.0

        if hasattr(self.ball, "pull_booster_timer") and self.ball.pull_booster_timer > 0:"""
    if target_py in content:
        content = content.replace(target_py, replacement_py)
        print("Patched timer decrement in action.py")

    with open("src/ai/action.py", "w") as f:
        f.write(content)

    # 2. Decrement timer in action.gd
    with open("src/ai/action.gd", "r") as f:
        content_gd = f.read()

    target_gd = """        var pbt = 0.0
        if "pull_booster_timer" in self.ball: pbt = self.ball.pull_booster_timer
        elif self.ball.has_method("has_meta") and self.ball.has_meta("pull_booster_timer"): pbt = self.ball.get_meta("pull_booster_timer")"""

    replacement_gd = """        var ppb = 0.0
        if "pinball_projectile_timer" in self.ball: ppb = self.ball.pinball_projectile_timer
        elif self.ball.has_method("has_meta") and self.ball.has_meta("pinball_projectile_timer"): ppb = self.ball.get_meta("pinball_projectile_timer")
        if ppb > 0:
            ppb -= delta
            if ppb < 0: ppb = 0.0
            if "pinball_projectile_timer" in self.ball: self.ball.pinball_projectile_timer = ppb
            elif self.ball.has_method("set_meta"): self.ball.set_meta("pinball_projectile_timer", ppb)

        var pbt = 0.0
        if "pull_booster_timer" in self.ball: pbt = self.ball.pull_booster_timer
        elif self.ball.has_method("has_meta") and self.ball.has_meta("pull_booster_timer"): pbt = self.ball.get_meta("pull_booster_timer")"""

    if target_gd in content_gd:
        content_gd = content_gd.replace(target_gd, replacement_gd)
        print("Patched timer decrement in action.gd")

    # 3. Add projectile bounce check to action.gd equivalent to action.py lines 9355-9366
    # Where does `bounced_wall` happen in action.gd?
    with open("src/ai/action.gd", "w") as f:
        f.write(content_gd)

apply_patch()
