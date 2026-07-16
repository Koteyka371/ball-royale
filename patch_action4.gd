import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

# Fix the Dictionary issue in action.gd
search_str = """    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()

    if bounced_wall:
        if not (self.ball.has_meta("wall_stick_timer") and self.ball.get_meta("wall_stick_timer") > 0.0):
            self.ball.set_meta("wall_stick_timer", 2.0)
            self.ball.set("is_stunned", true)"""

replace_str = """    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()

    if bounced_wall:
        if typeof(self.ball) == TYPE_DICTIONARY:
            if not (self.ball.has("wall_stick_timer") and self.ball["wall_stick_timer"] > 0.0):
                self.ball["wall_stick_timer"] = 2.0
                self.ball["is_stunned"] = true
        elif "wall_stick_timer" in self.ball:
            if not self.ball.wall_stick_timer > 0.0:
                self.ball.wall_stick_timer = 2.0
                if "is_stunned" in self.ball: self.ball.is_stunned = true
                elif self.ball.has_method("set_meta"): self.ball.set_meta("is_stunned", true)
        elif self.ball.has_method("set_meta"):
            if not (self.ball.has_meta("wall_stick_timer") and self.ball.get_meta("wall_stick_timer") > 0.0):
                self.ball.set_meta("wall_stick_timer", 2.0)
                self.ball.set_meta("is_stunned", true)"""

if search_str in content:
    content = content.replace(search_str, replace_str)
    print("Action.gd patch 4 applied!")
else:
    print("Search string not found in action.gd")

with open("src/ai/action.gd", "w") as f:
    f.write(content)
