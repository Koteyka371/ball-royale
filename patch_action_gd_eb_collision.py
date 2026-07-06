import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

execute_patch = """                    elif hazard.kind == "sweeping_paddle":"""
execute_new = """                    elif hazard.kind == "energy_barrier":
                        var my_team = ""
                        if "team" in self.ball: my_team = self.ball.team
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
                        else: my_team = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()

                        var h_team = ""
                        if hazard.has_meta("team"): h_team = hazard.get_meta("team")

                        if my_team != h_team:
                            var dx = self.ball.x - hazard.x
                            var dy = self.ball.y - hazard.y
                            var dist = sqrt(dx*dx + dy*dy)
                            if dist == 0.0: dist = 0.0001
                            var b_rad = 10.0
                            if "radius" in self.ball: b_rad = float(self.ball.radius)
                            elif self.ball.has_method("has_meta") and self.ball.has_meta("radius"): b_rad = float(self.ball.get_meta("radius"))

                            var h_rad = 40.0
                            if "radius" in hazard: h_rad = float(hazard.radius)
                            elif hazard.has_meta("radius"): h_rad = float(hazard.get_meta("radius"))

                            if dist < (b_rad + h_rad):
                                var overlap = (b_rad + h_rad) - dist
                                var nx = dx / dist
                                var ny = dy / dist

                                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                                    self.ball.set_meta("x", self.ball.get_meta("x") + nx * overlap)
                                    self.ball.set_meta("y", self.ball.get_meta("y") + ny * overlap)
                                else:
                                    self.ball.x += nx * overlap
                                    self.ball.y += ny * overlap

                                var bvx = 0.0
                                if "vx" in self.ball: bvx = float(self.ball.vx)
                                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("vx"): bvx = float(self.ball.get_meta("vx"))

                                var bvy = 0.0
                                if "vy" in self.ball: bvy = float(self.ball.vy)
                                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("vy"): bvy = float(self.ball.get_meta("vy"))

                                var dot = bvx * nx + bvy * ny
                                if dot < 0:
                                    if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                                        self.ball.set_meta("vx", bvx - 2 * dot * nx)
                                        self.ball.set_meta("vy", bvy - 2 * dot * ny)
                                    else:
                                        self.ball.vx = bvx - 2 * dot * nx
                                        self.ball.vy = bvy - 2 * dot * ny
                    elif hazard.kind == "sweeping_paddle":"""
content = content.replace(execute_patch, execute_new)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
