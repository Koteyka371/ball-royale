with open("src/ai/action.py", "r") as f:
    content = f.read()

execute_suspend_patch = """
        if hasattr(self.ball, "suspended_projectiles"):
            gm = getattr(self.world, "game_mode", None)
            cx = 500.0
            cy = 500.0
            if gm and getattr(gm, "name", "") == "Physics Anomaly Event":
                cx = getattr(gm, "cx", 500.0)
                cy = getattr(gm, "cy", 500.0)

            for sp in list(self.ball.suspended_projectiles):
                sp["timer"] -= delta
                if sp.get("is_anomaly", False):
                    import math
                    sp["x"] += sp.get("vx", 0.0) * delta
                    sp["y"] += sp.get("vy", 0.0) * delta

                    dx = cx - sp["x"]
                    dy = cy - sp["y"]
                    dist = math.hypot(dx, dy)
                    if dist > 0.01:
                        ndx = dx / dist
                        ndy = dy / dist
                        tx = -ndy
                        ty = ndx
                        force_mag = 400.0 * delta
                        sp["vx"] += tx * force_mag
                        sp["vy"] += ty * force_mag

                        target = sp["target"]
                        tdx = getattr(target, 'x', 0.0) - sp["x"]
                        tdy = getattr(target, 'y', 0.0) - sp["y"]
                        tdist = math.hypot(tdx, tdy)
                        t_rad = getattr(target, 'radius', 10.0)

                        if tdist <= (t_rad + 20.0):
                            self.ball.suspended_projectiles.remove(sp)
                            if getattr(target, "alive", True) or getattr(target, "hp", 0) > 0:
                                self.ball._is_resuming_projectile = True
                                self._attempt_damage(self.ball, target)
                                self.ball._is_resuming_projectile = False
                            continue

                if sp["timer"] <= 0:
                    if sp in self.ball.suspended_projectiles:
                        self.ball.suspended_projectiles.remove(sp)
                    if not sp.get("is_anomaly", False):
                        if getattr(sp["target"], "alive", True) or getattr(sp["target"], "hp", 0) > 0:
                            self.ball._is_resuming_projectile = True
                            self._attempt_damage(self.ball, sp["target"])
                            self.ball._is_resuming_projectile = False
"""

old_suspend_logic = """
        if hasattr(self.ball, "suspended_projectiles"):
            for sp in list(self.ball.suspended_projectiles):
                sp["timer"] -= delta
                if sp["timer"] <= 0:
                    self.ball.suspended_projectiles.remove(sp)
                    # Resumed projectile hits target if target is alive
                    if getattr(sp["target"], "alive", True) or getattr(sp["target"], "hp", 0) > 0:
                        self.ball._is_resuming_projectile = True
                        self._attempt_damage(self.ball, sp["target"])
                        self.ball._is_resuming_projectile = False
"""
content = content.replace(old_suspend_logic.strip(), execute_suspend_patch.strip())

with open("src/ai/action.py", "w") as f:
    f.write(content)
