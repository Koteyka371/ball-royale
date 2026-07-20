import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

# Make sure GDScript also decrements the timer!
pattern = r'''(        if self\.ball\.has_meta\("_wall_knockback_combo_timer"\):
            var wkt = float\(self\.ball\.get_meta\("_wall_knockback_combo_timer"\)\)
            if wkt > 0:
                self\.ball\.set_meta\("_wall_knockback_combo_timer", max\(0\.0, wkt - delta\)\)
                if self\.ball\.get_meta\("_wall_knockback_combo_timer"\) == 0:
                    self\.ball\.set_meta\("_wall_knockback_combo", 0\))'''

replacement = r'''\1

        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("_wall_knockback_combo_timer"):
            var wkt = float(self.ball.get("_wall_knockback_combo_timer", 0.0))
            if wkt > 0.0:
                self.ball["_wall_knockback_combo_timer"] = max(0.0, wkt - delta)

        if typeof(self.ball) == TYPE_OBJECT and "_wall_knockback_combo_timer" in self.ball:
            var wkt = float(self.ball.get("_wall_knockback_combo_timer")) if self.ball.get("_wall_knockback_combo_timer") != null else 0.0
            if wkt > 0.0:
                self.ball.set("_wall_knockback_combo_timer", max(0.0, wkt - delta))'''

content = re.sub(pattern, replacement, content)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
