import re

with open("src/ai/action.py", "r") as f:
    text = f.read()

trigger_code = """
                if getattr(hazard, "kind", "") == "shockwave_mine":
                    if getattr(hazard, "owner_id", None) != getattr(self.ball, "id", None):
                        dist_sq = (hazard.x - self.ball.x)**2 + (hazard.y - self.ball.y)**2
                        if dist_sq < (getattr(hazard, "radius", 60.0) + getattr(self.ball, "radius", 10.0))**2:
                            hazard.duration = 0.0 # Destroy trap
                            if hasattr(self.world, "events"):
                                self.world.events.append({'type': 'visual_effect', 'data': {'type': 'explosion', 'x': hazard.x, 'y': hazard.y, 'radius': 250.0, 'damage': 5.0}})

                            if hasattr(self.world, "balls"):
                                import math
                                for b in self.world.balls:
                                    if getattr(b, "alive", True) and getattr(b, "id", None) != getattr(hazard, "owner_id", None):
                                        b_dist_sq = (hazard.x - b.x)**2 + (hazard.y - b.y)**2
                                        if b_dist_sq <= 250.0**2:
                                            b_dist = math.sqrt(b_dist_sq)
                                            if b_dist > 0:
                                                nx = (b.x - hazard.x) / b_dist
                                                ny = (b.y - hazard.y) / b_dist
                                                b.vx = getattr(b, "vx", 0.0) + nx * 2000.0
                                                b.vy = getattr(b, "vy", 0.0) + ny * 2000.0

                                            # Deal 5.0 damage
                                            if hasattr(b, "hp"):
                                                b.hp -= 5.0

                                            # Disable movement abilities
                                            b.anchor_trap_timer = max(getattr(b, "anchor_trap_timer", 0.0), 1.5)

                if getattr(hazard, "kind", "") == "ethereal_trap":
"""

text = re.sub(r'\s+if getattr\(hazard, "kind", ""\) == "ethereal_trap":', trigger_code, text, count=1, flags=re.DOTALL)

with open("src/ai/action.py", "w") as f:
    f.write(text)
