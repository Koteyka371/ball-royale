import sys
import re

with open('src/ai/action.gd', 'r') as f:
    content = f.read()

# We know the duplicate block starts with `    if self.world != null and "balls" in self.world:` and ends with `                            enemies.append(b)`
block = """
    if self.world != null and "balls" in self.world:
        for b in self.world.balls:
            var is_decoy = false
            if b.has_method("has_meta") and b.has_meta("is_decoy") and b.get_meta("is_decoy"):
                is_decoy = true
            elif typeof(b) == TYPE_DICTIONARY and b.has("is_decoy") and b["is_decoy"]:
                is_decoy = true

            var is_alive = true
            if "alive" in b:
                is_alive = b.alive
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive"):
                is_alive = b["alive"]

            if is_decoy and is_alive:
                var is_enemy = false
                var b_type = null
                var my_type = null

                if "ball_type" in b:
                    b_type = b.ball_type
                elif typeof(b) == TYPE_DICTIONARY and b.has("ball_type"):
                    b_type = b["ball_type"]

                if "ball_type" in self.ball:
                    my_type = self.ball.ball_type
                elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("ball_type"):
                    my_type = self.ball["ball_type"]

                if b_type != null and my_type != null and b_type != my_type:
                    is_enemy = true

                var already_in = false
                for e in enemies:
                    if typeof(e) == typeof(b):
                        if typeof(e) == TYPE_DICTIONARY and e.has("id") and b.has("id") and e.id == b.id:
                            already_in = true
                            break
                        elif typeof(e) == TYPE_OBJECT and e == b:
                            already_in = true
                            break

                if is_enemy and not already_in:
                    var bx = null
                    var by = null
                    if "x" in b and "y" in b:
                        bx = b.x
                        by = b.y
                    elif typeof(b) == TYPE_DICTIONARY:
                        if b.has("x"): bx = b["x"]
                        if b.has("y"): by = b["y"]

                    if bx != null and by != null:
                        var dx = bx - self.ball.x
                        var dy = by - self.ball.y
                        if dx*dx + dy*dy <= perception_radius*perception_radius:
                            enemies.append(b)"""

# Clean all duplicates
pattern = re.escape(block) + r'(\n*' + re.escape(block) + r')+'
content = re.sub(pattern, block, content)

with open('src/ai/action.gd', 'w') as f:
    f.write(content)
