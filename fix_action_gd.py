with open("src/ai/action.gd", "r") as f:
    content = f.read()

bad_block = """        if "invert_timer" in self.ball:
        var inv_t = float(self.ball.invert_timer)
        if inv_t > 0:
            inv_t -= delta
            if inv_t < 0: inv_t = 0.0
            self.ball.invert_timer = inv_t
    elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"):
        var inv_t = float(self.ball.get_meta("invert_timer"))
        if inv_t > 0:
            inv_t -= delta
            if inv_t < 0: inv_t = 0.0
            self.ball.set_meta("invert_timer", inv_t)

    if "nemesis_booster_timer" in self.ball:"""

good_block = """        if "invert_timer" in self.ball:
            var inv_t = float(self.ball.invert_timer)
            if inv_t > 0:
                inv_t -= delta
                if inv_t < 0: inv_t = 0.0
                self.ball.invert_timer = inv_t
        elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"):
            var inv_t = float(self.ball.get_meta("invert_timer"))
            if inv_t > 0:
                inv_t -= delta
                if inv_t < 0: inv_t = 0.0
                self.ball.set_meta("invert_timer", inv_t)

        if "nemesis_booster_timer" in self.ball:"""

content = content.replace(bad_block, good_block)

content = content.replace(
"""                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step
                var inv_t = 0.0""",
"""                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step
                var unused_t = 0.0"""
)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
