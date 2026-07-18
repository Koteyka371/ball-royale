with open("src/ai/action.gd", "r") as f:
    content = f.read()

search1 = """		elif skill_name == "corpse_explosion":"""
replace1 = """		elif skill_name == "bone_wall":
			if "arena" in self.world and "hazards" in self.world.arena:
				var target_x = self.ball.x if typeof(self.ball) == TYPE_OBJECT else self.ball["x"]
				var target_y = self.ball.y if typeof(self.ball) == TYPE_OBJECT else self.ball["y"]
				var enemies = self._get_enemies()
				if enemies.size() > 0:
					var nearest = enemies[0]
					var min_d = (nearest.x - target_x)*(nearest.x - target_x) + (nearest.y - target_y)*(nearest.y - target_y)
					for e in enemies:
						var d = (e.x - target_x)*(e.x - target_x) + (e.y - target_y)*(e.y - target_y)
						if d < min_d:
							nearest = e
							min_d = d
					var dx = nearest.x - target_x
					var dy = nearest.y - target_y
					var dist = sqrt(dx*dx + dy*dy)
					if dist > 0.0001:
						target_x += (dx/dist) * 60.0
						target_y += (dy/dist) * 60.0
				else:
					target_x += 60.0

				var h_id = 15000 + self.world.arena.hazards.size() + (randi() % 1000)
				var wall = {
					"id": h_id,
					"x": target_x,
					"y": target_y,
					"radius": 40.0,
					"kind": "bone_wall",
					"damage": 0.0,
					"hp": 300.0,
					"duration": 10.0,
					"active": true
				}
				self.world.arena.hazards.append(wall)
			var cooldown = 8.0
			if typeof(self.ball) == TYPE_DICTIONARY: cooldown = self.ball.get("skill_cooldown", 8.0)
			elif "skill_cooldown" in self.ball: cooldown = self.ball.skill_cooldown
			if typeof(self.ball) == TYPE_DICTIONARY: self.ball["skill_timer"] = cooldown
			elif "skill_timer" in self.ball: self.ball.skill_timer = cooldown
		elif skill_name == "corpse_explosion":"""

content = content.replace(search1, replace1)

search2 = """			if h_kind == "orbital_debris":
				var hx = float(h.x if "x" in h else h.get_meta("x"))
				var hy = float(h.y if "y" in h else h.get_meta("y"))
				var hr = float(h.radius if "radius" in h else (h.get_meta("radius") if h.has_meta("radius") else 40.0))
				if sqrt((t_x2 - hx)*(t_x2 - hx) + (t_y2 - hy)*(t_y2 - hy)) <= hr:
					return"""
replace2 = """			if h_kind == "orbital_debris" or h_kind == "bone_wall":
				var hx = float(h.x if "x" in h else h.get_meta("x"))
				var hy = float(h.y if "y" in h else h.get_meta("y"))
				var hr = float(h.radius if "radius" in h else (h.get_meta("radius") if h.has_meta("radius") else 40.0))

				var l2 = (t_x2 - a_x2)*(t_x2 - a_x2) + (t_y2 - a_y2)*(t_y2 - a_y2)
				var dist_to_line = 0.0
				if l2 == 0.0:
					dist_to_line = sqrt((hx - a_x2)*(hx - a_x2) + (hy - a_y2)*(hy - a_y2))
				else:
					var t = max(0.0, min(1.0, ((hx - a_x2) * (t_x2 - a_x2) + (hy - a_y2) * (t_y2 - a_y2)) / l2))
					var proj_x = a_x2 + t * (t_x2 - a_x2)
					var proj_y = a_y2 + t * (t_y2 - a_y2)
					dist_to_line = sqrt((hx - proj_x)*(hx - proj_x) + (hy - proj_y)*(hy - proj_y))

				if dist_to_line <= hr:
					if h_kind == "bone_wall":
						var dmg = 10.0
						if "damage" in attacker: dmg = attacker.damage
						elif typeof(attacker) == TYPE_DICTIONARY and attacker.has("damage"): dmg = attacker["damage"]

						if typeof(h) == TYPE_DICTIONARY and h.has("hp"):
							h["hp"] -= dmg
							if h["hp"] <= 0:
								h["active"] = false
						elif typeof(h) == TYPE_OBJECT and h.has_method("set_meta"):
							var current_hp = h.get_meta("hp") if h.has_meta("hp") else 300.0
							var new_hp = current_hp - dmg
							h.set_meta("hp", new_hp)
							if new_hp <= 0:
								h.set_meta("active", false)
					return"""

content = content.replace(search2, replace2)

search3 = """                    elif hazard.kind == "breakable_wall":"""
replace3 = """                    elif hazard.kind == "bone_wall":
                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var d = sqrt(dx*dx + dy*dy)
                        var b_rad = 10.0
                        if "radius" in self.ball:
                            b_rad = self.ball.radius
                        if d < (b_rad + hazard.radius) and d > 0:
                            var nx = dx / d
                            var ny = dy / d
                            var overlap = (b_rad + hazard.radius) - d

                            var b_type = ""
                            if "ball_type" in self.ball: b_type = str(self.ball.ball_type).to_lower()
                            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("ball_type"): b_type = str(self.ball["ball_type"]).to_lower()

                            var is_projectile = (b_type == "projectile" or b_type == "spell")
                            if "is_projectile" in self.ball and self.ball.is_projectile: is_projectile = true
                            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("is_projectile") and self.ball["is_projectile"]: is_projectile = true

                            if is_projectile:
                                if "alive" in self.ball: self.ball.alive = false
                                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["alive"] = false
                                if "hp" in self.ball: self.ball.hp = 0
                                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["hp"] = 0

                                var dmg = 10.0
                                if "damage" in self.ball: dmg = self.ball.damage
                                elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("damage"): dmg = self.ball["damage"]

                                if typeof(hazard) == TYPE_DICTIONARY and hazard.has("hp"):
                                    hazard["hp"] -= dmg
                                    if hazard["hp"] <= 0:
                                        hazard["active"] = false
                                elif typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"):
                                    var current_hp = hazard.get_meta("hp") if hazard.has_meta("hp") else 300.0
                                    var new_hp = current_hp - dmg
                                    hazard.set_meta("hp", new_hp)
                                    if new_hp <= 0:
                                        hazard.active = false
                                        hazard.set_meta("active", false)
                            else:
                                self.ball.x += nx * overlap
                                self.ball.y += ny * overlap

                                var dmg = 10.0
                                if "damage" in self.ball: dmg = self.ball.damage
                                elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("damage"): dmg = self.ball["damage"]

                                if typeof(hazard) == TYPE_DICTIONARY and hazard.has("hp"):
                                    hazard["hp"] -= dmg * delta * 5.0
                                    if hazard["hp"] <= 0:
                                        hazard["active"] = false
                                elif typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"):
                                    var current_hp = hazard.get_meta("hp") if hazard.has_meta("hp") else 300.0
                                    var new_hp = current_hp - dmg * delta * 5.0
                                    hazard.set_meta("hp", new_hp)
                                    if new_hp <= 0:
                                        hazard.active = false
                                        hazard.set_meta("active", false)
                        continue
                    elif hazard.kind == "breakable_wall":"""

content = content.replace(search3, replace3)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
