import re

with open('src/ai/action.gd', 'r') as f:
    content = f.read()

search = """        if "speed_multiplier" in self.ball:
            self.ball.speed_multiplier = max(float(self.ball.speed_multiplier), 1.5)
        elif self.ball.has_method("set_meta") and self.ball.has_meta("speed_multiplier"):
            self.ball.set_meta("speed_multiplier", max(float(self.ball.get_meta("speed_multiplier")), 1.5))"""

replace = """        var shadow_speed_applied = false
        if "shadow_speed_applied" in self.ball:
            shadow_speed_applied = self.ball.shadow_speed_applied
        elif self.ball.has_method("get_meta") and self.ball.has_meta("shadow_speed_applied"):
            shadow_speed_applied = self.ball.get_meta("shadow_speed_applied")

        if not shadow_speed_applied:
            if "speed_multiplier" in self.ball:
                self.ball.speed_multiplier = float(self.ball.speed_multiplier) * 1.5
            elif self.ball.has_method("set_meta") and self.ball.has_meta("speed_multiplier"):
                self.ball.set_meta("speed_multiplier", float(self.ball.get_meta("speed_multiplier")) * 1.5)

            if "shadow_speed_applied" in self.ball:
                self.ball.shadow_speed_applied = true
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("shadow_speed_applied", true)"""

if search in content:
    content = content.replace(search, replace)
else:
    print("Could not find search block in action.gd")

search2 = """        if shadow_timer < 0.0:
            shadow_timer = 0.0"""

replace2 = """        if shadow_timer <= 0.0:
            shadow_timer = 0.0
            var shadow_speed_applied = false
            if "shadow_speed_applied" in self.ball:
                shadow_speed_applied = self.ball.shadow_speed_applied
            elif self.ball.has_method("get_meta") and self.ball.has_meta("shadow_speed_applied"):
                shadow_speed_applied = self.ball.get_meta("shadow_speed_applied")

            if shadow_speed_applied:
                if "speed_multiplier" in self.ball:
                    self.ball.speed_multiplier = float(self.ball.speed_multiplier) / 1.5
                elif self.ball.has_method("set_meta") and self.ball.has_meta("speed_multiplier"):
                    self.ball.set_meta("speed_multiplier", float(self.ball.get_meta("speed_multiplier")) / 1.5)

                if "shadow_speed_applied" in self.ball:
                    self.ball.shadow_speed_applied = false
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("shadow_speed_applied", false)"""

if search2 in content:
    content = content.replace(search2, replace2)
else:
    print("Could not find search2 block in action.gd")

with open('src/ai/action.gd', 'w') as f:
    f.write(content)
