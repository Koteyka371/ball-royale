import re

file_path = "src/ai/action.py"
with open(file_path, "r") as f:
    content = f.read()

deploy_logic = """        if strategy in ("flee", "defend", "attack") and hasattr(self.ball, "inventory") and "deployable_mud_puddle" in self.ball.inventory:
            nearest = self._get_nearest_enemy()
            if nearest:
                dist = math.hypot(self.ball.x - nearest.x, self.ball.y - nearest.y)
                if dist < 300:
                    self.ball.inventory.remove("deployable_mud_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        try:
                            from arena.procedural_arena import Hazard
                            mud_id = f"{len(self.world.arena.hazards)}_{self.world.tick}_mud"
                            puddle = Hazard(mud_id, self.ball.x, self.ball.y, 60.0, "sticky_mud_puddle", 0.0)
                            puddle.duration = 10.0
                            setattr(puddle, 'owner_id', getattr(self.ball, 'id', None))
                            self.world.arena.hazards.append(puddle)
                        except ImportError:
                            pass"""

new_deploy_logic = deploy_logic + """

        if strategy in ("flee", "defend", "attack") and hasattr(self.ball, "inventory") and "deployable_proximity_mud_puddle" in self.ball.inventory:
            nearest = self._get_nearest_enemy()
            if nearest:
                dist = math.hypot(self.ball.x - nearest.x, self.ball.y - nearest.y)
                if dist < 300:
                    self.ball.inventory.remove("deployable_proximity_mud_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        try:
                            from arena.procedural_arena import Hazard
                            mud_id = f"{len(self.world.arena.hazards)}_{getattr(self.world, 'tick', 0)}_proxmud"
                            # Spawns with 60 radius but proximity logic triggers on 30.
                            puddle = Hazard(mud_id, self.ball.x, self.ball.y, 60.0, "proximity_mud_puddle", 0.0)
                            puddle.duration = 30.0 # Stays active longer
                            setattr(puddle, 'owner_id', getattr(self.ball, 'id', None))
                            self.world.arena.hazards.append(puddle)
                        except ImportError:
                            pass"""

content = content.replace(deploy_logic, new_deploy_logic)

with open(file_path, "w") as f:
    f.write(content)
