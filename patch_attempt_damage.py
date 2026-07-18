with open("src/ai/action.py", "r") as f:
    content = f.read()

search = """                    if getattr(h, "kind", "") == "orbital_debris":
                        # Debris provides cover from projectiles
                        hx = h.x
                        hy = h.y
                        hr = getattr(h, "radius", 40.0)
                        if math.hypot(t_x - hx, t_y - hy) <= hr:
                            return"""
replace = """                    if getattr(h, "kind", "") in ["orbital_debris", "bone_wall"]:
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

content = content.replace(search, replace)

with open("src/ai/action.py", "w") as f:
    f.write(content)
