import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

tick_logic = """
		var inf_timer = 0.0
		if typeof(self.ball) == TYPE_OBJECT and "chain_infection_timer" in self.ball:
			inf_timer = float(self.ball.chain_infection_timer)
		elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("chain_infection_timer"):
			inf_timer = float(self.ball["chain_infection_timer"])
		elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("chain_infection_timer"):
			inf_timer = float(self.ball.get_meta("chain_infection_timer"))

		if inf_timer > 0:
			var current_hp = 100.0
			if typeof(self.ball) == TYPE_OBJECT and "hp" in self.ball:
				current_hp = float(self.ball.hp)
			elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("hp"):
				current_hp = float(self.ball["hp"])
			elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("hp"):
				current_hp = float(self.ball.get_meta("hp"))

			var prev_hp = current_hp
			if typeof(self.ball) == TYPE_OBJECT and "_prev_hp_for_infection" in self.ball:
				prev_hp = float(self.ball._prev_hp_for_infection)
			elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("_prev_hp_for_infection"):
				prev_hp = float(self.ball["_prev_hp_for_infection"])
			elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("_prev_hp_for_infection"):
				prev_hp = float(self.ball.get_meta("_prev_hp_for_infection"))

			if current_hp < prev_hp:
				var dmg_taken = prev_hp - current_hp
				var threshold = 100.0
				if typeof(self.ball) == TYPE_OBJECT and "chain_infection_damage_threshold" in self.ball:
					threshold = float(self.ball.chain_infection_damage_threshold)
				elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("chain_infection_damage_threshold"):
					threshold = float(self.ball["chain_infection_damage_threshold"])
				elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("chain_infection_damage_threshold"):
					threshold = float(self.ball.get_meta("chain_infection_damage_threshold"))

				threshold -= dmg_taken

				if typeof(self.ball) == TYPE_OBJECT and "chain_infection_damage_threshold" in self.ball:
					self.ball.chain_infection_damage_threshold = threshold
				elif typeof(self.ball) == TYPE_DICTIONARY:
					self.ball["chain_infection_damage_threshold"] = threshold
				elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
					self.ball.set_meta("chain_infection_damage_threshold", threshold)

				if threshold <= 0:
					inf_timer = 0.0

			if typeof(self.ball) == TYPE_OBJECT and "_prev_hp_for_infection" in self.ball:
				self.ball._prev_hp_for_infection = current_hp
			elif typeof(self.ball) == TYPE_DICTIONARY:
				self.ball["_prev_hp_for_infection"] = current_hp
			elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
				self.ball.set_meta("_prev_hp_for_infection", current_hp)

			if inf_timer > 0:
				inf_timer -= delta
				if inf_timer <= 0:
					inf_timer = 0.0
				else:
					var tick = 2.0
					if typeof(self.ball) == TYPE_OBJECT and "chain_infection_tick_timer" in self.ball:
						tick = float(self.ball.chain_infection_tick_timer)
					elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("chain_infection_tick_timer"):
						tick = float(self.ball["chain_infection_tick_timer"])
					elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("chain_infection_tick_timer"):
						tick = float(self.ball.get_meta("chain_infection_tick_timer"))

					tick -= delta
					if tick <= 0:
						tick = 2.0

						var my_team = -1
						if typeof(self.ball) == TYPE_OBJECT and "team" in self.ball: my_team = self.ball.team
						elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("team"): my_team = self.ball["team"]
						elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")

						var my_x = 0.0
						var my_y = 0.0
						if typeof(self.ball) == TYPE_OBJECT and "x" in self.ball: my_x = self.ball.x
						elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("x"): my_x = self.ball["x"]
						if typeof(self.ball) == TYPE_OBJECT and "y" in self.ball: my_y = self.ball.y
						elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("y"): my_y = self.ball["y"]

						var best_dist = 90000.0
						var nearest = null
						var balls_array = []
						if typeof(self.world) == TYPE_DICTIONARY and self.world.has("balls"): balls_array = self.world["balls"]
						elif typeof(self.world) == TYPE_OBJECT and "balls" in self.world: balls_array = self.world.balls

						for b in balls_array:
							var is_alive = true
							if typeof(b) == TYPE_DICTIONARY and b.has("alive"): is_alive = b["alive"]
							elif typeof(b) == TYPE_OBJECT and "alive" in b: is_alive = b.alive
							if not is_alive or str(b) == str(self.ball):
								continue

							var b_team = -1
							if typeof(b) == TYPE_OBJECT and "team" in b: b_team = b.team
							elif typeof(b) == TYPE_DICTIONARY and b.has("team"): b_team = b["team"]
							elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("team"): b_team = b.get_meta("team")

							if str(b_team) != str(my_team):
								continue

							var bx = 0.0
							var by = 0.0
							if typeof(b) == TYPE_OBJECT and "x" in b: bx = b.x
							elif typeof(b) == TYPE_DICTIONARY and b.has("x"): bx = b["x"]
							if typeof(b) == TYPE_OBJECT and "y" in b: by = b.y
							elif typeof(b) == TYPE_DICTIONARY and b.has("y"): by = b["y"]

							var dist_sq = (bx - my_x) * (bx - my_x) + (by - my_y) * (by - my_y)
							if dist_sq < best_dist:
								best_dist = dist_sq
								nearest = b

						if nearest != null:
							var nearest_id = -1
							if typeof(nearest) == TYPE_OBJECT and "id" in nearest: nearest_id = nearest.id
							elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("id"): nearest_id = nearest["id"]
							var my_id = -1
							if typeof(self.ball) == TYPE_OBJECT and "id" in self.ball: my_id = self.ball.id
							elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): my_id = self.ball["id"]

							if typeof(self.world) == TYPE_OBJECT and self.world.has_method("add_event"):
								var nx = 0.0
								var ny = 0.0
								if typeof(nearest) == TYPE_OBJECT and "x" in nearest: nx = nearest.x
								elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("x"): nx = nearest["x"]
								if typeof(nearest) == TYPE_OBJECT and "y" in nearest: ny = nearest.y
								elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("y"): ny = nearest["y"]
								self.world.add_event("visual_effect", {"type": "lightning", "x": my_x, "y": my_y, "tx": nx, "ty": ny})

							if typeof(nearest) == TYPE_OBJECT and "hp" in nearest:
								nearest.hp -= 20.0
								if nearest.hp <= 0: nearest.alive = false
							elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("hp"):
								nearest["hp"] -= 20.0
								if nearest["hp"] <= 0: nearest["alive"] = false

					if typeof(self.ball) == TYPE_OBJECT and "chain_infection_tick_timer" in self.ball:
						self.ball.chain_infection_tick_timer = tick
					elif typeof(self.ball) == TYPE_DICTIONARY:
						self.ball["chain_infection_tick_timer"] = tick
					elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
						self.ball.set_meta("chain_infection_tick_timer", tick)

			if typeof(self.ball) == TYPE_OBJECT and "chain_infection_timer" in self.ball:
				self.ball.chain_infection_timer = inf_timer
			elif typeof(self.ball) == TYPE_DICTIONARY:
				self.ball["chain_infection_timer"] = inf_timer
			elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
				self.ball.set_meta("chain_infection_timer", inf_timer)

"""

