with open("src/ai/action.py", "r") as f:
    content = f.read()

import re

search1 = r"""            elif skill_name == "corpse_explosion":"""
replace1 = r"""            elif skill_name == "bone_wall":
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
            elif skill_name == "corpse_explosion":"""

content = content.replace(search1, replace1)

with open("src/ai/action.py", "w") as f:
    f.write(content)
