import re

file_path = "src/ai/action.gd"
with open(file_path, "r") as f:
    content = f.read()

deploy_logic = """		if inv.has("deployable_mud_puddle"):
			var nearest = _get_nearest_enemy()
			if nearest != null:
				var dist = sqrt(pow(self.ball.x - nearest.x, 2) + pow(self.ball.y - nearest.y, 2))
				if dist < 300:
					inv.erase("deployable_mud_puddle")
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
					elif "inventory" in self.ball: self.ball.inventory = inv
					if world != null and "arena" in world and "hazards" in world.arena:
						var arena = world.arena
						var mud_id = str(arena.hazards.size()) + "_" + str(world.tick if "tick" in world else 0) + "_mud"
						var p_puddle = null
						if load("res://src/arena/procedural_arena.gd") != null:
							p_puddle = load("res://src/arena/procedural_arena.gd").Hazard.new(mud_id, self.ball.x, self.ball.y, 60.0, "sticky_mud_puddle", 0.0)
							p_puddle.set_meta("duration", 10.0)
							if "id" in self.ball: p_puddle.set_meta("owner_id", self.ball.id)
							arena.hazards.append(p_puddle)"""

new_deploy_logic = deploy_logic + """

		if inv.has("deployable_proximity_mud_puddle"):
			var nearest = _get_nearest_enemy()
			if nearest != null:
				var dist = sqrt(pow(self.ball.x - nearest.x, 2) + pow(self.ball.y - nearest.y, 2))
				if dist < 300:
					inv.erase("deployable_proximity_mud_puddle")
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
					elif "inventory" in self.ball: self.ball.inventory = inv
					if world != null and "arena" in world and "hazards" in world.arena:
						var arena = world.arena
						var mud_id = str(arena.hazards.size()) + "_" + str(world.tick if "tick" in world else 0) + "_proxmud"
						var p_puddle = null
						if load("res://src/arena/procedural_arena.gd") != null:
							p_puddle = load("res://src/arena/procedural_arena.gd").Hazard.new(mud_id, self.ball.x, self.ball.y, 60.0, "proximity_mud_puddle", 0.0)
							p_puddle.set_meta("duration", 30.0)
							if "id" in self.ball: p_puddle.set_meta("owner_id", self.ball.id)
							arena.hazards.append(p_puddle)"""

content = content.replace(deploy_logic, new_deploy_logic)

with open(file_path, "w") as f:
    f.write(content)
