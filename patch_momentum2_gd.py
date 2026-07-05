import re
with open("src/ai/action.gd", "r") as f:
    code = f.read()

new_code = code.replace(
"""        else:
            _use_skill()
    else:
        _idle(delta)""",
"""        else:
            _use_skill()
    else:
        _idle(delta)

    var in_ice_patch2 = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("in_ice_patch"):
        in_ice_patch2 = self.ball.get_meta("in_ice_patch")
    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("in_ice_patch"):
        in_ice_patch2 = self.ball["in_ice_patch"]

    if in_ice_patch2:
        var bvx = 0.0
        var bvy = 0.0
        if "vx" in self.ball: bvx = self.ball.vx
        elif self.ball.has_method("get_meta") and self.ball.has_meta("vx"): bvx = self.ball.get_meta("vx")
        if "vy" in self.ball: bvy = self.ball.vy
        elif self.ball.has_method("get_meta") and self.ball.has_meta("vy"): bvy = self.ball.get_meta("vy")

        self.ball.x = old_x + bvx * delta
        self.ball.y = old_y + bvy * delta""")

with open("src/ai/action.gd", "w") as f:
    f.write(new_code)
