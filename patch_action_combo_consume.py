import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

pattern = r'''(                    wkt = getattr\(self\.ball, "_wall_knockback_combo_timer", 0\.0\)
                    if wkt > 0:
                        combo = getattr\(self\.ball, "_wall_knockback_combo", 0\)
                        combo_dmg_mult = 1\.0 \+ \(combo \* 1\.0\) # Double damage \(actually, combo=1 -> 2\.0x, combo=2 -> 3\.0x etc\.\)

                        # Apply bonus damage
                        bonus_dmg = getattr\(self\.ball, "damage", 10\.0\) \* combo_dmg_mult
                        if hasattr\(other, "hp"\):
                            other\.hp -= bonus_dmg
                        elif hasattr\(other, "take_damage"\):
                            other\.take_damage\(bonus_dmg\)

                        # Apply bonus knockback
                        if hasattr\(other, "vx"\):
                            other\.vx -= nx \* 500\.0 \* combo_dmg_mult
                        if hasattr\(other, "vy"\):
                            other\.vy -= ny \* 500\.0 \* combo_dmg_mult

                        # Consume combo
                        self\.ball\._wall_knockback_combo = 0
                        self\.ball\._wall_knockback_combo_timer = 0\.0

                        # Add a ripple effect
                        if hasattr\(self\.world, "add_event"\):
                            self\.world\.add_event\("explosion", \{"x": other\.x, "y": other\.y, "radius": 100\.0, "damage": 0\.0\}\))'''

replacement = r'''                    wkt = getattr(self.ball, "_wall_knockback_combo_timer", 0.0)
                    if wkt > 0:
                        # Double damage and knockback on collision immediately after a wall bounce
                        combo_dmg_mult = 2.0

                        # Apply bonus damage
                        bonus_dmg = getattr(self.ball, "damage", 10.0) * combo_dmg_mult
                        if hasattr(other, "hp"):
                            other.hp -= bonus_dmg
                        elif hasattr(other, "take_damage"):
                            other.take_damage(bonus_dmg)

                        # Apply bonus knockback
                        if hasattr(other, "vx"):
                            other.vx -= nx * 500.0 * combo_dmg_mult
                        if hasattr(other, "vy"):
                            other.vy -= ny * 500.0 * combo_dmg_mult

                        # Consume combo
                        self.ball._wall_knockback_combo_timer = 0.0
                        self.ball._wall_knockback_combo = 0

                        # Add a ripple effect
                        if hasattr(self.world, "add_event"):
                            self.world.add_event("explosion", {"x": other.x, "y": other.y, "radius": 100.0, "damage": 0.0})'''

content = re.sub(pattern, replacement, content)

with open("src/ai/action.py", "w") as f:
    f.write(content)