anchor_tick_gd = '		if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("chain_lightning_timer") and float(self.ball["chain_lightning_timer"]) > 0:'
content = content.replace(anchor_tick_gd, tick_logic + "\n" + anchor_tick_gd)

collision_logic = """								elif trap_variant == "chain_infection":
									if typeof(self.ball) == TYPE_OBJECT:
										self.ball.set("chain_infection_timer", 30.0)
										self.ball.set("chain_infection_damage_threshold", 100.0)
										self.ball.set("chain_infection_tick_timer", 2.0)
										if "hp" in self.ball:
											self.ball.set("_prev_hp_for_infection", float(self.ball.hp))
									elif typeof(self.ball) == TYPE_DICTIONARY:
										self.ball["chain_infection_timer"] = 30.0
										self.ball["chain_infection_damage_threshold"] = 100.0
										self.ball["chain_infection_tick_timer"] = 2.0
										if self.ball.has("hp"):
											self.ball["_prev_hp_for_infection"] = float(self.ball["hp"])
									if typeof(hazard) == TYPE_OBJECT:
										hazard.set("duration", 0.0)
									elif typeof(hazard) == TYPE_DICTIONARY:
										hazard["duration"] = 0.0
"""
anchor_collision_gd = '								elif trap_variant == "chain_lightning":'
content = content.replace(anchor_collision_gd, collision_logic + anchor_collision_gd)

cleanse_booster_anchor = '					if typeof(self.ball) == TYPE_OBJECT:\n						self.ball.set("immunity_timer", 15.0)'
cleanse_booster_addition = '					if typeof(self.ball) == TYPE_OBJECT:\n						self.ball.set("chain_infection_timer", 0.0)\n					elif typeof(self.ball) == TYPE_DICTIONARY:\n						self.ball["chain_infection_timer"] = 0.0\n'
content = content.replace(cleanse_booster_anchor, cleanse_booster_addition + cleanse_booster_anchor)

cleanser_item_anchor = '					if typeof(self.ball) == TYPE_OBJECT:\n						self.ball.set("burn_timer", 0.0)'
cleanser_item_addition = '					if typeof(self.ball) == TYPE_OBJECT:\n						self.ball.set("chain_infection_timer", 0.0)\n					elif typeof(self.ball) == TYPE_DICTIONARY:\n						self.ball["chain_infection_timer"] = 0.0\n'
content = content.replace(cleanser_item_anchor, cleanser_item_addition + cleanser_item_anchor)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
