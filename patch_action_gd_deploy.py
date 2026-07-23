import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

deploy_code = """
		if inv.has("deployable_acid_puddle"):
			var nearest = _get_nearest_enemy()
			if nearest != null:
				var dist = sqrt(pow(self.ball.x - nearest.x, 2) + pow(self.ball.y - nearest.y, 2))
				if dist < 300:
					inv.erase("deployable_acid_puddle")
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
					elif "inventory" in self.ball: self.ball.inventory = inv
					if world != null and "arena" in world and "hazards" in world.arena:
						var arena = world.arena
						var acid_id = str(arena.hazards.size()) + "_" + str(world.tick if "tick" in world else 0) + "_acid"
						var p_puddle = null
						if load("res://src/arena/procedural_arena.gd") != null:
							p_puddle = load("res://src/arena/procedural_arena.gd").Hazard.new(acid_id, self.ball.x, self.ball.y, 60.0, "acid_puddle", 0.0)
							p_puddle.set_meta("duration", 10.0)
							if "id" in self.ball: p_puddle.set_meta("owner_id", self.ball.id)
							arena.hazards.append(p_puddle)

		if inv.has("deployable_shockwave_mine"):
			var nearest = _get_nearest_enemy()
			if nearest != null:
				var dist = sqrt(pow(self.ball.x - nearest.x, 2) + pow(self.ball.y - nearest.y, 2))
				if dist < 300:
					inv.erase("deployable_shockwave_mine")
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
					elif "inventory" in self.ball: self.ball.inventory = inv
					if world != null and "arena" in world and "hazards" in world.arena:
						var arena = world.arena
						var mine_id = str(arena.hazards.size()) + "_" + str(world.tick if "tick" in world else 0) + "_shockmine"
						var p_mine = null
						if load("res://src/arena/procedural_arena.gd") != null:
							p_mine = load("res://src/arena/procedural_arena.gd").Hazard.new(mine_id, self.ball.x, self.ball.y, 60.0, "shockwave_mine", 0.0)
							p_mine.set_meta("duration", 30.0)
							if "id" in self.ball: p_mine.set_meta("owner_id", self.ball.id)
							arena.hazards.append(p_mine)
"""

text = re.sub(r'\s+if inv\.has\("deployable_acid_puddle"\):\s+var nearest = _get_nearest_enemy\(\)\s+if nearest != null:\s+var dist = sqrt\(pow\(self\.ball\.x - nearest\.x, 2\) \+ pow\(self\.ball\.y - nearest\.y, 2\)\)\s+if dist < 300:\s+inv\.erase\("deployable_acid_puddle"\)\s+if typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("set_meta"\): self\.ball\.set_meta\("inventory", inv\)\s+elif "inventory" in self\.ball: self\.ball\.inventory = inv\s+if world != null and "arena" in world and "hazards" in world\.arena:\s+var arena = world\.arena\s+var acid_id = str\(arena\.hazards\.size\(\)\) \+ "_" \+ str\(world\.tick if "tick" in world else 0\) \+ "_acid"\s+var p_puddle = null\s+if load\("res://src/arena/procedural_arena\.gd"\) != null:\s+p_puddle = load\("res://src/arena/procedural_arena\.gd"\)\.Hazard\.new\(acid_id, self\.ball\.x, self\.ball\.y, 60\.0, "acid_puddle", 0\.0\)\s+p_puddle\.set_meta\("duration", 10\.0\)\s+if "id" in self\.ball: p_puddle\.set_meta\("owner_id", self\.ball\.id\)\s+arena\.hazards\.append\(p_puddle\)', deploy_code, text)


with open("src/ai/action.gd", "w") as f:
    f.write(text)
