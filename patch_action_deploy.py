import re

with open("src/ai/action.py", "r") as f:
    text = f.read()

deploy_code = """
        if strategy in ("flee", "defend", "attack") and hasattr(self.ball, "inventory") and "deployable_acid_puddle" in self.ball.inventory:
            nearest = self._get_nearest_enemy()
            if nearest:
                dist = math.hypot(self.ball.x - nearest.x, self.ball.y - nearest.y)
                if dist < 300:
                    self.ball.inventory.remove("deployable_acid_puddle")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        try:
                            from arena.procedural_arena import Hazard
                            acid_id = f"{len(self.world.arena.hazards)}_{getattr(self.world, 'tick', 0)}_acid"
                            puddle = Hazard(acid_id, self.ball.x, self.ball.y, 60.0, "acid_puddle", 0.0)
                            puddle.duration = 10.0
                            setattr(puddle, 'owner_id', getattr(self.ball, 'id', None))
                            self.world.arena.hazards.append(puddle)
                        except ImportError:
                            pass

        if strategy in ("flee", "defend", "attack") and hasattr(self.ball, "inventory") and "deployable_shockwave_mine" in self.ball.inventory:
            nearest = self._get_nearest_enemy()
            if nearest:
                dist = math.hypot(self.ball.x - nearest.x, self.ball.y - nearest.y)
                if dist < 300:
                    self.ball.inventory.remove("deployable_shockwave_mine")
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        try:
                            from arena.procedural_arena import Hazard
                            mine_id = f"{len(self.world.arena.hazards)}_{getattr(self.world, 'tick', 0)}_shockmine"
                            mine = Hazard(mine_id, self.ball.x, self.ball.y, 60.0, "shockwave_mine", 0.0)
                            mine.duration = 30.0
                            setattr(mine, 'owner_id', getattr(self.ball, 'id', None))
                            self.world.arena.hazards.append(mine)
                        except ImportError:
                            pass
"""

text = re.sub(r'\s+if strategy in \("flee", "defend", "attack"\) and hasattr\(self\.ball, "inventory"\) and "deployable_acid_puddle" in self\.ball\.inventory:\s+nearest = self\._get_nearest_enemy\(\)\s+if nearest:\s+dist = math\.hypot\(self\.ball\.x - nearest\.x, self\.ball\.y - nearest\.y\)\s+if dist < 300:\s+self\.ball\.inventory\.remove\("deployable_acid_puddle"\)\s+if hasattr\(self\.world, "arena"\) and hasattr\(self\.world\.arena, "hazards"\):\s+try:\s+from arena\.procedural_arena import Hazard\s+acid_id = f"\{len\(self\.world\.arena\.hazards\)}_{self\.world\.tick}_acid"\s+puddle = Hazard\(acid_id, self\.ball\.x, self\.ball\.y, 60\.0, "acid_puddle", 0\.0\)\s+puddle\.duration = 10\.0\s+setattr\(puddle, \'owner_id\', getattr\(self\.ball, \'id\', None\)\)\s+self\.world\.arena\.hazards\.append\(puddle\)\s+except ImportError:\s+pass', deploy_code, text, count=1, flags=re.DOTALL)

with open("src/ai/action.py", "w") as f:
    f.write(text)
