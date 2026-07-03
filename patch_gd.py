with open("src/ai/action.gd", "r") as f:
    code = f.read()

code = code.replace("""                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            var nx = dx / dist
                            var ny = dy / dist
                            var min_dist = 10.0
                            if dist > min_dist:
                                min_dist = dist
                            var pull_strength = (hazard.radius * 2.0 / min_dist) * 50.0 * delta
                            self.ball.x += nx * pull_strength
                            self.ball.y += ny * pull_strength""",
"""                        var anchor_timer = 0.0
                        if "anchor_booster_timer" in self.ball:
                            anchor_timer = float(self.ball.anchor_booster_timer)
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("anchor_booster_timer"):
                            anchor_timer = float(self.ball.get_meta("anchor_booster_timer"))

                        if anchor_timer <= 0.0:
                            if dist_sq > 0.0001:
                                var dist = sqrt(dist_sq)
                                var nx = dx / dist
                                var ny = dy / dist
                                var min_dist = 10.0
                                if dist > min_dist:
                                    min_dist = dist
                                var pull_strength = (hazard.radius * 2.0 / min_dist) * 50.0 * delta
                                if pull_strength > dist * 0.5:
                                    pull_strength = dist * 0.5
                                if typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["x"] += nx * pull_strength
                                    self.ball["y"] += ny * pull_strength
                                else:
                                    self.ball.x += nx * pull_strength
                                    self.ball.y += ny * pull_strength""")

with open("src/ai/action.gd", "w") as f:
    f.write(code)
