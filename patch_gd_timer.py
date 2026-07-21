def apply_patch():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()

    target_gd = """    var pull_timer = 0.0
    if "pull_booster_timer" in self.ball:"""

    replacement_gd = """    var pinball_timer = 0.0
    if "pinball_projectile_timer" in self.ball:
        pinball_timer = float(self.ball.pinball_projectile_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("pinball_projectile_timer"):
        pinball_timer = self.ball.get_meta("pinball_projectile_timer")
    if pinball_timer > 0:
        pinball_timer -= delta
        if pinball_timer < 0: pinball_timer = 0.0
        if "pinball_projectile_timer" in self.ball:
            self.ball.pinball_projectile_timer = pinball_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("pinball_projectile_timer", pinball_timer)

    var pull_timer = 0.0
    if "pull_booster_timer" in self.ball:"""

    if target_gd in content:
        content = content.replace(target_gd, replacement_gd)
        print("Patched timer decrement in action.gd")
    else:
        print("Not found")

    with open("src/ai/action.gd", "w") as f:
        f.write(content)
apply_patch()
