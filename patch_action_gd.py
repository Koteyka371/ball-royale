import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

replacement = r"""                elif hazard.kind == "frictionless_zone":
                    var active = true
                    if hazard.has_method("get_meta") and hazard.has_meta("active"):
                        active = hazard.get_meta("active")
                    elif "active" in hazard:
                        active = hazard.active
                    if active:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq < hazard.radius * hazard.radius:
                            if "vx" in self.ball and "vy" in self.ball:
                                self.ball.x += self.ball.vx * delta
                                self.ball.y += self.ball.vy * delta
                            var base_s = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_s = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_s = self.ball.base_speed
                            self.ball.speed = base_s * 0.001
                            if typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["is_frictionless"] = true
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("is_frictionless", true)
                elif hazard.kind == "ice_patches":
                    var active = true
                    if hazard.has_method("get_meta") and hazard.has_meta("active"):
                        active = hazard.get_meta("active")
                    elif "active" in hazard:
                        active = hazard.active
                    if active:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq < hazard.radius * hazard.radius:
                            if "vx" in self.ball and "vy" in self.ball:
                                self.ball.x += self.ball.vx * delta
                                self.ball.y += self.ball.vy * delta
                            var base_s = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_s = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_s = self.ball.base_speed
                            self.ball.speed = base_s * 0.0
                            if typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["is_frictionless"] = true
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("is_frictionless", true)"""

# Instead of using sub, which might fail due to the complexity, I'll just use string replacement
start_idx = content.find('                elif hazard.kind == "frictionless_zone":')
end_idx = content.find('                elif hazard.kind == "fire_zone":', start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + replacement + "\n" + content[end_idx:]

with open("src/ai/action.gd", "w") as f:
    f.write(content)
