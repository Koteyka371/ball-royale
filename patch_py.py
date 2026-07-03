with open("src/ai/action.py", "r") as f:
    code = f.read()

code = code.replace("""                            if dist_sq > 0.0001 and getattr(self.ball, "anchor_booster_timer", 0.0) <= 0:
                                dist = math.sqrt(dist_sq)
                                nx, ny = dx / dist, dy / dist
                                pull_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta
                                pull_strength = min(pull_strength, dist * 0.5) # Prevent overshooting
                                self.ball.x += nx * pull_strength
                                self.ball.y += ny * pull_strength""",
"""                            if getattr(self.ball, "anchor_booster_timer", 0.0) <= 0:
                                if dist_sq > 0.0001:
                                    dist = math.sqrt(dist_sq)
                                    nx, ny = dx / dist, dy / dist
                                    pull_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta
                                    pull_strength = min(pull_strength, dist * 0.5) # Prevent overshooting
                                    self.ball.x += nx * pull_strength
                                    self.ball.y += ny * pull_strength""")

with open("src/ai/action.py", "w") as f:
    f.write(code)
