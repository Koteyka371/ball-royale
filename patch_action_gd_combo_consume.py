import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

pattern = r'''(                    var wkt = 0\.0
                    if typeof\(self\.ball\) == TYPE_DICTIONARY:
                        wkt = float\(self\.ball\.get\("_wall_knockback_combo_timer", 0\.0\)\)
                    elif typeof\(self\.ball\) == TYPE_OBJECT and "_wall_knockback_combo_timer" in self\.ball:
                        wkt = float\(self\.ball\.get\("_wall_knockback_combo_timer"\)\) if self\.ball\.get\("_wall_knockback_combo_timer"\) != null else 0\.0
                    elif typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("get_meta"\) and self\.ball\.has_meta\("_wall_knockback_combo_timer"\):
                        wkt = float\(self\.ball\.get_meta\("_wall_knockback_combo_timer"\)\)

                    if wkt > 0\.0:
                        var combo = 0
                        if typeof\(self\.ball\) == TYPE_DICTIONARY:
                            combo = self\.ball\.get\("_wall_knockback_combo", 0\)
                        elif typeof\(self\.ball\) == TYPE_OBJECT and "_wall_knockback_combo" in self\.ball:
                            combo = self\.ball\.get\("_wall_knockback_combo"\) if self\.ball\.get\("_wall_knockback_combo"\) != null else 0
                        elif typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("get_meta"\):
                            combo = self\.ball\.get_meta\("_wall_knockback_combo"\) if self\.ball\.has_meta\("_wall_knockback_combo"\) else 0

                        var combo_dmg_mult = 1\.0 \+ \(float\(combo\) \* 1\.0\)

                        var base_dmg = 10\.0
                        if typeof\(self\.ball\) == TYPE_DICTIONARY and self\.ball\.has\("damage"\): base_dmg = float\(self\.ball\["damage"\]\)
                        elif typeof\(self\.ball\) == TYPE_OBJECT and "damage" in self\.ball: base_dmg = float\(self\.ball\.damage\)

                        var bonus_dmg = base_dmg \* combo_dmg_mult

                        if typeof\(other\) == TYPE_OBJECT and other\.has_method\("take_damage"\):
                            other\.take_damage\(bonus_dmg\)
                        elif typeof\(other\) == TYPE_DICTIONARY and other\.has\("hp"\):
                            other\["hp"\] -= bonus_dmg
                        elif typeof\(other\) == TYPE_OBJECT and "hp" in other:
                            other\.hp -= bonus_dmg

                        if typeof\(other\) == TYPE_DICTIONARY:
                            if other\.has\("vx"\): other\["vx"\] -= nx \* 500\.0 \* combo_dmg_mult
                            if other\.has\("vy"\): other\["vy"\] -= ny \* 500\.0 \* combo_dmg_mult
                        elif typeof\(other\) == TYPE_OBJECT:
                            if "vx" in other: other\.vx -= nx \* 500\.0 \* combo_dmg_mult
                            if "vy" in other: other\.vy -= ny \* 500\.0 \* combo_dmg_mult

                        if typeof\(self\.ball\) == TYPE_DICTIONARY:
                            self\.ball\["_wall_knockback_combo"\] = 0
                            self\.ball\["_wall_knockback_combo_timer"\] = 0\.0
                        elif typeof\(self\.ball\) == TYPE_OBJECT and "_wall_knockback_combo" in self\.ball:
                            self\.ball\.set\("_wall_knockback_combo", 0\)
                            self\.ball\.set\("_wall_knockback_combo_timer", 0\.0\)
                        elif typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("set_meta"\):
                            self\.ball\.set_meta\("_wall_knockback_combo", 0\)
                            self\.ball\.set_meta\("_wall_knockback_combo_timer", 0\.0\)

                        if self\.world != null and self\.world\.has_method\("add_event"\):
                            self\.world\.add_event\("explosion", \{"x": other\.x, "y": other\.y, "radius": 100\.0, "damage": 0\.0\}\))'''

replacement = r'''                    var wkt = 0.0
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        wkt = float(self.ball.get("_wall_knockback_combo_timer", 0.0))
                    elif typeof(self.ball) == TYPE_OBJECT and "_wall_knockback_combo_timer" in self.ball:
                        wkt = float(self.ball.get("_wall_knockback_combo_timer")) if self.ball.get("_wall_knockback_combo_timer") != null else 0.0
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("_wall_knockback_combo_timer"):
                        wkt = float(self.ball.get_meta("_wall_knockback_combo_timer"))

                    if wkt > 0.0:
                        var combo_dmg_mult = 2.0

                        var base_dmg = 10.0
                        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("damage"): base_dmg = float(self.ball["damage"])
                        elif typeof(self.ball) == TYPE_OBJECT and "damage" in self.ball: base_dmg = float(self.ball.damage)

                        var bonus_dmg = base_dmg * combo_dmg_mult

                        if typeof(other) == TYPE_OBJECT and other.has_method("take_damage"):
                            other.take_damage(bonus_dmg)
                        elif typeof(other) == TYPE_DICTIONARY and other.has("hp"):
                            other["hp"] -= bonus_dmg
                        elif typeof(other) == TYPE_OBJECT and "hp" in other:
                            other.hp -= bonus_dmg

                        if typeof(other) == TYPE_DICTIONARY:
                            if other.has("vx"): other["vx"] -= nx * 500.0 * combo_dmg_mult
                            if other.has("vy"): other["vy"] -= ny * 500.0 * combo_dmg_mult
                        elif typeof(other) == TYPE_OBJECT:
                            if "vx" in other: other.vx -= nx * 500.0 * combo_dmg_mult
                            if "vy" in other: other.vy -= ny * 500.0 * combo_dmg_mult

                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_wall_knockback_combo"] = 0
                            self.ball["_wall_knockback_combo_timer"] = 0.0
                        elif typeof(self.ball) == TYPE_OBJECT and "_wall_knockback_combo" in self.ball:
                            self.ball.set("_wall_knockback_combo", 0)
                            self.ball.set("_wall_knockback_combo_timer", 0.0)
                        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                            self.ball.set_meta("_wall_knockback_combo", 0)
                            self.ball.set_meta("_wall_knockback_combo_timer", 0.0)

                        if self.world != null and self.world.has_method("add_event"):
                            self.world.add_event("explosion", {"x": other.x, "y": other.y, "radius": 100.0, "damage": 0.0})'''

content = re.sub(pattern, replacement, content)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
