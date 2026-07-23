import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

trigger_code = """
                elif hazard.kind == "shockwave_mine":
                    var owner_id = null
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("owner_id"): owner_id = hazard.get_meta("owner_id")
                    elif "owner_id" in hazard: owner_id = hazard.owner_id

                    var my_id = null
                    if "id" in self.ball: my_id = self.ball.id
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): my_id = self.ball["id"]
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

                    if owner_id != my_id:
                        var hx = 0.0
                        var hy = 0.0
                        if "x" in hazard: hx = hazard.x
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("x"): hx = hazard["x"]
                        if "y" in hazard: hy = hazard.y
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("y"): hy = hazard["y"]

                        var rad = 60.0
                        if "radius" in hazard: rad = hazard.radius
                        elif hazard.has_method("get_meta") and hazard.has_meta("radius"): rad = hazard.get_meta("radius")

                        var b_rad = 10.0
                        if "radius" in self.ball: b_rad = self.ball.radius
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("radius"): b_rad = self.ball.get_meta("radius")

                        var dist_sq = pow(hx - self.ball.x, 2) + pow(hy - self.ball.y, 2)
                        if dist_sq < pow(rad + b_rad, 2):
                            if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("duration", 0.0)
                            elif "duration" in hazard: hazard.duration = 0.0

                            if world != null and "events" in world:
                                world.events.append({'type': 'visual_effect', 'data': {'type': 'explosion', 'x': hx, 'y': hy, 'radius': 250.0, 'damage': 5.0}})

                            if world != null and "balls" in world:
                                for b in world.balls:
                                    var b_alive = true
                                    if "alive" in b: b_alive = b.alive
                                    elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]

                                    var b_id = null
                                    if "id" in b: b_id = b.id
                                    elif typeof(b) == TYPE_DICTIONARY and b.has("id"): b_id = b["id"]
                                    elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("id"): b_id = b.get_meta("id")

                                    if b_alive and b_id != owner_id:
                                        var bx = 0.0
                                        var by = 0.0
                                        if "x" in b: bx = b.x
                                        elif typeof(b) == TYPE_DICTIONARY and b.has("x"): bx = b["x"]
                                        if "y" in b: by = b.y
                                        elif typeof(b) == TYPE_DICTIONARY and b.has("y"): by = b["y"]

                                        var b_dist_sq = pow(hx - bx, 2) + pow(hy - by, 2)
                                        if b_dist_sq <= pow(250.0, 2):
                                            var b_dist = sqrt(b_dist_sq)
                                            if b_dist > 0:
                                                var nx = (bx - hx) / b_dist
                                                var ny = (by - hy) / b_dist
                                                if "vx" in b: b.vx += nx * 2000.0
                                                elif typeof(b) == TYPE_DICTIONARY and b.has("vx"): b["vx"] += nx * 2000.0
                                                if "vy" in b: b.vy += ny * 2000.0
                                                elif typeof(b) == TYPE_DICTIONARY and b.has("vy"): b["vy"] += ny * 2000.0

                                            var b_hp = 1.0
                                            if "hp" in b: b_hp = b.hp
                                            elif typeof(b) == TYPE_DICTIONARY and b.has("hp"): b_hp = b["hp"]
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("hp"): b_hp = b.get_meta("hp")

                                            b_hp -= 5.0

                                            if "hp" in b: b.hp = b_hp
                                            elif typeof(b) == TYPE_DICTIONARY and b.has("hp"): b["hp"] = b_hp
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("hp", b_hp)

                                            var b_anchor = 0.0
                                            if "anchor_trap_timer" in b: b_anchor = b.anchor_trap_timer
                                            elif typeof(b) == TYPE_DICTIONARY and b.has("anchor_trap_timer"): b_anchor = b["anchor_trap_timer"]
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("anchor_trap_timer"): b_anchor = b.get_meta("anchor_trap_timer")

                                            b_anchor = max(b_anchor, 1.5)

                                            if "anchor_trap_timer" in b: b.anchor_trap_timer = b_anchor
                                            elif typeof(b) == TYPE_DICTIONARY and b.has("anchor_trap_timer"): b["anchor_trap_timer"] = b_anchor
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("anchor_trap_timer", b_anchor)
"""

text = re.sub(r'\s+elif hazard\.kind == "ethereal_trap":', trigger_code + "\n                elif hazard.kind == \"ethereal_trap\":", text, count=1, flags=re.DOTALL)

with open("src/ai/action.gd", "w") as f:
    f.write(text)
