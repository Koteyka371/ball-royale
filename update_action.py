import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

puddle_block_search = """                        elif hazard.kind == "acid_puddle":
                            hazard_damage = hazard.damage * delta
                            if hasattr(self.ball, "take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif hasattr(self.ball, "hp"):
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = False
                            continue"""

puddle_block_replace = """                        elif hazard.kind == "acid_puddle":
                            hazard_damage = hazard.damage * delta
                            if hasattr(self.ball, "take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif hasattr(self.ball, "hp"):
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = False
                            continue
                        elif hazard.kind == "neutralizing_puddle":
                            if hasattr(self.ball, "base_max_hp"):
                                if getattr(self.ball, "max_hp", 100.0) < self.ball.base_max_hp:
                                    self.ball.max_hp = min(self.ball.base_max_hp, self.ball.max_hp + 20.0 * delta)
                            if hasattr(self.ball, "defense_multiplier"):
                                if self.ball.defense_multiplier < 1.0:
                                    self.ball.defense_multiplier = min(1.0, self.ball.defense_multiplier + 0.5 * delta)
                            continue"""

if puddle_block_search in content:
    content = content.replace(puddle_block_search, puddle_block_replace)
    with open("src/ai/action.py", "w") as f:
        f.write(content)
    print("Replaced successfully in src/ai/action.py")
else:
    print("Block not found in src/ai/action.py")
