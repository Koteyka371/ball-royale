import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

puddle_block_search = """                    elif hazard.kind == "acid_puddle":
                        var acid_damage = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(acid_damage)
                        elif "hp" in self.ball:
                            self.ball.hp -= acid_damage
                            if self.ball.hp <= 0 and "alive" in self.ball:
                                self.ball.alive = false
                        continue"""

puddle_block_replace = """                    elif hazard.kind == "acid_puddle":
                        var acid_damage = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(acid_damage)
                        elif "hp" in self.ball:
                            self.ball.hp -= acid_damage
                            if self.ball.hp <= 0 and "alive" in self.ball:
                                self.ball.alive = false
                        continue
                    elif hazard.kind == "neutralizing_puddle":
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            if self.ball.has("base_max_hp"):
                                if self.ball.get("max_hp", 100.0) < self.ball["base_max_hp"]:
                                    self.ball["max_hp"] = min(self.ball["base_max_hp"], self.ball["max_hp"] + 20.0 * delta)
                            if self.ball.has("defense_multiplier"):
                                if self.ball["defense_multiplier"] < 1.0:
                                    self.ball["defense_multiplier"] = min(1.0, self.ball["defense_multiplier"] + 0.5 * delta)
                        else:
                            if self.ball.has_meta("base_max_hp"):
                                var base_hp = self.ball.get_meta("base_max_hp")
                                if self.ball.max_hp < base_hp:
                                    self.ball.max_hp = min(base_hp, self.ball.max_hp + 20.0 * delta)
                            if "defense_multiplier" in self.ball:
                                if self.ball.defense_multiplier < 1.0:
                                    self.ball.defense_multiplier = min(1.0, self.ball.defense_multiplier + 0.5 * delta)
                            elif self.ball.has_meta("defense_multiplier"):
                                var cur_def = self.ball.get_meta("defense_multiplier")
                                if cur_def < 1.0:
                                    self.ball.set_meta("defense_multiplier", min(1.0, cur_def + 0.5 * delta))
                        continue"""

if puddle_block_search in content:
    content = content.replace(puddle_block_search, puddle_block_replace)
    with open("src/ai/action.gd", "w") as f:
        f.write(content)
    print("Replaced successfully in src/ai/action.gd")
else:
    print("Block not found in src/ai/action.gd")
