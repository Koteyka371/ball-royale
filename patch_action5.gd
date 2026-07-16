import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

# Fix the stun clearing logic in action.gd
search_str = """    if wall_stick:
        var new_ws = ws_timer - delta
        if typeof(self.ball) == TYPE_DICTIONARY:
            self.ball["wall_stick_timer"] = new_ws
            if new_ws <= 0.0: self.ball["is_stunned"] = false
        elif "wall_stick_timer" in self.ball:
            self.ball.wall_stick_timer = new_ws
            if new_ws <= 0.0:
                if "is_stunned" in self.ball: self.ball.is_stunned = false
                elif self.ball.has_method("set_meta"): self.ball.set_meta("is_stunned", false)
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("wall_stick_timer", new_ws)
            if new_ws <= 0.0: self.ball.set_meta("is_stunned", false)"""

replace_str = """    if wall_stick:
        var new_ws = ws_timer - delta
        if typeof(self.ball) == TYPE_DICTIONARY:
            self.ball["wall_stick_timer"] = new_ws
            if new_ws <= 0.0 and (not self.ball.has("stun_timer") or self.ball["stun_timer"] <= 0.0):
                self.ball["is_stunned"] = false
        elif "wall_stick_timer" in self.ball:
            self.ball.wall_stick_timer = new_ws
            if new_ws <= 0.0:
                var st = 0.0
                if "stun_timer" in self.ball: st = self.ball.stun_timer
                elif self.ball.has_method("has_meta") and self.ball.has_meta("stun_timer"): st = self.ball.get_meta("stun_timer")
                if st <= 0.0:
                    if "is_stunned" in self.ball: self.ball.is_stunned = false
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("is_stunned", false)
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("wall_stick_timer", new_ws)
            if new_ws <= 0.0:
                var st = 0.0
                if self.ball.has_meta("stun_timer"): st = self.ball.get_meta("stun_timer")
                if st <= 0.0:
                    self.ball.set_meta("is_stunned", false)"""

if search_str in content:
    content = content.replace(search_str, replace_str)
    print("Action.gd patch 5 applied!")
else:
    print("Search string not found in action.gd")

with open("src/ai/action.gd", "w") as f:
    f.write(content)
