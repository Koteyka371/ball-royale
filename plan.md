1. **Python Action (`src/ai/action.py`)**
   - Find `elif skill_name == "corpse_explosion":` inside `_use_skill`. Above it, insert `elif skill_name == "bone_wall":`.
     - Code to insert:
       ```python
            elif skill_name == "bone_wall":
                if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                    import random
                    import math
                    enemies = self._get_enemies()
                    target_x = self.ball.x
                    target_y = self.ball.y
                    if enemies:
                        nearest = min(enemies, key=lambda e: (e.x - self.ball.x)**2 + (e.y - self.ball.y)**2)
                        dx = nearest.x - self.ball.x
                        dy = nearest.y - self.ball.y
                        dist = math.hypot(dx, dy)
                        if dist > 0.0001:
                            target_x += (dx / dist) * 60.0
                            target_y += (dy / dist) * 60.0
                    else:
                        target_x += 60.0

                    try:
                        from arena.procedural_arena import Hazard
                    except ImportError:
                        class Hazard:
                            def __init__(self, id, x, y, radius, kind, damage):
                                self.id = id
                                self.x = x
                                self.y = y
                                self.radius = radius
                                self.kind = kind
                                self.damage = damage

                    h_id = 15000 + len(self.world.arena.hazards) + random.randint(0, 1000)
                    wall = Hazard(h_id, target_x, target_y, 40.0, "bone_wall", 0.0)
                    wall.hp = 300.0
                    wall.duration = 10.0
                    wall.active = True
                    self.world.arena.hazards.append(wall)
                self.ball.skill_timer = getattr(self.ball, "skill_cooldown", 8.0)
       ```
   - Find `elif hazard.kind == "breakable_wall":` inside `execute`. Under it or near it, insert `elif hazard.kind == "bone_wall":`:
     - Code to insert:
       ```python
                        elif hazard.kind == "bone_wall":
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
       ```

2. **GDScript Action (`src/ai/action.gd`)**
   - Translate the same logic for `_use_skill` and `execute` hazard handling.

3. **Python Action _attempt_damage (`src/ai/action.py`)**
   - For `bone_wall` blocking line of sight/attacks, find `elif getattr(h, "kind", "") == "orbital_debris":` and change it to `elif getattr(h, "kind", "") in ["orbital_debris", "bone_wall"]:`.
   - Also do the same in `src/ai/action.gd` around `elif h_kind == "orbital_debris":`. Wait, let's verify if `orbital_debris` logic is just checking radius.
   - Wait, if `bone_wall` blocking means line-of-sight is blocked, checking `math.hypot(t_x - hx, t_y - hy) <= hr` means the target is *inside* the wall. If I want it to block projectiles passing *through* it, we could calculate the distance from the hazard center to the line segment between attacker and target. If it's less than `hazard.radius`, it blocks it.
     Wait, I can just do:
     ```python
                    elif getattr(h, "kind", "") in ["orbital_debris", "bone_wall"]:
                        hx = h.x
                        hy = h.y
                        hr = getattr(h, "radius", 40.0)
                        # Point-to-line segment distance
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
                            return
     ```
     This actually makes `orbital_debris` and `bone_wall` properly block line of sight and absorb the attack!
   - I'll apply this line-of-sight intersection to both Python and GDScript.

4. **Testing and Committing**
   - Write tests. Run tests. Update pre-commit. Generate ideas. Submit.
