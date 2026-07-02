with open("src/ai/action.py", "r") as f:
    content = f.read()
import re
old = """                    elif hazard.kind == "shrinking_zone":
                        dx = hazard.x - self.ball.x
                        dy = hazard.y - self.ball.y
                        dist = math.hypot(dx, dy)
                        # We apply damage if ball is OUTSIDE the shrinking zone
                        if dist > hazard.radius:
                            if getattr(self.ball, "hp", 0) > 0:
                                if hasattr(self.ball, "take_damage"):
                                    self.ball.take_damage(getattr(hazard, "damage", 15.0) * delta, "shrinking_zone")
                                else:
                                    self.ball.hp -= getattr(hazard, "damage", 15.0) * delta
                                if self.ball.hp <= 0:
                                    self.ball.alive = False
                                    self.ball.killer = "shrinking_zone\""""
new = """                    elif hazard.kind == "shrinking_zone":
                        dx = hazard.x - self.ball.x
                        dy = hazard.y - self.ball.y
                        dist = (dx**2 + dy**2)**0.5
                        # We apply damage if ball is OUTSIDE the shrinking zone
                        if dist > hazard.radius:
                            if getattr(self.ball, "hp", 0) > 0:
                                if hasattr(self.ball, "take_damage"):
                                    self.ball.take_damage(getattr(hazard, "damage", 15.0) * delta, "shrinking_zone")
                                else:
                                    self.ball.hp -= getattr(hazard, "damage", 15.0) * delta
                                if self.ball.hp <= 0:
                                    self.ball.alive = False
                                    self.ball.killer = "shrinking_zone\""""
content = content.replace(old, new)
with open("src/ai/action.py", "w") as f:
    f.write(content)
