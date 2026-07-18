with open("src/ai/action.py", "r") as f:
    content = f.read()

search2 = r"""                    elif getattr(h, "kind", "") == "orbital_debris":
                        # Debris provides cover from projectiles
                        hx = h.x
                        hy = h.y
                        hr = getattr(h, "radius", 40.0)
                        if math.hypot(t_x - hx, t_y - hy) <= hr:
                            return"""
replace2 = r"""                    elif getattr(h, "kind", "") in ["orbital_debris", "bone_wall"]:
                        hx = h.x
                        hy = h.y
                        hr = getattr(h, "radius", 40.0)
                        l2 = (t_x - a_x)**2 + (t_y - a_y)**2
                        if l2 == 0:
                            dist_to_line = math.hypot(hx - a_x, hy - a_y)
                        else:
                            t = max(0, min(1, ((hx - a_x) * (t_x - a_x) + (hy - a_y) * (t_y - a_y)) / l2))
                            proj_x = a_x + t * (t_x - a_x)
                            proj_y = a_y + t * (t_y - a_y)
                            dist_to_line = math.hypot(hx - proj_x, hy - proj_y)
                        if dist_to_line <= hr:
                            if getattr(h, "kind", "") == "bone_wall" and hasattr(h, "hp"):
                                h.hp -= getattr(attacker, "damage", 10.0)
                                if h.hp <= 0:
                                    h.active = False
                            return"""

content = content.replace(search2, replace2)

search3 = r"""                        elif hazard.kind == "breakable_wall":
                            # Clamp position manually
                            dx = self.ball.x - hazard.x"""
replace3 = r"""                        elif hazard.kind == "bone_wall":
                            dx = self.ball.x - hazard.x
                            dy = self.ball.y - hazard.y
                            import math
                            dist = math.hypot(dx, dy)
                            if dist < (self.ball.radius + hazard.radius) and dist > 0:
                                nx, ny = dx / dist, dy / dist
                                overlap = (self.ball.radius + hazard.radius) - dist
                                is_projectile = getattr(self.ball, "ball_type", "") in ["projectile", "spell"] or getattr(self.ball, "is_projectile", False)
                                if is_projectile:
                                    self.ball.alive = False
                                    self.ball.hp = 0
                                    if hasattr(hazard, "hp"):
                                        hazard.hp -= getattr(self.ball, "damage", 10.0)
                                        if hazard.hp <= 0:
                                            hazard.active = False
                                else:
                                    self.ball.x += nx * overlap
                                    self.ball.y += ny * overlap
                                    if hasattr(hazard, "hp"):
                                        hazard.hp -= getattr(self.ball, "damage", 10.0) * delta * 5.0
                                        if hazard.hp <= 0:
                                            hazard.active = False
                            continue
                        elif hazard.kind == "breakable_wall":
                            # Clamp position manually
                            dx = self.ball.x - hazard.x"""

content = content.replace(search3, replace3)

with open("src/ai/action.py", "w") as f:
    f.write(content)
