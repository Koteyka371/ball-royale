import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

replacement = r"""                    elif hazard.kind == "frictionless_zone":
                        if getattr(hazard, "active", True):
                            dx = hazard.x - self.ball.x
                            dy = hazard.y - self.ball.y
                            dist_sq = dx * dx + dy * dy
                            if dist_sq < hazard.radius * hazard.radius:
                                self.ball.is_frictionless = True
                                if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                                    self.ball.x += self.ball.vx * delta
                                    self.ball.y += self.ball.vy * delta
                                self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.001
                    elif hazard.kind == "ice_patches":
                        if getattr(hazard, "active", True):
                            dx = hazard.x - self.ball.x
                            dy = hazard.y - self.ball.y
                            dist_sq = dx * dx + dy * dy
                            if dist_sq < hazard.radius * hazard.radius:
                                self.ball.is_frictionless = True
                                if hasattr(self.ball, "vx") and hasattr(self.ball, "vy"):
                                    self.ball.x += self.ball.vx * delta
                                    self.ball.y += self.ball.vy * delta
                                self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.0"""

content = re.sub(
    r'                    elif hazard\.kind == "frictionless_zone":\n                        if getattr\(hazard, "active", True\):\n                            dx = hazard\.x - self\.ball\.x\n                            dy = hazard\.y - self\.ball\.y\n                            dist_sq = dx \* dx \+ dy \* dy\n                            if dist_sq < hazard\.radius \* hazard\.radius:\n                                self\.ball\.is_frictionless = True\n                                if hasattr\(self\.ball, "vx"\) and hasattr\(self\.ball, "vy"\):\n                                    self\.ball\.x \+= self\.ball\.vx \* delta\n                                    self\.ball\.y \+= self\.ball\.vy \* delta\n                                self\.ball\.speed = getattr\(self\.ball, \'base_speed\', 100\.0\) \* 0\.001',
    replacement,
    content
)

with open("src/ai/action.py", "w") as f:
    f.write(content)
