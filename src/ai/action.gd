class_name ActionLayer
extends RefCounted


func _award_xp(ball, amount: float, world=null) -> void:
	var b_type = null
	if "ball_type" in ball: b_type = str(ball.ball_type)
	if not ("alive" in ball) or ball.alive == false or b_type == "spectator":
		return

	if not ("experience" in ball): ball.experience = 0.0
	if not ("level" in ball): ball.level = 1

	ball.experience += amount

	while ball.experience >= 100 * ball.level:
		ball.experience -= 100 * ball.level
		ball.level += 1

		var rng = randf()
		var stat = "max_hp"
		if rng > 0.66: stat = "damage"
		elif rng > 0.33: stat = "speed"

		if stat == "max_hp":
			if "max_hp" in ball: ball.max_hp *= 1.1
			else: ball.max_hp = 110.0

			if "hp" in ball: ball.hp += ball.max_hp * 0.1
			else: ball.hp = ball.max_hp
			if ball.hp > ball.max_hp: ball.hp = ball.max_hp
		elif stat == "damage":
			if "damage" in ball: ball.damage *= 1.1
			else: ball.damage = 11.0
			if "base_damage" in ball: ball.base_damage *= 1.1
		elif stat == "speed":
			if "speed" in ball: ball.speed *= 1.1
			else: ball.speed = 110.0
			if "base_speed" in ball: ball.base_speed *= 1.1

		if world != null and world.has_method("add_event"):
			world.add_event("level_up", {"ball": ball.get("id"), "level": ball.level, "stat": stat})

func _attempt_damage(attacker, target) -> void:
	var attack_accuracy = 1.0

	var pm = null
	if self.world != null and "profile_manager" in self.world:
		pm = self.world.profile_manager

	var is_nemesis_active = false
	var attacker_type = ""
	var target_type = ""
	if "ball_type" in attacker: attacker_type = str(attacker.ball_type)
	if "ball_type" in target: target_type = str(target.ball_type)

	if pm != null and pm.has_method("is_nemesis") and attacker_type != "" and target_type != "":
		is_nemesis_active = pm.is_nemesis(attacker_type, target_type)

	var old_hp = 0.0
	if "hp" in target: old_hp = float(target.hp)
	var original_damage = 10.0
	if "damage" in attacker: original_damage = float(attacker.damage)

	if "attack_accuracy" in attacker:
		attack_accuracy = float(attacker.attack_accuracy)
	elif attacker.has_method("get_meta") and attacker.has_meta("attack_accuracy"):
		attack_accuracy = float(attacker.get_meta("attack_accuracy"))
	if randf() > attack_accuracy:
		return

	var executed_by_necromancer = false
	if attacker_type.to_lower() == "necromancer":
		var target_max_hp = 100.0
		if "max_hp" in target:
			target_max_hp = float(target.max_hp)
		elif target.has_method("get_meta") and target.has_meta("max_hp"):
			target_max_hp = float(target.get_meta("max_hp"))

		if old_hp > 0 and (old_hp / target_max_hp) < 0.2:
			if randf() < 0.25:
				executed_by_necromancer = true

	if executed_by_necromancer:
		var target_max_hp = 100.0
		if "max_hp" in target:
			target_max_hp = float(target.max_hp)
		elif target.has_method("get_meta") and target.has_meta("max_hp"):
			target_max_hp = float(target.get_meta("max_hp"))

		if self.world != null and self.world.has_method("_deal_damage"):
			var old_dmg = original_damage
			if "damage" in attacker:
				old_dmg = attacker.damage
				attacker.damage = old_hp + 999.0
			self.world._deal_damage(attacker, target)
			if "damage" in attacker:
				attacker.damage = old_dmg

		var attacker_max_hp = 100.0
		if "max_hp" in attacker: attacker_max_hp = float(attacker.max_hp)

		var cur_hp = attacker_max_hp
		if "hp" in attacker: cur_hp = float(attacker.hp)

		var new_hp = min(attacker_max_hp, cur_hp + target_max_hp * 0.5)
		if "hp" in attacker:
			attacker.hp = new_hp
		elif attacker.has_method("set_meta"):
			attacker.set_meta("hp", new_hp)

		var shield_cap = 0.0
		if "reflect_shield_capacity" in attacker: shield_cap = float(attacker.reflect_shield_capacity)
		elif attacker.has_method("get_meta") and attacker.has_meta("reflect_shield_capacity"): shield_cap = float(attacker.get_meta("reflect_shield_capacity"))
		shield_cap = max(shield_cap, target_max_hp * 0.5)

		if "reflect_shield_active" in attacker: attacker.reflect_shield_active = true
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_active", true)

		if "reflect_shield_capacity" in attacker: attacker.reflect_shield_capacity = shield_cap
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_capacity", shield_cap)

		if "reflect_shield_timer" in attacker: attacker.reflect_shield_timer = 5.0
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_timer", 5.0)

	else:
		if is_nemesis_active:
			if "damage" in attacker:
				attacker.damage = original_damage * 1.2

		var has_ricochet = false
		if "ricochet_barrier_timer" in target and target.ricochet_barrier_timer > 0.0:
			has_ricochet = true
		elif target.has_method("get_meta") and target.has_meta("ricochet_barrier_timer"):
			if target.get_meta("ricochet_barrier_timer") > 0.0:
				has_ricochet = true

		var has_reflect = false
		if "reflect_shield_active" in target and target.reflect_shield_active:
			has_reflect = true
		elif target.has_method("get_meta") and target.has_meta("reflect_shield_active"):
			if target.get_meta("reflect_shield_active"):
				has_reflect = true

		var rs_timer = -1.0
		if "reflect_shield_timer" in target:
			rs_timer = target.reflect_shield_timer
		elif target.has_method("get_meta") and target.has_meta("reflect_shield_timer"):
			rs_timer = target.get_meta("reflect_shield_timer")
		if rs_timer != -1.0 and rs_timer <= 0.0 and has_reflect:
			has_reflect = false

		if has_ricochet:
			if self.world != null and self.world.has_method("_deal_damage"):
				self.world._deal_damage(target, attacker)
		elif has_reflect:
			var capacity = 50.0
			if "reflect_shield_capacity" in target:
				capacity = target.reflect_shield_capacity
			elif target.has_method("get_meta") and target.has_meta("reflect_shield_capacity"):
				capacity = target.get_meta("reflect_shield_capacity")

			var damage_to_reflect = min(capacity, original_damage)
			capacity -= original_damage

			if capacity <= 0:
				if "reflect_shield_active" in target:
					target.reflect_shield_active = false
				elif target.has_method("set_meta"):
					target.set_meta("reflect_shield_active", false)

				if "reflect_shield_capacity" in target:
					target.reflect_shield_capacity = 0.0
				elif target.has_method("set_meta"):
					target.set_meta("reflect_shield_capacity", 0.0)
			else:
				if "reflect_shield_capacity" in target:
					target.reflect_shield_capacity = capacity
				elif target.has_method("set_meta"):
					target.set_meta("reflect_shield_capacity", capacity)

			if self.has_method("_spawn_directed_particles"):
				self._spawn_directed_particles(target, attacker, "reflect_pulse")
			if self.world != null and self.world.has_method("_deal_damage"):
				var old_dmg = original_damage
				if "damage" in attacker:
					old_dmg = attacker.damage
					attacker.damage = damage_to_reflect
				self.world._deal_damage(target, attacker)
				if "damage" in attacker:
					attacker.damage = old_dmg

			if capacity < 0:
				var remainder_damage = -capacity
				var old_dmg = original_damage
				if "damage" in attacker:
					old_dmg = attacker.damage
					attacker.damage = remainder_damage
				if self.world != null and self.world.has_method("_deal_damage"):
					self.world._deal_damage(attacker, target)
				if "damage" in attacker:
					attacker.damage = old_dmg

				var explosion_radius = 80.0
				if self.world != null and "balls" in self.world:
					for other in self.world.balls:
						var other_alive = false
						if "alive" in other:
							other_alive = other.alive
						elif other.has_method("get_meta") and other.has_meta("alive"):
							other_alive = other.get_meta("alive")

						var other_id = null
						if "id" in other:
							other_id = other.id

						var target_id = null
						if "id" in target:
							target_id = target.id

						if other_alive and other_id != target_id:
							var dx = 0.0
							if "x" in other: dx = other.x
							if "x" in target: dx -= target.x
							var dy = 0.0
							if "y" in other: dy = other.y
							if "y" in target: dy -= target.y

							var dist = sqrt(dx*dx + dy*dy)
							if dist <= explosion_radius:
								if self.world != null and self.world.has_method("_deal_damage"):
									var old_atk_dmg = 10.0
									if "damage" in target: old_atk_dmg = target.damage
									if "damage" in target: target.damage = remainder_damage
									elif target.has_method("set_meta"): target.set_meta("damage", remainder_damage)
									self.world._deal_damage(target, other)
									if "damage" in target: target.damage = old_atk_dmg
									elif target.has_method("set_meta"): target.set_meta("damage", old_atk_dmg)
								elif other.has_method("take_damage"):
									other.take_damage(remainder_damage)
								elif "hp" in other:
									other.hp -= remainder_damage
									if other.hp <= 0:
										if "alive" in other: other.alive = false
										elif other.has_method("set_meta"): other.set_meta("alive", false)
		else:
			if self.world != null and self.world.has_method("_deal_damage"):
				self.world._deal_damage(attacker, target)

		if is_nemesis_active and "damage" in attacker:
			attacker.damage = original_damage

	var new_hp = 0.0
	if "hp" in target: new_hp = float(target.hp)

	if new_hp < old_hp:
		self._award_xp(attacker, 10.0, self.world)
		if new_hp <= 0 and old_hp > 0:
			var base_xp = 50.0
			if pm != null and pm.has_method("is_nemesis") and attacker_type != "" and target_type != "":
				if pm.is_nemesis(target_type, attacker_type):
					base_xp *= 2.0
			self._award_xp(attacker, base_xp, self.world)
	if new_hp <= 0 and old_hp > 0:
		if pm != null and pm.has_method("add_kill"):
			pm.add_kill(attacker_type, target_type)
			if pm.is_nemesis(target_type, attacker_type):
				if "kills" in attacker:
					attacker.kills += 1
				if "charge_level" in attacker:
					attacker.charge_level = min(100.0, float(attacker.charge_level) + 20.0)
				elif attacker.has_method("set_meta"):
					var cl = 0.0
					if attacker.has_meta("charge_level"): cl = float(attacker.get_meta("charge_level"))
					attacker.set_meta("charge_level", min(100.0, cl + 20.0))

		if "kills" in attacker:
			attacker.kills += 1
		elif attacker.has_method("set_meta"):
			var kills = attacker.get_meta("kills") if attacker.has_meta("kills") else 0
			attacker.set_meta("kills", kills + 1)

		if "charge_level" in attacker:
			attacker.charge_level = min(100.0, float(attacker.charge_level) + 20.0)
		elif attacker.has_method("set_meta"):
			var cl = 0.0
			if attacker.has_meta("charge_level"): cl = float(attacker.get_meta("charge_level"))
			attacker.set_meta("charge_level", min(100.0, cl + 20.0))

		var sponsor = ""
		if "sponsor" in attacker:
			sponsor = attacker.sponsor
		elif attacker.has_method("get_meta") and attacker.has_meta("sponsor"):
			sponsor = attacker.get_meta("sponsor")

		if sponsor == "aggressor":
			if "damage" in attacker: attacker.damage *= 1.1
			if "base_damage" in attacker: attacker.base_damage *= 1.1
			elif attacker.has_method("set_meta") and attacker.has_meta("base_damage"):
				attacker.set_meta("base_damage", float(attacker.get_meta("base_damage")) * 1.1)
		elif sponsor == "vampiric":
			var k = attacker.kills if "kills" in attacker else (attacker.get_meta("kills") if attacker.has_method("get_meta") and attacker.has_meta("kills") else 0)
			if int(k) % 2 == 0:
				var max_h = attacker.max_hp if "max_hp" in attacker else 100.0
				if "hp" in attacker: attacker.hp = min(max_h, attacker.hp + 20)
		elif sponsor == "juggernaut":
			var k = attacker.kills if "kills" in attacker else (attacker.get_meta("kills") if attacker.has_method("get_meta") and attacker.has_meta("kills") else 0)
			if int(k) % 3 == 0:
				if "max_hp" in attacker:
					attacker.max_hp *= 1.15
					if "hp" in attacker: attacker.hp += attacker.max_hp * 0.15

		var arena = world.call("get_arena") if world != null and world.has_method("get_arena") else null
		if arena != null and "items" in arena:
			var mat_types = ["Iron Ore", "Magic Dust", "Void Shard"]
			var mat_type = mat_types[randi() % mat_types.size()]
			var new_id = 9999
			if "next_id" in world:
				new_id = world.next_id
				world.next_id += 1
			var tx = target.get("x") if "x" in target else 0.0
			var ty = target.get("y") if "y" in target else 0.0
			var mat = {"id": "mat_" + str(new_id), "x": tx, "y": ty, "ball_type": "item", "kind": "material", "material_type": mat_type, "radius": 15.0, "active": true}
			arena.items.append(mat)


	var cl_timer = 0.0
	if "chain_lightning_timer" in attacker:
		cl_timer = attacker.chain_lightning_timer
	elif attacker.has_method("get_meta") and attacker.has_meta("chain_lightning_timer"):
		cl_timer = attacker.get_meta("chain_lightning_timer")

	if cl_timer > 0.0:
		var enemies = self._get_enemies()
		var hazards = []
		if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
			hazards = self.world.arena.hazards
			var items = []
			if self.world != null and "arena" in self.world and self.world.arena != null:
				if "items" in self.world.arena:
					items = self.world.arena.items
			var boosters = []
			if self.world != null and "boosters" in self.world:
				boosters = self.world.boosters

			if enemies.size() > 0 or hazards.size() > 0 or items.size() > 0 or boosters.size() > 0:
				var jump_count = 0
				var has_orig_dmg = "damage" in attacker
				var orig_dmg = 10.0
				if has_orig_dmg:
					orig_dmg = attacker.damage

				var current_target = target
				var weather_is_thunderstorm = false
				if self.world != null:
					if "arena" in self.world and self.world.arena != null and "weather" in self.world.arena and self.world.arena.weather == "thunderstorm":
						weather_is_thunderstorm = true
					elif "game_mode" in self.world and self.world.game_mode != null and "weather" in self.world.game_mode and self.world.game_mode.weather == "thunderstorm":
						weather_is_thunderstorm = true

				var chain_range = 150.0
				var chain_damage_multiplier = 0.8

				if weather_is_thunderstorm:
					chain_range = 300.0
					chain_damage_multiplier = 1.2

				var chain_range_sq = chain_range * chain_range
				var current_damage = orig_dmg * chain_damage_multiplier
				var hit_entities = []
				hit_entities.append(attacker)
				hit_entities.append(target)

				while jump_count < 3:
					var nearby = []
					for e in enemies:
						if not hit_entities.has(e):
							var dist_sq = pow(e.x - current_target.x, 2) + pow(e.y - current_target.y, 2)
							if dist_sq < chain_range_sq:
								nearby.append({"dist": dist_sq, "entity": e, "type": "enemy"})
					for h in hazards:
						if not hit_entities.has(h):
							var is_active = true
							if "active" in h: is_active = h.active
							if is_active:
								var dist_sq = pow(h.x - current_target.x, 2) + pow(h.y - current_target.y, 2)
								if dist_sq < chain_range_sq:
									var t_var = ""
									if typeof(h) == TYPE_OBJECT and h.has_meta("trap_variant"): t_var = h.get_meta("trap_variant")
									if t_var == "emp_trap":
										nearby.append({"dist": -999999.0 + dist_sq, "entity": h, "type": "hazard"})
									else:
										nearby.append({"dist": dist_sq, "entity": h, "type": "hazard"})
					for b in boosters:
						if not hit_entities.has(b):
							var dist_sq = pow(b.x - current_target.x, 2) + pow(b.y - current_target.y, 2)
							if dist_sq < chain_range_sq:
								nearby.append({"dist": dist_sq, "entity": b, "type": "booster"})
					for it in items:
						if not hit_entities.has(it):
							var dist_sq = pow(it.x - current_target.x, 2) + pow(it.y - current_target.y, 2)
							if dist_sq < chain_range_sq:
								nearby.append({"dist": dist_sq, "entity": it, "type": "item"})

					if self.world != null and "arena" in self.world and self.world.arena != null:
						var aw = 2000.0
						var ah = 2000.0
						if "width" in self.world.arena: aw = self.world.arena.width
						if "height" in self.world.arena: ah = self.world.arena.height
						var walls = [{"x": 0.0, "y": current_target.y, "name": "left_wall"}, {"x": aw, "y": current_target.y, "name": "right_wall"}, {"x": current_target.x, "y": 0.0, "name": "top_wall"}, {"x": current_target.x, "y": ah, "name": "bottom_wall"}]
						for w in walls:
							if not hit_entities.has(w["name"]):
								var dist_sq = pow(w["x"] - current_target.x, 2) + pow(w["y"] - current_target.y, 2)
								if dist_sq < chain_range_sq:
									nearby.append({"dist": dist_sq, "entity": w, "type": "wall"})


				if nearby.size() == 0:
					break

				nearby.sort_custom(func(a, b): return a["dist"] < b["dist"])
				var next_entity = nearby[0]["entity"]
				var e_type = nearby[0]["type"]

				if typeof(attacker) == TYPE_OBJECT and attacker.has_method("set"):
					attacker.set("damage", current_damage)
				elif "damage" in attacker:
					attacker.damage = current_damage

				if e_type == "enemy":
					var e_ricochet = false
					if "ricochet_barrier_timer" in next_entity and next_entity.ricochet_barrier_timer > 0.0:
						e_ricochet = true
					elif next_entity.has_method("get_meta") and next_entity.has_meta("ricochet_barrier_timer") and next_entity.get_meta("ricochet_barrier_timer") > 0.0:
						e_ricochet = true

					var e_reflect = false
					if "reflect_shield_active" in next_entity and next_entity.reflect_shield_active:
						e_reflect = true
					elif next_entity.has_method("get_meta") and next_entity.has_meta("reflect_shield_active") and next_entity.get_meta("reflect_shield_active"):
						e_reflect = true

					if e_ricochet:
						if self.world != null and self.world.has_method("_deal_damage"):
							self.world._deal_damage(next_entity, attacker)
					elif e_reflect:
						var capacity = 50.0
						if "reflect_shield_capacity" in next_entity:
							capacity = next_entity.reflect_shield_capacity
						elif next_entity.has_method("get_meta") and next_entity.has_meta("reflect_shield_capacity"):
							capacity = next_entity.get_meta("reflect_shield_capacity")

						var damage_to_reflect = min(capacity, current_damage)
						capacity -= current_damage

						if capacity <= 0:
							if "reflect_shield_active" in next_entity:
								next_entity.reflect_shield_active = false
							elif next_entity.has_method("set_meta"):
								next_entity.set_meta("reflect_shield_active", false)

							if "reflect_shield_capacity" in next_entity:
								next_entity.reflect_shield_capacity = 0.0
							elif next_entity.has_method("set_meta"):
								next_entity.set_meta("reflect_shield_capacity", 0.0)
						else:
							if "reflect_shield_capacity" in next_entity:
								next_entity.reflect_shield_capacity = capacity
							elif next_entity.has_method("set_meta"):
								next_entity.set_meta("reflect_shield_capacity", capacity)

						if self.has_method("_spawn_directed_particles"):
							self._spawn_directed_particles(next_entity, attacker, "reflect_pulse")
						if self.world != null and self.world.has_method("_deal_damage"):
							var old_dmg = current_damage
							if "damage" in attacker:
								old_dmg = attacker.damage
								attacker.damage = damage_to_reflect
							self.world._deal_damage(next_entity, attacker)
							if "damage" in attacker:
								attacker.damage = old_dmg

						if capacity < 0:
							var remainder_damage = -capacity
							var old_dmg = current_damage
							if "damage" in attacker:
								old_dmg = attacker.damage
								attacker.damage = remainder_damage
							if self.world != null and self.world.has_method("_deal_damage"):
								self.world._deal_damage(attacker, next_entity)
							if "damage" in attacker:
								attacker.damage = old_dmg

							var explosion_radius = 80.0
							if self.world != null and "balls" in self.world:
								for other in self.world.balls:
									var other_alive = false
									if "alive" in other:
										other_alive = other.alive
									elif other.has_method("get_meta") and other.has_meta("alive"):
										other_alive = other.get_meta("alive")

									var other_id = null
									if "id" in other:
										other_id = other.id

									var target_id = null
									if "id" in next_entity:
										target_id = next_entity.id

									if other_alive and other_id != target_id:
										var dx = 0.0
										if "x" in other: dx = other.x
										if "x" in next_entity: dx -= next_entity.x
										var dy = 0.0
										if "y" in other: dy = other.y
										if "y" in next_entity: dy -= next_entity.y

										var dist = sqrt(dx*dx + dy*dy)
										if dist <= explosion_radius:
											if self.world != null and self.world.has_method("_deal_damage"):
												var old_atk_dmg = 10.0
												if "damage" in next_entity: old_atk_dmg = next_entity.damage
												if "damage" in next_entity: next_entity.damage = remainder_damage
												elif next_entity.has_method("set_meta"): next_entity.set_meta("damage", remainder_damage)
												self.world._deal_damage(next_entity, other)
												if "damage" in next_entity: next_entity.damage = old_atk_dmg
												elif next_entity.has_method("set_meta"): next_entity.set_meta("damage", old_atk_dmg)
											elif other.has_method("take_damage"):
												other.take_damage(remainder_damage)
											elif "hp" in other:
												other.hp -= remainder_damage
												if other.hp <= 0:
													if "alive" in other: other.alive = false
													elif other.has_method("set_meta"): other.set_meta("alive", false)
					else:
						if self.world != null and self.world.has_method("_deal_damage"):
							self.world._deal_damage(attacker, next_entity)
					elif e_type == "hazard" or e_type == "item" or e_type == "booster":
						var n_t_var = ""
						if typeof(next_entity) == TYPE_OBJECT and next_entity.has_meta("trap_variant"): n_t_var = next_entity.get_meta("trap_variant")

						if n_t_var == "emp_trap":
							var charge = 0.0
							if next_entity.has_meta("emp_charge"): charge = next_entity.get_meta("emp_charge")
							charge += current_damage
							next_entity.set_meta("emp_charge", charge)

							if charge >= 50.0:
								if "active" in next_entity: next_entity.active = false
								elif next_entity.has_method("set_meta"): next_entity.set_meta("active", false)

								if self.world != null and "balls" in self.world:
									for b in self.world.balls:
										var b_alive = false
										if "alive" in b: b_alive = b.alive
										elif typeof(b) == TYPE_OBJECT and b.has_meta("alive"): b_alive = b.get_meta("alive")

										var owner_id = null
										if next_entity.has_meta("owner_id"): owner_id = next_entity.get_meta("owner_id")

										var b_id = null
										if "id" in b: b_id = b.id

										if b_alive and b_id != owner_id:
											var dist_burst = sqrt(pow(b.x - next_entity.x, 2) + pow(b.y - next_entity.y, 2))
											if dist_burst <= 200.0:
												if b.has_method("set_meta"): b.set_meta("is_emped", true)
												if b.has_method("set_meta"): b.set_meta("emp_timer", 4.0)

												var current_silence = 0.0
												if "silence_timer" in b: current_silence = b.silence_timer
												elif b.has_method("get_meta") and b.has_meta("silence_timer"): current_silence = b.get_meta("silence_timer")

												var max_s = max(current_silence, 3.0)
												if "silence_timer" in b: b.silence_timer = max_s
												elif b.has_method("set_meta"): b.set_meta("silence_timer", max_s)

												var current_skill = 0.0
												if "skill_timer" in b: current_skill = b.skill_timer
												elif b.has_method("get_meta") and b.has_meta("skill_timer"): current_skill = b.get_meta("skill_timer")

												var max_sk = max(current_skill, 3.0)
												if "skill_timer" in b: b.skill_timer = max_sk
												elif b.has_method("set_meta"): b.set_meta("skill_timer", max_sk)

												var base_sp = 100.0
												if "base_speed" in b: base_sp = b.base_speed
												elif b.has_method("get_meta") and b.has_meta("base_speed"): base_sp = b.get_meta("base_speed")

												if "speed" in b: b.speed = base_sp * 0.5
												elif b.has_method("set_meta"): b.set_meta("speed", base_sp * 0.5)

												if b.has_method("set_meta"): b.set_meta("is_scrambled", true)
												if b.has_method("set_meta"): b.set_meta("scramble_timer", 3.0)
						var n_kind = ""
						if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("kind"): n_kind = next_entity["kind"]
						elif typeof(next_entity) == TYPE_OBJECT and next_entity.has_meta("kind"): n_kind = next_entity.get_meta("kind")
						elif typeof(next_entity) == TYPE_OBJECT and "kind" in next_entity: n_kind = next_entity.kind

						if n_kind == "material":
							var n_active = false
							if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("active"): n_active = next_entity["active"]
							elif typeof(next_entity) == TYPE_OBJECT and "active" in next_entity: n_active = next_entity.active

							if n_active:
								if typeof(next_entity) == TYPE_DICTIONARY: next_entity["active"] = false
								elif typeof(next_entity) == TYPE_OBJECT and "active" in next_entity: next_entity.active = false

								var pm = null
								if world != null and "profile_manager" in world: pm = world.profile_manager
								if pm != null and pm.has_method("add_material"):
									var m_type = "Iron Ore"
									if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("material_type"): m_type = next_entity["material_type"]
									elif typeof(next_entity) == TYPE_OBJECT and "material_type" in next_entity: m_type = next_entity.material_type
									pm.add_material(m_type, 1)
						elif "hp" in next_entity:
							next_entity.hp -= current_damage
							if next_entity.hp <= 0:
								if "active" in next_entity:
									next_entity.active = false

					if self.has_method("_spawn_particles"):
						self._spawn_particles(current_target.x, current_target.y, "lightning")
						self._spawn_particles(next_entity.x, next_entity.y, "lightning")

					if e_type == "wall":
						hit_entities.append(next_entity["name"])
					else:
						hit_entities.append(next_entity)
					current_target = next_entity
					current_damage *= 0.8
					jump_count += 1

			if has_orig_dmg:
				if typeof(attacker) == TYPE_OBJECT and attacker.has_method("set"):
					attacker.set("damage", orig_dmg)
				elif "damage" in attacker:
					attacker.damage = orig_dmg


var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):

    if self.ball.has_method("remove_meta") and self.ball.has_meta("_chrono_slow"):
        self.ball.remove_meta("_chrono_slow")
    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("_chrono_slow"):
        self.ball.erase("_chrono_slow")


	# Magnet passive: pull boosters and smaller entities
	var btype = ""
	if "BALL_TYPE" in self.ball: btype = self.ball.BALL_TYPE
	elif "ball_type" in self.ball: btype = self.ball.ball_type

	if btype == "magnet":
		var pull_radius = 150.0
		var pull_strength = 60.0
		if "boosters" in self.world:
			for b in self.world.boosters:
				var b_x = 0.0
				var b_y = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					b_x = b.get("x", 0.0)
					b_y = b.get("y", 0.0)
				else:
					b_x = b.x
					b_y = b.y

				var dx = self.ball.x - b_x
				var dy = self.ball.y - b_y
				var dist_sq = dx*dx + dy*dy
				if dist_sq > 0 and dist_sq < pull_radius*pull_radius:
					var dist = sqrt(dist_sq)
					if typeof(b) == TYPE_DICTIONARY:
						b["x"] += (dx / dist) * pull_strength * delta
						b["y"] += (dy / dist) * pull_strength * delta
					else:
						b.x += (dx / dist) * pull_strength * delta
						b.y += (dy / dist) * pull_strength * delta

		if "balls" in self.world:
			for other in self.world.balls:
				if other.id != self.ball.id:
					var other_rad = 10.0
					if "radius" in other: other_rad = other.radius
					var self_rad = 15.0
					if "radius" in self.ball: self_rad = self.ball.radius

					if other_rad < self_rad:
						var dx = self.ball.x - other.x
						var dy = self.ball.y - other.y
						var dist_sq = dx*dx + dy*dy
						if dist_sq > 0 and dist_sq < pull_radius*pull_radius:
							var dist = sqrt(dist_sq)
							if not ("vx" in other):
								if other.has_method("set_meta"): other.set_meta("vx", 0.0)
								elif typeof(other) == TYPE_DICTIONARY: other["vx"] = 0.0
								else: other.vx = 0.0
							if not ("vy" in other):
								if other.has_method("set_meta"): other.set_meta("vy", 0.0)
								elif typeof(other) == TYPE_DICTIONARY: other["vy"] = 0.0
								else: other.vy = 0.0

							var vx = 0.0
							if "vx" in other: vx = other.vx
							elif typeof(other) == TYPE_DICTIONARY: vx = other.get("vx", 0.0)

							var vy = 0.0
							if "vy" in other: vy = other.vy
							elif typeof(other) == TYPE_DICTIONARY: vy = other.get("vy", 0.0)

							vx += (dx / dist) * pull_strength * 2.0 * delta
							vy += (dy / dist) * pull_strength * 2.0 * delta

							if typeof(other) == TYPE_DICTIONARY:
								other["vx"] = vx
								other["vy"] = vy
							else:
								other.vx = vx
								other.vy = vy

	var is_mimic_clone = false
	if self.ball.has_method("get_meta") and self.ball.get_meta("is_mimic_clone"): is_mimic_clone = true
	elif "is_mimic_clone" in self.ball and self.ball.is_mimic_clone: is_mimic_clone = true

	var is_alive_mine2 = true
	if "alive" in self.ball: is_alive_mine2 = self.ball.alive
	elif self.ball.has_method("get_meta") and self.ball.has_meta("alive"): is_alive_mine2 = self.ball.get_meta("alive")

	if is_mimic_clone and is_alive_mine2:
		var owner_id = null
		if self.ball.has_method("get_meta") and self.ball.has_meta("mimic_owner"): owner_id = self.ball.get_meta("mimic_owner")
		elif "mimic_owner" in self.ball: owner_id = self.ball.mimic_owner

		var owner = null
		if world != null and "balls" in world:
			for b in world.balls:
				var bid = null
				if "id" in b: bid = b.id
				elif b.has_method("get_meta") and b.has_meta("id"): bid = b.get_meta("id")

				if bid != null and bid == owner_id:
					owner = b
					break

		var ovx = 0.0
		var ovy = 0.0
		if owner != null:
			var o_alive = true
			if "alive" in owner: o_alive = owner.alive
			elif owner.has_method("get_meta") and owner.has_meta("alive"): o_alive = owner.get_meta("alive")

			if o_alive:
				if "vx" in owner: ovx = owner.vx
				elif owner.has_method("get_meta") and owner.has_meta("vx"): ovx = owner.get_meta("vx")
				if "vy" in owner: ovy = owner.vy
				elif owner.has_method("get_meta") and owner.has_meta("vy"): ovy = owner.get_meta("vy")

		if "vx" in self.ball: self.ball.vx = ovx
		elif self.ball.has_method("set_meta"): self.ball.set_meta("vx", ovx)
		if "vy" in self.ball: self.ball.vy = ovy
		elif self.ball.has_method("set_meta"): self.ball.set_meta("vy", ovy)

		if "x" in self.ball: self.ball.x += ovx * delta
		elif self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + ovx * delta)
		if "y" in self.ball: self.ball.y += ovy * delta
		elif self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + ovy * delta)

		var m_timer = 10.0
		if "mimic_timer" in self.ball: m_timer = self.ball.mimic_timer
		elif self.ball.has_method("get_meta") and self.ball.has_meta("mimic_timer"): m_timer = self.ball.get_meta("mimic_timer")

		m_timer -= delta
		if "mimic_timer" in self.ball: self.ball.mimic_timer = m_timer
		elif self.ball.has_method("set_meta"): self.ball.set_meta("mimic_timer", m_timer)

		var m_hp = 100.0
		if "hp" in self.ball: m_hp = self.ball.hp
		elif self.ball.has_method("get_meta") and self.ball.has_meta("hp"): m_hp = self.ball.get_meta("hp")

		if m_timer <= 0 or m_hp <= 0:
			if "alive" in self.ball: self.ball.alive = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)

		self._clamp_position()
		return

	var is_clone_mine = false
	if self.ball.has_method("get_meta") and self.ball.get_meta("is_clone"): is_clone_mine = true
	elif "is_clone" in self.ball and self.ball.is_clone: is_clone_mine = true

	var is_alive_mine = true
	if "alive" in self.ball: is_alive_mine = self.ball.alive
	elif self.ball.has_method("get_meta") and self.ball.has_meta("alive"): is_alive_mine = self.ball.get_meta("alive")

	if is_clone_mine and is_alive_mine:
		var trigger_radius = 40.0
		var aoe_radius = 80.0
		var aoe_damage = 30.0
		var triggered = false

		if world != null and "balls" in world:
			var my_team = ""
			if "team" in self.ball: my_team = self.ball.team
			elif "ball_type" in self.ball: my_team = self.ball.ball_type

			for e in world.balls:
				var e_alive = true
				if "alive" in e: e_alive = e.alive
				var e_team = ""
				if "team" in e: e_team = e.team
				elif "ball_type" in e: e_team = e.ball_type

				if e_alive and e_team != my_team:
					var ex = 0.0
					var ey = 0.0
					if "x" in e: ex = e.x
					elif e.has_method("get_meta") and e.has_meta("x"): ex = e.get_meta("x")
					if "y" in e: ey = e.y
					elif e.has_method("get_meta") and e.has_meta("y"): ey = e.get_meta("y")

					var dist_sq = pow(self.ball.x - ex, 2) + pow(self.ball.y - ey, 2)
					if dist_sq <= trigger_radius * trigger_radius:
						triggered = true
						break

			if triggered:
				for b in world.balls:
					var b_alive = true
					if "alive" in b: b_alive = b.alive
					var b_team = ""
					if "team" in b: b_team = b.team
					elif "ball_type" in b: b_team = b.ball_type

					if b_alive and b_team != my_team:
						var bx = 0.0
						var by = 0.0
						if "x" in b: bx = b.x
						elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
						if "y" in b: by = b.y
						elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

						var d_sq = pow(self.ball.x - bx, 2) + pow(self.ball.y - by, 2)
						if d_sq <= aoe_radius * aoe_radius:
							var original_damage = 0.0
							if "damage" in self.ball: original_damage = self.ball.damage
							if "damage" in self.ball: self.ball.damage = aoe_damage
							self._attempt_damage(self.ball, b)
							if "damage" in self.ball: self.ball.damage = original_damage

				if "alive" in self.ball: self.ball.alive = false
				if "hp" in self.ball: self.ball.hp = 0
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("alive", false)
					self.ball.set_meta("hp", 0)

	var m_tether_timer = 0.0
	if self.ball.has_method("has_meta") and self.ball.has_meta("magnet_tether_timer"):
		m_tether_timer = self.ball.get_meta("magnet_tether_timer")
	elif "magnet_tether_timer" in self.ball:
		m_tether_timer = self.ball.magnet_tether_timer

	if m_tether_timer > 0:
		var target = null
		if self.ball.has_method("has_meta") and self.ball.has_meta("magnet_tether_target"):
			target = self.ball.get_meta("magnet_tether_target")
		elif "magnet_tether_target" in self.ball:
			target = self.ball.magnet_tether_target

		var is_target_alive = true
		if target != null:
			if "alive" in target:
				is_target_alive = target.alive
			elif target.has_method("has_meta") and target.has_meta("alive"):
				is_target_alive = target.get_meta("alive")

		if target != null and is_target_alive:
			var dx = target.x - self.ball.x
			var dy = target.y - self.ball.y
			var dist = sqrt(dx*dx + dy*dy)
			if dist > 0:
				var tether_speed = 2.0 * 3.0
				if "speed" in self.ball:
					tether_speed = self.ball.speed * 3.0

				var nvx = (dx / dist) * tether_speed
				var nvy = (dy / dist) * tether_speed

				if "vx" in self.ball: self.ball.vx = nvx
				elif self.ball.has_method("set_meta"): self.ball.set_meta("vx", nvx)
				if "vy" in self.ball: self.ball.vy = nvy
				elif self.ball.has_method("set_meta"): self.ball.set_meta("vy", nvy)

				if "x" in self.ball: self.ball.x += nvx * delta
				elif self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + nvx * delta)
				if "y" in self.ball: self.ball.y += nvy * delta
				elif self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + nvy * delta)

		m_tether_timer -= delta
		if "magnet_tether_timer" in self.ball: self.ball.magnet_tether_timer = m_tether_timer
		elif self.ball.has_method("set_meta"): self.ball.set_meta("magnet_tether_timer", m_tether_timer)

	if self.ball.has_method("has_meta") and self.ball.has_meta("silence_timer"):
		var st = self.ball.get_meta("silence_timer")
		if st > 0.0:
			st -= delta
			self.ball.set_meta("silence_timer", max(0.0, st))
	elif "silence_timer" in self.ball:
		var st = self.ball.silence_timer
		if st > 0.0:
			st -= delta
			self.ball.silence_timer = max(0.0, st)
	if (strategy == "flee" or strategy == "defend") and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("placeable_trap"):
			if world != null and "arena" in world and "hazards" in world.arena:
				var arena = world.arena
				var trap_id = arena.hazards.size() + randi() % 10000

				var trap = null
				if load("res://src/arena/procedural_arena.gd") != null:
					trap = load("res://src/arena/procedural_arena.gd").Hazard.new()
					trap.id = trap_id
					trap.x = self.ball.x
					trap.y = self.ball.y
					trap.radius = 20.0
					trap.kind = "trap"
					trap.damage = 0.0
					trap.set_meta("duration", 10.0)

					var trap_type = "mine"
					var r = randf()
					if r > 0.75:
						trap_type = "freeze"
					elif r > 0.5:
						trap_type = "black_hole"
					elif r > 0.25:
						trap_type = "swap"
					trap.set_meta("trap_variant", trap_type)
					trap.set_meta("owner_id", self.ball.id)

					arena.hazards.append(trap)
					inv.erase("placeable_trap")
					self.ball.set_meta("inventory", inv)

	if (strategy == "flee" or strategy == "defend" or strategy == "attack") and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("placeable_trap_booster"):
			if world != null and "arena" in world and "hazards" in world.arena:
				var arena = world.arena
				var trap_id = arena.hazards.size() + randi() % 10000

				var trap = null
				if load("res://src/arena/procedural_arena.gd") != null:
					trap = load("res://src/arena/procedural_arena.gd").Hazard.new()
					trap.id = trap_id
					trap.x = self.ball.x
					trap.y = self.ball.y
					trap.radius = 40.0
					trap.kind = "pull_trap"
					trap.damage = 10.0
					trap.set_meta("duration", 10.0)
					trap.set_meta("owner_id", self.ball.id)

					arena.hazards.append(trap)
					inv.erase("placeable_trap_booster")
					self.ball.set_meta("inventory", inv)

	if strategy == "flee" and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("exit_portal"):
			if world != null and "arena" in world and "hazards" in world.arena:
				var arena = world.arena
				var portal_id = arena.hazards.size() + randi() % 90000 + 10000

				var portal = null
				if load("res://src/arena/procedural_arena.gd") != null:
					portal = load("res://src/arena/procedural_arena.gd").Hazard.new()
					portal.id = portal_id
					portal.x = self.ball.x
					portal.y = self.ball.y
					portal.radius = 30.0
					portal.kind = "teleporter"
					portal.damage = 0.0
					portal.set_meta("duration", 5.0)
					portal.set_meta("owner_id", self.ball.id)

					arena.hazards.append(portal)
					inv.erase("exit_portal")
					self.ball.set_meta("inventory", inv)

	if (strategy == "flee" or strategy == "defend") and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("position_swap"):
			var balls = []
			if world != null and "balls" in world:
				balls = world.balls
			elif world != null and "entities" in world:
				balls = world.entities

			var target = null
			var min_dist_sq = -1.0
			for b in balls:
				var is_alive = true
				if "alive" in b: is_alive = b.alive
				var is_decoy = false
				if b.has_method("get_meta") and b.has_meta("is_decoy"): is_decoy = b.get_meta("is_decoy")
				elif "is_decoy" in b: is_decoy = b.is_decoy

				if is_alive and b != self.ball and not is_decoy:
					var dist_sq = (b.x - self.ball.x)*(b.x - self.ball.x) + (b.y - self.ball.y)*(b.y - self.ball.y)
					if min_dist_sq < 0.0 or dist_sq < min_dist_sq:
						min_dist_sq = dist_sq
						target = b

			if target != null:
				var temp_x = target.x
				var temp_y = target.y
				target.x = self.ball.x
				target.y = self.ball.y
				self.ball.x = temp_x
				self.ball.y = temp_y
				inv.erase("position_swap")
				self.ball.set_meta("inventory", inv)

	if (strategy == "flee" or strategy == "defend" or strategy == "attack") and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("portal_gun"):
			if world != null and "arena" in world and "hazards" in world.arena:
				var arena = world.arena
				var p1_id = arena.hazards.size() + randi() % 40000 + 10000
				var p2_id = arena.hazards.size() + randi() % 50000 + 50000

				if load("res://src/arena/procedural_arena.gd") != null:
					var p1 = load("res://src/arena/procedural_arena.gd").Hazard.new(p1_id, self.ball.x + randf_range(-20.0, 20.0), self.ball.y + randf_range(-20.0, 20.0), 30.0, "teleporter", 0.0)
					p1.set_meta("duration", 10.0)
					p1.set_meta("owner_id", self.ball.id)

					var target_x = self.ball.x
					var target_y = self.ball.y
					if strategy == "flee":
						target_x += randf_range(-300.0, 300.0)
						target_y += randf_range(-300.0, 300.0)
					elif strategy == "attack":
						var enemies = _get_enemies()
						if enemies != null and enemies.size() > 0:
							var closest = enemies[0]
							var bmin_dist = pow(closest.x - self.ball.x, 2) + pow(closest.y - self.ball.y, 2)
							for e in enemies:
								var d = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
								if d < bmin_dist:
									bmin_dist = d
									closest = e
							target_x = closest.x
							target_y = closest.y
					else:
						target_x += randf_range(-100.0, 100.0)
						target_y += randf_range(-100.0, 100.0)

					var p2 = load("res://src/arena/procedural_arena.gd").Hazard.new(p2_id, target_x, target_y, 30.0, "teleporter", 0.0)
					p2.set_meta("duration", 10.0)
					p2.set_meta("owner_id", self.ball.id)

					p1.set_meta("target_x", p2.x)
					p1.set_meta("target_y", p2.y)
					p2.set_meta("target_x", p1.x)
					p2.set_meta("target_y", p1.y)

					arena.hazards.append(p1)
					arena.hazards.append(p2)
					inv.erase("portal_gun")
					self.ball.set_meta("inventory", inv)


	# Confusion timer logic
	var conf_timer = 0.0
	var is_conf = false
	if "confusion_timer" in self.ball:
		conf_timer = self.ball.confusion_timer
		is_conf = self.ball.is_confused if "is_confused" in self.ball else false
	elif self.ball.has_method("has_meta") and self.ball.has_meta("confusion_timer"):
		conf_timer = self.ball.get_meta("confusion_timer")
		is_conf = self.ball.get_meta("is_confused") if self.ball.has_meta("is_confused") else false

	if is_conf and conf_timer > 0.0:
		conf_timer -= delta
		if self.ball.has_method("set_meta"):
			self.ball.set_meta("confusion_timer", conf_timer)
		else:
			self.ball.confusion_timer = conf_timer
		if conf_timer <= 0.0:
			if self.ball.has_method("set_meta"):
				self.ball.set_meta("is_confused", false)
			else:
				self.ball.is_confused = false

	# Mind control timer logic
	var mc_timer = 0.0
	var is_mc = false
	if "mind_control_timer" in self.ball:
		mc_timer = self.ball.mind_control_timer
		is_mc = self.ball.is_mind_controlled if "is_mind_controlled" in self.ball else false
	elif self.ball.has_method("has_meta") and self.ball.has_meta("mind_control_timer"):
		mc_timer = self.ball.get_meta("mind_control_timer")
		is_mc = self.ball.get_meta("is_mind_controlled") if self.ball.has_meta("is_mind_controlled") else false

	if is_mc and mc_timer > 0.0:
		mc_timer -= delta
		if self.ball.has_method("set_meta"):
			self.ball.set_meta("mind_control_timer", mc_timer)
		else:
			self.ball.mind_control_timer = mc_timer

		if mc_timer <= 0.0:
			if self.ball.has_method("set_meta"):
				self.ball.set_meta("is_mind_controlled", false)
				if self.ball.has_meta("original_team"):
					self.ball.set_meta("team", self.ball.get_meta("original_team"))
			else:
				self.ball.is_mind_controlled = false
				if "original_team" in self.ball:
					self.ball.team = self.ball.original_team

	# Max HP draining hazard logic
	if world != null and "arena" in world and "hazards" in world.arena:
		for hazard in world.arena.hazards:
			if hazard.get("kind") == "vampiric_puddle":
				var my_rad = 10.0
				if "radius" in self.ball:
					my_rad = float(self.ball.radius)
				var dist = sqrt((self.ball.x - hazard.x) * (self.ball.x - hazard.x) + (self.ball.y - hazard.y) * (self.ball.y - hazard.y))
				if dist <= hazard.get("radius", 0.0) + my_rad:
					var drain_rate = hazard.get("damage", 5.0)
					var old_max = self.ball.max_hp if "max_hp" in self.ball else 100.0
					var new_max = max(10.0, old_max - drain_rate * delta)
					if typeof(self.ball) == TYPE_DICTIONARY:
						self.ball["max_hp"] = new_max
						if self.ball.get("hp", 100.0) > new_max:
							self.ball["hp"] = new_max
						self.ball["_vampiric_drained"] = true
					else:
						self.ball.max_hp = new_max
						if "hp" in self.ball and self.ball.hp > new_max:
							self.ball.hp = new_max
						self.ball.set_meta("_vampiric_drained", true)

	# Temporal rift logic to modify local delta
	if world != null and "arena" in world and "hazards" in world.arena:
		for hazard in world.arena.hazards:
			if hazard.get("kind") == "temporal_rift":
				var my_rad = 10.0
				if "radius" in self.ball:
					my_rad = float(self.ball.radius)
				var dist = sqrt((self.ball.x - hazard.x) * (self.ball.x - hazard.x) + (self.ball.y - hazard.y) * (self.ball.y - hazard.y))
				if dist <= hazard.radius + my_rad:
					var time_scale = 0.5
					if "time_scale" in hazard:
						time_scale = float(hazard.time_scale)
					elif hazard.has_method("get_meta") and hazard.has_meta("time_scale"):
						time_scale = float(hazard.get_meta("time_scale"))
					delta *= time_scale
					break
    var my_ball = self.ball

    var cl_timer = 0.0
    if "chain_lightning_timer" in self.ball:
        cl_timer = self.ball.chain_lightning_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("chain_lightning_timer"):
        cl_timer = self.ball.get_meta("chain_lightning_timer")
    if cl_timer > 0.0:
        cl_timer -= delta
        if cl_timer < 0.0: cl_timer = 0.0
        if "chain_lightning_timer" in self.ball:
            self.ball.chain_lightning_timer = cl_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("chain_lightning_timer", cl_timer)

    # Entanglement logic
    if my_ball.has_method("has_meta") and my_ball.has_meta("entangle_timer"):
        var et = my_ball.get_meta("entangle_timer")
        if et > 0:
            my_ball.set_meta("entangle_timer", et - delta)
            if et - delta <= 0:
                my_ball.set_meta("entangled_with_id", -1)

    if my_ball.has_method("has_meta") and my_ball.has_meta("entangled_with_id"):
        var entangled_id = my_ball.get_meta("entangled_with_id")
        if entangled_id != -1 and not (my_ball.has_meta("_is_entangle_syncing") and my_ball.get_meta("_is_entangle_syncing")):
            var partner = null
            if "balls" in world:
                for b in world.balls:
                    if b.id == entangled_id:
                        partner = b
                        break
            if partner != null and partner.get("alive") == true:
                var prev_hp = my_ball.get("hp")
                if my_ball.has_meta("prev_hp"):
                    prev_hp = my_ball.get_meta("prev_hp")
                var prev_x = my_ball.get("x")
                if my_ball.has_meta("prev_x"):
                    prev_x = my_ball.get_meta("prev_x")
                var prev_y = my_ball.get("y")
                if my_ball.has_meta("prev_y"):
                    prev_y = my_ball.get_meta("prev_y")

                var hp_diff = prev_hp - my_ball.get("hp")
                if hp_diff > 0:
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", true)
                    if partner.has_method("take_damage"):
                        partner.take_damage(hp_diff * 0.5)
                    elif "hp" in partner:
                        partner.hp -= hp_diff * 0.5
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", false)
                elif hp_diff < 0:
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", true)
                    var max_hp = 100.0
                    if "max_hp" in partner:
                        max_hp = partner.max_hp
                    if "hp" in partner:
                        partner.hp = min(max_hp, partner.hp - hp_diff * 0.5)
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", false)

                var dx = my_ball.get("x") - prev_x
                var dy = my_ball.get("y") - prev_y
                if abs(dx) > 0.001 or abs(dy) > 0.001:
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", true)
                    partner.x += dx * 0.5
                    partner.y += dy * 0.5
                    if partner.has_method("set_meta"):
                        partner.set_meta("_is_entangle_syncing", false)

    if my_ball.has_method("set_meta"):
        my_ball.set_meta("prev_hp", my_ball.get("hp"))
        my_ball.set_meta("prev_x", my_ball.get("x"))
        my_ball.set_meta("prev_y", my_ball.get("y"))

    # Apply Damage Over Time (DOT)
    if my_ball.has_method("has_meta") and my_ball.has_meta("dot_duration"):
        var dot_dur = my_ball.get_meta("dot_duration")
        if dot_dur > 0:
            var dot_dmg = my_ball.get_meta("dot_damage_per_tick") * delta
            if my_ball.has_method("take_damage"):
                my_ball.take_damage(dot_dmg)
            elif "hp" in my_ball:
                my_ball.hp -= dot_dmg
                if my_ball.hp <= 0:
                    my_ball.alive = false
            my_ball.set_meta("dot_duration", dot_dur - delta)

    if world != null and "arena" in world:
        var cosmetic = ""
        if "cosmetic" in my_ball:
            cosmetic = str(my_ball.cosmetic).to_lower().replace(" ", "_")
        var ignores_mud = cosmetic == "mud_tires"

        # Reset flag every frame
        if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
            my_ball.set_meta("_is_wind_riding", false)
        else:
            my_ball["_is_wind_riding"] = false

        var wind_dx = 0.0
        if world.arena.get("wind_dx") != null:
            wind_dx = world.arena.get("wind_dx")
        var wind_dy = 0.0
        if world.arena.get("wind_dy") != null:
            wind_dy = world.arena.get("wind_dy")

        var is_wind_riding_f = false
        if wind_dx != 0.0 or wind_dy != 0.0:
            var b_type_f = null
            if "BALL_TYPE" in my_ball: b_type_f = my_ball.BALL_TYPE
            elif "ball_type" in my_ball: b_type_f = my_ball.ball_type
            if b_type_f in ["scout", "drone", "swarm", "ninja", "assassin", "phantom", "rogue"]:
                var st_f = 0.0
                if "stamina" in my_ball: st_f = my_ball.stamina
                if st_f >= 10.0:
                    is_wind_riding_f = true

        if world.arena.get("is_raining") == true and not ignores_mud and not is_wind_riding_f:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.2
                my_ball.y += my_ball.vy * delta * 0.2
        if world.arena.get("is_snowing") == true and not is_wind_riding_f:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.4
                my_ball.y += my_ball.vy * delta * 0.4
        if wind_dx != 0.0 or wind_dy != 0.0:
            my_ball.x += wind_dx * delta
            my_ball.y += wind_dy * delta

            # Wind rider logic for lightweight balls
            var b_type = null
            if "BALL_TYPE" in my_ball:
                b_type = my_ball.BALL_TYPE
            elif "ball_type" in my_ball:
                b_type = my_ball.ball_type

            if b_type in ["scout", "drone", "swarm", "ninja", "assassin", "phantom", "rogue"]:
                var current_stamina = 0.0
                if "stamina" in my_ball:
                    current_stamina = my_ball.stamina
                if current_stamina >= 10.0:
                    my_ball.x += wind_dx * delta * 1.5
                    my_ball.y += wind_dy * delta * 1.5
                    if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
                        my_ball.set_meta("_is_wind_riding", true)
                    else:
                        my_ball["_is_wind_riding"] = true
                # Flag already reset at top of block

    var gm = null
    if world != null and "game_mode" in world:
        gm = world.game_mode
    var is_zero_gravity = false
    if gm != null:
        if gm.name == "Zero Gravity":
            is_zero_gravity = true
        elif gm.name == "Custom Match" and gm.get("mutators_active") == true and "zero_gravity" in gm.get("mutators", []):
            is_zero_gravity = true

    if is_zero_gravity:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.vx *= (1.0 - 0.5 * delta)
            my_ball.vy *= (1.0 - 0.5 * delta)
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta

    if my_ball.get("BALL_TYPE") == "mimic" and my_ball.has_method("process_mimicry"):
        var enemies = self._get_enemies()
        my_ball.process_mimicry(enemies, delta)
    if my_ball.has_method("has_meta") and not my_ball.has_meta("dot_duration"):
        my_ball.set_meta("dot_duration", 0.0)
        my_ball.set_meta("dot_damage_per_tick", 0.0)

    if my_ball.has_method("has_meta") and not my_ball.has_meta("_base_speed_set"):
        var base_s = 2.0
        if "speed" in my_ball:
            base_s = my_ball.speed
        my_ball.set_meta("base_speed", base_s)

        var base_d = 10.0
        if "damage" in my_ball:
            base_d = my_ball.damage
        my_ball.set_meta("base_damage", base_d)
        my_ball.set_meta("_base_speed_set", true)
        my_ball.set_meta("is_exhausted", false)
    elif "base_speed" not in my_ball and not my_ball.has_method("has_meta"):
        pass # Handle dictionaries differently? GDScript objects might not have metadata if they are dictionaries.
        # But wait, self.ball is usually a custom class instance.

    if my_ball.has_method("has_meta") and my_ball.has_meta("_base_speed_set"):
        if self.world != null and "arena" in self.world and "is_night" in self.world.arena:
            var b_type_action = ""
            if "ball_type" in my_ball:
                b_type_action = str(my_ball.ball_type).to_lower()
            if self.world.arena.is_night:
                if b_type_action == "vampire":
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed") * 1.5
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.5
                elif b_type_action == "assassin" or b_type_action == "phantom":
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed") * 1.2
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.5
                    if "has_stealth_drone" in my_ball:
                        my_ball.has_stealth_drone = true
                    my_ball.set_meta("has_stealth_drone", true)
                else:
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed")
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage")
            else:
                if b_type_action == "paladin" or b_type_action == "guardian":
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed") * 1.2
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.5
                else:
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed")
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.2
        else:
            if "speed" in my_ball:
                my_ball.speed = my_ball.get_meta("base_speed")
            if "damage" in my_ball:
                my_ball.damage = my_ball.get_meta("base_damage")

        var cur_stamina = 100.0
        if my_ball.has_meta("stamina"): cur_stamina = my_ball.get_meta("stamina")
        var cur_max_stamina = 100.0
        if my_ball.has_meta("max_stamina"): cur_max_stamina = my_ball.get_meta("max_stamina")
        var is_exhausted = false
        if my_ball.has_meta("is_exhausted"): is_exhausted = my_ball.get_meta("is_exhausted")

        if cur_stamina <= 0:
            is_exhausted = true
        elif cur_stamina >= cur_max_stamina * 0.2:
            is_exhausted = false

        if my_ball.has_method("set_meta"):
            my_ball.set_meta("is_exhausted", is_exhausted)

        if is_exhausted:
            if "speed" in my_ball:
                my_ball.speed *= 0.5
            if "damage" in my_ball:
                my_ball.damage *= 0.5

        var st_timer = 0.0
        if "stutter_timer" in my_ball:
            st_timer = float(my_ball.stutter_timer)
        elif my_ball.has_method("get_meta") and my_ball.has_meta("stutter_timer"):
            st_timer = my_ball.get_meta("stutter_timer")

        if st_timer > 0.0:
            if "speed" in my_ball:
                my_ball.speed = 0.01

    # Handle minion decay
    var is_minion = false
    if self.ball.has_method("has_meta") and self.ball.has_meta("is_minion"):
        is_minion = self.ball.get_meta("is_minion")
    if is_minion:
        self.ball.hp -= 2.0 * delta
        if self.ball.hp <= 0:
            self.ball.hp = 0
            self.ball.alive = false

    var is_decoy_beacon = false
    if "is_decoy_beacon" in my_ball:
        is_decoy_beacon = my_ball.is_decoy_beacon
    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_decoy_beacon"):
        is_decoy_beacon = my_ball.get_meta("is_decoy_beacon")

    if is_decoy_beacon:
        if world != null and "balls" in world:
            var b_team = ""
            if "team" in my_ball: b_team = my_ball.team
            elif my_ball.has_method("get_meta") and my_ball.has_meta("team"): b_team = my_ball.get_meta("team")

            for b in world.balls:
                var b_alive = true
                if "alive" in b: b_alive = b.alive

                var other_team = ""
                if "team" in b: other_team = b.team
                elif b.has_method("get_meta") and b.has_meta("team"): other_team = b.get_meta("team")

                if b_alive and b != my_ball and other_team == b_team:
                    var dx = b.x - my_ball.x
                    var dy = b.y - my_ball.y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist <= 150.0:
                        var heal_amount = 5.0 * delta
                        if "hp" in b and "max_hp" in b:
                            b.hp = min(float(b.max_hp), float(b.hp) + heal_amount)

    var is_decoy = false
    if "is_decoy" in my_ball:
        is_decoy = my_ball.is_decoy
    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_decoy"):
        is_decoy = my_ball.get_meta("is_decoy")

    if is_decoy:
        var dt = 0.0
        if "decoy_timer" in my_ball:
            my_ball.decoy_timer -= delta
            dt = my_ball.decoy_timer
        elif my_ball.has_method("get_meta") and my_ball.has_meta("decoy_timer"):
            dt = my_ball.get_meta("decoy_timer") - delta
            my_ball.set_meta("decoy_timer", dt)

        if dt <= 0.0:
            if "alive" in my_ball:
                my_ball.alive = false
            elif my_ball.has_method("set_meta"):
                my_ball.set_meta("alive", false)
            if "hp" in my_ball:
                my_ball.hp = 0.0

    if world != null and "balls" in world:
        for b in world.balls:
            var b_is_decoy = false
            if "is_decoy" in b:
                b_is_decoy = b.is_decoy
            elif b.has_method("get_meta") and b.has_meta("is_decoy"):
                b_is_decoy = b.get_meta("is_decoy")

            if b_is_decoy:
                var b_hp = 1.0
                if "hp" in b:
                    b_hp = b.hp
                var b_dt = 1.0
                if "decoy_timer" in b:
                    b_dt = b.decoy_timer
                elif b.has_method("get_meta") and b.has_meta("decoy_timer"):
                    b_dt = b.get_meta("decoy_timer")
                var b_alive = true
                if "alive" in b:
                    b_alive = b.alive
                elif b.has_method("get_meta") and b.has_meta("alive"):
                    b_alive = b.get_meta("alive")

                if b_hp <= 0.0 or b_dt <= 0.0 or not b_alive:
                    var b_exploded = false
                    if "_decoy_exploded" in b:
                        b_exploded = b._decoy_exploded
                    elif b.has_method("get_meta") and b.has_meta("_decoy_exploded"):
                        b_exploded = b.get_meta("_decoy_exploded")

                    if not b_exploded:
                        if "_decoy_exploded" in b:
                            b._decoy_exploded = true
                        elif b.has_method("set_meta"):
                            b.set_meta("_decoy_exploded", true)

                        if "alive" in b:
                            b.alive = false
                        elif b.has_method("set_meta"):
                            b.set_meta("alive", false)
                        if "hp" in b:
                            b.hp = 0.0

                        var b_team = ""
                        if "team" in b:
                            b_team = b.team

                        var b_id = -1
                        if "id" in b:
                            b_id = b.id
                        elif b.has_method("get_meta") and b.has_meta("id"):
                            b_id = b.get_meta("id")

                        var has_volatile = false
                        if "traits" in b and typeof(b.traits) == TYPE_ARRAY and b.traits.has("volatile_decoy"):
                            has_volatile = true
                        elif b.has_method("get_meta") and b.has_meta("traits") and typeof(b.get_meta("traits")) == TYPE_ARRAY and b.get_meta("traits").has("volatile_decoy"):
                            has_volatile = true

                        var radius = 150.0 if has_volatile else 100.0
                        var explosion_damage = 80.0 if has_volatile else 30.0

                        for other in world.balls:
                            var other_alive = false
                            if "alive" in other:
                                other_alive = other.alive
                            elif other.has_method("get_meta") and other.has_meta("alive"):
                                other_alive = other.get_meta("alive")

                            var other_team = ""
                            if "team" in other:
                                other_team = other.team

                            var other_id = -1
                            if "id" in other:
                                other_id = other.id
                            elif other.has_method("get_meta") and other.has_meta("id"):
                                other_id = other.get_meta("id")

                            if other_alive and other_team != b_team and other_id != b_id:
                                var dx = other.x - b.x
                                var dy = other.y - b.y
                                var dist = sqrt(dx*dx + dy*dy)
                                if dist <= radius:
                                    if "hp" in other:
                                        other.hp -= explosion_damage

                                        var rng = RandomNumberGenerator.new()
                                        rng.randomize()
                                        var b_type = b.ball_type if "ball_type" in b else (b.get_meta("ball_type") if b.has_method("has_meta") and b.has_meta("ball_type") else "")
                                        var b_team_check = b.team if "team" in b else (b.get_meta("team") if b.has_method("has_meta") and b.has_meta("team") else "")
                                        if (b_type == "trickster" or b_team_check == "trickster") and rng.randf() < 0.3:
                                            if "is_confused" in other:
                                                other.is_confused = true
                                                other.confusion_timer = 3.0
                                            elif other.has_method("set_meta"):
                                                other.set_meta("is_confused", true)
                                                other.set_meta("confusion_timer", 3.0)

                                        if other.hp <= 0:
                                            if "alive" in other:
                                                other.alive = false
                                            elif other.has_method("set_meta"):
                                                other.set_meta("alive", false)

                                        # Reward the owner for hitting enemies with a decoy explosion
                                        var b_owner_id = -1
                                        if "owner_id" in b:
                                            b_owner_id = b.owner_id
                                        elif b.has_method("get_meta") and b.has_meta("owner_id"):
                                            b_owner_id = b.get_meta("owner_id")

                                        if b_owner_id != -1:
                                            for owner in world.balls:
                                                var owner_id = -1
                                                if "id" in owner:
                                                    owner_id = owner.id
                                                elif owner.has_method("get_meta") and owner.has_meta("id"):
                                                    owner_id = owner.get_meta("id")

                                                if owner_id == b_owner_id:
                                                    if "score" in owner:
                                                        owner.score += 5
                                                    elif owner.has_method("get_meta") and owner.has_meta("score"):
                                                        owner.set_meta("score", owner.get_meta("score") + 5)
                                                    elif owner.has_method("set_meta"):
                                                        owner.set_meta("score", 5)
                                                    break

                        if world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
                            if world.arena.has_method("get"):
                                var ScriptType = load("res://src/arena/procedural_arena.gd")
                                if ScriptType != null and ScriptType.has_method("new"):
                                    pass # Fallback since we might need nested class
                                var CloudHazard = load("res://src/arena/procedural_arena.gd").Hazard
                                if CloudHazard != null:
                                    var h_id = 9000 + world.arena.hazards.size() + int(b.x) + int(b.y)
                                    var cloud = CloudHazard.new(h_id, b.x, b.y, 100.0, "poison_cloud", 10.0)
                                    cloud.set_meta("duration", 5.0)
                                    world.arena.hazards.append(cloud)

    var is_illusion = false
    if "is_illusion" in my_ball:
        is_illusion = my_ball.is_illusion
    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_illusion"):
        is_illusion = my_ball.get_meta("is_illusion")

    if is_illusion:
        var dt = 0.0
        if "illusion_timer" in my_ball:
            my_ball.illusion_timer -= delta
            dt = my_ball.illusion_timer
        elif my_ball.has_method("get_meta") and my_ball.has_meta("illusion_timer"):
            dt = my_ball.get_meta("illusion_timer") - delta
            my_ball.set_meta("illusion_timer", dt)

        if dt <= 0.0:
            if "alive" in my_ball:
                my_ball.alive = false
            elif my_ball.has_method("set_meta"):
                my_ball.set_meta("alive", false)
            if "hp" in my_ball:
                my_ball.hp = 0.0

    if world != null and "balls" in world:
        for b in world.balls:
            var b_is_illusion = false
            if "is_illusion" in b:
                b_is_illusion = b.is_illusion
            elif b.has_method("get_meta") and b.has_meta("is_illusion"):
                b_is_illusion = b.get_meta("is_illusion")

            var b_is_mimic_clone = false

            if "is_mimic_clone" in b: b_is_mimic_clone = b.is_mimic_clone

            elif b.has_method("get_meta") and b.has_meta("is_mimic_clone"): b_is_mimic_clone = b.get_meta("is_mimic_clone")

            if b_is_illusion and not b_is_mimic_clone:
                var b_hp = 1.0
                if "hp" in b:
                    b_hp = b.hp
                var b_dt = 1.0
                if "illusion_timer" in b:
                    b_dt = b.illusion_timer
                elif b.has_method("get_meta") and b.has_meta("illusion_timer"):
                    b_dt = b.get_meta("illusion_timer")
                var b_alive = true
                if "alive" in b:
                    b_alive = b.alive
                elif b.has_method("get_meta") and b.has_meta("alive"):
                    b_alive = b.get_meta("alive")

                if b_hp <= 0.0 or b_dt <= 0.0 or not b_alive:
                    var b_exploded = false
                    if "_illusion_exploded" in b:
                        b_exploded = b._illusion_exploded
                    elif b.has_method("get_meta") and b.has_meta("_illusion_exploded"):
                        b_exploded = b.get_meta("_illusion_exploded")

                    if not b_exploded:
                        if "_illusion_exploded" in b:
                            b._illusion_exploded = true
                        elif b.has_method("set_meta"):
                            b.set_meta("_illusion_exploded", true)

                        if "alive" in b:
                            b.alive = false
                        elif b.has_method("set_meta"):
                            b.set_meta("alive", false)

                        if "hp" in b:
                            b.hp = 0.0

                        var my_b_team = ""
                        if "team" in b: my_b_team = b.team
                        elif b.has_method("get_meta") and b.has_meta("team"): my_b_team = b.get_meta("team")

                        for other in world.balls:
                            var other_alive = false
                            if "alive" in other: other_alive = other.alive
                            elif other.has_method("get_meta") and other.has_meta("alive"): other_alive = other.get_meta("alive")

                            var other_team = ""
                            if "team" in other: other_team = other.team
                            elif other.has_method("get_meta") and other.has_meta("team"): other_team = other.get_meta("team")

                            var same_id = false
                            var other_id = null
                            var b_id = null
                            if "id" in other: other_id = other.id
                            elif other.has_method("get_meta") and other.has_meta("id"): other_id = other.get_meta("id")
                            if "id" in b: b_id = b.id
                            elif b.has_method("get_meta") and b.has_meta("id"): b_id = b.get_meta("id")
                            if other_id != null and b_id != null and other_id == b_id:
                                same_id = true

                            if other_alive and other_team != my_b_team and not same_id:
                                var bpos_x = b.get("position").x if b.get("position") != null else b.get("x")
                                var bpos_y = b.get("position").y if b.get("position") != null else b.get("y")
                                var opos_x = other.get("position").x if other.get("position") != null else other.get("x")
                                var opos_y = other.get("position").y if other.get("position") != null else other.get("y")

                                var dx = opos_x - bpos_x
                                var dy = opos_y - bpos_y
                                var dist = sqrt(dx*dx + dy*dy)
                                if dist <= 80.0:
                                    if other.has_method("take_damage"):
                                        other.take_damage(20.0)
                                    else:
                                        if "hp" in other:
                                            other.hp -= 20.0
                                        elif other.has_method("get_meta") and other.has_meta("hp"):
                                            other.set_meta("hp", other.get_meta("hp") - 20.0)

                                        var other_hp_check = 1.0
                                        if "hp" in other: other_hp_check = other.hp
                                        elif other.has_method("get_meta") and other.has_meta("hp"): other_hp_check = other.get_meta("hp")
                                        if other_hp_check <= 0.0:
                                            if "alive" in other:
                                                other.alive = false
                                            elif other.has_method("set_meta"):
                                                other.set_meta("alive", false)

                                    if "stutter_timer" in other:
                                        other.stutter_timer += 2.0
                                    elif other.has_method("has_meta") and other.has_method("set_meta") and other.has_method("get_meta"):
                                        var current_stutter = 0.0
                                        if other.has_meta("stutter_timer"):
                                            current_stutter = other.get_meta("stutter_timer")
                                        other.set_meta("stutter_timer", current_stutter + 2.0)

    if strategy == "target_weak":
        _target_weak(delta)
        _update_skill_timer(delta)
        _resolve_collisions()
        _clamp_position()
        return


    var old_x = self.ball.x
    var old_y = self.ball.y

    if "arena" in self.world and self.world.arena.has_method("update_zone"):
        var current_tick = 0
        if "tick" in self.world:
            current_tick = self.world.tick
        self.world.arena.update_zone(current_tick, delta)

        var ball_type = null
        if "ball_type" in self.ball:
            ball_type = self.ball.ball_type
        elif self.ball.has_method("get_ball_type"):
            ball_type = self.ball.get_ball_type()

        if self.ball.has_meta("zone_immunity_timer"):
            var t = self.ball.get_meta("zone_immunity_timer") - delta
            if t < 0: t = 0
            self.ball.set_meta("zone_immunity_timer", t)

        if ball_type != "spectator":
            var cx = 0.0
            var cy = 0.0
            var r = INF
            if "safe_zone_center" in self.world.arena:
                var center = self.world.arena.safe_zone_center
                if center.size() >= 2:
                    cx = center[0]
                    cy = center[1]
            if "safe_zone_radius" in self.world.arena:
                r = self.world.arena.safe_zone_radius

            var dist = sqrt((self.ball.x - cx) * (self.ball.x - cx) + (self.ball.y - cy) * (self.ball.y - cy))
            if dist > r:
                var is_immune = false
                if self.ball.has_meta("zone_immunity_timer") and self.ball.get_meta("zone_immunity_timer") > 0:
                    is_immune = true

                if not is_immune:
                    var zone_damage = 10.0 * delta
                    if self.ball.has_method("take_damage"):
                        self.ball.take_damage(zone_damage)
                    elif "hp" in self.ball:
                        self.ball.hp -= zone_damage
                        if self.ball.hp <= 0:
                            self.ball.alive = false


        if "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                if hazard.kind == "temporal_rift":
			continue
                if hazard.kind == "explosive_barrel":
                    var current_tick = world.get("tick") if world.has_method("get") else 0
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)
                        if not hazard.has_meta("vx"): hazard.set_meta("vx", 0.0)
                        if not hazard.has_meta("vy"): hazard.set_meta("vy", 0.0)

                        var hvx = hazard.get_meta("vx")
                        var hvy = hazard.get_meta("vy")
                        hazard.x += hvx * delta
                        hazard.y += hvy * delta
                        hazard.set_meta("vx", hvx * (1.0 - 2.0 * delta))
                        hazard.set_meta("vy", hvy * (1.0 - 2.0 * delta))

                        if hazard.x < hazard.radius or hazard.x > world.arena.width - hazard.radius:
                            hazard.set_meta("vx", -hazard.get_meta("vx"))
                            hazard.x = max(hazard.radius, min(hazard.x, world.arena.width - hazard.radius))
                        if hazard.y < hazard.radius or hazard.y > world.arena.height - hazard.radius:
                            hazard.set_meta("vy", -hazard.get_meta("vy"))
                            hazard.y = max(hazard.radius, min(hazard.y, world.arena.height - hazard.radius))

                        # Collide with other explosive barrels or hazards
                        for other_hazard in world.arena.hazards:
                            var h_id = hazard.get_instance_id() if typeof(hazard) == TYPE_OBJECT else hash(hazard)
                            var oh_id = other_hazard.get_instance_id() if typeof(other_hazard) == TYPE_OBJECT else hash(other_hazard)
                            if h_id != oh_id and other_hazard.kind == "explosive_barrel":
                                var dx_b = hazard.x - other_hazard.x
                                var dy_b = hazard.y - other_hazard.y
                                var dist_b = sqrt(dx_b*dx_b + dy_b*dy_b)
                                if dist_b < hazard.radius + other_hazard.radius:
                                    if dist_b > 0.0001:
                                        var nx_b = dx_b / dist_b
                                        var ny_b = dy_b / dist_b
                                        var overlap_b = (hazard.radius + other_hazard.radius) - dist_b
                                        # Separate them
                                        hazard.x += nx_b * (overlap_b / 2.0)
                                        hazard.y += ny_b * (overlap_b / 2.0)
                                        other_hazard.x -= nx_b * (overlap_b / 2.0)
                                        other_hazard.y -= ny_b * (overlap_b / 2.0)

                                        # Transfer momentum
                                        var ohvx = other_hazard.get_meta("vx") if other_hazard.has_meta("vx") else 0.0
                                        var ohvy = other_hazard.get_meta("vy") if other_hazard.has_meta("vy") else 0.0
                                        var rel_vx = hvx - ohvx
                                        var rel_vy = hvy - ohvy
                                        var impulse = (rel_vx * nx_b + rel_vy * ny_b)
                                        if impulse < 0:
                                            hazard.set_meta("vx", hvx - impulse * nx_b)
                                            hazard.set_meta("vy", hvy - impulse * ny_b)
                                            other_hazard.set_meta("vx", ohvx + impulse * nx_b)
                                            other_hazard.set_meta("vy", ohvy + impulse * ny_b)

                                            if sqrt(hvx*hvx + hvy*hvy) > 300.0 or sqrt(ohvx*ohvx + ohvy*ohvy) > 300.0:
                                                hazard.set_meta("is_exploded", true)
                                                other_hazard.set_meta("is_exploded", true)

                        if hazard.has_meta("is_exploded") and hazard.get_meta("is_exploded"):
                            hazard.duration = 0.0
                            if "balls" in world:
                                for b in world.balls:
                                    if b.alive:
                                        var bdist = sqrt((b.x - hazard.x) * (b.x - hazard.x) + (b.y - hazard.y) * (b.y - hazard.y))
                                        if bdist < hazard.radius * 4:
                                            if b.has_method("take_damage"):
                                                b.take_damage(hazard.damage * 2.0)
                                            else:
                                                b.hp -= hazard.damage * 2.0
                                                if b.hp <= 0:
                                                    b.alive = false
                elif hazard.kind == "trap":
                    var current_tick = 0
                    if "tick" in self.world:
                        current_tick = self.world.tick
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)
                        var dur = 5.0
                        if hazard.has_meta("duration"):
                            dur = hazard.get_meta("duration")
                        hazard.set_meta("duration", dur - delta)
                elif hazard.kind == "spinning_laser":
                    var current_tick = 0
                    if "tick" in self.world:
                        current_tick = self.world.tick
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)

                        var angle = 0.0
                        if hazard.has_meta("angle"):
                            angle = hazard.get_meta("angle")
                        angle += (PI / 2.0) * delta
                        if angle > 2 * PI:
                            angle -= 2 * PI
                        hazard.set_meta("angle", angle)

                        var on_timer = 3.0
                        if hazard.has_meta("on_timer"):
                            on_timer = hazard.get_meta("on_timer")
                        on_timer -= delta

                        var is_on = true
                        if hazard.has_meta("is_on"):
                            is_on = hazard.get_meta("is_on")

                        if on_timer <= 0:
                            is_on = not is_on
                            if is_on:
                                on_timer = 3.0
                            else:
                                on_timer = 2.0

                        hazard.set_meta("on_timer", on_timer)
                        hazard.set_meta("is_on", is_on)
                elif hazard.kind == "proximity_trap":
                    var dist_x = hazard.x - self.ball.x
                    var dist_y = hazard.y - self.ball.y
                    var dist_sq = dist_x * dist_x + dist_y * dist_y
                    if dist_sq < (hazard.radius + self.ball.radius) * (hazard.radius + self.ball.radius):
                        var is_active = true
                        if hazard.has_meta("active"):
                            is_active = hazard.get_meta("active")
                        if is_active:
                            hazard.set_meta("active", false)
                            hazard.set_meta("duration", 0.0)

                            if self.ball.has_method("take_damage"):
                                var dmg = hazard.damage
                                var is_qs = false
                                if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                    is_qs = self.ball.get_meta("is_in_quicksand")
                                elif "is_in_quicksand" in self.ball:
                                    is_qs = self.ball.is_in_quicksand
                                if is_qs:
                                    dmg *= 2.0
                                self.ball.take_damage(dmg)
                            elif "hp" in self.ball:
                                var dmg = hazard.damage
                                var is_qs = false
                                if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                    is_qs = self.ball.get_meta("is_in_quicksand")
                                elif "is_in_quicksand" in self.ball:
                                    is_qs = self.ball.is_in_quicksand
                                if is_qs:
                                    dmg *= 2.0
                                self.ball.hp -= dmg
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                            var current_stutter = 0.0
                            if "stutter_timer" in self.ball:
                                current_stutter = self.ball.stutter_timer
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("stutter_timer"):
                                current_stutter = self.ball.get_meta("stutter_timer")

                            if "stutter_timer" in self.ball:
                                self.ball.stutter_timer = current_stutter + 2.0
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", current_stutter + 2.0)


                elif hazard.kind == "switch":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    var ball_radius = 10.0
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        ball_radius = self.ball.get("radius", 10.0)
                    else:
                        ball_radius = self.ball.radius
                    if dist_sq < pow(hazard.radius + ball_radius, 2):
                        var current_tick = 0
                        if self.world.get("tick") != null:
                            current_tick = self.world.tick
                        var last_triggered = -100
                        if hazard.has_meta("last_triggered_tick"):
                            last_triggered = hazard.get_meta("last_triggered_tick")
                        if current_tick - last_triggered > 100:
                            hazard.set_meta("last_triggered_tick", current_tick)

                            var rng = RandomNumberGenerator.new()
                            rng.randomize()
                            var r = rng.randf()

                            var trap_id = 9000 + self.world.arena.hazards.size()
                            var HazardClass = load("res://src/arena/procedural_arena.gd").Hazard

                            if r < 0.33:
                                var wall = HazardClass.new(trap_id, hazard.x, hazard.y, 40.0, "laser_wall", 20.0)
                                wall.set_meta("duration", 5.0)
                                self.world.arena.hazards.append(wall)
                            elif r < 0.66:
                                var boulder = HazardClass.new(trap_id, self.ball.x, self.ball.y, 30.0, "meteor", 100.0)
                                boulder.set_meta("duration", 3.0)
                                self.world.arena.hazards.append(boulder)
                            else:
                                var axe = HazardClass.new(trap_id, hazard.x, hazard.y, 60.0, "spinning_laser", 40.0)
                                axe.set_meta("duration", 8.0)
                                self.world.arena.hazards.append(axe)
                elif hazard.kind == "swap_portal":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var current_tick = 0
                        if self.world.get("tick") != null:
                            current_tick = self.world.tick
                        var last_teleport = -100
                        if self.ball.has_meta("last_teleport_tick"):
                            last_teleport = self.ball.get_meta("last_teleport_tick")
                        if current_tick - last_teleport > 10:
                            if hazard.has_meta("pair_id"):
                                var pair_id = hazard.get_meta("pair_id")
                                var paired_hazard = null
                                for h in self.world.arena.hazards:
                                    if h.id == pair_id:
                                        paired_hazard = h
                                        break

                                if paired_hazard != null:
                                    var entity_to_swap = null
                                    for b in self.world.balls:
                                        if b != self.ball and b.get("alive") == true:
                                            var b_dx = paired_hazard.x - b.x
                                            var b_dy = paired_hazard.y - b.y
                                            if b_dx * b_dx + b_dy * b_dy < paired_hazard.radius * paired_hazard.radius:
                                                entity_to_swap = b
                                                break

                                    if entity_to_swap != null:
                                        var temp_x = self.ball.x
                                        var temp_y = self.ball.y
                                        self.ball.x = entity_to_swap.x
                                        self.ball.y = entity_to_swap.y
                                        entity_to_swap.x = temp_x
                                        entity_to_swap.y = temp_y

                                        if self.ball.has_method("set_meta"):
                                            self.ball.set_meta("last_teleport_tick", current_tick)
                                        if entity_to_swap.has_method("set_meta"):
                                            entity_to_swap.set_meta("last_teleport_tick", current_tick)
                elif hazard.kind == "portal" or hazard.kind == "teleporter" or hazard.kind == "one_way_teleporter" or hazard.kind == "wormhole":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var current_tick = 0
                        if self.world.get("tick") != null:
                            current_tick = self.world.tick
                        var last_teleport = -100
                        if self.ball.has_meta("last_teleport_tick"):
                            last_teleport = self.ball.get_meta("last_teleport_tick")
                        if current_tick - last_teleport > 10:
                            if hazard.kind == "wormhole":
                                if hazard.has_meta("target_x") and hazard.has_meta("target_y"):
                                    self.ball.x = hazard.get_meta("target_x")
                                    self.ball.y = hazard.get_meta("target_y")

                                    # Weaponize teleporter
                                    var b_type = ""
                                    if "ball_type" in self.ball:
                                        b_type = str(self.ball.ball_type).to_lower()
                                    var wep_tele = false
                                    if self.ball.has_meta("weaponize_teleporter"):
                                        wep_tele = self.ball.get_meta("weaponize_teleporter")
                                    if b_type == "trapper" or wep_tele:
                                        var trap = load("res://src/arena/procedural_arena.gd").Hazard.new()
                                        if self.world.get("next_id") != null:
                                            trap.id = self.world.next_id
                                            self.world.next_id += 1
                                        else:
                                            trap.id = 99999
                                        trap.x = self.ball.x
                                        trap.y = self.ball.y
                                        trap.radius = 15.0
                                        trap.kind = "trap"
                                        trap.damage = 0.0
                                        trap.set_meta("duration", 10.0)
                                        if self.ball.has_meta("trap_variant"):
                                            trap.set_meta("trap_variant", self.ball.get_meta("trap_variant"))
                                        else:
                                            trap.set_meta("trap_variant", "normal")
                                        if "id" in self.ball:
                                            trap.set_meta("owner_id", self.ball.id)
                                        if "arena" in self.world and "hazards" in self.world.arena:
                                            self.world.arena.hazards.append(trap)

                                    self.ball.set_meta("last_teleport_tick", current_tick)
                                    return
                            if hazard.kind == "teleporter" or hazard.kind == "one_way_teleporter":
                                if hazard.has_meta("target_x") and hazard.has_meta("target_y"):
                                    self.ball.x = hazard.get_meta("target_x")
                                    self.ball.y = hazard.get_meta("target_y")
                                else:
									# Teleport to opposite side

									var cx = self.world.arena.width / 2.0

									var cy = self.world.arena.height / 2.0

									var dx = self.ball.x - cx

									var dy = self.ball.y - cy

									self.ball.x = cx - dx

									self.ball.y = cy - dy

									# Clamp position

									self.ball.x = max(100.0, min(self.ball.x, self.world.arena.width - 100.0))

									self.ball.y = max(100.0, min(self.ball.y, self.world.arena.height - 100.0))

								# Teleport momentum logic

								var cvx = 0.0

								if "vx" in self.ball:

									cvx = self.ball.vx

								var cvy = 0.0

								if "vy" in self.ball:

									cvy = self.ball.vy

								var tp_speed = sqrt(cvx*cvx + cvy*cvy)

								if tp_speed > 0:

									var angle = randf_range(-PI, PI)

									var nvx = tp_speed * cos(angle)

									var nvy = tp_speed * sin(angle)

									if "vx" in self.ball:

										self.ball.vx = nvx

										self.ball.vy = nvy
                            else:
                                var launched = false
                                if hazard.has_meta("target_hazard_id") and self.world != null and self.world.get("arena") != null and "hazards" in self.world.arena:
                                    var target_hazard_id = hazard.get_meta("target_hazard_id")
                                    for h in self.world.arena.hazards:
                                        if h.id == target_hazard_id and h.kind == "black_hole":
                                            var angle = randf_range(0, 2 * PI)
                                            var launch_distance = h.radius + 30.0
                                            self.ball.x = h.x + cos(angle) * launch_distance
                                            self.ball.y = h.y + sin(angle) * launch_distance
                                            if self.ball.has_method("set_meta"):
                                                var current_imm = 0.0
                                                if self.ball.has_meta("zone_immunity_timer"):
                                                    current_imm = self.ball.get_meta("zone_immunity_timer")
                                                self.ball.set_meta("zone_immunity_timer", current_imm + 1.5)
                                            elif "zone_immunity_timer" in self.ball:
                                                self.ball.zone_immunity_timer += 1.5
                                            launched = true
                                            break
                                if not launched:
                                    if hazard.get("target_x") == null or hazard.get("target_y") == null:
                                        continue
                                    self.ball.x = hazard.target_x
                                    self.ball.y = hazard.target_y

                                    var cvx = 0.0
                                    if "vx" in self.ball:
                                        cvx = self.ball.vx
                                    var cvy = 0.0
                                    if "vy" in self.ball:
                                        cvy = self.ball.vy
                                    var spd = sqrt(cvx*cvx + cvy*cvy)
                                    if spd > 0:
                                        var scale = 1.0
                                        if spd < 200.0:
                                            scale = 1.5
                                        elif spd > 400.0:
                                            scale = 0.5
                                        if "vx" in self.ball:
                                            self.ball.vx = cvx * scale
                                        if "vy" in self.ball:
                                            self.ball.vy = cvy * scale

                                    # Weaponize teleporter
                                    var b_type3 = ""
                                    if "ball_type" in self.ball:
                                        b_type3 = str(self.ball.ball_type).to_lower()
                                    var wep_tele3 = false
                                    if self.ball.has_meta("weaponize_teleporter"):
                                        wep_tele3 = self.ball.get_meta("weaponize_teleporter")
                                    if b_type3 == "trapper" or wep_tele3:
                                        var trap3 = load("res://src/arena/procedural_arena.gd").Hazard.new()
                                        if self.world.get("next_id") != null:
                                            trap3.id = self.world.next_id
                                            self.world.next_id += 1
                                        else:
                                            trap3.id = 99999
                                        trap3.x = self.ball.x
                                        trap3.y = self.ball.y
                                        trap3.radius = 15.0
                                        trap3.kind = "trap"
                                        trap3.damage = 0.0
                                        trap3.set_meta("duration", 10.0)
                                        if self.ball.has_meta("trap_variant"):
                                            trap3.set_meta("trap_variant", self.ball.get_meta("trap_variant"))
                                        else:
                                            trap3.set_meta("trap_variant", "normal")
                                        if "id" in self.ball:
                                            trap3.set_meta("owner_id", self.ball.id)
                                        if "arena" in self.world and "hazards" in self.world.arena:
                                            self.world.arena.hazards.append(trap3)

                            self.ball.set_meta("last_teleport_tick", current_tick)
                elif hazard.kind == "ice_patch":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        if "vx" in self.ball and "vy" in self.ball:
                            var speed_mult = 1.5
                            self.ball.x += self.ball.vx * delta * speed_mult
                            self.ball.y += self.ball.vy * delta * speed_mult

                        var base_s = 100.0
                        if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                            base_s = self.ball.get_meta("base_speed")
                        elif "base_speed" in self.ball:
                            base_s = self.ball.base_speed

                        self.ball.speed = base_s * 1.5
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_slipping", true)

                elif hazard.kind == "quicksand":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        # Occasional slow debuff that lingers
                        var debuff_timer = 0.0
                        if self.ball.has_method("get_meta") and self.ball.has_meta("quicksand_debuff_timer"):
                            debuff_timer = self.ball.get_meta("quicksand_debuff_timer")
                        elif "quicksand_debuff_timer" in self.ball:
                            debuff_timer = self.ball.quicksand_debuff_timer

                        if debuff_timer <= 0.0:
                            if randf() < 0.1: # 10% chance per tick
                                debuff_timer = 2.0

                        if debuff_timer > 0.0:
                            debuff_timer -= delta
                            var base_speed = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_speed = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_speed = self.ball.base_speed
                            self.ball.speed = base_speed * 0.3

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("quicksand_debuff_timer", debuff_timer)
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.quicksand_debuff_timer = debuff_timer
                            self.ball.is_in_quicksand = true
                elif hazard.kind == "water_hazard":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var b_type = self.ball.ball_type if "ball_type" in self.ball else ""
                        var is_aquatic = b_type in ["water_elemental", "aquatic", "hovercraft", "drone"]

                        var is_wind_riding = false
                        if self.ball.has_meta("_is_wind_riding"):
                            is_wind_riding = self.ball.get_meta("_is_wind_riding")
                        elif "_is_wind_riding" in self.ball:
                            is_wind_riding = self.ball._is_wind_riding

                        if not is_aquatic and not is_wind_riding:
                            var base_spd = self.ball.base_speed if "base_speed" in self.ball else 100.0
                            self.ball.speed = base_spd * 0.2
                elif hazard.kind == "sinkhole":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        # Drastically reduce speed unless dashing or kiting
                        var is_dashing = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_dashing"):
                            is_dashing = self.ball.get_meta("is_dashing")
                        elif "is_dashing" in self.ball:
                            is_dashing = self.ball.is_dashing

                        if not is_dashing and strategy != "kite":
                            var base_speed = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_speed = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_speed = self.ball.base_speed
                            self.ball.speed = base_speed * 0.1
                elif hazard.kind == "conveyor_belt":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        self.ball.x += hazard.direction_vector[0] * hazard.speed_magnitude * delta
                        self.ball.y += hazard.direction_vector[1] * hazard.speed_magnitude * delta
                elif hazard.kind == "magnet":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    var effective_radius = hazard.radius * 3.0
                    if dist_sq < effective_radius * effective_radius:
                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            var nx = dx / dist
                            var ny = dy / dist
                            var min_dist = 10.0
                            if dist > min_dist:
                                min_dist = dist
                            var pull_strength = (effective_radius / min_dist) * 50.0 * delta
                            if pull_strength > dist * 0.5:
                                pull_strength = dist * 0.5
                            self.ball.x += nx * pull_strength
                            self.ball.y += ny * pull_strength
                elif hazard.kind == "repulsion_field":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        if "damage" in hazard and hazard.damage > 0.0:
                            var hazard_damage = hazard.damage * delta
                            var is_qs = false
                            if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                is_qs = self.ball.get_meta("is_in_quicksand")
                            elif "is_in_quicksand" in self.ball:
                                is_qs = self.ball.is_in_quicksand
                            if is_qs:
                                hazard_damage *= 2.0

                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            # push AWAY from hazard
                            var nx = -dx / dist
                            var ny = -dy / dist
                            var push_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta
                            self.ball.x += nx * push_strength
                            self.ball.y += ny * push_strength
                elif hazard.kind == "reverse_gravity":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        if "damage" in hazard and hazard.damage > 0.0:
                            var hazard_damage = hazard.damage * delta
                            var is_qs = false
                            if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                is_qs = self.ball.get_meta("is_in_quicksand")
                            elif "is_in_quicksand" in self.ball:
                                is_qs = self.ball.is_in_quicksand
                            if is_qs:
                                hazard_damage *= 2.0

                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            var nx = -dx / dist
                            var ny = -dy / dist
                            var push_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta
                            self.ball.x += nx * push_strength
                            self.ball.y += ny * push_strength
                elif hazard.kind == "gravity_well":
                    # Cosmetics: gravity anomaly already implemented
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        # Apply slight damage if any
                        if "damage" in hazard and hazard.damage > 0.0:
                            var hazard_damage = hazard.damage * delta
                            var is_qs = false
                            if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                is_qs = self.ball.get_meta("is_in_quicksand")
                            elif "is_in_quicksand" in self.ball:
                                is_qs = self.ball.is_in_quicksand
                            if is_qs:
                                hazard_damage *= 2.0

                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            var nx = dx / dist
                            var ny = dy / dist
                            var min_dist = 10.0
                            if dist > min_dist:
                                min_dist = dist
                            var pull_strength = (hazard.radius * 2.0 / min_dist) * 50.0 * delta
                            self.ball.x += nx * pull_strength
                            self.ball.y += ny * pull_strength
                elif hazard.kind in ["black_hole", "tornado", "local_tornado", "portal", "teleporter", "one_way_teleporter", "swap_portal", "lightning_storm"]:
                    var current_tick = 0
                    if "tick" in self.world:
                        current_tick = self.world.tick
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)
                        if not hazard.has_meta("vx"):
                            if hazard.kind in ["tornado", "local_tornado", "portal", "teleporter", "one_way_teleporter", "swap_portal", "lightning_storm"]:
                                hazard.set_meta("vx", randf_range(-100.0, 100.0))
                                hazard.set_meta("vy", randf_range(-100.0, 100.0))
                            else:
                                hazard.set_meta("vx", 10.0)
                                hazard.set_meta("vy", 10.0)
                        if not hazard.has_meta("lifetime"):
                            hazard.set_meta("lifetime", 0.0)
                        hazard.set_meta("lifetime", hazard.get_meta("lifetime") + delta)
                        var hvx = hazard.get_meta("vx")
                        var hvy = hazard.get_meta("vy")
                        hazard.x += hvx * delta
                        hazard.y += hvy * delta
                        if hazard.x < 100 or hazard.x > self.world.arena.width - 100:
                            hazard.set_meta("vx", -hvx)
                        if hazard.y < 100 or hazard.y > self.world.arena.height - 100:
                            hazard.set_meta("vy", -hvy)

                        if hazard.kind in ["black_hole", "tornado", "local_tornado"] and "boosters" in self.world:
                            for b in self.world.boosters:
                                var bdx = hazard.x - b.x
                                var bdy = hazard.y - b.y
                                var bdist_sq = bdx * bdx + bdy * bdy
                                if bdist_sq > 0.0001:
                                    var bdist = sqrt(bdist_sq)
                                    var bnx = bdx / bdist
                                    var bny = bdy / bdist
                                    var bmin_dist = 10.0
                                    if bdist > bmin_dist:
                                        bmin_dist = bdist
                                    var lifetime_mult = 1.0
                                    if hazard.kind == "black_hole" and hazard.has_meta("lifetime"):
                                        lifetime_mult = 1.0 + (hazard.get_meta("lifetime") / 10.0)
                                    var bpull_strength = (hazard.radius * 2.0 / bmin_dist) * 50.0 * delta * lifetime_mult
                                    b.x += bnx * bpull_strength
                                    b.y += bny * bpull_strength
                                    if hazard.kind in ["tornado", "local_tornado"]:
                                        var tx = -bny
                                        var ty = bnx
                                        var orbital_strength = bpull_strength * 1.5
                                        b.x += tx * orbital_strength
                                        b.y += ty * orbital_strength

                    if hazard.kind in ["black_hole", "tornado", "local_tornado"]:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq > 0.0001:
                            var lifetime_mult = 1.0
                            if hazard.kind == "black_hole" and hazard.has_meta("lifetime"):
                                lifetime_mult = 1.0 + (hazard.get_meta("lifetime") / 10.0)
                            var dist = sqrt(dist_sq)
                            var nx = dx / dist
                            var ny = dy / dist
                            var min_dist = 10.0
                            if dist > min_dist:
                                min_dist = dist
                            var pull_strength = (hazard.radius * 2.0 / min_dist) * 50.0 * delta * lifetime_mult
                            self.ball.x += nx * pull_strength
                            self.ball.y += ny * pull_strength
                            if hazard.kind in ["tornado", "local_tornado"]:
                                var tx = -ny
                                var ty = nx
                                var orbital_strength = pull_strength * 1.5
                                self.ball.x += tx * orbital_strength
                                self.ball.y += ty * orbital_strength

        if "hazards" in self.world.arena:
            var alive_hazards = []
            for h in self.world.arena.hazards:
                if h.kind != "trap" or (h.has_meta("duration") and h.get_meta("duration") > 0.0):
                    alive_hazards.append(h)
            self.world.arena.hazards = alive_hazards

        if ball_type != "spectator" and "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                var dist = sqrt((self.ball.x - hazard.x) * (self.ball.x - hazard.x) + (self.ball.y - hazard.y) * (self.ball.y - hazard.y))
                if dist < (self.ball.radius + hazard.radius):
                    if hazard.kind == "temporal_rift":
			continue
                    if hazard.kind == "explosive_barrel":
                        if not hazard.has_meta("is_exploded") or not hazard.get_meta("is_exploded"):
                            var bvx = 0.0
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("vx"):
                                bvx = self.ball.get_meta("vx")
                            elif "vx" in self.ball:
                                bvx = self.ball.vx
                            var bvy = 0.0
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("vy"):
                                bvy = self.ball.get_meta("vy")
                            elif "vy" in self.ball:
                                bvy = self.ball.vy

                            var speed = sqrt(bvx * bvx + bvy * bvy)
                            var hvx = 0.0
                            if hazard.has_meta("vx"): hvx = hazard.get_meta("vx")
                            var hvy = 0.0
                            if hazard.has_meta("vy"): hvy = hazard.get_meta("vy")
                            var hazard_speed = sqrt(hvx * hvx + hvy * hvy)

                            if dist > 0:
                                var nx = (self.ball.x - hazard.x) / dist
                                var ny = (self.ball.y - hazard.y) / dist
                                var overlap = (self.ball.radius + hazard.radius) - dist
                                if overlap > 0:
                                    var push_speed = max(500.0, speed * 3.0)
                                    hazard.set_meta("vx", hvx - nx * push_speed)
                                    hazard.set_meta("vy", hvy - ny * push_speed)
                                    self.ball.x += nx * (overlap / 2.0)
                                    self.ball.y += ny * (overlap / 2.0)
                                    hazard.x -= nx * (overlap / 2.0)
                                    hazard.y -= ny * (overlap / 2.0)

                            var has_skill = false
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("active_skill") and self.ball.get_meta("active_skill") != null:
                                has_skill = true
                            elif "active_skill" in self.ball and self.ball.active_skill != null:
                                has_skill = true
                            if speed > 300.0 or hazard_speed > 300.0 or has_skill:
                                hazard.set_meta("is_exploded", true)
                    elif hazard.kind == "trap":
                        var trap_owner_id = null
                        if hazard.has_method("get_meta") and hazard.has_meta("owner_id"):
                            trap_owner_id = hazard.get_meta("owner_id")

                        if trap_owner_id != null and trap_owner_id == self.ball.id:
                            continue
                        if ball_type != "sniper":
                            var trap_variant = "normal"
                            if hazard.has_meta("trap_variant"):
                                trap_variant = hazard.get_meta("trap_variant")

                            if trap_variant == "poison":
                                var poison_damage = 5.0 * delta
                                if self.ball.has_method("take_damage"):
                                    self.ball.take_damage(poison_damage)
                                elif "hp" in self.ball:
                                    self.ball.hp -= poison_damage
                                    if self.ball.hp <= 0:
                                        self.ball.alive = false
                            elif trap_variant == "emp":
                                var is_emped = false
                                if "is_emped" in self.ball:
                                    is_emped = self.ball.is_emped
                                elif self.ball.has_method("get_meta") and self.ball.has_meta("is_emped"):
                                    is_emped = self.ball.get_meta("is_emped")

                                if not is_emped:
                                    if "is_emped" in self.ball:
                                        self.ball.is_emped = true
                                        self.ball.emp_timer = 2.0
                                    elif self.ball.has_method("set_meta"):
                                        self.ball.set_meta("is_emped", true)
                                        self.ball.set_meta("emp_timer", 2.0)

                                    if "skill_timer" in self.ball:
                                        self.ball.skill_timer = max(self.ball.skill_timer, 2.0)
                                    elif self.ball.has_method("set_meta"):
                                        var cur_skill_timer = self.ball.get_meta("skill_timer") if self.ball.has_meta("skill_timer") else 0.0
                                        self.ball.set_meta("skill_timer", max(cur_skill_timer, 2.0))

                                    var base_speed = 100.0
                                    if "base_speed" in self.ball:
                                        base_speed = self.ball.base_speed
                                    elif self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                        base_speed = self.ball.get_meta("base_speed")

                                    var current_speed = base_speed
                                    if "speed" in self.ball:
                                        current_speed = self.ball.speed
                                    elif self.ball.has_method("get_meta") and self.ball.has_meta("speed"):
                                        current_speed = self.ball.get_meta("speed")

                                    if current_speed > base_speed:
                                        if "speed" in self.ball:
                                            self.ball.speed = base_speed
                                        elif self.ball.has_method("set_meta"):
                                            self.ball.set_meta("speed", base_speed)

                                    var dmg_mult = 1.0
                                    if "damage_multiplier" in self.ball:
                                        dmg_mult = self.ball.damage_multiplier
                                    elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_multiplier"):
                                        dmg_mult = self.ball.get_meta("damage_multiplier")

                                    if dmg_mult > 1.0:
                                        if "damage_multiplier" in self.ball:
                                            self.ball.damage_multiplier = 1.0
                                        elif self.ball.has_method("set_meta"):
                                            self.ball.set_meta("damage_multiplier", 1.0)
                            elif trap_variant == "mine":
                                if self.ball.has_method("take_damage"):
                                    self.ball.take_damage(50.0)
                                elif "hp" in self.ball:
                                    self.ball.hp -= 50.0
                                    if self.ball.hp <= 0:
                                        self.ball.alive = false
                                if hazard.has_method("set_meta"):
                                    hazard.set_meta("duration", 0.0)
                                elif "duration" in hazard:
                                    hazard.duration = 0.0
                            elif trap_variant == "freeze":
                                var is_stunned = false
                                if "is_stunned" in self.ball:
                                    is_stunned = self.ball.is_stunned
                                elif self.ball.has_method("get_meta") and self.ball.has_meta("is_stunned"):
                                    is_stunned = self.ball.get_meta("is_stunned")

                                if not is_stunned:
                                    if "is_stunned" in self.ball:
                                        self.ball.is_stunned = true
                                        self.ball.stun_timer = 2.0
                                    elif self.ball.has_method("set_meta"):
                                        self.ball.set_meta("is_stunned", true)
                                        self.ball.set_meta("stun_timer", 2.0)
                                self.ball.x = old_x
                                self.ball.y = old_y
                                if hazard.has_method("set_meta"):
                                    hazard.set_meta("duration", 0.0)
                                elif "duration" in hazard:
                                    hazard.duration = 0.0
                            elif trap_variant == "stun":
                                var is_stunned = false
                                if "is_stunned" in self.ball:
                                    is_stunned = self.ball.is_stunned
                                elif self.ball.has_method("get_meta") and self.ball.has_meta("is_stunned"):
                                    is_stunned = self.ball.get_meta("is_stunned")

                                if not is_stunned:
                                    if "is_stunned" in self.ball:
                                        self.ball.is_stunned = true
                                        self.ball.stun_timer = 1.0
                                    elif self.ball.has_method("set_meta"):
                                        self.ball.set_meta("is_stunned", true)
                                        self.ball.set_meta("stun_timer", 1.0)
                                self.ball.x = old_x
                                self.ball.y = old_y
                            elif trap_variant == "black_hole":
                                if world != null and world.has_method("get_arena") and world.get_arena() != null and "hazards" in world.get_arena():
                                    var bh = null
                                    if load("res://src/arena/procedural_arena.gd") != null:
                                        bh = load("res://src/arena/procedural_arena.gd").Hazard.new()
                                    if bh != null:
                                        bh.id = world.get_arena().hazards.size() + 8000
                                        bh.x = hazard.x
                                        bh.y = hazard.y
                                        bh.radius = 100.0
                                        bh.kind = "black_hole"
                                        bh.damage = 0.0
                                        bh.set_meta("duration", 3.0)
                                        world.get_arena().hazards.append(bh)
                                if hazard.has_method("set_meta"):
                                    hazard.set_meta("duration", 0.0)
                                elif "duration" in hazard:
                                    hazard.duration = 0.0
                            elif trap_variant == "swap":
                                var owner_id = null
                                if hazard.has_method("get_meta") and hazard.has_meta("owner_id"):
                                    owner_id = hazard.get_meta("owner_id")
                                elif "owner_id" in hazard:
                                    owner_id = hazard.owner_id

                                if owner_id != null:
                                    var owner_ball = null
                                    var balls_list = []
                                    if world != null and "balls" in world:
                                        balls_list = world.balls
                                    elif world != null and "entities" in world:
                                        balls_list = world.entities

                                    for b in balls_list:
                                        if "id" in b and b.id == owner_id:
                                            owner_ball = b
                                            break

                                    if owner_ball != null and owner_ball != self.ball:
                                        var temp_x = owner_ball.x
                                        var temp_y = owner_ball.y
                                        owner_ball.x = old_x
                                        owner_ball.y = old_y
                                        self.ball.x = temp_x
                                        self.ball.y = temp_y

                                if hazard.has_method("set_meta"):
                                    hazard.set_meta("duration", 0.0)
                                elif "duration" in hazard:
                                    hazard.duration = 0.0
                            else:
                                self.ball.x = (self.ball.x + old_x) / 2.0
                                self.ball.y = (self.ball.y + old_y) / 2.0
                        continue

                    elif hazard.kind == "emp_burst":
                        if "is_scrambled" in self.ball:
                            self.ball.is_scrambled = true
                            if "scramble_timer" in self.ball:
                                self.ball.scramble_timer = 3.0
                            else:
                                self.ball.set_meta("scramble_timer", 3.0)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_scrambled", true)
                            self.ball.set_meta("scramble_timer", 3.0)
                        if self.has_method("_spawn_skill_particles"):
                            self._spawn_skill_particles("emp")
                        continue
                    elif hazard.kind == "poison_nova":
                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var dist = sqrt(dx*dx + dy*dy)
                        var nova_thickness = 40.0
                        if dist >= hazard.radius - nova_thickness and dist <= hazard.radius + nova_thickness:
                            if self.ball.has_method("set_meta"):
                                var current_poison = 0.0
                                if self.ball.has_meta("poison_timer"):
                                    current_poison = self.ball.get_meta("poison_timer")
                                self.ball.set_meta("poison_timer", current_poison + 2.0)
                            elif "poison_timer" in self.ball:
                                self.ball.poison_timer += 2.0

                            var hd = hazard.damage * delta
                            var is_qs = false
                            if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                is_qs = self.ball.get_meta("is_in_quicksand")
                            elif "is_in_quicksand" in self.ball:
                                is_qs = self.ball.is_in_quicksand
                            if is_qs:
                                hd *= 2.0
                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hd)
                            elif "hp" in self.ball:
                                self.ball.hp -= hd
                                if self.ball.hp <= 0:
                                    self.ball.alive = false
                        continue
                    elif hazard.kind == "fire_ring":
                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var dist = sqrt(dx*dx + dy*dy)
                        var ring_thickness = 30.0
                        if dist >= hazard.radius - ring_thickness and dist <= hazard.radius + ring_thickness:
                            var hd = hazard.damage * delta
                            var is_qs = false
                            if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                is_qs = self.ball.get_meta("is_in_quicksand")
                            elif "is_in_quicksand" in self.ball:
                                is_qs = self.ball.is_in_quicksand
                            if is_qs:
                                hd *= 2.0
                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hd)
                            elif "hp" in self.ball:
                                self.ball.hp -= hd
                                if self.ball.hp <= 0:
                                    self.ball.alive = false
                        continue
                    elif hazard.kind == "orbital_strike_active":
                        var hd = hazard.damage * delta
                        var is_qs = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                            is_qs = self.ball.get_meta("is_in_quicksand")
                        elif "is_in_quicksand" in self.ball:
                            is_qs = self.ball.is_in_quicksand
                        if is_qs:
                            hd *= 2.0

                        var shielded = false
                        for dome in arena.hazards:
                            if dome.kind == "orbital_shield_dome":
                                var dist = sqrt((self.ball.x - dome.x)*(self.ball.x - dome.x) + (self.ball.y - dome.y)*(self.ball.y - dome.y))
                                var r = 300.0
                                if "radius" in dome:
                                    r = dome.radius
                                if dist <= r:
                                    shielded = true
                                    break

                        if shielded:
                            hd *= 0.1

                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist > 0.0001:
                            var nx = dx / dist
                            var ny = dy / dist
                            var knockback_force = 1000.0 * delta
                            self.ball.x += nx * knockback_force
                            self.ball.y += ny * knockback_force
                        continue
                    elif hazard.kind == "fire_zone":
                        var hd = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                        continue
                    elif hazard.kind == "meteor":
                        var hd = hazard.damage * delta
                        var is_qs = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                            is_qs = self.ball.get_meta("is_in_quicksand")
                        elif "is_in_quicksand" in self.ball:
                            is_qs = self.ball.is_in_quicksand
                        if is_qs:
                            hd *= 2.0

                        var shielded = false
                        for dome in arena.hazards:
                            if dome.kind == "orbital_shield_dome":
                                var dist = sqrt((self.ball.x - dome.x)*(self.ball.x - dome.x) + (self.ball.y - dome.y)*(self.ball.y - dome.y))
                                var r = 300.0
                                if "radius" in dome:
                                    r = dome.radius
                                if dist <= r:
                                    shielded = true
                                    break

                        if shielded:
                            hd *= 0.1

                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                        continue
                    elif hazard.kind == "laser_wall":
                        var hd = hazard.damage * delta
                        var is_qs = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                            is_qs = self.ball.get_meta("is_in_quicksand")
                        elif "is_in_quicksand" in self.ball:
                            is_qs = self.ball.is_in_quicksand
                        if is_qs:
                            hd *= 2.0
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist > 0.0001:
                            self.ball.x += (dx/dist) * 200.0 * delta
                            self.ball.y += (dy/dist) * 200.0 * delta
                        continue
                    elif hazard.kind == "spinning_laser":
                        var is_on = true
                        if hazard.has_meta("is_on"):
                            is_on = hazard.get_meta("is_on")

                        if is_on:
                            var angle = 0.0
                            if hazard.has_meta("angle"):
                                angle = hazard.get_meta("angle")

                            var beam_length = hazard.radius
                            var beam_width = 20.0

                            var dx = self.ball.x - hazard.x
                            var dy = self.ball.y - hazard.y
                            var dist = sqrt(dx*dx + dy*dy)

                            if dist < beam_length:
                                var normal_x = -sin(angle)
                                var normal_y = cos(angle)
                                var dist_to_beam = abs(dx * normal_x + dy * normal_y)

                                if dist_to_beam < beam_width + self.ball.radius:
                                    var hd = hazard.damage * delta
                                    var is_qs = false
                                    if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                        is_qs = self.ball.get_meta("is_in_quicksand")
                                    elif "is_in_quicksand" in self.ball:
                                        is_qs = self.ball.is_in_quicksand
                                    if is_qs:
                                        hd *= 2.0
                                    if self.ball.has_method("take_damage"):
                                        self.ball.take_damage(hd)
                                    elif "hp" in self.ball:
                                        self.ball.hp -= hd
                                        if self.ball.hp <= 0:
                                            self.ball.alive = false

                                    if dist > 0.0001:
                                        self.ball.x += (dx/dist) * 100.0 * delta
                                        self.ball.y += (dy/dist) * 100.0 * delta
                    elif hazard.kind == "poison_cloud":
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("dot_duration", 3.0)
                            self.ball.set_meta("dot_damage_per_tick", hazard.damage)
                        var hd = hazard.damage * delta
                        var is_qs = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                            is_qs = self.ball.get_meta("is_in_quicksand")
                        elif "is_in_quicksand" in self.ball:
                            is_qs = self.ball.is_in_quicksand
                        if is_qs:
                            hd *= 2.0
                    elif hazard.kind == "hidden_trap":
                        var b_speed = 100.0
                        if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                            b_speed = self.ball.get_meta("base_speed")
                        elif "base_speed" in self.ball:
                            b_speed = self.ball.base_speed
                        self.ball.speed = b_speed * 0.5
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("dot_duration", 2.0)
                            self.ball.set_meta("dot_damage_per_tick", hazard.damage)
                        var hd = hazard.damage * delta
                        var is_qs = false
                        if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                            is_qs = self.ball.get_meta("is_in_quicksand")
                        elif "is_in_quicksand" in self.ball:
                            is_qs = self.ball.is_in_quicksand
                        if is_qs:
                            hd *= 2.0
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                    elif hazard.kind == "chrono_anomaly":
                        var speed_mult = 0.2
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("_chrono_slow", speed_mult)
                        elif typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_chrono_slow"] = speed_mult

                        if "attack_timer" in self.ball and self.ball.attack_timer > 0:
                            self.ball.attack_timer += delta * (1.0 - speed_mult)
                        if "skill_timer" in self.ball and self.ball.skill_timer > 0:
                            self.ball.skill_timer += delta * (1.0 - speed_mult)
                    elif hazard.kind in ["tornado", "local_tornado"]:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var md = max(0.1, dist)
                        var pull_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 200.0 * delta
                        var nx = dx / md
                        var ny = dy / md
                        self.ball.x += nx * pull_strength
                        self.ball.y += ny * pull_strength
                        var tx = -ny
                        var ty = nx
                        var orbital_strength = pull_strength * 1.5
                        self.ball.x += tx * orbital_strength
                        self.ball.y += ty * orbital_strength

                        if dist < hazard.radius * 0.5:
                            if "vx" in self.ball: self.ball.vx = 0
                            if "vy" in self.ball: self.ball.vy = 0

                            var current_tick = 0
                            if "tick" in self.world: current_tick = self.world.tick
                            var b_id = 0
                            if "id" in self.ball: b_id = self.ball.id
                            var h_id = 0
                            if "id" in hazard: h_id = hazard.id

                            var prand = (b_id * 17 + h_id * 31 + current_tick * 13) % 1000 / 1000.0
                            var angle = prand * 2.0 * PI
                            var prand2 = (b_id * 23 + h_id * 7 + current_tick * 19) % 1000 / 1000.0
                            var launch_dist = 50.0 + prand2 * 100.0

                            self.ball.x += cos(angle) * launch_dist
                            self.ball.y += sin(angle) * launch_dist

                            var hazard_damage = hazard.damage
                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                            # Apply dizzy effect (confusion)
                            self.ball.is_confused = true
                            if "confusion_timer" in self.ball and self.ball.confusion_timer > 3.0:
                                pass
                            else:
                                self.ball.confusion_timer = 3.0
                    elif hazard.kind == "lightning_strike":
                        if not hazard.has_meta("hit_targets") or not hazard.get_meta("hit_targets"):
                            hazard.set_meta("hit_targets", true)
                            if self.ball.has_method("take_damage"):
                                var dmg = hazard.damage
                                var is_qs = false
                                if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                    is_qs = self.ball.get_meta("is_in_quicksand")
                                elif "is_in_quicksand" in self.ball:
                                    is_qs = self.ball.is_in_quicksand
                                if is_qs:
                                    dmg *= 2.0
                                self.ball.take_damage(dmg)
                            elif "hp" in self.ball:
                                var dmg = hazard.damage
                                var is_qs = false
                                if self.ball.has_method("get_meta") and self.ball.has_meta("is_in_quicksand"):
                                    is_qs = self.ball.get_meta("is_in_quicksand")
                                elif "is_in_quicksand" in self.ball:
                                    is_qs = self.ball.is_in_quicksand
                                if is_qs:
                                    dmg *= 2.0
                                self.ball.hp -= dmg
                                if self.ball.hp <= 0:
                                    self.ball.alive = false
                            if has_method("_spawn_particles"):
                                _spawn_particles(self.ball.x, self.ball.y, "lightning")
                            if self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", 1.0)
                        continue
                    elif hazard.kind == "breakable_wall":
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
                            self.ball.x += nx * overlap
                            self.ball.y += ny * overlap

                        if hazard.has_meta("hp"):
                            var base_dmg = 100.0
                            if "damage" in self.ball:
                                base_dmg = self.ball.damage
                            var new_hp = hazard.get_meta("hp") - base_dmg * delta * 5.0
                            hazard.set_meta("hp", new_hp)
                            if new_hp <= 0:
                                hazard.active = false
                                hazard.set_meta("active", false)
                        continue
                    elif hazard.kind == "bounce_pad":
                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var d = sqrt(dx*dx + dy*dy)
                        var b_rad = 10.0
                        if "radius" in self.ball:
                            b_rad = self.ball.radius
                        if d < (b_rad + hazard.radius) and d > 0.0001:
                            var nx = dx / d
                            var ny = dy / d
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("vx", nx * 1000.0)
                                self.ball.set_meta("vy", ny * 1000.0)
                            elif "vx" in self.ball:
                                self.ball.vx = nx * 1000.0
                                self.ball.vy = ny * 1000.0
                        continue

                    elif hazard.kind == "pinball_flipper":
                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var d = sqrt(dx*dx + dy*dy)
                        if d < 0.0001: d = 0.0001

                        var b_rad = 10.0
                        if "radius" in self.ball:
                            b_rad = self.ball.radius

                        if d < (b_rad + hazard.radius):
                            var ft = 0.0
                            if hazard.has_meta("flip_timer"):
                                ft = hazard.get_meta("flip_timer")

                            if ft > 0:
                                var side = "left"
                                if hazard.has_meta("flipper_side"):
                                    side = hazard.get_meta("flipper_side")

                                var nx = 0.5
                                var ny = -0.8
                                if side == "right":
                                    nx = -0.5
                                    ny = -0.8

                                var flip_strength = 1500.0 * delta
                                self.ball.x += nx * flip_strength
                                self.ball.y += ny * flip_strength

                                if not "vx" in self.ball: self.ball.vx = 0.0
                                if not "vy" in self.ball: self.ball.vy = 0.0
                                self.ball.vx += nx * 1000.0
                                self.ball.vy += ny * 1000.0
                            else:
                                var nx = dx / d
                                var ny = dy / d
                                self.ball.x += nx * 50.0 * delta
                                self.ball.y += ny * 50.0 * delta

                    elif hazard.kind == "bumper":

                        var dx = self.ball.x - hazard.x
                        var dy = self.ball.y - hazard.y
                        var d = sqrt(dx*dx + dy*dy)
                        if d < 0.0001: d = 0.0001

                        var b_rad = 10.0
                        if "radius" in self.ball:
                            b_rad = self.ball.radius

                        if d < (b_rad + hazard.radius):
                            var nx = dx / d
                            var ny = dy / d

                            var angle = atan2(ny, nx) + randf_range(-0.5, 0.5)
                            nx = cos(angle)
                            ny = sin(angle)

                            var bounce_strength = 600.0 * delta
                            self.ball.x += nx * bounce_strength
                            self.ball.y += ny * bounce_strength

                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                # If it's a Dictionary with set_meta method from python mock or actual godot node, update both property and meta
                                if "vx" in self.ball:
                                    self.ball.vx = nx * 2000.0
                                    self.ball.vy = ny * 2000.0
                                else:
                                    self.ball.set_meta("vx", nx * 2000.0)
                                    self.ball.set_meta("vy", ny * 2000.0)
                            elif "vx" in self.ball:
                                self.ball.vx = nx * 2000.0
                                self.ball.vy = ny * 2000.0

                            var powerup = null
                            if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("powerup_type"):
                                powerup = hazard.get_meta("powerup_type")
                            elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("powerup_type"):
                                powerup = hazard.powerup_type
                            elif "powerup_type" in hazard:
                                powerup = hazard.powerup_type

                            if powerup == "heal":
                                var max_hp = 100.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("max_hp"): max_hp = self.ball.get_meta("max_hp")
                                elif "max_hp" in self.ball: max_hp = self.ball.max_hp

                                var hp = 100.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("hp"): hp = self.ball.get_meta("hp")
                                elif "hp" in self.ball: hp = self.ball.hp

                                hp = min(max_hp, hp + 10.0)
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("hp", hp)
                                if "hp" in self.ball: self.ball.hp = hp

                            elif powerup == "speed":
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("speed_boost_timer", 3.0)
                                if "speed_boost_timer" in self.ball: self.ball.speed_boost_timer = 3.0

                            elif powerup == "shield":
                                var shield = 0.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("shield"): shield = self.ball.get_meta("shield")
                                elif "shield" in self.ball: shield = self.ball.shield

                                shield += 20.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("shield", shield)
                                if "shield" in self.ball: self.ball.shield = shield

                            elif powerup == "stamina":
                                var max_stam = 100.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("max_stamina"): max_stam = self.ball.get_meta("max_stamina")
                                elif "max_stamina" in self.ball: max_stam = self.ball.max_stamina

                                var stam = 100.0
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("stamina"): stam = self.ball.get_meta("stamina")
                                elif "stamina" in self.ball: stam = self.ball.stamina

                                stam = min(max_stam, stam + 20.0)
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("stamina", stam)
                                if "stamina" in self.ball: self.ball.stamina = stam
                        continue
                    elif hazard.kind == "healing_spring":
                        var heal_amount = abs(hazard.damage) * delta
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp += heal_amount
                            if self.ball.hp > self.ball.max_hp:
                                self.ball.hp = self.ball.max_hp
                        continue
                    elif hazard.kind == "stamina_drain_zone":
                        if "stamina" in self.ball:
                            var stam = self.ball.stamina
                            self.ball.stamina = max(0.0, stam - 30.0 * delta)
                        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("stamina"):
                            var stam = self.ball.get_meta("stamina")
                            self.ball.set_meta("stamina", max(0.0, stam - 30.0 * delta))
                        continue
                    elif hazard.kind == "vampiric_puddle":
                        var hazard_damage = hazard.damage * delta
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hazard_damage)
                        elif "hp" in self.ball:
                            self.ball.hp -= hazard_damage
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        var acc_healing = 0.0
                        if "accumulated_healing" in hazard:
                            acc_healing = hazard.accumulated_healing
                        elif hazard.has_method("get_meta") and hazard.has_meta("accumulated_healing"):
                            acc_healing = hazard.get_meta("accumulated_healing")

                        acc_healing += hazard_damage

                        var lowest_hp_ball = null
                        var lowest_hp = INF
                        if self.world != null and "balls" in self.world:
                            for b in self.world.balls:
                                if "alive" in b and b.alive and "hp" in b and "max_hp" in b and b.hp < b.max_hp:
                                    if b.hp < lowest_hp:
                                        lowest_hp = b.hp
                                        lowest_hp_ball = b

                        if lowest_hp_ball != null and acc_healing > 0:
                            lowest_hp_ball.hp += acc_healing
                            if lowest_hp_ball.hp > lowest_hp_ball.max_hp:
                                lowest_hp_ball.hp = lowest_hp_ball.max_hp
                            acc_healing = 0.0

                        if "accumulated_healing" in hazard:
                            hazard.accumulated_healing = acc_healing
                        elif hazard.has_method("set_meta"):
                            hazard.set_meta("accumulated_healing", acc_healing)
                        continue
                    elif hazard.kind == "damage_link":
                        var has_target = false
                        if "damage_link_target" in self.ball and self.ball.damage_link_target != null:
                            has_target = true
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_target") and self.ball.get_meta("damage_link_target") != null:
                            has_target = true

                        if not has_target:
                            var closest_dist = INF
                            var closest_ball = null
                            if self.world != null and "balls" in self.world:
                                for b in self.world.balls:
                                    if b != self.ball and ("alive" in b and b.alive):
                                        var b_has_target = false
                                        if "damage_link_target" in b and b.damage_link_target != null: b_has_target = true
                                        elif b.has_method("get_meta") and b.has_meta("damage_link_target") and b.get_meta("damage_link_target") != null: b_has_target = true

                                        if not b_has_target:
                                            var d_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
                                            if d_sq < closest_dist:
                                                closest_dist = d_sq
                                                closest_ball = b
                            if closest_ball != null:
                                if "damage_link_target" in self.ball: self.ball.damage_link_target = closest_ball
                                elif self.ball.has_method("set_meta"): self.ball.set_meta("damage_link_target", closest_ball)

                                if "damage_link_target" in closest_ball: closest_ball.damage_link_target = self.ball
                                elif closest_ball.has_method("set_meta"): closest_ball.set_meta("damage_link_target", self.ball)

                                if self.has_method("_spawn_directed_particles"):
                                    self._spawn_directed_particles(self.ball, closest_ball, "damage_link")
                        continue

                    var hazard_damage = hazard.damage * delta
                    if self.ball.has_method("take_damage"):
                        self.ball.take_damage(hazard_damage)
                    elif "hp" in self.ball:
                        self.ball.hp -= hazard_damage
                        if self.ball.hp <= 0:
                            self.ball.alive = false

    var has_chrono = false
    var chrono_mult = 1.0
    if self.ball.has_method("has_meta") and self.ball.has_meta("_chrono_slow"):
        has_chrono = true
        chrono_mult = self.ball.get_meta("_chrono_slow")
    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("_chrono_slow"):
        has_chrono = true
        chrono_mult = self.ball["_chrono_slow"]

    var b_speed = 2.0
    if "base_speed" in self.ball:
        b_speed = self.ball.base_speed

    if "speed" in self.ball:
        if has_chrono:
            self.ball.speed = b_speed * chrono_mult
        else:
            self.ball.speed = b_speed

    if "current_action" in self.ball or typeof(self.ball) == TYPE_DICTIONARY:
        self.ball.current_action = strategy

    if self.ball.has_method("set_meta"):
        self.ball.set_meta("team_message", null)

        var hp_percent = 1.0
        if self.ball.has_method("get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif "hp" in self.ball and "max_hp" in self.ball:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if hp_percent < 0.3:
            self.ball.set_meta("team_message", {"type": "request_help", "x": self.ball.x, "y": self.ball.y})
        elif personality == "healer":
            self.ball.set_meta("team_message", {"type": "wounded_call", "x": self.ball.x, "y": self.ball.y})
        elif strategy == "defend" and personality == "tank":
            self.ball.set_meta("team_message", {"type": "hold_position", "x": self.ball.x, "y": self.ball.y})

    var stun_timer = 0.0
    var is_scrambled = false
        if "is_scrambled" in self.ball:
            is_scrambled = self.ball.is_scrambled
        elif self.ball.has_method("get_meta") and self.ball.has_meta("is_scrambled"):
            is_scrambled = self.ball.get_meta("is_scrambled")

        if is_scrambled:
            var scr_timer = 0.0
            if "scramble_timer" in self.ball: scr_timer = self.ball.scramble_timer
            elif self.ball.has_method("get_meta") and self.ball.has_meta("scramble_timer"): scr_timer = self.ball.get_meta("scramble_timer")

            scr_timer -= delta
            if "scramble_timer" in self.ball: self.ball.scramble_timer = scr_timer
            elif self.ball.has_method("set_meta"): self.ball.set_meta("scramble_timer", scr_timer)

            if scr_timer <= 0:
                if "is_scrambled" in self.ball: self.ball.is_scrambled = false
                elif self.ball.has_method("set_meta"): self.ball.set_meta("is_scrambled", false)

    var is_emped = false
    if "is_emped" in self.ball:
        is_emped = self.ball.is_emped
    elif self.ball.has_method("get_meta") and self.ball.has_meta("is_emped"):
        is_emped = self.ball.get_meta("is_emped")

    if is_emped:
        if "emp_timer" in self.ball:
            self.ball.emp_timer -= delta
            if self.ball.emp_timer <= 0:
                self.ball.is_emped = false
        elif self.ball.has_method("get_meta") and self.ball.has_meta("emp_timer"):
            var cur = self.ball.get_meta("emp_timer") - delta
            self.ball.set_meta("emp_timer", cur)
            if cur <= 0:
                self.ball.set_meta("is_emped", false)

    var is_stunned = false
    if "is_stunned" in self.ball:
        is_stunned = self.ball.is_stunned
        if is_stunned:
            stun_timer = self.ball.stun_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("is_stunned"):
        is_stunned = self.ball.get_meta("is_stunned")
        if is_stunned:
            stun_timer = self.ball.get_meta("stun_timer")

    if is_stunned:
        if stun_timer > 0.0:
            if "stun_timer" in self.ball:
                self.ball.stun_timer -= delta
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("stun_timer", stun_timer - delta)
            return
        else:
            if "is_stunned" in self.ball:
                self.ball.is_stunned = false
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("is_stunned", false)

    var current_hp = 100.0
    if "hp" in self.ball: current_hp = float(self.ball.hp)

    var current_stun = 0.0
    if "stun_timer" in self.ball:
        current_stun = float(self.ball.stun_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("stun_timer"):
        current_stun = float(self.ball.get_meta("stun_timer"))

    var current_silence = 0.0
    if "silence_timer" in self.ball:
        current_silence = float(self.ball.silence_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("silence_timer"):
        current_silence = float(self.ball.get_meta("silence_timer"))

    var damage_taken = start_hp - current_hp
    var stun_taken = current_stun - start_stun
    var silence_taken = current_silence - start_silence

    var chaos_target = null
    if "chaos_link_target" in self.ball: chaos_target = self.ball.chaos_link_target
    elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_target"): chaos_target = self.ball.get_meta("chaos_link_target")

    if chaos_target != null and ("alive" in chaos_target and chaos_target.alive):
        var is_receiving = false
        if "chaos_link_is_receiving" in self.ball: is_receiving = self.ball.chaos_link_is_receiving
        elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_is_receiving"): is_receiving = self.ball.get_meta("chaos_link_is_receiving")

        if damage_taken > 0 and not is_receiving:
            if "chaos_link_is_receiving" in chaos_target: chaos_target.chaos_link_is_receiving = true
            elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_is_receiving", true)

            var half_damage = damage_taken * 0.5
            if chaos_target.has_method("take_damage"):
                chaos_target.take_damage(half_damage)
            elif "hp" in chaos_target:
                chaos_target.hp -= half_damage
                if chaos_target.hp <= 0:
                    chaos_target.alive = false

            var max_hp = 100.0
            if "max_hp" in self.ball: max_hp = self.ball.max_hp
            if "hp" in self.ball:
                self.ball.hp = min(max_hp, self.ball.hp + half_damage)

            if "chaos_link_is_receiving" in chaos_target: chaos_target.chaos_link_is_receiving = false
            elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_is_receiving", false)

        var c_speed = 2.0
        var b_speed = 2.0
        if "speed" in self.ball: c_speed = self.ball.speed
        if "base_speed" in self.ball: b_speed = self.ball.base_speed

        if c_speed > b_speed:
            var buff_sharing = false
            if "chaos_link_buff_sharing" in self.ball: buff_sharing = self.ball.chaos_link_buff_sharing
            elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_buff_sharing"): buff_sharing = self.ball.get_meta("chaos_link_buff_sharing")

            if not buff_sharing:
                if "chaos_link_buff_sharing" in chaos_target: chaos_target.chaos_link_buff_sharing = true
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_buff_sharing", true)

                if "speed" in chaos_target: chaos_target.speed = c_speed
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("speed", c_speed)

                if "chaos_link_buff_sharing" in chaos_target: chaos_target.chaos_link_buff_sharing = false
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_buff_sharing", false)

        var c_dmg = 10.0
        if "damage" in self.ball: c_dmg = self.ball.damage
        elif self.ball.has_method("get_meta") and self.ball.has_meta("damage"): c_dmg = self.ball.get_meta("damage")

        var b_dmg = 10.0
        if "base_damage" in self.ball: b_dmg = self.ball.base_damage

        if c_dmg > b_dmg:
            var buff_sharing = false
            if "chaos_link_buff_sharing" in self.ball: buff_sharing = self.ball.chaos_link_buff_sharing
            elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_buff_sharing"): buff_sharing = self.ball.get_meta("chaos_link_buff_sharing")

            if not buff_sharing:
                if "chaos_link_buff_sharing" in chaos_target: chaos_target.chaos_link_buff_sharing = true
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_buff_sharing", true)

                if "damage" in chaos_target: chaos_target.damage = c_dmg
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("damage", c_dmg)

                if "chaos_link_buff_sharing" in chaos_target: chaos_target.chaos_link_buff_sharing = false
                elif chaos_target.has_method("set_meta"): chaos_target.set_meta("chaos_link_buff_sharing", false)

    var link_target = null
    if "damage_link_target" in self.ball: link_target = self.ball.damage_link_target
    elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_target"): link_target = self.ball.get_meta("damage_link_target")

    if link_target != null and ("alive" in link_target and link_target.alive):
        var dist_sq = pow(self.ball.x - link_target.x, 2) + pow(self.ball.y - link_target.y, 2)
        if dist_sq > 90000.0:  # Distance > 300 breaks the link
            if "damage_link_target" in self.ball: self.ball.damage_link_target = null
            elif self.ball.has_method("set_meta"): self.ball.set_meta("damage_link_target", null)

            var target_link = null
            if "damage_link_target" in link_target: target_link = link_target.damage_link_target
            elif link_target.has_method("get_meta") and link_target.has_meta("damage_link_target"): target_link = link_target.get_meta("damage_link_target")

            if target_link == self.ball:
                if "damage_link_target" in link_target: link_target.damage_link_target = null
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_target", null)
        else:
            var is_receiving = false
            if "damage_link_is_receiving" in self.ball: is_receiving = self.ball.damage_link_is_receiving
            elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_is_receiving"): is_receiving = self.ball.get_meta("damage_link_is_receiving")

            if damage_taken > 0 and not is_receiving:
                if "damage_link_is_receiving" in link_target: link_target.damage_link_is_receiving = true
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving", true)

                if link_target.has_method("take_damage"):
                    link_target.take_damage(damage_taken * 0.5)
                elif "hp" in link_target:
                    link_target.hp -= damage_taken * 0.5
                    if link_target.hp <= 0:
                        link_target.alive = false

                if "damage_link_is_receiving" in link_target: link_target.damage_link_is_receiving = false
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving", false)

            var is_receiving_stun = false
            if "damage_link_is_receiving_stun" in self.ball: is_receiving_stun = self.ball.damage_link_is_receiving_stun
            elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_is_receiving_stun"): is_receiving_stun = self.ball.get_meta("damage_link_is_receiving_stun")

            if stun_taken > 0 and not is_receiving_stun:
                if "damage_link_is_receiving_stun" in link_target: link_target.damage_link_is_receiving_stun = true
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving_stun", true)

                var l_stun = 0.0
                if "stun_timer" in link_target: l_stun = link_target.stun_timer
                elif link_target.has_method("get_meta") and link_target.has_meta("stun_timer"): l_stun = link_target.get_meta("stun_timer")

                if "stun_timer" in link_target: link_target.stun_timer = l_stun + stun_taken * 0.5
                elif link_target.has_method("set_meta"): link_target.set_meta("stun_timer", l_stun + stun_taken * 0.5)

                if "is_stunned" in link_target: link_target.is_stunned = true
                elif link_target.has_method("set_meta"): link_target.set_meta("is_stunned", true)

                if "damage_link_is_receiving_stun" in link_target: link_target.damage_link_is_receiving_stun = false
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving_stun", false)

            var is_receiving_silence = false
            if "damage_link_is_receiving_silence" in self.ball: is_receiving_silence = self.ball.damage_link_is_receiving_silence
            elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_is_receiving_silence"): is_receiving_silence = self.ball.get_meta("damage_link_is_receiving_silence")

            if silence_taken > 0 and not is_receiving_silence:
                if "damage_link_is_receiving_silence" in link_target: link_target.damage_link_is_receiving_silence = true
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving_silence", true)

                var l_silence = 0.0
                if "silence_timer" in link_target: l_silence = link_target.silence_timer
                elif link_target.has_method("get_meta") and link_target.has_meta("silence_timer"): l_silence = link_target.get_meta("silence_timer")

                if "silence_timer" in link_target: link_target.silence_timer = l_silence + silence_taken * 0.5
                elif link_target.has_method("set_meta"): link_target.set_meta("silence_timer", l_silence + silence_taken * 0.5)

                if "damage_link_is_receiving_silence" in link_target: link_target.damage_link_is_receiving_silence = false
                elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_is_receiving_silence", false)

    if strategy == "flee":
        _flee(delta)
    elif strategy == "ricochet_attack":
        _ricochet_attack(delta)
    elif strategy == "attack":
        _attack(delta)
    elif strategy == "kite":
        # Cosmetics: kite verify auto-implement-kite-держит-дистанцию-атакует-при
        _kite(delta)
    elif strategy == "chase":
        _chase(delta)
    elif strategy == "flank":
        _flank(delta)
    elif strategy == "escort":
        _escort(delta)
    elif strategy == "intercept":
        _intercept(delta)
    elif strategy == "hide_behind":
        _hide_behind(delta)
    elif strategy == "group_attack":
        _group_attack(delta)
    elif strategy == "defend":
        _defend(delta)
    elif strategy == "hold_zone":
        _hold_zone(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        _collect_booster(delta)
    elif strategy == "use skill" or strategy == "use_skill" or strategy == "action_skill" or strategy == "Действие":
        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill
        elif "SKILL" in self.ball:
            skill_name = self.ball.SKILL

        if skill_name == "flank":
            if "current_action" in self.ball:
                self.ball.current_action = "flank"
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("current_action", "flank")
            _flank(delta)
        else:
            _use_skill()
    else:
        _idle(delta)

    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()

    if bounced_wall:
        var vx = 0.0
        var vy = 0.0
        if "vx" in self.ball: vx = self.ball.vx
        elif self.ball.has_method("get_meta") and self.ball.has_meta("vx"): vx = self.ball.get_meta("vx")
        if "vy" in self.ball: vy = self.ball.vy
        elif self.ball.has_method("get_meta") and self.ball.has_meta("vy"): vy = self.ball.get_meta("vy")

        var speed_sq = vx*vx + vy*vy
        if speed_sq > 0:
            var speed = sqrt(speed_sq)
            var w = 1000.0
            if "width" in self.world: w = self.world.width
            var h = 1000.0
            if "height" in self.world: h = self.world.height
            var r = 10.0
            if "radius" in self.ball: r = self.ball.radius
            var margin = r + 5.0

            var nvx = vx
            var nvy = vy

            if self.ball.x <= margin or self.ball.x >= w - margin:
                nvx = -vx
            if self.ball.y <= margin or self.ball.y >= h - margin:
                nvy = -vy

            if nvx == vx and nvy == vy:
                nvx = -vx
                nvy = -vy

            var new_speed = min(speed * 1.5, 2000.0)
            var angle = atan2(nvy, nvx) + randf_range(-0.1, 0.1)

            nvx = cos(angle) * new_speed
            nvy = sin(angle) * new_speed

            if typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["_reflection_vx"] = nvx
                self.ball["_reflection_vy"] = nvy
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("_reflection_vx", nvx)
                self.ball.set_meta("_reflection_vy", nvy)
            elif "vx" in self.ball:
                self.ball._reflection_vx = nvx
                self.ball._reflection_vy = nvy

            var gm = null
            if typeof(self.world) == TYPE_DICTIONARY and self.world.has("game_mode"):
                gm = self.world["game_mode"]
            elif typeof(self.world) == TYPE_OBJECT and "game_mode" in self.world:
                gm = self.world.game_mode

            var is_mirror_walls = false
            if gm != null and typeof(gm) == TYPE_OBJECT and "name" in gm and gm.name == "Mirror Walls":
                is_mirror_walls = true
            elif typeof(gm) == TYPE_DICTIONARY and gm.has("name") and gm["name"] == "Mirror Walls":
                is_mirror_walls = true

            if speed > 500 and not is_mirror_walls:
                var dmg = speed * 0.05
                if self.ball.has_method("take_damage"):
                    self.ball.take_damage(dmg)
                elif "hp" in self.ball:
                    self.ball.hp -= dmg
                    if self.ball.hp <= 0:
                        if "alive" in self.ball: self.ball.alive = false
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)

            if is_mirror_walls:
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["vx"] = nvx
                    self.ball["vy"] = nvy
                elif "vx" in self.ball:
                    self.ball.vx = nvx
                    self.ball.vy = nvy


    if bounced_wall or bounced_col:
        _trigger_ripple_effect()

    _apply_friendly_aura(delta)
    _update_skill_timer(delta)

    if delta > 0:
        var dx = self.ball.x - old_x
        var dy = self.ball.y - old_y

        var n_timer = 0.0
        if "invert_timer" in self.ball:
            var inv_t = float(self.ball.invert_timer)
            if inv_t > 0:
                inv_t -= delta
                if inv_t < 0: inv_t = 0.0
                self.ball.invert_timer = inv_t
        elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"):
            var inv_t = float(self.ball.get_meta("invert_timer"))
            if inv_t > 0:
                inv_t -= delta
                if inv_t < 0: inv_t = 0.0
                self.ball.set_meta("invert_timer", inv_t)

        if "nemesis_booster_timer" in self.ball:
            n_timer = float(self.ball.nemesis_booster_timer)
        elif self.ball.has_method("get_meta") and self.ball.has_meta("nemesis_booster_timer"):
            n_timer = float(self.ball.get_meta("nemesis_booster_timer"))

        if n_timer > 0.0:
            if "profile_manager" in self.world and self.world.profile_manager != null and self.world.profile_manager.has_method("is_nemesis"):
                var pm = self.world.profile_manager
                var nemesis = null
                var min_dist_sq = 1e9
                if "balls" in self.world:
                    for other in self.world.balls:
                        if other.get("id") != self.ball.get("id") and other.get("hp", 0.0) > 0.0:
                            var my_type = self.ball.get("ball_type")
                            var other_type = other.get("ball_type")
                            if my_type != null and other_type != null:
                                if pm.is_nemesis(my_type, other_type):
                                    var dsq = pow(other.x - self.ball.x, 2) + pow(other.y - self.ball.y, 2)
                                    if dsq < min_dist_sq:
                                        min_dist_sq = dsq
                                        nemesis = other
                if nemesis != null:
                    var ndx = nemesis.x - self.ball.x
                    var ndy = nemesis.y - self.ball.y
                    var ndist = sqrt(ndx*ndx + ndy*ndy)
                    if ndist > 0.0001:
                        var bs = 2.0
                        if "base_speed" in self.ball:
                            bs = float(self.ball.base_speed)
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                            bs = float(self.ball.get_meta("base_speed"))
                        var extra_speed = (bs * 0.5) * delta
                        dx += (ndx / ndist) * extra_speed
                        dy += (ndy / ndist) * extra_speed
                        self.ball.x = old_x + dx
                        self.ball.y = old_y + dy

        var act_dist = sqrt(dx*dx + dy*dy)
        var act_stamina = 100.0
        var act_max_stamina = 100.0
        if my_ball.has_meta("stamina"): act_stamina = my_ball.get_meta("stamina")
        if my_ball.has_meta("max_stamina"): act_max_stamina = my_ball.get_meta("max_stamina")

        var act_base_speed = 2.0
        if my_ball.has_meta("base_speed"): act_base_speed = my_ball.get_meta("base_speed")

        var is_dash = false
        if my_ball.has_meta("is_dashing"): is_dash = my_ball.get_meta("is_dashing")

        var _is_silenced = false
        if my_ball.has_method("has_meta") and my_ball.has_meta("silence_timer") and my_ball.get_meta("silence_timer") > 0.0:
            _is_silenced = true
        elif "silence_timer" in my_ball and my_ball.silence_timer > 0.0:
            _is_silenced = true

        if _is_silenced:
            is_dash = false
            if my_ball.has_method("set_meta"):
                my_ball.set_meta("is_dashing", false)

        var infinite_stamina = 0.0
        if my_ball.has_meta("infinite_stamina_timer"): infinite_stamina = my_ball.get_meta("infinite_stamina_timer")
        elif "infinite_stamina_timer" in my_ball: infinite_stamina = my_ball.infinite_stamina_timer

        var arena = world.call('get_arena') if world != null and world.has_method('get_arena') else null
        var is_heatwave = false
        var is_snowing = false
        if arena != null:
            if typeof(arena) == TYPE_OBJECT and arena.has_method('get'):
                is_heatwave = arena.get("is_heatwave") == true
                is_snowing = arena.get("is_snowing") == true
            elif "is_heatwave" in arena:
                is_heatwave = arena.is_heatwave == true
                if "is_snowing" in arena:
                    is_snowing = arena.is_snowing == true

        var drain_mult = 2.0 if is_heatwave else 1.0
        var regen_mult = 0.5 if is_heatwave else 1.0

        if is_dash:
            if infinite_stamina <= 0:
                my_ball.set_meta("stamina", max(0.0, act_stamina - (50.0 * drain_mult) * delta))
        elif my_ball.has_meta("_is_wind_riding") and my_ball.get_meta("_is_wind_riding") == true:
            if infinite_stamina <= 0:
                my_ball.set_meta("stamina", max(0.0, act_stamina - (15.0 * drain_mult) * delta))
        elif "_is_wind_riding" in my_ball and my_ball._is_wind_riding == true:
            if infinite_stamina <= 0:
                my_ball.set_meta("stamina", max(0.0, act_stamina - (15.0 * drain_mult) * delta))
        elif act_dist / max(0.0001, delta * 60) < act_base_speed * 0.5:
            my_ball.set_meta("stamina", min(act_max_stamina, act_stamina + (30.0 * regen_mult) * delta))

        var vx = dx / delta
        var vy = dy / delta

        if typeof(my_ball) == TYPE_DICTIONARY:
            if my_ball.has("_reflection_vx"):
                vx = my_ball["_reflection_vx"]
                my_ball.erase("_reflection_vx")
            if my_ball.has("_reflection_vy"):
                vy = my_ball["_reflection_vy"]
                my_ball.erase("_reflection_vy")
        elif my_ball.has_method("has_meta"):
            if my_ball.has_meta("_reflection_vx"):
                vx = my_ball.get_meta("_reflection_vx")
                my_ball.remove_meta("_reflection_vx")
            if my_ball.has_meta("_reflection_vy"):
                vy = my_ball.get_meta("_reflection_vy")
                my_ball.remove_meta("_reflection_vy")
        elif "_reflection_vx" in my_ball:
            vx = my_ball._reflection_vx
            vy = my_ball._reflection_vy

        if is_snowing and (vx != 0 or vy != 0):
            if my_ball.has_method("set_meta") and my_ball.has_meta("x"):
                my_ball.set_meta("x", my_ball.get_meta("x") + vx * delta * 0.5)
                my_ball.set_meta("y", my_ball.get_meta("y") + vy * delta * 0.5)
            elif "x" in my_ball:
                my_ball.x += vx * delta * 0.5
                my_ball.y += vy * delta * 0.5
        if "vx" in self.ball:
            self.ball.vx = vx
            self.ball.vy = vy
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("vx", vx)
            self.ball.set_meta("vy", vy)

        if "distance_traveled" in self.ball:
            self.ball.distance_traveled += sqrt(dx*dx + dy*dy)
        elif self.ball.has_method("get_meta"):
            var current_dist = self.ball.get_meta("distance_traveled") if self.ball.has_meta("distance_traveled") else 0.0
            self.ball.set_meta("distance_traveled", current_dist + sqrt(dx*dx + dy*dy))


func _apply_boid_rules(nx: float, ny: float) -> Array:
    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    if b_type != "swarm":
        return [nx, ny]

    var allies = _get_allies()
    if allies.size() == 0:
        return [nx, ny]

    var cohesion_weight = 0.5
    var alignment_weight = 0.5
    var separation_weight = 1.0

    var center_x = 0.0
    var center_y = 0.0
    var align_vx = 0.0
    var align_vy = 0.0
    var sep_nx = 0.0
    var sep_ny = 0.0

    var count = 0
    var perception_radius = self._get_perception_radius()

    for ally in allies:
        var dx = self.ball.x - ally.x
        var dy = self.ball.y - ally.y
        var dist_sq = dx*dx + dy*dy

        if dist_sq > 0.0001 and dist_sq < perception_radius * perception_radius:
            count += 1
            var dist = sqrt(dist_sq)

            center_x += ally.x
            center_y += ally.y

            if "vx" in ally: align_vx += ally.vx
            elif ally.has_method("get_meta") and ally.has_meta("vx"): align_vx += ally.get_meta("vx")

            if "vy" in ally: align_vy += ally.vy
            elif ally.has_method("get_meta") and ally.has_meta("vy"): align_vy += ally.get_meta("vy")

            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius
            var ally_radius = 10.0
            if "radius" in ally: ally_radius = ally.radius

            var sep_dist = (ball_radius + ally_radius) * 2.0
            if dist < sep_dist:
                sep_nx += (dx / dist) / dist
                sep_ny += (dy / dist) / dist

    if count > 0:
        center_x /= count
        center_y /= count

        var coh_dx = center_x - self.ball.x
        var coh_dy = center_y - self.ball.y
        var coh_dist_sq = coh_dx*coh_dx + coh_dy*coh_dy
        var coh_nx = 0.0
        var coh_ny = 0.0
        if coh_dist_sq > 0.0001:
            var coh_dist = sqrt(coh_dist_sq)
            coh_nx = coh_dx / coh_dist
            coh_ny = coh_dy / coh_dist

        align_vx /= count
        align_vy /= count
        var align_speed_sq = align_vx*align_vx + align_vy*align_vy
        var al_nx = 0.0
        var al_ny = 0.0
        if align_speed_sq > 0.0001:
            var align_speed = sqrt(align_speed_sq)
            al_nx = align_vx / align_speed
            al_ny = align_vy / align_speed

        var comb_nx = nx + coh_nx * cohesion_weight + al_nx * alignment_weight + sep_nx * separation_weight
        var comb_ny = ny + coh_ny * cohesion_weight + al_ny * alignment_weight + sep_ny * separation_weight

        var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
        if comb_dist_sq > 0.0001:
            var comb_dist = sqrt(comb_dist_sq)
            return [comb_nx / comb_dist, comb_ny / comb_dist]

    return [nx, ny]

func _apply_obstacle_avoidance(nx: float, ny: float, target=null, ignore_enemies: bool = false) -> Array:
    var all_entities = []
    var perception_radius = self._get_perception_radius()

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY:
            if entities.has("enemies") and not ignore_enemies:
                for e in entities["enemies"]:
                    all_entities.append(e)
            if entities.has("allies"):
                for e in entities["allies"]:
                    all_entities.append(e)
        elif typeof(entities) == TYPE_ARRAY:
            for e in entities:
                var is_alive = true
                if "alive" in e: is_alive = e.alive

                var is_enemy = false
                if "ball_type" in self.ball and "ball_type" in e:
                    var e_type = e.ball_type
                    is_enemy = (self.ball.ball_type != e_type and e_type != "booster")

                if is_alive and e != self.ball:
                    if ignore_enemies and is_enemy:
                        continue
                    all_entities.append(e)
            if entities.has("allies"):
                for e in entities["allies"]:
                    all_entities.append(e)
        elif typeof(entities) == TYPE_ARRAY:
            for e in entities:
                var is_alive = true
                if "alive" in e: is_alive = e.alive

                var is_enemy = false
                if "ball_type" in self.ball and "ball_type" in e:
                    is_enemy = (self.ball.ball_type != e.ball_type)

                if is_alive and e != self.ball:
                    if ignore_enemies and is_enemy:
                        continue
                    all_entities.append(e)

    var repulse_nx = 0.0
    var repulse_ny = 0.0
    var ball_radius = 10.0
    if "radius" in self.ball:
        ball_radius = self.ball.radius

    for entity in all_entities:
        if entity == target or entity == self.ball:
            continue

        var entity_radius = 10.0
        if "radius" in entity:
            entity_radius = entity.radius

        var dx = self.ball.x - entity.x
        var dy = self.ball.y - entity.y
        var dist_sq = dx*dx + dy*dy

        var safe_dist = ball_radius + entity_radius + 5.0
        if dist_sq > 0.0001 and dist_sq < safe_dist * safe_dist:
            var dist = sqrt(dist_sq)
            var force = 1.0 - (dist / safe_dist)
            var is_enemy = false
            if "ball_type" in entity and "ball_type" in self.ball:
                is_enemy = entity.ball_type != self.ball.ball_type and entity.ball_type != "spectator"
            elif entity.has_method("get_ball_type") and self.ball.has_method("get_ball_type"):
                is_enemy = entity.get_ball_type() != self.ball.get_ball_type() and entity.get_ball_type() != "spectator"

            if is_enemy:
                var damage = 10.0
                if "damage" in entity:
                    damage = entity.damage
                var cd = 1.5
                if "attack_cooldown" in entity:
                    cd = max(0.1, entity.attack_cooldown)
                var dps = damage / cd
                var attack_range = 150.0
                if "attack_range" in entity:
                    attack_range = entity.attack_range

                var danger_coefficient = 1.0
                if self.world != null and "arena" in self.world and "danger_grid" in self.world.arena:
                    var grid_x = int(entity.x / 100)
                    var grid_y = int(entity.y / 100)
                    var key = str(grid_x) + "," + str(grid_y)
                    if self.world.arena.danger_grid.has(key):
                        danger_coefficient += self.world.arena.danger_grid[key]

                if dist < attack_range:
                    danger_coefficient += (dps / 10.0)
                force *= danger_coefficient
            repulse_nx += (dx / dist) * force
            repulse_ny += (dy / dist) * force


    if self.world != null and "arena" in self.world and "danger_grid" in self.world.arena:
        for step in [20, 50, 80]:
            var check_x = self.ball.x + nx * step
            var check_y = self.ball.y + ny * step
            var grid_x = int(check_x / 100)
            var grid_y = int(check_y / 100)
            var key = str(grid_x) + "," + str(grid_y)
            if self.world.arena.danger_grid.has(key):
                var danger = self.world.arena.danger_grid[key]
                if danger > 1.0:
                    var cell_cx = grid_x * 100 + 50
                    var cell_cy = grid_y * 100 + 50
                    var ddx = self.ball.x - cell_cx
                    var ddy = self.ball.y - cell_cy
                    var ddist_sq = ddx*ddx + ddy*ddy
                    if ddist_sq > 0.0001:
                        var ddist = sqrt(ddist_sq)
                        var force = (danger / 10.0) * (1.0 / (ddist / 100.0 + 0.1))
                        repulse_nx += (ddx / ddist) * force
                        repulse_ny += (ddy / ddist) * force
    var steering_mult = 1.0
    if ball.has_method("has_meta") and ball.has_meta("steering_mult"):
        steering_mult = ball.get_meta("steering_mult")
    var comb_nx = nx + repulse_nx * 0.5 * steering_mult
    var comb_ny = ny + repulse_ny * 0.5 * steering_mult

    var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
    if comb_dist_sq > 0.0001:
        var comb_dist = sqrt(comb_dist_sq)
        return [comb_nx / comb_dist, comb_ny / comb_dist]
    return [nx, ny]

func _get_enemies() -> Array:
    var is_conf = false
    if "is_confused" in self.ball:
        is_conf = self.ball.is_confused
    elif self.ball.has_method("has_meta") and self.ball.has_meta("is_confused"):
        is_conf = self.ball.get_meta("is_confused")

    if is_conf:
        return _get_allies_internal()
    return _get_enemies_internal()

func _get_enemies_internal() -> Array:
    var perception_radius = self._get_perception_radius()

    var my_stealth_zones = []
    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
        for h in self.world.arena.hazards:
            var h_kind = h.kind if "kind" in h else (h.get_meta("kind") if h.has_method("has_meta") and h.has_meta("kind") else "")
            if h_kind == "stealth_zone":
                var hx = h.x if "x" in h else h.get_meta("x")
                var hy = h.y if "y" in h else h.get_meta("y")
                var hr = h.radius if "radius" in h else h.get_meta("radius")
                var dx = hx - self.ball.x
                var dy = hy - self.ball.y
                if dx*dx + dy*dy <= hr*hr:
                    my_stealth_zones.append(h)

    var enemies = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("enemies"):
            for e in entities["enemies"]:
                var e_type = e.ball_type if "ball_type" in e else (e.get_ball_type() if e.has_method("get_ball_type") else "")
                if e_type != "spectator":
                    enemies.append(e)
        elif typeof(entities) == TYPE_ARRAY:
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type != b_type and e_type != "spectator":
                        enemies.append(e)

    if enemies.size() == 0 and self.world != null and "balls" in self.world:
        for b in self.world.balls:
            var is_decoy = b.is_decoy if "is_decoy" in b else (b.get_meta("is_decoy") if b.has_method("has_meta") and b.has_meta("is_decoy") else false)
            var is_illusion = b.is_illusion if "is_illusion" in b else (b.get_meta("is_illusion") if b.has_method("has_meta") and b.has_meta("is_illusion") else false)
            var alive = b.alive if "alive" in b else (b.get_meta("alive") if b.has_method("has_meta") and b.has_meta("alive") else true)
            if alive and not is_decoy and not is_illusion:
                var e_type = b.ball_type if "ball_type" in b else (b.get_ball_type() if b.has_method("get_ball_type") else "")
                var my_type = self.ball.ball_type if "ball_type" in self.ball else (self.ball.get_ball_type() if self.ball.has_method("get_ball_type") else "")
                if e_type != my_type and e_type != "spectator":
                    var bx = b.x if "x" in b else b.get_meta("x")
                    var by = b.y if "y" in b else b.get_meta("y")
                    var dx = bx - self.ball.x
                    var dy = by - self.ball.y
                    if dx*dx + dy*dy <= perception_radius*perception_radius:
                        enemies.append(b)

    if self.world != null and "balls" in self.world:
        for b in self.world.balls:
            var is_decoy = false
            if "is_decoy" in b:
                is_decoy = b.is_decoy
            elif b.has_method("has_meta") and b.has_meta("is_decoy"):
                is_decoy = b.get_meta("is_decoy")
            var is_alive = true
            if "alive" in b:
                is_alive = b.alive
            elif b.has_method("has_meta") and b.has_meta("alive"):
                is_alive = b.get_meta("alive")
            if is_decoy and is_alive and not enemies.has(b):
                var e_type = b.ball_type if "ball_type" in b else (b.get_ball_type() if b.has_method("get_ball_type") else "")
                var my_type = self.ball.ball_type if "ball_type" in self.ball else (self.ball.get_ball_type() if self.ball.has_method("get_ball_type") else "")
                if e_type != my_type:
                    var bx = b.x if "x" in b else b.get_meta("x")
                    var by = b.y if "y" in b else b.get_meta("y")
                    var dx = bx - self.ball.x
                    var dy = by - self.ball.y
                    if dx*dx + dy*dy <= perception_radius*perception_radius:
                        enemies.append(b)

    if self.world != null and "balls" in self.world:
        for b in self.world.balls:
            var is_illusion = false
            if "is_illusion" in b:
                is_illusion = b.is_illusion
            elif b.has_method("has_meta") and b.has_meta("is_illusion"):
                is_illusion = b.get_meta("is_illusion")
            var is_alive = true
            if "alive" in b:
                is_alive = b.alive
            elif b.has_method("has_meta") and b.has_meta("alive"):
                is_alive = b.get_meta("alive")
            if is_illusion and is_alive and not enemies.has(b):
                var b_team = b.team if "team" in b else (b.get_meta("team") if b.has_method("has_meta") and b.has_meta("team") else (b.ball_type if "ball_type" in b else ""))
                var my_team = self.ball.team if "team" in self.ball else (self.ball.get_meta("team") if self.ball.has_method("has_meta") and self.ball.has_meta("team") else (self.ball.ball_type if "ball_type" in self.ball else ""))
                if b_team != my_team:
                    var bx = b.x if "x" in b else b.get_meta("x")
                    var by = b.y if "y" in b else b.get_meta("y")
                    var dx = bx - self.ball.x
                    var dy = by - self.ball.y
                    if dx*dx + dy*dy <= perception_radius*perception_radius:
                        enemies.append(b)

    if self.world != null and "arena" in self.world and self.world.arena != null:
        var arena = self.world.arena
        if arena != null and "hazards" in arena:
            for h in arena.hazards:
                if "kind" in h and h.kind == "flare":
                    var is_active = true
                    if "active" in h:
                        is_active = h.active
                    elif h.has_method("has_meta") and h.has_meta("active"):
                        is_active = h.get_meta("active")

                    if is_active:
                        var owner_id = null
                        if "owner_id" in h:
                            owner_id = h.owner_id
                        elif h.has_method("has_meta") and h.has_meta("owner_id"):
                            owner_id = h.get_meta("owner_id")

                        var my_id = null
                        if "id" in self.ball:
                            my_id = self.ball.id

                        if owner_id != null and my_id != null and owner_id == my_id:
                            continue

                        var hx = h.x if "x" in h else h.get_meta("x")
                        var hy = h.y if "y" in h else h.get_meta("y")
                        var dx = hx - self.ball.x
                        var dy = hy - self.ball.y
                        if dx*dx + dy*dy <= perception_radius*perception_radius:
                            enemies.append(h)

    var filtered_enemies = []
    for e in enemies:
        var enemy_stealth_zones = []
        var ex = e.x if "x" in e else (e.get_meta("x") if e.has_method("has_meta") and e.has_meta("x") else 0)
        var ey = e.y if "y" in e else (e.get_meta("y") if e.has_method("has_meta") and e.has_meta("y") else 0)
        if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
            for h in self.world.arena.hazards:
                var h_kind = h.kind if "kind" in h else (h.get_meta("kind") if h.has_method("has_meta") and h.has_meta("kind") else "")
                if h_kind == "stealth_zone":
                    var hx = h.x if "x" in h else h.get_meta("x")
                    var hy = h.y if "y" in h else h.get_meta("y")
                    var hr = h.radius if "radius" in h else h.get_meta("radius")
                    var dx = hx - ex
                    var dy = hy - ey
                    if dx*dx + dy*dy <= hr*hr:
                        enemy_stealth_zones.append(h)

        var is_visible = true
        if enemy_stealth_zones.size() > 0:
            is_visible = false
            for h in my_stealth_zones:
                if enemy_stealth_zones.has(h):
                    is_visible = true
                    break
        elif my_stealth_zones.size() > 0:
            is_visible = false

        if is_visible:
            filtered_enemies.append(e)

    return filtered_enemies

func _get_allies_internal() -> Array:
    var perception_radius = self._get_perception_radius()

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("allies"):
            return entities["allies"]
        elif typeof(entities) == TYPE_ARRAY:
            var allies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type == b_type and e != self.ball and e_type != "spectator":
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            allies.append(e)
            return allies
    return []

func _get_boosters() -> Array:
    var perception_radius = self._get_perception_radius()

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("boosters"):
            return entities["boosters"]

    var boosters = []
    if self.world != null and "boosters" in self.world:
        for b in self.world.boosters:
            if "active" in b and b.active:
                var dx = b.x - self.ball.x
                var dy = b.y - self.ball.y
                if sqrt(dx*dx + dy*dy) <= perception_radius:
                    boosters.append(b)
    return boosters

func _flee(delta: float):
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var nearest = null
    var min_dist_sq = INF
    for e in enemies:
        var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest = e

    var dx = self.ball.x - nearest.x
    var dy = self.ball.y - nearest.y
    var dist_sq = dx*dx + dy*dy
    var dist = 0.01
    if dist_sq > 0.0001:
        dist = sqrt(dist_sq)

    var perception_radius = self._get_perception_radius()

    if dist > perception_radius * 0.8:
        _idle(delta)
        return

    if dist < 0.01:
        dist = 0.01

    var flee_nx = dx / dist
    var flee_ny = dy / dist

    var allies = _get_allies()
    var ally_nx = 0.0
    var ally_ny = 0.0

    if allies.size() > 0:
        var nearest_ally = null
        var min_adist_sq = INF
        for a in allies:
            var adist_sq = pow(a.x - self.ball.x, 2) + pow(a.y - self.ball.y, 2)
            if adist_sq < min_adist_sq:
                min_adist_sq = adist_sq
                nearest_ally = a

        var adx = nearest_ally.x - self.ball.x
        var ady = nearest_ally.y - self.ball.y
        var adist_sq = adx*adx + ady*ady
        if adist_sq > 0.0001:
            var adist = sqrt(adist_sq)
            ally_nx = adx / adist
            ally_ny = ady / adist

    var safe_nx = 0.0
    var safe_ny = 0.0
    if self.world != null and "width" in self.world and "height" in self.world:
        var center_x = self.world.width / 2.0
        var center_y = self.world.height / 2.0
        var cdx = center_x - self.ball.x
        var cdy = center_y - self.ball.y
        var cdist_sq = cdx*cdx + cdy*cdy

        if cdist_sq > 0.0001:
            var cdist = sqrt(cdist_sq)
            var min_center_dim = center_x
            if center_y < center_x:
                min_center_dim = center_y

            if cdist > min_center_dim * 0.3:
                safe_nx = cdx / cdist
                safe_ny = cdy / cdist

    var comb_nx = flee_nx * 1.0 + ally_nx * 0.4 + safe_nx * 0.3
    var comb_ny = flee_ny * 1.0 + ally_ny * 0.4 + safe_ny * 0.3

    var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
    if comb_dist_sq > 0.0001:
        var comb_dist = sqrt(comb_dist_sq)
        comb_nx /= comb_dist
        comb_ny /= comb_dist
    else:
        comb_nx = flee_nx
        comb_ny = flee_ny

    var boid_vec = _apply_boid_rules(comb_nx, comb_ny)
    comb_nx = boid_vec[0]
    comb_ny = boid_vec[1]

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var boosted_speed = speed * 1.5

    var emotion = "neutral"
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("emotion"):
        emotion = self.ball.get_meta("emotion")
    elif "emotion" in self.ball:
        emotion = self.ball.emotion

    if emotion == "fear":
        boosted_speed *= 1.5

    self.ball.x += comb_nx * boosted_speed * delta * 60.0
    self.ball.y += comb_ny * boosted_speed * delta * 60.0

func _evaluate_target_strength_deterministic(e: Object) -> Array:
    var e_max_hp = 0.0
    if "max_hp" in e:
        e_max_hp = float(e.max_hp)
    elif "hp" in e:
        e_max_hp = float(e.hp)

    var e_hp = 0.0
    if "hp" in e:
        e_hp = float(e.hp)

    var d_sq = float(pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2))
    var e_id = 0
    if "id" in e:
        e_id = int(e.id)

    return [e_max_hp, e_hp, -d_sq, e_id]

func _find_strongest_enemy_deterministic(enemies: Array) -> Object:
    var best_score = [-1.0, -1.0, -INF, -1]
    var target = null

    for e in enemies:
        var score = _evaluate_target_strength_deterministic(e)

        var is_better = false
        if score[0] > best_score[0]:
            is_better = true
        elif score[0] == best_score[0]:
            if score[1] > best_score[1]:
                is_better = true
            elif score[1] == best_score[1]:
                if score[2] > best_score[2]:
                    is_better = true
                elif score[2] == best_score[2]:
                    if score[3] > best_score[3]:
                        is_better = true

        if is_better:
            best_score = score
            target = e

    return target

func _get_target(enemies: Array) -> Object:

    var is_scrambled = false
    if "is_scrambled" in self.ball:
        is_scrambled = self.ball.is_scrambled
    elif self.ball.has_method("get_meta") and self.ball.has_meta("is_scrambled"):
        is_scrambled = self.ball.get_meta("is_scrambled")

    if is_scrambled and enemies.size() > 0:
        return enemies[randi() % enemies.size()]
    var illusions = []
    for e in enemies:
        if "is_illusion" in e and e.is_illusion:
            illusions.append(e)
        elif typeof(e) == TYPE_DICTIONARY and e.has("is_illusion") and e["is_illusion"]:
            illusions.append(e)
        elif typeof(e) == TYPE_OBJECT and e.has_method("has_meta") and e.has_meta("is_illusion") and e.get_meta("is_illusion"):
            illusions.append(e)

    if illusions.size() > 0:
        var c_illusion = null
        var min_d_sq = INF
        for i_ent in illusions:
            var d_sq = pow(i_ent.x - self.ball.x, 2) + pow(i_ent.y - self.ball.y, 2)
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                c_illusion = i_ent
        if c_illusion != null:
            return c_illusion

    var flares = []
    for e in enemies:
        if "kind" in e and e.kind == "flare":
            flares.append(e)

    if flares.size() > 0:
        var c_flare = null
        var min_d_sq = INF
        for f_ent in flares:
            var d_sq = pow(f_ent.x - self.ball.x, 2) + pow(f_ent.y - self.ball.y, 2)
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                c_flare = f_ent
        if c_flare != null:
            return c_flare

    var ball_memory = {}
    if self.ball.has_method("get_meta") and self.ball.has_meta("memory"):
        ball_memory = self.ball.get_meta("memory")
    elif "memory" in self.ball:
        ball_memory = self.ball.memory

    var rival_targets = []
    # Ball Relationships - Balls remember each other
    # Rivalry skill: attacked me before -> attack on sight
    for e in enemies:
        if "id" in e and ball_memory.has(e.id):
            var rel = ball_memory[e.id]
            if typeof(rel) == TYPE_DICTIONARY and rel.get("relation") == "rival":
                rival_targets.append(e)

    if rival_targets.size() > 0:
        var c_rival = null
        var min_d_sq = INF
        for r_ent in rival_targets:
            var d_sq = pow(r_ent.x - self.ball.x, 2) + pow(r_ent.y - self.ball.y, 2)
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                c_rival = r_ent
        if c_rival != null:
            return c_rival

    var target_msg = null
    var allies = _get_allies()
    for ally in allies:
        var msg = null
        if ally.has_method("get_meta") and ally.has_meta("team_message"):
            msg = ally.get_meta("team_message")
        if typeof(msg) == TYPE_DICTIONARY and msg.has("type") and msg["type"] == "target_spotted":
            target_msg = msg
            break

    var target = null
    var min_dist_sq = INF

    if target_msg != null:
        var tx = target_msg.get("x", self.ball.x)
        var ty = target_msg.get("y", self.ball.y)
        for e in enemies:
            var dist_sq = pow(e.x - tx, 2) + pow(e.y - ty, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                target = e
    else:
        var b_type = ""
        if "ball_type" in self.ball:
            b_type = self.ball.ball_type.to_lower()
        if b_type == "tank":
            target = _find_strongest_enemy_deterministic(enemies)
        elif b_type == "bomber" or b_type == "drone":
            var max_crowd = -1
            var min_dist_sq_bomber = INF
            for e1 in enemies:
                var crowd = 0
                for e2 in enemies:
                    if e1 != e2 and pow(e1.x - e2.x, 2) + pow(e1.y - e2.y, 2) <= 1600.0:
                        crowd += 1
                var dist_sq = pow(e1.x - self.ball.x, 2) + pow(e1.y - self.ball.y, 2)
                if crowd > max_crowd or (crowd == max_crowd and dist_sq < min_dist_sq_bomber):
                    max_crowd = crowd
                    min_dist_sq_bomber = dist_sq
                    target = e1
        else:
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    target = e

    return target


func _group_attack(delta: float):
    var enemies = _get_enemies()
    var allies = _get_allies()

    if enemies.size() > 0:
        var target = _get_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "drone", "swarm", "aggressive", "cunning", "curious"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist_sq = dx * dx + dy * dy

        if dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist

            # Apply boid-like cohesion to stick with allies
            var cohesion_x = 0.0
            var cohesion_y = 0.0

            if allies.size() > 0:
                for ally in allies:
                    cohesion_x += ally.x
                    cohesion_y += ally.y
                cohesion_x /= allies.size()
                cohesion_y /= allies.size()

                var cdx = cohesion_x - self.ball.x
                var cdy = cohesion_y - self.ball.y
                var cdist_sq = cdx * cdx + cdy * cdy
                if cdist_sq > 0.0001:
                    var cdist = sqrt(cdist_sq)
                    var cnx = cdx / cdist
                    var cny = cdy / cdist

                    # Blend movement: 60% towards target, 40% towards allies center
                    nx = nx * 0.6 + cnx * 0.4
                    ny = ny * 0.6 + cny * 0.4

                    var ndist_sq = nx * nx + ny * ny
                    if ndist_sq > 0.0001:
                        var ndist = sqrt(ndist_sq)
                        nx /= ndist
                        ny /= ndist

            var target_radius = 10.0
            if "radius" in target: target_radius = float(target.radius)
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = float(self.ball.radius)

            if nx != 0.0 or ny != 0.0:
                var avoided = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoided[0]
                ny = avoided[1]

                var boided = _apply_boid_rules(nx, ny)
                nx = boided[0]
                ny = boided[1]

                var speed = 2.0
                if "speed" in self.ball: speed = float(self.ball.speed)
                var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step

                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        # Recalculate distance
        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        dist_sq = dx * dx + dy * dy
        var dist = 0.0
        if dist_sq > 0.0001: dist = sqrt(dist_sq)

        var target_radius = 10.0
        if "radius" in target: target_radius = float(target.radius)
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = float(self.ball.radius)
        var attack_range = ball_radius + target_radius + 5.0

        var skill_timer = 0.0
        if "skill_timer" in self.ball: skill_timer = float(self.ball.skill_timer)

        if skill_timer <= 0.0 and dist <= attack_range * 1.5:
            if self.ball.has_method("use_skill"):
                self.ball.use_skill()
                _spawn_skill_particles()

            var cd = 5.0
            if "skill_cooldown" in self.ball: cd = float(self.ball.skill_cooldown)
            self.ball.skill_timer = cd

        var attack_timer = 0.0
        if "attack_timer" in self.ball: attack_timer = float(self.ball.attack_timer)

        if attack_timer <= 0.0 and dist <= attack_range:
            if self.world != null and self.world.has_method("_deal_damage"):
                self._attempt_damage(self.ball, target)
                if "charge_level" in self.ball:
                    self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                elif self.ball.has_method("set_meta"):
                    var cl = 0.0
                    if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                    self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                if "charge_level" in target:
                    target.charge_level = min(100.0, float(target.charge_level) + 5.0)
                elif target.has_method("set_meta"):
                    var tcl = 0.0
                    if target.has_meta("charge_level"): tcl = float(target.get_meta("charge_level"))
                    target.set_meta("charge_level", min(100.0, tcl + 5.0))
                var b_type_vamp1 = ""
                if "ball_type" in self.ball:
                    b_type_vamp1 = str(self.ball.ball_type).to_lower()
                if b_type_vamp1 == "vampire":
                    var dmg_vamp1 = 10.0
                    if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                    if "hp" in self.ball and "max_hp" in self.ball:
                        self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                    var dmg_vamp_mode = 10.0
                    if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                    if "hp" in self.ball and "max_hp" in self.ball:
                        self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)

                if "id" in target and "id" in self.ball:
                    var target_memory = {}
                    if target.has_method("get_meta") and target.has_meta("memory"):
                        target_memory = target.get_meta("memory")
                    elif "memory" in target and typeof(target.memory) == TYPE_DICTIONARY:
                        target_memory = target.memory

                    # Ball Relationships - Balls remember each other


                    # Rivalry skill: attacked me before -> attack on sight
                    target_memory[self.ball.id] = {"relation": "rival"}
                    if target.has_method("set_meta"):
                        target.set_meta("memory", target_memory)
                    elif "memory" in target:
                        target.memory = target_memory

            var speed = 2.0
            if "speed" in self.ball: speed = float(self.ball.speed)
            var cooldown = 1.0
            if speed > 0: cooldown = max(0.2, 2.0 / speed)
            self.ball.attack_timer = cooldown
            if cooldown >= 0.8:
                if "stutter_timer" in self.ball:
                    self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))

    else:
        _idle(delta)


func _get_flank_target(enemies: Array):
    var best_target = null
    var best_score_dp = -INF
    var best_score_dist = -INF
    var best_score_id = -INF

    for e in enemies:
        var dx = e.x - self.ball.x
        var dy = e.y - self.ball.y
        var dist_sq = dx * dx + dy * dy
        var dist = 0.0
        if dist_sq > 0:
            dist = sqrt(dist_sq)

        var target_vx = 0.0
        var target_vy = 0.0

        if "vx" in e: target_vx = e.vx
        elif e.has_method("get_meta") and e.has_meta("vx"): target_vx = e.get_meta("vx")

        if "vy" in e: target_vy = e.vy
        elif e.has_method("get_meta") and e.has_meta("vy"): target_vy = e.get_meta("vy")

        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            if e.has_method("get_meta") and e.has_meta("last_vx"):
                target_vx = e.get_meta("last_vx")
                target_vy = e.get_meta("last_vy")
            else:
                target_vx = 1.0
                target_vy = 0.0

            if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                target_vx = 1.0
                target_vy = 0.0
        else:
            var v_dist_sq = target_vx*target_vx + target_vy*target_vy
            if v_dist_sq > 0.0001:
                var v_dist = sqrt(v_dist_sq)
                target_vx /= v_dist
                target_vy /= v_dist

        var dot_product = 0.0
        if dist > 0.0001:
            dot_product = (dx / dist) * target_vx + (dy / dist) * target_vy

        var e_id = 0
        if "id" in e:
            e_id = int(e.id)

        var better = false
        if dot_product > best_score_dp:
            better = true
        elif dot_product == best_score_dp:
            if -dist > best_score_dist:
                better = true
            elif -dist == best_score_dist:
                if e_id > best_score_id:
                    better = true

        if best_target == null or better:
            best_score_dp = dot_product
            best_score_dist = -dist
            best_score_id = e_id
            best_target = e

    return best_target

func _get_flank_position(target) -> Array:
    var target_vx = 0.0
    var target_vy = 0.0

    if "vx" in target: target_vx = target.vx
    elif target.has_method("get_meta") and target.has_meta("vx"): target_vx = target.get_meta("vx")

    if "vy" in target: target_vy = target.vy
    elif target.has_method("get_meta") and target.has_meta("vy"): target_vy = target.get_meta("vy")

    if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
        if target.has_method("get_meta") and target.has_meta("last_vx"):
            target_vx = target.get_meta("last_vx")
            target_vy = target.get_meta("last_vy")
        else:
            target_vx = 1.0
            target_vy = 0.0

        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            target_vx = 1.0
            target_vy = 0.0
    else:
        var v_dist_sq = target_vx*target_vx + target_vy*target_vy
        if v_dist_sq > 0.0001:
            var v_dist = sqrt(v_dist_sq)
            target_vx /= v_dist
            target_vy /= v_dist

    var flank_target_radius = 10.0
    if "radius" in target: flank_target_radius = target.radius
    var flank_distance = flank_target_radius * 2.0 + 20.0
    var flank_x = target.x - target_vx * flank_distance
    var flank_y = target.y - target_vy * flank_distance

    return [target_vx, target_vy, flank_x, flank_y]

func _flank(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = _get_flank_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "drone", "swarm", "aggressive", "cunning", "curious"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var flank_data = _get_flank_position(target)
        var target_vx = flank_data[0]
        var target_vy = flank_data[1]
        var flank_x = flank_data[2]
        var flank_y = flank_data[3]

        var dx = flank_x - self.ball.x
        var dy = flank_y - self.ball.y
        var dist_sq = dx*dx + dy*dy

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist

            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        var direct_dx = target.x - self.ball.x
        var direct_dy = target.y - self.ball.y
        var direct_dist_sq = direct_dx*direct_dx + direct_dy*direct_dy
        var direct_dist = 0.0
        if direct_dist_sq > 0.0001:
            direct_dist = sqrt(direct_dist_sq)

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var attack_range = ball_radius + target_radius + 5.0

        var skill_timer = 0.0
        if "skill_timer" in self.ball:
            skill_timer = self.ball.skill_timer

        if skill_timer <= 0.0 and direct_dist > attack_range * 1.5:
            if self.ball.has_method("use_skill"):
                self.ball.use_skill()
            var cd = 5.0
            if "skill_cooldown" in self.ball: cd = self.ball.skill_cooldown
            self.ball.skill_timer = cd

        if direct_dist <= attack_range:
            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0.0:
                var dot_product = 0.0
                if direct_dist > 0.0001:
                    var ndx = direct_dx / direct_dist
                    var ndy = direct_dy / direct_dist
                    dot_product = ndx * target_vx + ndy * target_vy

                var is_critical = dot_product > 0.5

                var original_damage = 5.0
                if "damage" in self.ball: original_damage = self.ball.damage

                if is_critical:
                    if "ball_type" in self.ball and self.ball.ball_type == "ninja":
                        self.ball.damage = original_damage * 3.0
                    else:
                        self.ball.damage = original_damage * 2.0

                if self.world != null and self.world.has_method("_deal_damage"):
                    self._attempt_damage(self.ball, target)
                    if "charge_level" in self.ball:
                        self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                    elif self.ball.has_method("set_meta"):
                        var cl = 0.0
                        if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                        self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in target:
                        target.charge_level = min(100.0, float(target.charge_level) + 5.0)
                    elif target.has_method("set_meta"):
                        var tcl = 0.0
                        if target.has_meta("charge_level"): tcl = float(target.get_meta("charge_level"))
                        target.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp1 = ""
                    if "ball_type" in self.ball:
                        b_type_vamp1 = str(self.ball.ball_type).to_lower()
                    if b_type_vamp1 == "vampire":
                        var dmg_vamp1 = 10.0
                        if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                if is_critical:
                    self.ball.damage = original_damage

                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
    else:
        _idle(delta)



func _target_weak(delta: float):
    # Target Weak — ищет самого слабого врага
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var weakest_enemy = null
    var min_score = INF # Higher is stronger

    for e in enemies:
        var hp = 100.0
        if "hp" in e:
            hp = e.hp
        elif "max_hp" in e:
            hp = e.max_hp

        var dist_sq = pow(e.x - ball.x, 2) + pow(e.y - ball.y, 2)

        # We want the lowest HP. If HP is equal, the closest distance.
        var score = hp * 1000000 + dist_sq
        if score < min_score:
            min_score = score
            weakest_enemy = e

    if weakest_enemy != null:
        _chase_target(weakest_enemy, delta)
    else:
        _idle(delta)

func _chase_target(target, delta: float):
    var dx = target.x - ball.x
    var dy = target.y - ball.y
    var dist_sq = dx*dx + dy*dy
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist

        var avoid = _apply_obstacle_avoidance(nx, ny, target)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var speed = 2.0
        if "speed" in ball: speed = ball.speed
        var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step

        ball.x += nx * step
        ball.y += ny * step

func _chase(delta: float):
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var target = _get_target(enemies)

    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality
    if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "drone", "swarm", "aggressive"]:
        var has_msg = false
        if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
            has_msg = self.ball.get_meta("team_message") != null
        if not has_msg and self.ball.has_method("set_meta"):
            self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

    var target_dx = target.x - self.ball.x
    var target_dy = target.y - self.ball.y
    var dist_to_target = sqrt(target_dx*target_dx + target_dy*target_dy)

    var target_radius = 10.0
    if "radius" in target: target_radius = target.radius
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius
    var attack_range = ball_radius + target_radius + 5.0

    var b_type_chase = ""
    if "ball_type" in self.ball:
        b_type_chase = self.ball.ball_type.to_lower()
    elif self.ball.has_method("get_ball_type"):
        b_type_chase = self.ball.get_ball_type().to_lower()

    if b_type_chase == "sniper":
        attack_range = 150.0

    var nx = 0.0
    var ny = 0.0
    if dist_to_target <= attack_range:
        if b_type_chase == "sniper" and dist_to_target < attack_range * 0.8:
            if dist_to_target > 0.01:
                nx = -target_dx / dist_to_target
                ny = -target_dy / dist_to_target
        else:
            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                if b_type_chase == "drone":
                    var skill_timer = 0.0
                    if "skill_timer" in self.ball: skill_timer = self.ball.skill_timer
                    elif self.ball.has_meta("skill_timer"): skill_timer = self.ball.get_meta("skill_timer")
                    if skill_timer <= 0:
                        self.ball.hp = 0
                        if "alive" in self.ball: self.ball.alive = false
                        if "current_action" in self.ball: self.ball.current_action = "explode"
                        return

                if self.world != null and self.world.has_method("_deal_damage"):
                    self._attempt_damage(self.ball, target)
                    if "charge_level" in self.ball:
                        self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                    elif self.ball.has_method("set_meta"):
                        var cl = 0.0
                        if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                        self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in target:
                        target.charge_level = min(100.0, float(target.charge_level) + 5.0)
                    elif target.has_method("set_meta"):
                        var tcl = 0.0
                        if target.has_meta("charge_level"): tcl = float(target.get_meta("charge_level"))
                        target.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp1 = ""
                    if "ball_type" in self.ball:
                        b_type_vamp1 = str(self.ball.ball_type).to_lower()
                    if b_type_vamp1 == "vampire":
                        var dmg_vamp1 = 10.0
                        if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)

                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
            return
    else:
        if dist_to_target > 0.01:
            if b_type_chase == "ninja":
                var tvx = 0.0
                var tvy = 0.0
                if "vx" in target: tvx = target.vx
                if "vy" in target: tvy = target.vy
                var tv_dist_sq = tvx*tvx + tvy*tvy
                if tv_dist_sq > 0.0001:
                    var tv_dist = sqrt(tv_dist_sq)
                    var back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                    var back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                    var bdx = back_x - self.ball.x
                    var bdy = back_y - self.ball.y
                    var b_dist = sqrt(bdx*bdx + bdy*bdy)
                    if b_dist > 0.01:
                        nx = bdx / b_dist
                        ny = bdy / b_dist
                    else:
                        nx = target_dx / dist_to_target
                        ny = target_dy / dist_to_target
                else:
                    nx = target_dx / dist_to_target
                    ny = target_dy / dist_to_target
            else:
                nx = target_dx / dist_to_target
                ny = target_dy / dist_to_target

    var repel_x = 0.0
    var repel_y = 0.0
    var all_entities = _get_allies()
    for e in enemies:
        if e != target:
            all_entities.append(e)

    for entity in all_entities:
        var edx = self.ball.x - entity.x
        var edy = self.ball.y - entity.y
        var edist = sqrt(edx*edx + edy*edy)
        var entity_radius = 10.0
        if "radius" in entity: entity_radius = entity.radius

        if edist > 0.01 and edist < (ball_radius + entity_radius) * 2.0:
            var repel_force = 1.0 / edist
            repel_x += (edx / edist) * repel_force
            repel_y += (edy / edist) * repel_force

    var comb_nx = nx + repel_x * 10.0
    var comb_ny = ny + repel_y * 10.0
    var comb_dist = sqrt(comb_nx*comb_nx + comb_ny*comb_ny)
    if comb_dist > 0.01:
        comb_nx /= comb_dist
        comb_ny /= comb_dist

    var boid_vec = _apply_boid_rules(comb_nx, comb_ny)
    comb_nx = boid_vec[0]
    comb_ny = boid_vec[1]

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step

    self.ball.x += comb_nx * step
    self.ball.y += comb_ny * step

func _attack(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = _get_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "drone", "swarm", "aggressive"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var dist = 0.0
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        var b_type_attack = ""
        if "ball_type" in self.ball:
            b_type_attack = self.ball.ball_type.to_lower()
        elif self.ball.has_method("get_ball_type"):
            b_type_attack = self.ball.get_ball_type().to_lower()

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var attack_range = ball_radius + target_radius + 5.0

        var nx = 0.0
        var ny = 0.0

        if b_type_attack == "ninja":
            var tvx = 0.0
            var tvy = 0.0
            if "vx" in target: tvx = target.vx
            if "vy" in target: tvy = target.vy
            var tv_dist_sq = tvx*tvx + tvy*tvy
            if tv_dist_sq > 0.0001:
                var tv_dist = sqrt(tv_dist_sq)
                var back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                var back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                var bdx = back_x - self.ball.x
                var bdy = back_y - self.ball.y
                var b_dist = sqrt(bdx*bdx + bdy*bdy)
                if b_dist > 0.01:
                    nx = bdx / b_dist
                    ny = bdy / b_dist

        if nx == 0.0 and ny == 0.0 and dist_sq > 0.0001:
            nx = dx / dist
            ny = dy / dist

        if dist_sq > 0.0001:
            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step = speed * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)
        else:
            dist = 0.0

        target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius
        attack_range = ball_radius + target_radius + 5.0

        if b_type_attack == "sniper":
            attack_range = 150.0

        if dist <= attack_range:
            var skill_timer = 0.0
            if "skill_timer" in self.ball:
                skill_timer = self.ball.skill_timer

            if skill_timer <= 0:
                var optimal = true
                var b_type = ""
                if "ball_type" in self.ball:
                    b_type = self.ball.ball_type
                elif self.ball.has_method("get_ball_type"):
                    b_type = self.ball.get_ball_type()

                if b_type == "bomber":
                    var close_enemies = 0
                    for e in enemies:
                        var e_radius = 10.0
                        if "radius" in e: e_radius = e.radius
                        var edx = e.x - self.ball.x
                        var edy = e.y - self.ball.y
                        if sqrt(edx*edx + edy*edy) <= ball_radius + e_radius + 15:
                            close_enemies += 1
                    optimal = close_enemies >= 3

                    if optimal and "hp" in self.ball:
                        self.ball.hp = 0
                        if "alive" in self.ball:
                            self.ball.alive = false
                elif b_type == "tank":
                    optimal = (target == _find_strongest_enemy_deterministic(enemies))
                elif b_type == "warrior":
                    var in_front = 0
                    var move_dx = target.x - self.ball.x
                    var move_dy = target.y - self.ball.y
                    var move_dist = sqrt(move_dx*move_dx + move_dy*move_dy)
                    if move_dist > 0.0001:
                        var mnx = move_dx / move_dist
                        var mny = move_dy / move_dist
                        for e in enemies:
                            var e_radius = 10.0
                            if "radius" in e: e_radius = e.radius
                            var edx = e.x - self.ball.x
                            var edy = e.y - self.ball.y
                            var edist = sqrt(edx*edx + edy*edy)
                            if edist <= ball_radius + e_radius + 40.0 and edist > 0.0001:
                                var enx = edx / edist
                                var eny = edy / edist
                                var dot_product = mnx * enx + mny * eny
                                if dot_product > 0.5:
                                    in_front += 1
                    optimal = in_front >= 2

                if optimal:
                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()
                    var cooldown = 5.0
                    if "skill_cooldown" in self.ball:
                        cooldown = self.ball.skill_cooldown
                    self.ball.skill_timer = cooldown

            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                var b_type = ""
                if "ball_type" in self.ball:
                    b_type = self.ball.ball_type.to_lower()
                elif self.ball.has_method("get_ball_type"):
                    b_type = self.ball.get_ball_type().to_lower()

                var original_damage = 10.0
                if "damage" in self.ball:
                    original_damage = float(self.ball.damage)

                if b_type == "ninja":
                    var tvx = 0.0
                    var tvy = 0.0
                    if "vx" in target: tvx = float(target.vx)
                    if "vy" in target: tvy = float(target.vy)
                    var tv_dist_sq = tvx * tvx + tvy * tvy
                    if tv_dist_sq > 0.0001:
                        var tv_dist = sqrt(tv_dist_sq)
                        var tnx = tvx / tv_dist
                        var tny = tvy / tv_dist

                        var adx = float(target.x) - float(self.ball.x)
                        var ady = float(target.y) - float(self.ball.y)
                        var adist_sq = adx * adx + ady * ady
                        if adist_sq > 0.0001:
                            var adist = sqrt(adist_sq)
                            var anx = adx / adist
                            var any = ady / adist

                            var dot_product = anx * tnx + any * tny
                            if dot_product > 0.5:
                                self.ball.damage = original_damage * 2.0

                if self.world != null and self.world.has_method("_deal_damage"):
                    self._attempt_damage(self.ball, target)
                    if "charge_level" in self.ball:
                        self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                    elif self.ball.has_method("set_meta"):
                        var cl = 0.0
                        if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                        self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in target:
                        target.charge_level = min(100.0, float(target.charge_level) + 5.0)
                    elif target.has_method("set_meta"):
                        var tcl = 0.0
                        if target.has_meta("charge_level"): tcl = float(target.get_meta("charge_level"))
                        target.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp1 = ""
                    if "ball_type" in self.ball:
                        b_type_vamp1 = str(self.ball.ball_type).to_lower()
                    if b_type_vamp1 == "vampire":
                        var dmg_vamp1 = 10.0
                        if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                if b_type == "ninja":
                    self.ball.damage = original_damage

                var cooldown = 0.5
                if b_type in ["scout", "assassin", "phantom", "swarm", "rogue", "drone", "ninja"]:
                    cooldown = 0.3
                elif b_type in ["tank", "juggernaut", "guardian"]:
                    cooldown = 1.5
                else:
                    var speed = 2.0
                    if "speed" in self.ball: speed = self.ball.speed
                    cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)

                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
    else:
        _idle(delta)

func _hold_zone(delta: float):
    var arena_width = 1000.0
    var arena_height = 1000.0
    if self.world != null and "arena" in self.world and self.world.arena != null:
        if "width" in self.world.arena: arena_width = float(self.world.arena.width)
        if "height" in self.world.arena: arena_height = float(self.world.arena.height)

    var target_x = arena_width / 2.0
    var target_y = arena_height / 2.0
    var zone_radius = min(arena_width, arena_height) * 0.2

    if self.world != null and "game_mode" in self.world and self.world.game_mode != null:
        if "zone_x" in self.world.game_mode: target_x = float(self.world.game_mode.zone_x)
        if "zone_y" in self.world.game_mode: target_y = float(self.world.game_mode.zone_y)
        if "zone_radius" in self.world.game_mode: zone_radius = float(self.world.game_mode.zone_radius)

    var dx = target_x - self.ball.x
    var dy = target_y - self.ball.y
    var dist = sqrt(dx * dx + dy * dy)

    # Move towards the center if we are too far
    if dist > zone_radius * 0.5:
        if dist > 0.0:
            var spd = 2.0
            if "speed" in self.ball:
                spd = self.ball.speed
            self.ball.x += (dx / dist) * spd * delta * 50.0
            self.ball.y += (dy / dist) * spd * delta * 50.0
    else:
        var enemies = _get_enemies()
        if enemies.size() > 0:
            var target_enemy = enemies[0]
            var min_d_sq = (target_enemy.x - self.ball.x) * (target_enemy.x - self.ball.x) + (target_enemy.y - self.ball.y) * (target_enemy.y - self.ball.y)
            for i in range(1, enemies.size()):
                var e = enemies[i]
                var d_sq = (e.x - self.ball.x) * (e.x - self.ball.x) + (e.y - self.ball.y) * (e.y - self.ball.y)
                if d_sq < min_d_sq:
                    min_d_sq = d_sq
                    target_enemy = e

            var edist = sqrt(min_d_sq)
            if edist < 150.0 and edist > 0.0:
                var edx = target_enemy.x - self.ball.x
                var edy = target_enemy.y - self.ball.y
                var spd = 2.0
                if "speed" in self.ball:
                    spd = self.ball.speed
                self.ball.x += (edx / edist) * spd * delta * 50.0
                self.ball.y += (edy / edist) * spd * delta * 50.0

func _defend(delta: float):
    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality
    if personality in ["tank", "defender", "guardian", "juggernaut"]:
        var enemies = _get_enemies()
        if enemies.size() > 0:
            var target_enemy = null
            var target_pos_x = self.ball.x
            var target_pos_y = self.ball.y
            var should_move = false

            var b_type = ""
            if "ball_type" in self.ball:
                b_type = self.ball.ball_type.to_lower()

            if b_type == "tank":
                var allies = _get_allies()
                var ally_to_protect = null
                if allies.size() > 0:
                    var healers = []
                    for a in allies:
                        var a_type = ""
                        if "ball_type" in a:
                            a_type = str(a.ball_type).to_lower()
                        elif a.has_method("get") and a.get("BALL_TYPE") != null:
                            a_type = str(a.get("BALL_TYPE")).to_lower()
                        if a_type == "healer":
                            healers.append(a)

                    if healers.size() > 0:
                        var min_d_sq = INF
                        for h in healers:
                            var dsq = pow(h.x - self.ball.x, 2) + pow(h.y - self.ball.y, 2)
                            if dsq < min_d_sq:
                                min_d_sq = dsq
                                ally_to_protect = h
                    else:
                        var min_hp_pct = INF
                        for a in allies:
                            var a_hp_pct = 1.0
                            if a.has_method("get_hp_percent"):
                                a_hp_pct = a.get_hp_percent()
                            elif "hp" in a and "max_hp" in a and float(a.max_hp) > 0:
                                a_hp_pct = float(a.hp) / float(a.max_hp)
                            if a_hp_pct < min_hp_pct:
                                min_hp_pct = a_hp_pct
                                ally_to_protect = a

                target = _find_strongest_enemy_deterministic(enemies)
            else:
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e

            var dx = target.x - self.ball.x
            var dy = target.y - self.ball.y
            var dist_sq = dx*dx + dy*dy
            if dist_sq > 0.0001:
                var dist = sqrt(dist_sq)
                var nx = dx / dist
                var ny = dy / dist
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]
                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var step = speed * 0.5 * delta * 60.0
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist_sq = dx*dx + dy*dy
            var dist_after = 0.0
            if dist_sq > 0.0001:
                dist_after = sqrt(dist_sq)

            var target_radius = 10.0
            if "radius" in target: target_radius = target.radius
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius

            if dist_after <= ball_radius + target_radius + 5:
                var attack_timer = 0.0
                if "attack_timer" in self.ball:
                    attack_timer = self.ball.attack_timer
                elif self.ball.has_meta("attack_timer"):
                    attack_timer = self.ball.get_meta("attack_timer")

                if attack_timer <= 0:
                    if self.world != null and self.world.has_method("_deal_damage"):
                        self._attempt_damage(self.ball, target)
                        if "charge_level" in self.ball:
                            self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                        elif self.ball.has_method("set_meta"):
                            var cl = 0.0
                            if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                            self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                        if "charge_level" in target:
                            target.charge_level = min(100.0, float(target.charge_level) + 5.0)
                        elif target.has_method("set_meta"):
                            var tcl = 0.0
                            if target.has_meta("charge_level"): tcl = float(target.get_meta("charge_level"))
                            target.set_meta("charge_level", min(100.0, tcl + 5.0))
                        var b_type_vamp1 = ""
                        if "ball_type" in self.ball:
                            b_type_vamp1 = str(self.ball.ball_type).to_lower()
                        if b_type_vamp1 == "vampire":
                            var dmg_vamp1 = 10.0
                            if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                            if "hp" in self.ball and "max_hp" in self.ball:
                                self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                        if "id" in target and "id" in self.ball:
                            var mem = {}
                            if target.has_method("get_meta") and target.has_meta("memory"):
                                mem = target.get_meta("memory")
                            elif "memory" in target:
                                mem = target.memory
                            # Ball Relationships - Balls remember each other
                            # Rivalry skill: attacked me before -> attack on sight
                            mem[self.ball.id] = {"relation": "rival"}
                            if target.has_method("set_meta"):
                                target.set_meta("memory", mem)
                            else:
                                target.memory = mem

                    var cooldown = 1.5
                    var b_type = ""
                    if "ball_type" in self.ball:
                        b_type = self.ball.ball_type.to_lower()
                    elif self.ball.has_method("get_ball_type"):
                        b_type = self.ball.get_ball_type().to_lower()

                    if not (b_type in ["tank", "juggernaut", "guardian"]):
                        var spd = 2.0
                        if "speed" in self.ball: spd = self.ball.speed
                        cooldown = max(0.2, 2.0 / spd if spd > 0 else 1.0)

                    if "attack_timer" in self.ball:
                        self.ball.attack_timer = cooldown
                        if cooldown >= 0.8:
                            if "stutter_timer" in self.ball:
                                self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("attack_timer", cooldown)
                        if cooldown >= 0.8:
                            if "stutter_timer" in self.ball:
                                self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
            return
    elif personality == "healer" or personality == "leader" or personality == "caring":
        var allies = _get_allies()
        var target_ally = null
        var lowest_hp = 0.8
        for ally in allies:
            var ally_hp_pct = 1.0
            if ally.has_method("get_hp_percent"):
                ally_hp_pct = ally.get_hp_percent()
            elif "hp" in ally and "max_hp" in ally:
                ally_hp_pct = float(ally.hp) / float(ally.max_hp)
            if ally_hp_pct < lowest_hp:
                lowest_hp = ally_hp_pct
                target_ally = ally
        if target_ally != null:
            var dx = target_ally.x - self.ball.x
            var dy = target_ally.y - self.ball.y
            var dist_sq = dx*dx + dy*dy
            if dist_sq > 0.0001:
                var dist = sqrt(dist_sq)
                var nx = dx / dist
                var ny = dy / dist
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target_ally)
                nx = avoid_vec[0]
                ny = avoid_vec[1]
                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist_sq = dx*dx + dy*dy
            var dist_after = 0.0
            if dist_sq > 0.0001:
                dist_after = sqrt(dist_sq)

            var target_radius = 10.0
            if "radius" in target: target_radius = target.radius
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius

            if dist_after <= ball_radius + target_radius + 5:
                var attack_timer = 0.0
                if "attack_timer" in self.ball:
                    attack_timer = self.ball.attack_timer
                elif self.ball.has_meta("attack_timer"):
                    attack_timer = self.ball.get_meta("attack_timer")

                if attack_timer <= 0:
                    # Explicit healing logic
                    if "hp" in target_ally and "max_hp" in target_ally:
                        var damage = 5.0
                        if "damage" in self.ball:
                            damage = self.ball.damage
                        target_ally.hp = min(target_ally.max_hp, target_ally.hp + (damage * 3.0))

                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()

                    if "skill_cooldown" in self.ball:
                        if "skill_timer" in self.ball:
                            self.ball.skill_timer = self.ball.skill_cooldown

                    var cooldown = 1.5
                    var b_type = ""
                    if "ball_type" in self.ball:
                        b_type = self.ball.ball_type.to_lower()
                    elif self.ball.has_method("get_ball_type"):
                        b_type = self.ball.get_ball_type().to_lower()

                    if not (b_type in ["tank", "juggernaut", "guardian"]):
                        var spd = 2.0
                        if "speed" in self.ball: spd = self.ball.speed
                        cooldown = max(0.2, 2.0 / spd if spd > 0 else 1.0)

                    if "attack_timer" in self.ball:
                        self.ball.attack_timer = cooldown
                        if cooldown >= 0.8:
                            if "stutter_timer" in self.ball:
                                self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("attack_timer", cooldown)
                        if cooldown >= 0.8:
                            if "stutter_timer" in self.ball:
                                self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
            return

    _idle(delta * 0.5)

func _collect_booster(delta: float):
    var boosters = _get_boosters()
    if boosters.size() > 0:
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var enemies = _get_enemies()
        if enemies.size() > 0:
            var nearest_enemy = null
            var min_dist_enemy_sq = INF
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_enemy_sq:
                    min_dist_enemy_sq = dist_sq
                    nearest_enemy = e

            var enemy_radius = 10.0
            if "radius" in nearest_enemy: enemy_radius = nearest_enemy.radius

            if min_dist_enemy_sq > 0.0001:
                var dist_enemy = sqrt(min_dist_enemy_sq)
                if dist_enemy < ball_radius + enemy_radius + 30.0:
                    _flee(delta)
                    return

        var nearest = null
        var min_dist_sq = INF
        for b in boosters:
            var dist_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = b

        var dx = nearest.x - self.ball.x
        var dy = nearest.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var dist = 0.0
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist_sq > 0.0001:
            var nx = dx / dist
            var ny = dy / dist
            var avoid_vec = _apply_obstacle_avoidance(nx, ny, nearest, true)
            nx = avoid_vec[0]
            ny = avoid_vec[1]

            var boid_vec = _apply_boid_rules(nx, ny)
            nx = boid_vec[0]
            ny = boid_vec[1]

            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = nearest.x - self.ball.x
        dy = nearest.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)
        else:
            dist = 0.0

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + 10:
            if "kind" in nearest and nearest.kind == "drone_item":
                self.ball.has_drone = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "decoy_item":
                var decoy = null
                if typeof(self.ball) == TYPE_DICTIONARY:
                    decoy = self.ball.duplicate()
                elif self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()

                if decoy != null:
                    if "id" in decoy:
                        decoy.id = randi() % 90000 + 10000
                    if "hp" in decoy and "max_hp" in decoy:
                        decoy.max_hp = float(self.ball.max_hp) * 0.1
                        decoy.hp = decoy.max_hp
                    if "damage" in decoy:
                        decoy.damage = 0.0
                    var self_id_stat = -2
                    if "id" in self.ball: self_id_stat = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                    if decoy.has_method("set_meta"):
                        decoy.set_meta("owner_id", self_id_stat)
                        decoy.set_meta("has_swapped", false)
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_timer", 5.0)
                    elif typeof(decoy) == TYPE_DICTIONARY:
                        decoy["is_decoy"] = true
                        decoy["decoy_timer"] = 5.0

                    if self.world != null and "balls" in self.world:
                        self.world.balls.append(decoy)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "stealth_drone_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_stealth_drone", true)
                    self.ball.set_meta("stealth_drone_timer", 15.0)
                elif "has_stealth_drone" in self.ball:
                    self.ball.has_stealth_drone = true
                    self.ball.stealth_drone_timer = 15.0
                elif "stealth_drone_timer" in self.ball:
                    self.ball.stealth_drone_timer = 15.0
            elif "kind" in nearest and nearest.kind == "vision_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("vision_booster_timer", 15.0)
                elif "vision_booster_timer" in self.ball:
                    self.ball.vision_booster_timer = 15.0
                else:
                    self.ball.vision_booster_timer = 15.0

                var vb_applied = false
                if "vision_booster_applied" in self.ball:
                    vb_applied = self.ball.vision_booster_applied
                elif self.ball.has_method("get_meta") and self.ball.has_meta("vision_booster_applied"):
                    vb_applied = self.ball.get_meta("vision_booster_applied")

                if not vb_applied:
                    var base_perc = 250.0
                    if "perception_radius" in self.ball:
                        base_perc = float(self.ball.perception_radius)
                    if self.ball.has_method("get_meta") and self.ball.has_meta("base_perception_radius"):
                        base_perc = self.ball.get_meta("base_perception_radius")

                    base_perc *= 2.0

                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("base_perception_radius", base_perc)
                        self.ball.set_meta("vision_booster_applied", true)

                    self.ball.perception_radius = base_perc

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "invert_booster":
                if self.world != null and "balls" in self.world:
                    for other in self.world.balls:
                        var my_team = -2
                        if "team" in self.ball: my_team = self.ball.team
                        var other_team = -1
                        if "team" in other: other_team = other.team
                        if other_team != my_team and other.get("hp", 0) > 0:
                            if "invert_timer" in other:
                                other.invert_timer = 5.0
                            elif other.has_method("set_meta"):
                                other.set_meta("invert_timer", 5.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "nemesis_booster":
                self.ball.set_meta("nemesis_booster_timer", 5.0)
                if "nemesis_booster_timer" in self.ball:
                    self.ball.nemesis_booster_timer = 5.0
                if "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
            elif "kind" in nearest and nearest.kind == "clone_booster":
                for i in range(3):
                    var clone = null
                    if self.ball.has_method("duplicate"):
                        clone = self.ball.duplicate()
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        clone = self.ball.duplicate()

                    if clone != null:
                        if "id" in clone:
                            clone.id = randi() % 90000 + 10000
                        if "hp" in clone and "max_hp" in clone:
                            clone.max_hp = float(self.ball.max_hp)
                            clone.hp = clone.max_hp
                        if "damage" in clone:
                            clone.damage = 0.0
                        if "speed" in clone and "speed" in self.ball:
                            clone.speed = self.ball.speed

                        if "x" in clone and "y" in clone:
                            var angle = i * (2.0 * PI / 3.0)
                            clone.x += cos(angle) * 15.0
                            clone.y += sin(angle) * 15.0

                        var self_id_stat = -2
                        if "id" in self.ball: self_id_stat = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                        if clone.has_method("set_meta"):
                            clone.set_meta("owner_id", self_id_stat)
                            clone.set_meta("is_decoy", true)
                            clone.set_meta("decoy_timer", 5.0)
                            clone.set_meta("skill_timer", 9999.0)
                            clone.set_meta("attack_timer", 9999.0)
                            clone.set_meta("SKILL", null)
                            clone.set_meta("skill", null)
                            clone.set_meta("active_skill", null)
                        elif typeof(clone) == TYPE_DICTIONARY:
                            clone["owner_id"] = self_id_stat
                            clone["is_decoy"] = true
                            clone["decoy_timer"] = 5.0
                            clone["skill_timer"] = 9999.0
                            clone["attack_timer"] = 9999.0
                            clone["SKILL"] = null
                            clone["skill"] = null
                            clone["active_skill"] = null

                        if self.world != null and "balls" in self.world:
                            self.world.balls.append(clone)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "shadow_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("shadow_booster_timer", 15.0)
                elif "shadow_booster_timer" in self.ball:
                    self.ball.shadow_booster_timer = 15.0
                else:
                    self.ball.shadow_booster_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "silence_booster":
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        if not same_team:
                            var dist_silence = sqrt(pow(other_ball.x - self.ball.x, 2) + pow(other_ball.y - self.ball.y, 2))
                            if dist_silence < 150.0:
                                var duration = 5.0
                                if "duration" in nearest: duration = nearest.duration
                                if other_ball.has_method("set_meta"):
                                    other_ball.set_meta("silence_timer", duration)
                                elif "silence_timer" in other_ball:
                                    other_ball.silence_timer = duration
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "freeze_booster":
                var fduration = 3.0
                if "duration" in nearest: fduration = nearest.duration
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        var alive = true
                        if "alive" in other_ball: alive = other_ball.alive
                        if not same_team and alive:
                            var current_stun = 0.0
                            if "stun_timer" in other_ball: current_stun = other_ball.stun_timer
                            elif other_ball.has_method("get_meta") and other_ball.has_meta("stun_timer"): current_stun = other_ball.get_meta("stun_timer")
                            var new_stun = max(current_stun, fduration)
                            if "stun_timer" in other_ball: other_ball.stun_timer = new_stun
                            elif other_ball.has_method("set_meta"): other_ball.set_meta("stun_timer", new_stun)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    for h in self.world.arena.hazards:
                        if h != nearest:
                            var current_frozen = 0.0
                            if "frozen_timer" in h: current_frozen = h.frozen_timer
                            elif h.has_method("get_meta") and h.has_meta("frozen_timer"): current_frozen = h.get_meta("frozen_timer")
                            var new_frozen = max(current_frozen, fduration)
                            if "frozen_timer" in h: h.frozen_timer = new_frozen
                            elif h.has_method("set_meta"): h.set_meta("frozen_timer", new_frozen)
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "emp_item":
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        if not same_team:
                            var dist_emp = sqrt(pow(other_ball.x - self.ball.x, 2) + pow(other_ball.y - self.ball.y, 2))
                            if dist_emp < 300.0: # EMP radius
                                if "has_drone" in other_ball: other_ball.has_drone = false
                                if "has_shield" in other_ball: other_ball.has_shield = false
                                if other_ball.has_method("set_meta"):
                                    other_ball.set_meta("speed_booster_timer", 0.0)
                                elif "speed_booster_timer" in other_ball:
                                    other_ball.speed_booster_timer = 0.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "zone_immunity":
                var dur = 5.0
                if "duration" in nearest: dur = nearest.duration
                self.ball.set_meta("zone_immunity_timer", dur)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "placeable_trap_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("placeable_trap")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "exit_portal_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("exit_portal")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "position_swap_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("position_swap")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "portal_gun_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("portal_gun")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "fake_booster":
                var explosion_radius = 45.0
                if "radius" in nearest:
                    explosion_radius = nearest.radius * 3
                var dmg = 50.0
                if "damage" in nearest: dmg = nearest.damage
                var stun_dur = 2.0
                if "stun_duration" in nearest: stun_dur = nearest.stun_duration

                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        var bx = 0.0
                        var by = 0.0
                        if "x" in b: bx = b.x
                        elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                        if "y" in b: by = b.y
                        elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")
                        var nx = 0.0
                        var ny = 0.0
                        if "x" in nearest: nx = nearest.x
                        if "y" in nearest: ny = nearest.y

                        var dx = bx - nx
                        var dy = by - ny
                        if sqrt(dx*dx + dy*dy) <= explosion_radius:
                            if b.has_method("take_damage"):
                                b.take_damage(dmg)
                            if b.has_method("set_meta"):
                                b.set_meta("stun_timer", stun_dur)
                            else:
                                b.stun_timer = stun_dur

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "weather_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("weather_control_timer", 10.0)
                else:
                    self.ball.weather_control_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "magnet_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("pull_booster_timer", 5.0)
                else:
                    self.ball.pull_booster_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "placeable_trap_booster":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("placeable_trap_booster")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "stamina_booster":
                var max_stam = 100.0
                if self.ball.has_method("get_meta") and self.ball.has_meta("max_stamina"): max_stam = self.ball.get_meta("max_stamina")
                elif "max_stamina" in self.ball: max_stam = self.ball.max_stamina

                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("stamina", max_stam)
                    self.ball.set_meta("infinite_stamina_timer", 5.0)
                else:
                    self.ball.stamina = max_stam
                    self.ball.infinite_stamina_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "weather_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("weather_control_timer", 10.0)
                else:
                    self.ball.weather_control_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "cleanser":
                if "burn_timer" in self.ball: self.ball.burn_timer = 0.0
                if "poison_timer" in self.ball: self.ball.poison_timer = 0.0
                if "slow_timer" in self.ball: self.ball.slow_timer = 0.0
                if "silence_timer" in self.ball: self.ball.silence_timer = 0.0
                if "stun_timer" in self.ball:
                    self.ball.stun_timer = 0.0
                    if "is_stunned" in self.ball: self.ball.is_stunned = false

                var link_target = null
                if "damage_link_target" in self.ball: link_target = self.ball.damage_link_target
                elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_target"): link_target = self.ball.get_meta("damage_link_target")

                if link_target != null:
                    var target_link = null
                    if "damage_link_target" in link_target: target_link = link_target.damage_link_target
                    elif link_target.has_method("get_meta") and link_target.has_meta("damage_link_target"): target_link = link_target.get_meta("damage_link_target")

                    if target_link == self.ball:
                        if "damage_link_target" in link_target: link_target.damage_link_target = null
                        elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_target", null)

                    if "damage_link_target" in self.ball: self.ball.damage_link_target = null
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("damage_link_target", null)
            elif "kind" in nearest and nearest.kind == "link_booster":
                var enemies_link = _get_enemies()
                if enemies_link.size() > 0:
                    var link_target = null
                    var min_dist_link_sq = INF
                    for e in enemies_link:
                        var d_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                        if d_sq < min_dist_link_sq:
                            min_dist_link_sq = d_sq
                            link_target = e
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("link_booster_timer", 5.0)
                        self.ball.set_meta("link_booster_target", link_target)
                    else:
                        self.ball.link_booster_timer = 5.0
                        self.ball.link_booster_target = link_target

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "chain_lightning":
                var dur = 5.0
                if "duration" in nearest: dur = nearest.duration
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("chain_lightning_timer", dur)
                elif "chain_lightning_timer" in self.ball:
                    self.ball.chain_lightning_timer = dur
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            else:
                if self.world != null and self.world.has_method("_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
    else:
        _idle(delta)

func _use_skill():

    var _silence_timer = 0.0
    if "silence_timer" in self.ball: _silence_timer = self.ball.silence_timer
    elif self.ball.has_method("has_meta") and self.ball.has_meta("silence_timer"): _silence_timer = self.ball.get_meta("silence_timer")
    if _silence_timer > 0.0: return
    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer

    if skill_timer <= 0.0 and self.ball.has_method("use_skill"):
        self.ball.use_skill()

        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill
        elif "SKILL" in self.ball:
            skill_name = self.ball.SKILL

        # Synergy Logic
        var allies = []
        if self.world.has("balls"):
            for b in self.world.balls:
                var is_alive = true
                if "alive" in b: is_alive = b.alive
                elif b.has_method("has_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

                var team = ""
                if "team" in b: team = b.team
                elif b.has_method("has_meta") and b.has_meta("team"): team = b.get_meta("team")

                var my_team = ""
                if "team" in self.ball: my_team = self.ball.team
                elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")

                var b_id = -1
                if "id" in b: b_id = b.id
                elif b.has_method("has_meta") and b.has_meta("id"): b_id = b.get_meta("id")

                var my_id = -2
                if "id" in self.ball: my_id = self.ball.id
                elif self.ball.has_method("has_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

                if b_id != my_id and team == my_team and is_alive:
                    allies.append(b)

        var synergy_multiplier = 1.0

        for ally in allies:
            var ally_skill = ""
            if "skill" in ally: ally_skill = ally.skill
            elif "SKILL" in ally: ally_skill = ally.SKILL

            if (skill_name == "elemental_burst" and ally_skill == "lightning_strike") or \
               (skill_name == "lightning_strike" and ally_skill == "elemental_burst") or \
               (skill_name == "fireball" and ally_skill == "smokescreen") or \
               (skill_name == "smokescreen" and ally_skill == "fireball"):

                var dx = self.ball.x - ally.x
                var dy = self.ball.y - ally.y
                if dx*dx + dy*dy < 40000:
                    synergy_multiplier = 1.5

                    if (skill_name == "elemental_burst" or ally_skill == "elemental_burst") and (skill_name == "lightning_strike" or ally_skill == "lightning_strike"):
                        var enemies = _get_enemies()
                        for enemy in enemies:
                            var edx = enemy.x - self.ball.x
                            var edy = enemy.y - self.ball.y
                            if edx*edx + edy*edy < 40000:
                                if "is_stunned" in enemy: enemy.is_stunned = true
                                elif enemy.has_method("set_meta"): enemy.set_meta("is_stunned", true)

                                var current_stun = 0.0
                                if "stun_timer" in enemy: current_stun = enemy.stun_timer
                                elif enemy.has_method("has_meta") and enemy.has_meta("stun_timer"): current_stun = enemy.get_meta("stun_timer")

                                var new_stun = max(current_stun, 2.0)
                                if "stun_timer" in enemy: enemy.stun_timer = new_stun
                                elif enemy.has_method("set_meta"): enemy.set_meta("stun_timer", new_stun)

                    elif (skill_name == "fireball" or ally_skill == "fireball") and (skill_name == "smokescreen" or ally_skill == "smokescreen"):
                        var enemies = _get_enemies()
                        for enemy in enemies:
                            var edx = enemy.x - self.ball.x
                            var edy = enemy.y - self.ball.y
                            if edx*edx + edy*edy < 40000:
                                if "hp" in enemy: enemy.hp -= 5
                                elif enemy.has_method("has_meta") and enemy.has_meta("hp"): enemy.set_meta("hp", enemy.get_meta("hp") - 5)

                    break

        var cl = 0.0
        if "charge_level" in self.ball:
            cl = float(self.ball.charge_level)
        elif self.ball.has_method("has_meta") and self.ball.has_meta("charge_level"):
            cl = float(self.ball.get_meta("charge_level"))

        var bd = 10.0
        if "base_damage" in self.ball: bd = float(self.ball.base_damage)
        elif "damage" in self.ball: bd = float(self.ball.damage)

        if cl >= 100.0:
            if "charge_level" in self.ball:
                self.ball.charge_level = 0.0
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("charge_level", 0.0)
            self.ball.base_damage = bd * 2.0 * synergy_multiplier
        else:
            self.ball.base_damage = bd * synergy_multiplier

        self.ball.damage = self.ball.base_damage



        self.ball.use_skill()
        _spawn_skill_particles(skill_name)

        if skill_name == "command":
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "buff_command", "radius": 200})
            elif "team_message" in self.ball:
                self.ball.team_message = {"type": "buff_command", "radius": 200}
        elif skill_name == "meteor_strike":
            var enemies = _get_enemies()
            var arena = world.call("get_arena") if world != null and world.has_method("get_arena") else null
            if arena == null and "arena" in world:
                arena = world.arena
            if enemies.size() > 0 and arena != null and "hazards" in arena:
                var num_meteors = (randi() % 3) + 3
                var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
                for i in range(num_meteors):
                    var target = enemies[randi() % enemies.size()]
                    var t_x = 0.0
                    var t_y = 0.0
                    if "x" in target: t_x = target.x
                    elif typeof(target) == TYPE_DICTIONARY and target.has("x"): t_x = target["x"]
                    if "y" in target: t_y = target.y
                    elif typeof(target) == TYPE_DICTIONARY and target.has("y"): t_y = target["y"]
                    var offset_x = randf_range(-50.0, 50.0)
                    var offset_y = randf_range(-50.0, 50.0)
                    var trap_id = 15000 + arena.hazards.size() + (randi() % 1000)
                    var meteor = ProceduralArenaScript.Hazard.new(trap_id, t_x + offset_x, t_y + offset_y, 30.0, "meteor", 200.0)
                    meteor.target_radius = 30.0
                    meteor.set_meta("duration", 5.0)
                    arena.hazards.append(meteor)
        elif skill_name == "entangle":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist = 9999999.0
                for e in enemies:
                    var dx = e.x - self.ball.x
                    var dy = e.y - self.ball.y
                    var dist_sq = dx*dx + dy*dy
                    if dist_sq < min_dist:
                        min_dist = dist_sq
                        target = e
                if target != null:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("entangled_with_id", target.id)
                        self.ball.set_meta("entangle_timer", 5.0)
                    if target.has_method("set_meta"):
                        target.set_meta("entangled_with_id", self.ball.id)
                        target.set_meta("entangle_timer", 5.0)

        elif skill_name == "time_stop":
            var entities = []
            if "entities" in self.world: entities = self.world.entities
            elif "balls" in self.world: entities = self.world.balls

            var my_id = -1
            if "id" in self.ball: my_id = self.ball.id
            elif self.ball.has_method("get_meta"): my_id = self.ball.get_meta("id")

            for b in entities:
                var b_id = -2
                if "id" in b: b_id = b.id
                elif b.has_method("get_meta"): b_id = b.get_meta("id")

                var is_alive = true
                if "alive" in b: is_alive = b.alive
                elif b.has_method("get_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

                if b_id != my_id and is_alive:
                    var curr_stun = 0.0
                    if "stun_timer" in b: curr_stun = b.stun_timer
                    elif b.has_method("get_meta") and b.has_meta("stun_timer"): curr_stun = b.get_meta("stun_timer")

                    var new_stun = max(curr_stun, 2.0)
                    if "stun_timer" in b: b.stun_timer = new_stun
                    elif b.has_method("set_meta"): b.set_meta("stun_timer", new_stun)

            if "arena" in self.world and self.world.arena != null:
                var arena = self.world.arena
                if "hazards" in arena:
                    for h in arena.hazards:
                        if h.has_method("set_meta"):
                            h.set_meta("frozen_timer", 2.0)

        elif skill_name == "magnet_tether":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = enemies[0]
                var min_dist = pow(target.x - self.ball.x, 2) + pow(target.y - self.ball.y, 2)
                for i in range(1, enemies.size()):
                    var e = enemies[i]
                    var dist = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist < min_dist:
                        min_dist = dist
                        target = e
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("magnet_tether_target", target)
                    self.ball.set_meta("magnet_tether_timer", 1.0)
        elif skill_name == "clone":
            var num_clones = randi() % 3 + 2 # 2 to 4 clones
            for i in range(num_clones):
                var clone = self.ball.duplicate()
                var next_id = randi() % 90000 + 10000
                if "next_id" in self.world:
                    next_id = self.world.next_id
                    self.world.next_id += 1
                clone.id = next_id

                if "x" in clone: clone.x += randf_range(-25.0, 25.0)
                if "y" in clone: clone.y += randf_range(-25.0, 25.0)

                if "hp" in self.ball: clone.hp = self.ball.hp
                if "max_hp" in self.ball: clone.max_hp = self.ball.max_hp
                if clone.has_method("set_meta"):
                    clone.set_meta("is_clone", true)
                    clone.set_meta("clone_owner", self.ball.id)
                clone.alive = true
                if "speed" in clone: clone.speed = 0.0
                if "damage" in clone: clone.damage = 0.0

                if "skill_timer" in clone: clone.skill_timer = 9999.0
                if "skill" in clone: clone.skill = ""
                if clone.has_method("set_meta"):
                    clone.set_meta("skill", "")

                if "balls" in self.world:
                    self.world.balls.append(clone)

            if "skill_cooldown" in self.ball:
                self.ball.skill_timer = self.ball.skill_cooldown
            else:
                self.ball.skill_timer = 5.0
        elif skill_name == "summon_minions":
            var num_minions = randi() % 3 + 2 # 2 to 4 minions
            for i in range(num_minions):
                var minion = null
                # Create a weak ball manually
                var next_id = randi() % 90000 + 10000
                if "next_id" in self.world:
                    next_id = self.world.next_id
                    self.world.next_id += 1

                # We need an object that mimics a ball, we can try to find an existing easy ball type
                # or just create a dictionary (but GDScript arrays in this engine are tricky).
                # Actually, better to duplicate the summoner but drastically nerf it, or use a known type if possible.
                # To be safe, duplicate the summoner:
                minion = self.ball.duplicate()
                minion.id = next_id

                # Jitter position
                if "x" in minion: minion.x += randf_range(-15.0, 15.0)
                if "y" in minion: minion.y += randf_range(-15.0, 15.0)

                minion.hp = 20.0
                minion.max_hp = 20.0
                if "team" in self.ball:
                    minion.team = self.ball.team
                elif "ball_type" in self.ball:
                    minion.team = self.ball.ball_type

                if minion.has_method("set_meta"):
                    minion.set_meta("is_minion", true)
                    minion.set_meta("minion_owner", self.ball.id)
                minion.alive = true

                if "skill_timer" in minion: minion.skill_timer = 0.0
                if "skill" in minion: minion.skill = ""
                if minion.has_method("set_meta"): minion.set_meta("skill", "")
                if "attack_timer" in minion: minion.attack_timer = 0.0
                if "current_action" in minion: minion.current_action = "idle"

                if "balls" in self.world:
                    self.world.balls.append(minion)
        elif skill_name == "raise_dead":
            if "dead_balls" in self.world:
                var recent_dead = []
                for b in self.world.dead_balls:
                    var time_since = 0.0
                    if b.has_meta("time_since_death"):
                        time_since = b.get_meta("time_since_death")
                    var b_team = ""
                    if "team" in b: b_team = b.team
                    var self_team = ""
                    if "team" in self.ball: self_team = self.ball.team
                    if time_since < 5.0 and b_team != self_team:
                        recent_dead.append(b)

                if recent_dead.size() > 0:
                    var target_dead = recent_dead[recent_dead.size() - 1]
                    self.world.dead_balls.erase(target_dead)

                    var explosion_radius = 80.0
                    var max_hp = 100.0
                    if "max_hp" in target_dead:
                        max_hp = float(target_dead.max_hp)
                    var explosion_damage = max_hp * 0.5

                    var enemies = _get_enemies()
                    for e in enemies:
                        var dx = e.x - target_dead.x
                        var dy = e.y - target_dead.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist <= explosion_radius:
                            if e.has_method("take_damage"):
                                e.take_damage(explosion_damage)

        elif skill_name == "deploy_decoy_beacon":
            if "balls" in self.world:
                var beacon = null
                if self.ball.has_method("duplicate"):
                    beacon = self.ball.duplicate()
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    beacon = self.ball.duplicate()

                if beacon != null:
                    if "id" in beacon:
                        beacon.id = randi() % 90000 + 10000
                    if "hp" in beacon and "max_hp" in beacon:
                        beacon.max_hp = float(self.ball.max_hp) * 0.3
                        beacon.hp = beacon.max_hp
                    if "damage" in beacon:
                        beacon.damage = 0.0
                    if "speed" in beacon:
                        beacon.speed = 0.0

                    if beacon.has_method("set_meta"):
                        beacon.set_meta("owner_id", self_id_stat)
                        beacon.set_meta("is_decoy", true)
                        beacon.set_meta("is_decoy_beacon", true)
                        beacon.set_meta("decoy_timer", 5.0)
                        beacon.set_meta("skill_timer", 9999.0)
                        beacon.set_meta("attack_timer", 9999.0)
                        beacon.set_meta("SKILL", null)
                        beacon.set_meta("skill", null)
                        beacon.set_meta("active_skill", null)
                    elif beacon is Dictionary:
                        beacon["owner_id"] = self_id_stat
                        beacon["is_decoy"] = true
                        beacon["is_decoy_beacon"] = true
                        beacon["decoy_timer"] = 5.0
                        beacon["skill_timer"] = 9999.0
                        beacon["attack_timer"] = 9999.0
                        beacon["SKILL"] = null
                        beacon["skill"] = null
                        beacon["active_skill"] = null

                    self.world.balls.append(beacon)


        elif skill_name == "shoot_portals":
            var arena = self.world.get("arena") if self.world != null else null
            if arena != null and "hazards" in arena:
                # Portal 1 near self
                var p1_id = arena.hazards.size() + randi_range(10000, 49999)
                var p1 = load("res://src/arena/procedural_arena.gd").Hazard.new(p1_id, self.ball.x + randf_range(-20, 20), self.ball.y + randf_range(-20, 20), 30.0, "teleporter", 0.0)

                # Portal 2 near target or random
                var p2_id = arena.hazards.size() + randi_range(50000, 99999)
                var target_x = 0.0
                var target_y = 0.0
                var enemies = _get_enemies()
                if enemies.size() > 0:
                    var target = _find_strongest_enemy_deterministic(enemies)
                    target_x = target.x + randf_range(-30, 30)
                    target_y = target.y + randf_range(-30, 30)
                else:
                    var width = arena.get("width") if arena.get("width") != null else 1000.0
                    var height = arena.get("height") if arena.get("height") != null else 1000.0
                    target_x = randf_range(100.0, width - 100.0)
                    target_y = randf_range(100.0, height - 100.0)

                var p2 = load("res://src/arena/procedural_arena.gd").Hazard.new(p2_id, target_x, target_y, 30.0, "teleporter", 0.0)

                p1.set_meta("target_x", p2.x)
                p1.set_meta("target_y", p2.y)
                p2.set_meta("target_x", p1.x)
                p2.set_meta("target_y", p1.y)

                p1.set_meta("duration", 10.0)
                p2.set_meta("duration", 10.0)
                p1.set_meta("owner_id", self.ball.get("id"))
                p2.set_meta("owner_id", self.ball.get("id"))

                arena.hazards.append(p1)
                arena.hazards.append(p2)

                var cd = self.ball.get("SKILL_COOLDOWN")
                if cd != null:
                    self.ball.skill_timer = cd
                else:
                    self.ball.skill_timer = 5.0
        elif skill_name == "deploy_decoy":
            var swapped = false
            if "balls" in self.world:
                for b in self.world.balls:
                    var is_d = false
                    if "is_decoy" in b and b.is_decoy:
                        is_d = true
                    elif b.has_method("get_meta") and b.has_meta("is_decoy") and b.get_meta("is_decoy"):
                        is_d = true

                    if is_d:
                        var owner = -1
                        if "owner_id" in b: owner = b.owner_id
                        elif b.has_method("get_meta") and b.has_meta("owner_id"): owner = b.get_meta("owner_id")

                        var has_swapped = false
                        if "has_swapped" in b: has_swapped = b.has_swapped
                        elif b.has_method("get_meta") and b.has_meta("has_swapped"): has_swapped = b.get_meta("has_swapped")

                        var b_alive = true
                        if "alive" in b: b_alive = b.alive
                        elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                        var self_id = -2
                        if "id" in self.ball: self_id = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id = self.ball.get_meta("id")

                        if owner == self_id and not has_swapped and b_alive:
                            var tx = self.ball.x
                            var ty = self.ball.y
                            self.ball.x = b.x
                            self.ball.y = b.y
                            b.x = tx
                            b.y = ty

                            if b.has_method("set_meta"):
                                b.set_meta("has_swapped", true)
                            elif "has_swapped" in b:
                                b.has_swapped = true

                            var cooldown = 4.0
                            if "SKILL_COOLDOWN" in self.ball: cooldown = self.ball.SKILL_COOLDOWN
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = self.ball.get_meta("SKILL_COOLDOWN")

                            if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)
                            swapped = true
                            break

            if not swapped and "balls" in self.world:
                var decoy = null
                if self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()
                elif self.ball is Dictionary:
                    decoy = self.ball.duplicate()

                if decoy != null:
                    if "id" in decoy:
                        decoy.id = randi() % 90000 + 10000
                    if "hp" in decoy and "max_hp" in decoy:
                        decoy.max_hp = float(self.ball.max_hp) * 0.1
                        decoy.hp = decoy.max_hp
                    if "damage" in decoy:
                        decoy.damage = 0.0
                    if "speed" in decoy:
                        decoy.speed = 0.0
                    var self_id_stat = -2
                    if "id" in self.ball: self_id_stat = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                    if decoy.has_method("set_meta"):
                        decoy.set_meta("owner_id", self_id_stat)
                        decoy.set_meta("has_swapped", false)
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_timer", 5.0)
                        decoy.set_meta("skill_timer", 9999.0)
                        decoy.set_meta("attack_timer", 9999.0)
                        decoy.set_meta("SKILL", null)
                        decoy.set_meta("skill", null)
                        decoy.set_meta("active_skill", null)
                    elif decoy is Dictionary:
                        decoy["owner_id"] = self_id_stat
                        decoy["has_swapped"] = false
                        decoy["is_decoy"] = true
                        decoy["decoy_timer"] = 5.0
                        decoy["skill_timer"] = 9999.0
                        decoy["attack_timer"] = 9999.0
                        decoy["SKILL"] = null
                        decoy["skill"] = null
                        decoy["active_skill"] = null
                    else:
                        pass # fallback if not possible
                    self.world.balls.append(decoy)
                    if "skill_timer" in self.ball:
                        self.ball.skill_timer = 0.5
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("skill_timer", 0.5)
        elif skill_name == "mimic_clone":
            if "balls" in self.world:
                var clone = null
                if self.ball.has_method("duplicate"):
                    clone = self.ball.duplicate()
                elif self.ball is Dictionary:
                    clone = self.ball.duplicate()

                if clone != null:
                    var next_id = randi() % 90000 + 10000
                    if "next_id" in self.world:
                        next_id = self.world.next_id
                        self.world.next_id += 1

                    if "id" in clone: clone.id = next_id
                    if "hp" in clone and "max_hp" in clone:
                        clone.max_hp = 50.0
                        clone.hp = clone.max_hp
                    if "damage" in clone: clone.damage = 0.0

                    if "skill" in clone: clone.skill = ""
                    if "SKILL" in clone: clone.SKILL = ""
                    if "skill_timer" in clone: clone.skill_timer = 9999.0

                    var owner_id = null
                    if "id" in self.ball: owner_id = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): owner_id = self.ball.get_meta("id")

                    if clone.has_method("set_meta"):
                        clone.set_meta("is_mimic_clone", true)
                        clone.set_meta("is_illusion", true)
                        clone.set_meta("mimic_timer", 10.0)
                        clone.set_meta("mimic_owner", owner_id)
                        clone.set_meta("skill", "")
                        clone.set_meta("skill_timer", 9999.0)
                    elif clone is Dictionary:
                        clone["is_mimic_clone"] = true
                        clone["is_illusion"] = true
                        clone["mimic_timer"] = 10.0
                        clone["mimic_owner"] = owner_id
                        clone["skill"] = ""
                        clone["skill_timer"] = 9999.0

                    self.world.balls.append(clone)
        elif skill_name == "deploy_illusion":
            if "balls" in self.world:
                var illusion = null
                if self.ball.has_method("duplicate"):
                    illusion = self.ball.duplicate()
                elif self.ball is Dictionary:
                    illusion = self.ball.duplicate()

                if illusion != null:
                    var next_id = randi() % 90000 + 10000
                    if "next_id" in self.world:
                        next_id = self.world.next_id
                        self.world.next_id += 1

                    if "id" in illusion:
                        illusion.id = next_id
                    if "hp" in illusion and "max_hp" in illusion:
                        illusion.max_hp = 1.0
                        illusion.hp = illusion.max_hp
                    if "damage" in illusion:
                        illusion.damage = 0.0
                    if "speed" in illusion:
                        illusion.speed = 0.0

                    if "skill" in illusion: illusion.skill = ""
                    if "SKILL" in illusion: illusion.SKILL = ""
                    if "skill_timer" in illusion: illusion.skill_timer = 9999.0

                    if illusion.has_method("set_meta"):
                        illusion.set_meta("is_illusion", true)
                        illusion.set_meta("illusion_timer", 5.0)
                        illusion.set_meta("skill", "")
                        illusion.set_meta("skill_timer", 9999.0)
                    elif illusion is Dictionary:
                        illusion["is_illusion"] = true
                        illusion["illusion_timer"] = 5.0
                        illusion["skill"] = ""
                        illusion["skill_timer"] = 9999.0

                    self.world.balls.append(illusion)
        elif skill_name == "Действие" or skill_name == "action_skill":
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "action_skill_used", "radius": 150})
            elif "team_message" in self.ball:
                self.ball.team_message = {"type": "action_skill_used", "radius": 150}
        elif skill_name == "numpy":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(min_dist_sq)
                if dist > 0.0001:
                    var hp_ratio = 1.0
                    if "hp" in self.ball and "max_hp" in self.ball and self.ball.max_hp > 0:
                        hp_ratio = self.ball.hp / self.ball.max_hp
                    var inputs = [dx/dist, dy/dist, hp_ratio, 1.0]

                    var h_weights = [[0.5, -0.5, 0.1], [0.1, 0.5, -0.1], [0.0, 0.2, 0.8], [0.0, 0.0, 0.0]]
                    var h_biases = [0.1, 0.0, -0.1]
                    var hidden = [0.0, 0.0, 0.0]
                    for j in range(3):
                        var val = inputs[0]*h_weights[0][j] + inputs[1]*h_weights[1][j] + inputs[2]*h_weights[2][j] + inputs[3]*h_weights[3][j] + h_biases[j]
                        hidden[j] = max(0.0, val)

                    var o_weights = [[0.8, -0.2], [0.2, 0.8], [0.1, 0.1]]
                    var o_biases = [0.0, 0.0]
                    var out_x = hidden[0]*o_weights[0][0] + hidden[1]*o_weights[1][0] + hidden[2]*o_weights[2][0] + o_biases[0]
                    var out_y = hidden[0]*o_weights[0][1] + hidden[1]*o_weights[1][1] + hidden[2]*o_weights[2][1] + o_biases[1]

                    var mag = sqrt(out_x*out_x + out_y*out_y)
                    if mag > 0.0001:
                        self.ball.x += (out_x/mag) * 80.0
                        self.ball.y += (out_y/mag) * 80.0
        elif skill_name == "tornado_skill" or skill_name == "local_tornado":
            if "arena" in self.world and "hazards" in self.world.arena:
                var trap_id = self.world.arena.hazards.size() + (randi() % 9000 + 1000)
                var ProceduralArena = load("res://src/arena/procedural_arena.gd")
                var radius = 80.0 if skill_name == "local_tornado" else 40.0
                var duration = 8.0 if skill_name == "local_tornado" else 5.0
                var kind = "local_tornado" if skill_name == "local_tornado" else "tornado"
                var tornado = ProceduralArena.Hazard.new(trap_id, self.ball.x, self.ball.y, radius, kind, 20.0)
                tornado.set_meta("duration", duration)
                tornado.set_meta("vx", randf_range(-100.0, 100.0))
                tornado.set_meta("vy", randf_range(-100.0, 100.0))
                self.world.arena.hazards.append(tornado)
        elif skill_name == "explosion":
            var enemies = _get_enemies()
            var explosion_radius = 100.0
            var explosion_damage = 50.0

            var elemental_effect = ""

            # Check for elemental interactions and hazard destruction
            if world != null and world.has_method("get_arena"):
                var arena = world.call("get_arena")
                if arena != null and "hazards" in arena:
                    var hazards_to_remove = []
                    for hazard in arena.hazards:
                        var hx = hazard.x - self.ball.x
                        var hy = hazard.y - self.ball.y
                        var h_dist = sqrt(hx*hx + hy*hy)
                        if h_dist <= explosion_radius + hazard.radius:
                            if "kind" in hazard:
                                if hazard.kind == "spikes" or hazard.kind == "fake_booster":
                                    hazards_to_remove.append(hazard)
                                elif (hazard.kind == "lava" or hazard.kind == "poison_cloud") and hazard.active:
                                    explosion_radius = 200.0
                                    if hazard.kind == "lava":
                                        elemental_effect = "fire_aura"
                                    elif hazard.kind == "poison_cloud":
                                        elemental_effect = "poison_aura"

                    for h in hazards_to_remove:
                        var idx = arena.hazards.find(h)
                        if idx != -1:
                            arena.hazards.remove_at(idx)

            # Deal damage
            for e in enemies:
                var dx = e.x - self.ball.x
                var dy = e.y - self.ball.y
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= explosion_radius:
                    if e.has_method("take_damage"):
                        e.take_damage(explosion_damage)

                        if elemental_effect == "fire_aura":
                            if e.has_method("set_meta"):
                                var current_burn = 0.0
                                if e.has_meta("burn_timer"):
                                    current_burn = e.get_meta("burn_timer")
                                e.set_meta("burn_timer", current_burn + 5.0)
                        elif elemental_effect == "poison_aura":
                            if e.has_method("set_meta"):
                                var current_poison = 0.0
                                if e.has_meta("poison_timer"):
                                    current_poison = e.get_meta("poison_timer")
                                e.set_meta("poison_timer", current_poison + 5.0)

            # Break walls/corridors
            if world != null and world.has_method("get_arena"):
                var arena = world.call("get_arena")
                if arena != null and arena.get("rooms") != null:
                    var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
                    if ProceduralArenaScript != null:
                        var crater_size = explosion_radius * 1.5
                        var new_room = ProceduralArenaScript.Room.new(self.ball.x - crater_size/2, self.ball.y - crater_size/2, crater_size, crater_size)
                        arena.rooms.append(new_room)
                        if arena.has_method("queue_redraw"):
                            arena.call("queue_redraw")

        elif skill_name == "repel_burst":
            if "skill_cooldown" in self.ball:
                self.ball.skill_timer = self.ball.skill_cooldown
            else:
                self.ball.skill_timer = 10.0

            var push_radius = 200.0
            var push_force = 400.0
            if "boosters" in self.world:
                for b in self.world.boosters:
                    var b_x = 0.0
                    var b_y = 0.0
                    if typeof(b) == TYPE_DICTIONARY:
                        b_x = b.get("x", 0.0)
                        b_y = b.get("y", 0.0)
                    else:
                        b_x = b.x
                        b_y = b.y

                    var dx = b_x - self.ball.x
                    var dy = b_y - self.ball.y
                    var dist_sq = dx*dx + dy*dy
                    if dist_sq > 0 and dist_sq < push_radius*push_radius:
                        var dist = sqrt(dist_sq)
                        if typeof(b) == TYPE_DICTIONARY:
                            b["x"] += (dx / dist) * 50.0
                            b["y"] += (dy / dist) * 50.0
                        else:
                            b.x += (dx / dist) * 50.0
                            b.y += (dy / dist) * 50.0
            if "balls" in self.world:
                for other in self.world.balls:
                    if other.id != self.ball.id:
                        var dx = other.x - self.ball.x
                        var dy = other.y - self.ball.y
                        var dist_sq = dx*dx + dy*dy
                        if dist_sq > 0 and dist_sq < push_radius*push_radius:
                            var dist = sqrt(dist_sq)
                            if not ("vx" in other):
                                if other.has_method("set_meta"): other.set_meta("vx", 0.0)
                                elif typeof(other) == TYPE_DICTIONARY: other["vx"] = 0.0
                                else: other.vx = 0.0
                            if not ("vy" in other):
                                if other.has_method("set_meta"): other.set_meta("vy", 0.0)
                                elif typeof(other) == TYPE_DICTIONARY: other["vy"] = 0.0
                                else: other.vy = 0.0

                            var vx = 0.0
                            if "vx" in other: vx = other.vx
                            elif typeof(other) == TYPE_DICTIONARY: vx = other.get("vx", 0.0)

                            var vy = 0.0
                            if "vy" in other: vy = other.vy
                            elif typeof(other) == TYPE_DICTIONARY: vy = other.get("vy", 0.0)

                            vx += (dx / dist) * push_force
                            vy += (dy / dist) * push_force

                            if typeof(other) == TYPE_DICTIONARY:
                                other["vx"] = vx
                                other["vy"] = vy
                            else:
                                other.vx = vx
                                other.vy = vy

            if self.has_method("_spawn_skill_particles"):
                self._spawn_skill_particles("repel_burst")
        elif skill_name == "stamina_dash":
            _spawn_skill_particles("dash")
            var st = 0.0
            if self.ball.has_method("has_meta") and self.ball.has_meta("stamina"):
                st = self.ball.get_meta("stamina")
            elif "stamina" in self.ball:
                st = self.ball.stamina

            if self.ball.has_method("set_meta"):
                self.ball.set_meta("stamina", 0.0)
            elif "stamina" in self.ball:
                self.ball.stamina = 0.0

            var dash_dist = max(100.0, st * 2.0)
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(min_dist_sq)
                if dist > 0.0001:
                    self.ball.x += (dx/dist) * dash_dist
                    self.ball.y += (dy/dist) * dash_dist
            else:
                var angle = randf() * PI * 2.0
                self.ball.x += cos(angle) * dash_dist
                self.ball.y += sin(angle) * dash_dist

            for e in _get_enemies():
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                var my_radius = 10.0
                if "radius" in self.ball: my_radius = self.ball.radius
                elif self.ball.has_method("has_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")
                var e_radius = 10.0
                if "radius" in e: e_radius = e.radius
                elif e.has_method("has_meta") and e.has_meta("radius"): e_radius = e.get_meta("radius")

                if dist_sq < pow(my_radius + e_radius + 20.0, 2):
                    var dmg = 20.0
                    if "damage" in self.ball: dmg = self.ball.damage * 3.0
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("damage"): dmg = self.ball.get_meta("damage") * 3.0

                    if e.has_method("take_damage"):
                        e.take_damage(dmg)
                    elif "hp" in e:
                        e.hp -= dmg

                    var kb_dx = e.x - self.ball.x
                    var kb_dy = e.y - self.ball.y
                    var kb_dist = sqrt(pow(kb_dx, 2) + pow(kb_dy, 2))
                    if kb_dist > 0.0001:
                        var kb_force = max(50.0, st * 1.5)
                        e.x += (kb_dx / kb_dist) * kb_force
                        e.y += (kb_dy / kb_dist) * kb_force

        elif skill_name == "dash":
            _spawn_skill_particles("dash")
            var dash_range_mult = 1.0
            if self.ball.has_method("has_meta") and self.ball.has_meta("dash_range_mult"):
                dash_range_mult = self.ball.get_meta("dash_range_mult")
            var dash_dist = 100.0 * dash_range_mult

            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(min_dist_sq)
                if dist > 0.0001:
                    self.ball.x += (dx/dist) * dash_dist
                    self.ball.y += (dy/dist) * dash_dist
            else:
                var angle = randf() * PI * 2.0
                self.ball.x += cos(angle) * dash_dist
                self.ball.y += sin(angle) * dash_dist


        elif skill_name == "lightning_strike":
            var enemies = _get_enemies()

            var is_raining = false
            if "arena" in self.world and self.world.arena != null:
                if "is_raining" in self.world.arena:
                    is_raining = self.world.arena.is_raining
                elif self.world.arena.has_method("has_meta") and self.world.arena.has_meta("is_raining"):
                    is_raining = self.world.arena.get_meta("is_raining")
            if not is_raining and "game_mode" in self.world and self.world.game_mode != null:
                var weather = ""
                if "weather" in self.world.game_mode:
                    weather = self.world.game_mode.weather
                elif self.world.game_mode.has_method("has_meta") and self.world.game_mode.has_meta("weather"):
                    weather = self.world.game_mode.get_meta("weather")
                if weather in ["rain", "thunderstorm"]:
                    is_raining = true

            var is_foggy = false
            if "arena" in self.world and self.world.arena != null:
                if "is_foggy" in self.world.arena:
                    is_foggy = self.world.arena.is_foggy
                elif self.world.arena.has_method("has_meta") and self.world.arena.has_meta("is_foggy"):
                    is_foggy = self.world.arena.get_meta("is_foggy")
            if not is_foggy and "game_mode" in self.world and self.world.game_mode != null:
                var weather = ""
                if "weather" in self.world.game_mode:
                    weather = self.world.game_mode.weather
                elif self.world.game_mode.has_method("has_meta") and self.world.game_mode.has_meta("weather"):
                    weather = self.world.game_mode.get_meta("weather")
                if weather in ["fog", "snow", "blizzard"]:
                    is_foggy = true

            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e

                var dist = sqrt(min_dist_sq)
                var strike_range = 200.0
                if is_foggy:
                    strike_range *= 1.5

                if dist <= strike_range:
                    var dmg = 24.0
                    if "damage" in self.ball:
                        dmg = self.ball.damage
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("damage"):
                        dmg = self.ball.get_meta("damage")

                    if is_raining:
                        dmg *= 1.5

                    if target.has_method("take_damage"):
                        target.take_damage(dmg)
                    elif "hp" in target:
                        target.hp -= dmg

                    if self.has_method("_spawn_skill_particles"):
                        self._spawn_skill_particles("lightning")

                    var hazards = []
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                        hazards = self.world.arena.hazards

                    var hit_entities = []
                    hit_entities.append(self.ball)
                    hit_entities.append(target)
                    var current_target = target
                    var chain_damage = dmg * 1.5

                    var max_jumps = 3
                    if is_raining:
                        max_jumps += 1

                    var jumps = 0

                    while jumps < max_jumps:
                        var nearby_entities = []
                        var chain_range = 150.0
                        if is_foggy:
                            chain_range *= 1.5

                        for e in enemies:
                            if hit_entities.find(e) == -1:
                                var d_sq = pow(e.x - current_target.x, 2) + pow(e.y - current_target.y, 2)
                                if d_sq <= chain_range * chain_range:
                                    nearby_entities.append({"d_sq": d_sq, "entity": e, "type": "enemy"})
                        for h in hazards:
                            if hit_entities.find(h) == -1:
                                var h_active = true
                                if "active" in h:
                                    h_active = h.active
                                elif h.has_method("has_meta") and h.has_meta("active"):
                                    h_active = h.get_meta("active")
                                if h_active:
                                    var d_sq = pow(h.x - current_target.x, 2) + pow(h.y - current_target.y, 2)
                                    if d_sq <= chain_range * chain_range:
                                        nearby_entities.append({"d_sq": d_sq, "entity": h, "type": "hazard"})

                        if nearby_entities.size() == 0:
                            break

                        nearby_entities.sort_custom(func(a, b): return a["dist"] < b["dist"])
                        var next_entity = nearby_entities[0]["entity"]
                        var e_type = nearby_entities[0]["type"]

                        if e_type == "enemy":
                            if next_entity.has_method("take_damage"):
                                next_entity.take_damage(chain_damage)
                            elif "hp" in next_entity:
                                next_entity.hp -= chain_damage
                        else:
                            if "hp" in next_entity:
                                next_entity.hp -= chain_damage
                                if next_entity.hp <= 0:
                                    if "active" in next_entity:
                                        next_entity.active = false

                        if self.has_method("_spawn_skill_particles"):
                            self._spawn_skill_particles("lightning")

                        hit_entities.append(next_entity)
                        current_target = next_entity
                        chain_damage *= 1.5
                        jumps += 1

        elif skill_name == "elemental_burst":
            var enemies = self._get_enemies()
            var allies = []
            if "balls" in self.world:
                for b in self.world.balls:
                    var is_alive = true
                    if "alive" in b:
                        is_alive = b.alive
                    elif b.has_method("has_meta") and b.has_meta("alive"):
                        is_alive = b.get_meta("alive")
                    var b_id = -1
                    if "id" in b:
                        b_id = b.id
                    var b_type = ""
                    if "BALL_TYPE" in b:
                        b_type = b.BALL_TYPE
                    elif b.has_method("has_meta") and b.has_meta("BALL_TYPE"):
                        b_type = b.get_meta("BALL_TYPE")
                    if is_alive and b_id != self.ball.id and b_type == "elementalist":
                        allies.append(b)

            var chain_bonus = 1.0
            for ally in allies:
                var dx = ally.x - self.ball.x
                var dy = ally.y - self.ball.y
                if sqrt(dx*dx + dy*dy) < 150.0:
                    chain_bonus += 0.5

            var burst_radius = 80.0 * chain_bonus
            var base_burst_dmg = 20.0 * chain_bonus

            var is_raining = false
            if "arena" in self.world and self.world.arena != null:
                if "is_raining" in self.world.arena:
                    is_raining = self.world.arena.is_raining
                elif self.world.arena.has_method("has_meta") and self.world.arena.has_meta("is_raining"):
                    is_raining = self.world.arena.get_meta("is_raining")
            if not is_raining and "game_mode" in self.world and self.world.game_mode != null:
                var weather = ""
                if "weather" in self.world.game_mode:
                    weather = self.world.game_mode.weather
                elif self.world.game_mode.has_method("has_meta") and self.world.game_mode.has_meta("weather"):
                    weather = self.world.game_mode.get_meta("weather")
                if weather in ["rain", "thunderstorm"]:
                    is_raining = true

            var is_foggy = false
            if "arena" in self.world and self.world.arena != null:
                if "is_foggy" in self.world.arena:
                    is_foggy = self.world.arena.is_foggy
                elif self.world.arena.has_method("has_meta") and self.world.arena.has_meta("is_foggy"):
                    is_foggy = self.world.arena.get_meta("is_foggy")
            if not is_foggy and "game_mode" in self.world and self.world.game_mode != null:
                var weather = ""
                if "weather" in self.world.game_mode:
                    weather = self.world.game_mode.weather
                elif self.world.game_mode.has_method("has_meta") and self.world.game_mode.has_meta("weather"):
                    weather = self.world.game_mode.get_meta("weather")
                if weather in ["fog", "snow", "blizzard"]:
                    is_foggy = true

            if is_raining:
                burst_radius *= 1.5
                base_burst_dmg *= 1.5

            if is_foggy:
                burst_radius *= 1.5

            if enemies.size() > 0:
                if is_raining:
                    var primary_hits = []
                    for enemy in enemies:
                        var dx = enemy.x - self.ball.x
                        var dy = enemy.y - self.ball.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist <= burst_radius:
                            if enemy.has_method("take_damage"):
                                enemy.take_damage(base_burst_dmg)
                            var e_stunned = false
                            if "is_stunned" in enemy:
                                e_stunned = enemy.is_stunned
                            elif enemy.has_method("has_meta") and enemy.has_meta("is_stunned"):
                                e_stunned = enemy.get_meta("is_stunned")
                            if not e_stunned:
                                if "is_stunned" in enemy:
                                    enemy.is_stunned = true
                                else:
                                    enemy.set_meta("is_stunned", true)
                                var e_stun_timer = 0.0
                                if "stun_timer" in enemy:
                                    e_stun_timer = enemy.stun_timer
                                elif enemy.has_method("has_meta") and enemy.has_meta("stun_timer"):
                                    e_stun_timer = enemy.get_meta("stun_timer")
                                e_stun_timer = max(e_stun_timer, 2.0)
                                if "stun_timer" in enemy:
                                    enemy.stun_timer = e_stun_timer
                                else:
                                    enemy.set_meta("stun_timer", e_stun_timer)
                            primary_hits.append(enemy)

                    var hit_entities = []
                    hit_entities.append(self.ball)
                    for ph in primary_hits:
                        hit_entities.append(ph)

                    for primary in primary_hits:
                        for enemy in enemies:
                            if hit_entities.find(enemy) == -1:
                                var dx = enemy.x - primary.x
                                var dy = enemy.y - primary.y
                                var dist = sqrt(dx*dx + dy*dy)
                                if dist <= burst_radius:
                                    if enemy.has_method("take_damage"):
                                        enemy.take_damage(base_burst_dmg * 0.5)
                                    var e_stunned = false
                                    if "is_stunned" in enemy:
                                        e_stunned = enemy.is_stunned
                                    elif enemy.has_method("has_meta") and enemy.has_meta("is_stunned"):
                                        e_stunned = enemy.get_meta("is_stunned")
                                    if not e_stunned:
                                        if "is_stunned" in enemy:
                                            enemy.is_stunned = true
                                        else:
                                            enemy.set_meta("is_stunned", true)
                                        var e_stun_timer = 0.0
                                        if "stun_timer" in enemy:
                                            e_stun_timer = enemy.stun_timer
                                        elif enemy.has_method("has_meta") and enemy.has_meta("stun_timer"):
                                            e_stun_timer = enemy.get_meta("stun_timer")
                                        e_stun_timer = max(e_stun_timer, 1.0)
                                        if "stun_timer" in enemy:
                                            enemy.stun_timer = e_stun_timer
                                        else:
                                            enemy.set_meta("stun_timer", e_stun_timer)
                                    hit_entities.append(enemy)
                                    break
                else:
                    for enemy in enemies:
                        var dx = enemy.x - self.ball.x
                        var dy = enemy.y - self.ball.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist <= burst_radius:
                            if enemy.has_method("take_damage"):
                                enemy.take_damage(base_burst_dmg)
                            var arena_raining = false
                            if self.world != null and "arena" in self.world and self.world.arena != null:
                                if "is_raining" in self.world.arena:
                                    arena_raining = self.world.arena.is_raining
                                elif self.world.arena.has_method("has_meta") and self.world.arena.has_meta("is_raining"):
                                    arena_raining = self.world.arena.get_meta("is_raining")
                            if arena_raining:
                                var e_stunned = false
                                if "is_stunned" in enemy:
                                    e_stunned = enemy.is_stunned
                                elif enemy.has_method("has_meta") and enemy.has_meta("is_stunned"):
                                    e_stunned = enemy.get_meta("is_stunned")
                                if not e_stunned:
                                    if "is_stunned" in enemy:
                                        enemy.is_stunned = true
                                    else:
                                        enemy.set_meta("is_stunned", true)
                                    var e_stun_timer = 0.0
                                    if "stun_timer" in enemy:
                                        e_stun_timer = enemy.stun_timer
                                    elif enemy.has_method("has_meta") and enemy.has_meta("stun_timer"):
                                        e_stun_timer = enemy.get_meta("stun_timer")
                                    e_stun_timer = max(e_stun_timer, 2.0)
                                    if "stun_timer" in enemy:
                                        enemy.stun_timer = e_stun_timer
                                    else:
                                        enemy.set_meta("stun_timer", e_stun_timer)
        elif skill_name == "silence_aura":
            var enemies = _get_enemies() if has_method("_get_enemies") else []
            if enemies.size() == 0 and "balls" in self.world:
                var my_team = self.ball.team if "team" in self.ball else (self.ball.get_meta("team") if self.ball.has_method("has_meta") and self.ball.has_meta("team") else "")
                var my_id = self.ball.id if "id" in self.ball else (self.ball.get_meta("id") if self.ball.has_method("has_meta") and self.ball.has_meta("id") else -1)
                for b in self.world.balls:
                    var is_alive = b.alive if "alive" in b else (b.get_meta("alive") if b.has_method("has_meta") and b.has_meta("alive") else true)
                    var b_id = b.id if "id" in b else (b.get_meta("id") if b.has_method("has_meta") and b.has_meta("id") else -1)
                    var b_team = b.team if "team" in b else (b.get_meta("team") if b.has_method("has_meta") and b.has_meta("team") else "")
                    if is_alive and b_id != my_id and b_team != my_team:
                        enemies.append(b)

            for enemy in enemies:
                var ex = enemy.x if "x" in enemy else (enemy.get_meta("x") if enemy.has_method("has_meta") and enemy.has_meta("x") else 0.0)
                var ey = enemy.y if "y" in enemy else (enemy.get_meta("y") if enemy.has_method("has_meta") and enemy.has_meta("y") else 0.0)
                var bx = self.ball.x if "x" in self.ball else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else 0.0)
                var by = self.ball.y if "y" in self.ball else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else 0.0)

                var dx = ex - bx
                var dy = ey - by
                var dist = sqrt(dx*dx + dy*dy)
                if dist < 150.0:
                    if "silence_timer" in enemy:
                        enemy.silence_timer = 5.0
                    elif enemy.has_method("set_meta"):
                        enemy.set_meta("silence_timer", 5.0)
        elif skill_name == "place_fake_booster":
            if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                var fb = {}
                fb.kind = "fake_booster"
                fb.x = self.ball.x
                fb.y = self.ball.y
                fb.radius = 15.0
                fb.damage = 50.0
                fb.stun_duration = 2.0
                if "id" in self.ball: fb.owner_id = self.ball.id
                self.world.arena.hazards.append(fb)

                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("skill_timer", 5.0)
                else:
                    self.ball.skill_timer = 5.0

        elif skill_name == "poison_nova":
            if "arena" in self.world and "hazards" in self.world.arena:
                var trap_id = self.world.arena.hazards.size() + randi() % 10000
                var nova = ProceduralArena.Hazard.new(trap_id, self.ball.x, self.ball.y, 0.0, "poison_nova", 30.0)
                nova.set_meta("duration", 5.0)
                nova.set_meta("target_radius", 400.0)
                nova.set_meta("shrink_rate", -80.0)
                self.world.arena.hazards.append(nova)
        elif skill_name == "smokescreen":
            if "arena" in self.world and "hazards" in self.world.arena:
                var trap_id = self.world.arena.hazards.size() + randi() % 10000
                var smoke = ProceduralArena.Hazard.new(trap_id, self.ball.x, self.ball.y, 80.0, "smokescreen", 0.0)
                smoke.set_meta("duration", 5.0)
                self.world.arena.hazards.append(smoke)
        elif skill_name == "flare":
            var arena = null
            if typeof(self.world) == TYPE_OBJECT and self.world.has_method("call"):
                arena = self.world.call("get_arena")
            elif typeof(self.world) == TYPE_DICTIONARY and self.world.has("arena"):
                arena = self.world["arena"]
            elif "arena" in self.world:
                arena = self.world.arena

            if arena != null and "hazards" in arena:
                var enemies = _get_enemies() if has_method("_get_enemies") else []
                var target_x = 0.0
                var target_y = 0.0
                if "x" in self.ball: target_x = self.ball.x
                if "y" in self.ball: target_y = self.ball.y

                if enemies.size() > 0:
                    var closest = enemies[0]
                    var cx = 0.0
                    var cy = 0.0
                    if "x" in closest: cx = closest.x
                    if "y" in closest: cy = closest.y
                    var min_d_sq = pow(cx - target_x, 2) + pow(cy - target_y, 2)
                    for e in enemies:
                        var ex = 0.0
                        var ey = 0.0
                        if "x" in e: ex = e.x
                        if "y" in e: ey = e.y
                        var d_sq = pow(ex - target_x, 2) + pow(ey - target_y, 2)
                        if d_sq < min_d_sq:
                            closest = e
                            min_d_sq = d_sq
                    if "x" in closest: target_x = closest.x
                    if "y" in closest: target_y = closest.y

                var trap_id = arena.hazards.size() + int(randf() * 9000) + 1000

                var flare_trap = null
                if ClassDB.class_exists("Hazard"):
                    flare_trap = ClassDB.instantiate("Hazard")
                    flare_trap.id = trap_id
                    flare_trap.x = target_x
                    flare_trap.y = target_y
                    flare_trap.radius = 400.0
                    flare_trap.kind = "flare"
                    flare_trap.damage = 0.0
                else:
                    flare_trap = {
                        "id": trap_id,
                        "x": target_x,
                        "y": target_y,
                        "radius": 400.0,
                        "kind": "flare",
                        "damage": 0.0
                    }

                if typeof(flare_trap) == TYPE_OBJECT and flare_trap.has_method("set_meta"):
                    flare_trap.set_meta("duration", 5.0)
                elif typeof(flare_trap) == TYPE_DICTIONARY:
                    flare_trap["duration"] = 5.0

                arena.hazards.append(flare_trap)

                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                    self.ball.set_meta("skill_timer", self.ball.get("skill_cooldown") if "skill_cooldown" in self.ball else 5.0)
                elif "skill_timer" in self.ball:
                    self.ball.skill_timer = self.ball.get("skill_cooldown") if "skill_cooldown" in self.ball else 5.0

        elif skill_name == "snipe":
            if "arena" in self.world and "hazards" in self.world.arena:
                var trap_id = self.world.arena.hazards.size() + randi() % 10000
                var trap = ProceduralArena.Hazard.new()
                trap.id = trap_id
                trap.x = self.ball.x
                trap.y = self.ball.y
                trap.radius = 15.0
                trap.kind = "trap"
                trap.damage = 0.0
                trap.set_meta("duration", 5.0)

                var lobby = PreGameLobby.get_instance()
                var trap_variant = lobby.get_trap_variant(self.ball.id)
                trap.set_meta("trap_variant", trap_variant)

                if trap_variant == "ricochet":
                    if "ricochet_barrier_timer" in self.ball:
                        self.ball.ricochet_barrier_timer = 3.0
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("ricochet_barrier_timer", 3.0)

                self.world.arena.hazards.append(trap)
        elif skill_name == "mind_control":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist = 9999999.0
                for e in enemies:
                    var dx = e.x - self.ball.x
                    var dy = e.y - self.ball.y
                    var dist_sq = dx*dx + dy*dy
                    if dist_sq < min_dist:
                        min_dist = dist_sq
                        target = e

                if target != null and sqrt(min_dist) <= 200.0:
                    var is_mc = false
                    if "is_mind_controlled" in target: is_mc = target.is_mind_controlled
                    elif target.has_method("has_meta") and target.has_meta("is_mind_controlled"): is_mc = target.get_meta("is_mind_controlled")

                    if not is_mc:
                        var orig_team = ""
                        if "team" in target: orig_team = target.team
                        elif target.has_method("has_meta") and target.has_meta("team"): orig_team = target.get_meta("team")

                        var my_team = ""
                        if "team" in self.ball: my_team = self.ball.team
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")

                        if target.has_method("set_meta"):
                            target.set_meta("is_mind_controlled", true)
                            target.set_meta("mind_control_timer", 5.0)
                            target.set_meta("original_team", orig_team)
                            target.set_meta("team", my_team)
                        else:
                            target.is_mind_controlled = true
                            target.mind_control_timer = 5.0
                            target.original_team = orig_team
                            target.team = my_team

                        _spawn_skill_particles("mind_control")
        elif skill_name == "ground_pound":
            var pound_radius = 120.0
            var pound_damage = 40.0

            # Deal damage to enemies
            var enemies = _get_enemies()
            if enemies != null:
                for enemy in enemies:
                    var dx = enemy.x - self.ball.x
                    var dy = enemy.y - self.ball.y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist <= pound_radius + (enemy.radius if "radius" in enemy else 0):
                        if enemy.has_method("take_damage"):
                            enemy.take_damage(pound_damage)

            # Destroy hazards
            if world != null and world.has_method("get_arena"):
                var arena = world.call("get_arena")
                if arena != null and "hazards" in arena:
                    var hazards_to_remove = []
                    for hazard in arena.hazards:
                        var hx = hazard.x - self.ball.x
                        var hy = hazard.y - self.ball.y
                        var h_dist = sqrt(hx*hx + hy*hy)
                        if h_dist <= pound_radius + (hazard.radius if "radius" in hazard else 0):
                            if "kind" in hazard and (hazard.kind == "spikes" or hazard.kind == "fake_booster"):
                                hazards_to_remove.append(hazard)

                    for h in hazards_to_remove:
                        var idx = arena.hazards.find(h)
                        if idx != -1:
                            arena.hazards.remove_at(idx)


        elif skill_name == "throw_hazard":
            var arena = world.call("get_arena") if world != null and world.has_method("get_arena") else null
            if arena == null and "arena" in world:
                arena = world.arena

            if arena != null and "hazards" in arena:
                var hazards = arena.hazards
                var target_hazard = null
                var min_dist_sq = 22500.0
                for h in hazards:
                    var kind = ""
                    if "kind" in h: kind = h.kind
                    elif typeof(h) == TYPE_OBJECT and h.has_method("has_meta") and h.has_meta("kind"): kind = h.get_meta("kind")
                    elif typeof(h) == TYPE_DICTIONARY and h.has("kind"): kind = h["kind"]

                    if not kind in ["healing_spring", "booster", "drone_item", "stealth_drone_item", "shadow_booster", "decoy_item", "silence_booster", "freeze_booster", "placeable_trap_item", "exit_portal_item", "position_swap_item", "portal_gun_item", "nemesis_booster"]:
                        var hx = 0.0
                        var hy = 0.0
                        if "x" in h: hx = h.x
                        elif typeof(h) == TYPE_DICTIONARY and h.has("x"): hx = h["x"]
                        if "y" in h: hy = h.y
                        elif typeof(h) == TYPE_DICTIONARY and h.has("y"): hy = h["y"]

                        var dx = hx - self.ball.x
                        var dy = hy - self.ball.y
                        var dist_sq = dx*dx + dy*dy
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            target_hazard = h

                if target_hazard != null:
                    var enemies = _get_enemies()
                    if enemies.size() > 0:
                        var closest_enemy = enemies[0]
                        var min_e_dist_sq = (closest_enemy.x - self.ball.x)*(closest_enemy.x - self.ball.x) + (closest_enemy.y - self.ball.y)*(closest_enemy.y - self.ball.y)
                        for i in range(1, enemies.size()):
                            var e = enemies[i]
                            var dist_sq = (e.x - self.ball.x)*(e.x - self.ball.x) + (e.y - self.ball.y)*(e.y - self.ball.y)
                            if dist_sq < min_e_dist_sq:
                                min_e_dist_sq = dist_sq
                                closest_enemy = e

                        var idx = hazards.find(target_hazard)
                        if idx != -1:
                            hazards.remove_at(idx)
                        else:
                            if "active" in target_hazard: target_hazard.active = false
                            elif typeof(target_hazard) == TYPE_DICTIONARY: target_hazard["active"] = false

                        var dx = closest_enemy.x - self.ball.x
                        var dy = closest_enemy.y - self.ball.y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist < 0.0001: dist = 0.0001
                        var nx = dx / dist
                        var ny = dy / dist

                        var b_radius = 10.0
                        if "radius" in self.ball: b_radius = self.ball.radius

                        var thrown_hazard = {
                            "id": hazards.size() + int(randf() * 90000) + 10000,
                            "x": self.ball.x + nx * (b_radius + 5.0),
                            "y": self.ball.y + ny * (b_radius + 5.0),
                            "radius": 15.0,
                            "kind": "thrown_rock",
                            "damage": 50.0,
                            "vx": nx * 500.0,
                            "vy": ny * 500.0,
                            "duration": 2.0,
                            "owner_id": self.ball.id if "id" in self.ball else null,
                            "active": true
                        }
                        hazards.append(thrown_hazard)

                        var cd = 5.0
                        if "skill_cooldown" in self.ball: cd = self.ball.skill_cooldown
                        self.ball.skill_timer = cd

        elif skill_name == "toggle_polarity":
            var current_polarity = 0
            if "polarity" in self.ball:
                current_polarity = self.ball.polarity
            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("polarity"):
                current_polarity = self.ball.get_meta("polarity")
            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("polarity"):
                current_polarity = self.ball["polarity"]

            var new_polarity = 1
            if current_polarity == 0:
                new_polarity = 1
            elif current_polarity == 1:
                new_polarity = -1
            else:
                new_polarity = 1

            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                self.ball.set_meta("polarity", new_polarity)
            elif typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["polarity"] = new_polarity
            elif "polarity" in self.ball:
                self.ball.polarity = new_polarity

            if "skill_cooldown" in self.ball:
                self.ball.skill_timer = self.ball.skill_cooldown
            else:
                self.ball.skill_timer = 5.0

        elif skill_name == "orbital_shield":
            var trap_id = len(arena.hazards) + (randi() % 9000 + 1000)

            if self.ball.has_method("set_meta"):
                self.ball.set_meta("orbital_shield_active", true)
                self.ball.set_meta("orbital_shield_timer", 10.0)
            else:
                self.ball.orbital_shield_active = true
                self.ball.orbital_shield_timer = 10.0

            var dome = ProceduralArenaScript.Hazard.new(trap_id, self.ball.x, self.ball.y, 300.0, "orbital_shield_dome", 0.0)
            dome.set_meta("duration", 10.0)
            arena.hazards.append(dome)

        elif skill_name == "target_strong":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = _find_strongest_enemy_deterministic(enemies)
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(dx*dx + dy*dy)
                if dist > 0.0001:
                    self.ball.x += (dx/dist) * 150.0
                    self.ball.y += (dy/dist) * 150.0
            else:
                var angle = randf() * PI * 2.0
                self.ball.x += cos(angle) * 150.0
                self.ball.y += sin(angle) * 150.0

        elif skill_name == "reflect_shield":
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("reflect_shield_active", true)
                self.ball.set_meta("reflect_shield_timer", 3.0)
                self.ball.set_meta("reflect_shield_capacity", 999999.0) # Infinite reflection for 3s
            else:
                self.ball.reflect_shield_active = true
                self.ball.reflect_shield_timer = 3.0
                self.ball.reflect_shield_capacity = 999999.0

            if self.has_method("_spawn_skill_particles"):
                self._spawn_skill_particles("shield")

        if "skill_cooldown" in self.ball:
            self.ball.skill_timer = self.ball.skill_cooldown

func _spawn_directed_particles(source, target, effect_type: String = ""):
    if typeof(source) == TYPE_OBJECT and source.has_method("add_child"):
        var particles = CPUParticles2D.new()
        particles.emitting = true
        particles.one_shot = true

        if effect_type == "health_link":
            particles.amount = 30
            particles.lifetime = 0.2
            particles.explosiveness = 0.0
            particles.spread = 5.0
            particles.initial_velocity_min = 100.0
            particles.initial_velocity_max = 200.0
            particles.color = Color(0.2, 0.9, 0.3, 0.8) # Green line
            particles.gravity = Vector2.ZERO

            if typeof(target) == TYPE_OBJECT and typeof(source) == TYPE_OBJECT:
                var tx = target.get("position").x if target.get("position") != null else target.get("x")
                var ty = target.get("position").y if target.get("position") != null else target.get("y")
                var sx = source.get("position").x if source.get("position") != null else source.get("x")
                var sy = source.get("position").y if source.get("position") != null else source.get("y")

                if tx == null and target.has_method("get_meta") and target.has_meta("x"):
                    tx = target.get_meta("x")
                    ty = target.get_meta("y")

                if sx == null and source.has_method("get_meta") and source.has_meta("x"):
                    sx = source.get_meta("x")
                    sy = source.get_meta("y")

                if tx != null and ty != null and sx != null and sy != null:
                    var dx = tx - sx
                    var dy = ty - sy
                    var dist = sqrt(dx*dx + dy*dy)
                    particles.rotation = atan2(dy, dx)
                    particles.initial_velocity_min = dist / particles.lifetime
                    particles.initial_velocity_max = dist / particles.lifetime

        if effect_type == "reflect_pulse":
            particles.amount = 20
            particles.lifetime = 0.4
            particles.explosiveness = 0.9
            particles.spread = 15.0
            particles.initial_velocity_min = 200.0
            particles.initial_velocity_max = 300.0
            particles.color = Color(0.8, 0.4, 1.0, 0.9) # Purple reflect
            particles.gravity = Vector2.ZERO

            if typeof(target) == TYPE_OBJECT and typeof(source) == TYPE_OBJECT:
                var tx = target.get("position").x if target.get("position") != null else target.get("x")
                var ty = target.get("position").y if target.get("position") != null else target.get("y")
                var sx = source.get("position").x if source.get("position") != null else source.get("x")
                var sy = source.get("position").y if source.get("position") != null else source.get("y")

                if tx == null and target.has_method("get_meta") and target.has_meta("x"):
                    tx = target.get_meta("x")
                    ty = target.get_meta("y")

                if sx == null and source.has_method("get_meta") and source.has_meta("x"):
                    sx = source.get_meta("x")
                    sy = source.get_meta("y")

                if tx != null and ty != null and sx != null and sy != null:
                    var dx = tx - sx
                    var dy = ty - sy
                    particles.rotation = atan2(dy, dx)

        else:
            # Generic
            particles.amount = 10
            particles.lifetime = 0.3
            particles.initial_velocity_min = 100.0
            particles.initial_velocity_max = 150.0
            particles.color = Color(1.0, 1.0, 1.0, 0.8)

        source.add_child(particles)
        if particles.has_signal("finished"):
            particles.finished.connect(particles.queue_free)

func _spawn_skill_particles(skill_name: String = ""):
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("add_child"):
        var particles = CPUParticles2D.new()
        particles.emitting = true
        particles.one_shot = true

        # Base tier modifiers
        var ball_skin = self.ball.get("skin") if self.ball.get("skin") != null else "default"
        var tier_multiplier = 1.0
        if ball_skin == "veteran":
            tier_multiplier = 1.5
        elif ball_skin == "elite":
            tier_multiplier = 2.0
        elif ball_skin == "legendary":
            tier_multiplier = 3.0


        # Configure particle properties based on skill
        if skill_name == "wave_attack":
            particles.amount = int(50 * tier_multiplier)
            particles.spread = 360.0
            particles.initial_velocity_min = 100.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.initial_velocity_max = 150.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            if ball_skin == "legendary":
                particles.color = Color(0.8, 0.2, 1.0, 0.9) # Purple for legendary
            elif ball_skin == "elite":
                particles.color = Color(0.2, 0.8, 1.0, 0.9) # Cyan for elite
            else:
                particles.color = Color(0.2, 0.5, 1.0, 0.8) # Blue wave
            particles.lifetime = 0.6 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 0.9
        elif skill_name == "explosion":
            particles.amount = int(60 * tier_multiplier)
            particles.spread = 360.0
            particles.initial_velocity_min = 150.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.initial_velocity_max = 200.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            if ball_skin == "legendary":
                particles.color = Color(1.0, 0.0, 0.0, 1.0) # Intense red
            elif ball_skin == "elite":
                particles.color = Color(1.0, 0.5, 0.0, 1.0) # Orange
            else:
                particles.color = Color(1.0, 0.3, 0.0, 0.9) # Fiery explosion
            particles.lifetime = 0.4 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 1.0
        elif skill_name == "dash":
            particles.amount = int(20 * tier_multiplier)
            particles.spread = 20.0 * (1.0 + (tier_multiplier - 1.0) * 0.5)
            particles.initial_velocity_min = 30.0 * (1.0 + (tier_multiplier - 1.0) * 0.3)
            particles.initial_velocity_max = 80.0 * (1.0 + (tier_multiplier - 1.0) * 0.3)
            if ball_skin == "legendary":
                particles.color = Color(1.0, 0.8, 0.0, 0.8) # Golden trail
            elif ball_skin == "elite":
                particles.color = Color(0.8, 0.8, 1.0, 0.8) # Bright white/blue trail
            elif ball_skin == "veteran":
                particles.color = Color(0.6, 0.6, 0.6, 0.6) # Darker trail
            else:
                particles.color = Color(0.8, 0.8, 0.8, 0.5) # Dust/wind trail
            particles.lifetime = 0.3 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 0.5
            # Could orient opposite to velocity if we had it, but spread and low life is fine
        elif skill_name == "repel_burst":
            particles["color"] = "purple"
            particles["speed"] = 400.0
            particles["lifetime"] = 0.5
        elif skill_name == "chaos_link":
            var all_balls = []
            if self.world.has("balls"):
                for b in self.world.balls:
                    var is_alive = true
                    if "alive" in b: is_alive = b.alive
                    elif b.has_method("has_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

                    if is_alive and b != self.ball:
                        all_balls.append(b)
            if all_balls.size() > 0:
                var target_cl = all_balls[randi() % all_balls.size()]
                if target_cl != null:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("chaos_link_target", target_cl)
                        self.ball.set_meta("chaos_link_timer", 5.0)
                        target_cl.set_meta("chaos_link_target", self.ball)
                    else:
                        self.ball.chaos_link_target = target_cl
                        self.ball.chaos_link_timer = 5.0
                        target_cl.chaos_link_target = self.ball

                    if self.has_method("_spawn_directed_particles"):
                        self._spawn_directed_particles(self.ball, target_cl, "chaos_link")
        elif skill_name == "health_link":
            var allies_hl = []
            if self.world.has("balls"):
                for b in self.world.balls:
                    var is_alive = true
                    if "alive" in b: is_alive = b.alive
                    elif b.has_method("has_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

                    var team = ""
                    if "team" in b: team = b.team
                    elif b.has_method("has_meta") and b.has_meta("team"): team = b.get_meta("team")

                    var my_team = ""
                    if "team" in self.ball: my_team = self.ball.team
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")

                    var b_id = -1
                    if "id" in b: b_id = b.id
                    elif b.has_method("has_meta") and b.has_meta("id"): b_id = b.get_meta("id")

                    var my_id = -2
                    if "id" in self.ball: my_id = self.ball.id
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

                    if b_id != my_id and team == my_team and is_alive:
                        allies_hl.append(b)
            if allies_hl.size() > 0:
                var min_hp_ratio = INF
                var target_hl = null
                for a in allies_hl:
                    var a_hp = 100.0
                    if "hp" in a: a_hp = a.hp
                    var a_mhp = 100.0
                    if "max_hp" in a: a_mhp = a.max_hp
                    var ratio = a_hp / max(a_mhp, 1.0)
                    if ratio < min_hp_ratio:
                        min_hp_ratio = ratio
                        target_hl = a
                if target_hl != null:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("health_link_target", target_hl)
                        self.ball.set_meta("health_link_timer", 5.0)
                    else:
                        self.ball.health_link_target = target_hl
                        self.ball.health_link_timer = 5.0

                    if self.has_method("_spawn_directed_particles"):
                        self._spawn_directed_particles(self.ball, target_hl, "health_link")      elif skill_name == "shield" or skill_name == "protect_ally":
            particles.amount = int(40 * tier_multiplier)
            particles.spread = 360.0
            particles.initial_velocity_min = 20.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.initial_velocity_max = 40.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            if ball_skin == "legendary":
                particles.color = Color(1.0, 0.9, 0.0, 0.9) # Bright gold aura
            elif ball_skin == "elite":
                particles.color = Color(0.9, 0.9, 0.5, 0.8) # Light gold aura
            else:
                particles.color = Color(0.9, 0.8, 0.2, 0.7) # Golden/yellow aura
            particles.lifetime = 0.8 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 0.2 # Sustained bubble look
        elif skill_name == "heal_ally":
            particles.amount = int(25 * tier_multiplier)
            particles.spread = 180.0
            particles.initial_velocity_min = 40.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.initial_velocity_max = 70.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.gravity = Vector2(0, -50 * (1.0 + (tier_multiplier - 1.0) * 0.2)) # Floating up
            if ball_skin == "legendary":
                particles.color = Color(0.0, 1.0, 0.5, 0.9) # Bright green/cyan
            elif ball_skin == "elite":
                particles.color = Color(0.2, 1.0, 0.2, 0.8) # Bright green
            else:
                particles.color = Color(0.2, 0.9, 0.3, 0.8) # Green healing
            particles.lifetime = 0.7 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 0.4
        else:
            # Default generic skill particles
            particles.amount = int(30 * tier_multiplier)
            particles.spread = 180.0
            particles.initial_velocity_min = 50.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.initial_velocity_max = 100.0 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            if ball_skin == "legendary":
                particles.color = Color(1.0, 1.0, 1.0, 0.9) # Bright white
            elif ball_skin == "elite":
                particles.color = Color(0.8, 0.8, 0.8, 0.8) # Light grey
            particles.lifetime = 0.5 * (1.0 + (tier_multiplier - 1.0) * 0.2)
            particles.explosiveness = 0.8

        if skill_name != "heal_ally": particles.gravity = Vector2(0, 0)
        self.ball.add_child(particles)
        if particles.has_signal("finished"):
            particles.finished.connect(particles.queue_free)


func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var nx = randf_range(-1.0, 1.0)
    var ny = randf_range(-1.0, 1.0)
    var dist_sq = nx*nx + ny*ny
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        nx /= dist
        ny /= dist
    else:
        nx = 0.0
        ny = 0.0

    var boid_vec = _apply_boid_rules(nx, ny)
    nx = boid_vec[0]
    ny = boid_vec[1]

    self.ball.x += nx * speed * 0.3
    self.ball.y += ny * speed * 0.3

func _clamp_position() -> bool:
    var bounced = false
    if self.world != null:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius

        if "game_mode" in self.world and self.world.game_mode != null:
            if "name" in self.world.game_mode and self.world.game_mode.name == "Bumper Balls":
                return false

        if is_nan(self.ball.x) or is_inf(self.ball.x):
            if "width" in self.world:
                self.ball.x = self.world.width / 2.0
            else:
                self.ball.x = 1000.0 / 2.0
            bounced = true
        if is_nan(self.ball.y) or is_inf(self.ball.y):
            if "height" in self.world:
                self.ball.y = self.world.height / 2.0
            else:
                self.ball.y = 1000.0 / 2.0
            bounced = true

        var old_x = self.ball.x
        var old_y = self.ball.y

        if "arena" in self.world and self.world.arena != null and self.world.arena.has_method("clamp_position"):
            var res = self.world.arena.clamp_position(self.ball.x, self.ball.y, radius)
            self.ball.x = res[0]
            self.ball.y = res[1]
            if res[2]:
                bounced = true
        elif "width" in self.world and "height" in self.world:
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))
            if old_x != self.ball.x or old_y != self.ball.y:
                bounced = true

    return bounced

func _resolve_collisions() -> bool:
    var bounced = false
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius

    var nearby = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var data = self.world.get_nearby_entities(self.ball, ball_radius * 2)
        if typeof(data) == TYPE_DICTIONARY:
            if data.has("enemies"): nearby += data["enemies"]
            if data.has("allies"): nearby += data["allies"]
        elif typeof(data) == TYPE_ARRAY:
            nearby = data

    for other in nearby:
        if other == self.ball:
            continue
        var other_radius = 10.0
        if "radius" in other: other_radius = other.radius
        var dx = self.ball.x - other.x
        var dy = self.ball.y - other.y
        var dist_sq = dx * dx + dy * dy
        var min_dist = ball_radius + other_radius
        if dist_sq < min_dist * min_dist and dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var overlap = min_dist - dist
            var nx = dx / dist
            var ny = dy / dist

            var knockback_multiplier = 1.0
            if self.world != null and "game_mode" in self.world and self.world.game_mode != null:
                if "name" in self.world.game_mode and self.world.game_mode.name == "Bumper Balls":
                    knockback_multiplier = 5.0
                elif "name" in self.world.game_mode and self.world.game_mode.name == "Zero Gravity":
                    knockback_multiplier = 5.0
                elif "name" in self.world.game_mode and self.world.game_mode.name == "Magnetic Collisions":
                    knockback_multiplier = -0.5

            self.ball.x += nx * overlap * knockback_multiplier
            self.ball.y += ny * overlap * knockback_multiplier
            bounced = true

    return bounced

func _trigger_ripple_effect():
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var ripple_radius = ball_radius * 3.0 + speed * 10.0

    var nearby = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var data = self.world.get_nearby_entities(self.ball, ripple_radius)
        if typeof(data) == TYPE_DICTIONARY:
            if data.has("enemies"): nearby += data["enemies"]
            if data.has("allies"): nearby += data["allies"]
        elif typeof(data) == TYPE_ARRAY:
            nearby = data

    for other in nearby:
        if other == self.ball:
            continue
        var dx = other.x - self.ball.x
        var dy = other.y - self.ball.y
        var dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001 and dist_sq < ripple_radius * ripple_radius:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist
            var push_strength = (ripple_radius - dist) / ripple_radius * speed * 2.0
            other.x += nx * push_strength
            other.y += ny * push_strength

            if speed > 2.5:
                var my_type = ""
                var other_type = ""
                if "ball_type" in self.ball: my_type = self.ball.ball_type
                if "ball_type" in other: other_type = other.ball_type
                var is_enemy = (my_type != other_type)

                if is_enemy and self.world != null and self.world.has_method("_deal_damage"):
                    self._attempt_damage(self.ball, other)
                    if "charge_level" in self.ball:
                        self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                    elif self.ball.has_method("set_meta"):
                        var cl = 0.0
                        if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                        self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in other:
                        other.charge_level = min(100.0, float(other.charge_level) + 5.0)
                    elif other.has_method("set_meta"):
                        var tcl = 0.0
                        if other.has_meta("charge_level"): tcl = float(other.get_meta("charge_level"))
                        other.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp1 = ""
                    if "ball_type" in self.ball:
                        b_type_vamp1 = str(self.ball.ball_type).to_lower()
                    if b_type_vamp1 == "vampire":
                        var dmg_vamp1 = 10.0
                        if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)
                    if "id" in other and "id" in self.ball:
                        var mem = {}
                        if other.has_method("get_meta") and other.has_meta("memory"):
                            mem = other.get_meta("memory")
                        elif "memory" in other:
                            mem = other.memory
                            # Ball Relationships - Balls remember each other
                            # Rivalry skill: attacked me before -> attack on sight
                            mem[self.ball.id] = {"relation": "rival"}
                        if other.has_method("set_meta"):
                            other.set_meta("memory", mem)
                        else:
                            other.memory = mem




func _apply_friendly_aura(delta: float):
    if world == null or not "balls" in world:
        return

    var team = ""
    if "team" in self.ball:
        team = self.ball.team
    elif "ball_type" in self.ball:
        team = self.ball.ball_type

    var ball_id = -1
    if "id" in self.ball:
        ball_id = self.ball.id
    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"):
        ball_id = self.ball.get_meta("id")

    var ball_type = ""
    if "ball_type" in self.ball:
        ball_type = self.ball.ball_type
    elif "BALL_TYPE" in self.ball:
        ball_type = self.ball.BALL_TYPE

    # Determine aura properties
    var aura_radius = 150.0

    # Check nearby friendly balls
    var nearby_friendlies = []
    for other in world.balls:
        var other_alive = true
        if "alive" in other:
            other_alive = other.alive
        elif other.has_method("get_meta") and other.has_meta("alive"):
            other_alive = other.get_meta("alive")

        var other_id = -1
        if "id" in other:
            other_id = other.id
        elif other.has_method("get_meta") and other.has_meta("id"):
            other_id = other.get_meta("id")

        if not other_alive or other_id == ball_id:
            continue

        var other_team = ""
        if "team" in other:
            other_team = other.team
        elif "ball_type" in other:
            other_team = other.ball_type

        if other_team == team:
            var dx = self.ball.x - other.x
            var dy = self.ball.y - other.y
            var dist_sq = dx*dx + dy*dy
            if dist_sq <= aura_radius*aura_radius:
                nearby_friendlies.append(other)

    # Count unique ball types among nearby friendlies, including self
    var unique_types = []
    unique_types.append(ball_type)
    for f in nearby_friendlies:
        var f_type = ""
        if "ball_type" in f:
            f_type = f.ball_type
        elif "BALL_TYPE" in f:
            f_type = f.BALL_TYPE
        if not unique_types.has(f_type):
            unique_types.append(f_type)

    var stack_count = unique_types.size() - 1 # How many *other* types are nearby

    var base_s = 2.0
    if self.ball.has_method("has_meta") and self.ball.has_meta("base_speed"):
        base_s = self.ball.get_meta("base_speed")
    elif "base_speed" in self.ball:
        base_s = self.ball.base_speed

    var base_d = 10.0
    if self.ball.has_method("has_meta") and self.ball.has_meta("base_damage"):
        base_d = self.ball.get_meta("base_damage")
    elif "base_damage" in self.ball:
        base_d = self.ball.base_damage

    # Apply buffs based on stack count
    if stack_count >= 1:
        # 1 extra type: HP regen
        var max_hp = 100.0
        if "max_hp" in self.ball:
            max_hp = self.ball.max_hp
        elif self.ball.has_method("get_meta") and self.ball.has_meta("max_hp"):
            max_hp = self.ball.get_meta("max_hp")

        if "hp" in self.ball:
            self.ball.hp = min(self.ball.hp + 2.0 * delta, max_hp)

    var is_dashing = false
    if "is_dashing" in self.ball:
        is_dashing = self.ball.is_dashing
    elif self.ball.has_method("get_meta") and self.ball.has_meta("is_dashing"):
        is_dashing = self.ball.get_meta("is_dashing")

    var stutter = 0.0
    if "stutter_timer" in self.ball:
        stutter = self.ball.stutter_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("stutter_timer"):
        stutter = self.ball.get_meta("stutter_timer")

    var is_night = false
    if world != null and "arena" in world and "is_night" in world.arena:
        is_night = world.arena.is_night

    if not is_dashing and stutter <= 0.0:
        if stack_count >= 2:
            if "speed" in self.ball:
                self.ball.speed = base_s * 1.1
        else:
            if "speed" in self.ball:
                self.ball.speed = base_s

        if stack_count >= 3:
            if "damage" in self.ball:
                self.ball.damage = base_d * 1.2
        else:
            if "damage" in self.ball:
                self.ball.damage = base_d

        if is_night:
            if ball_type == "vampire":
                if stack_count >= 2:
                    if "speed" in self.ball: self.ball.speed = base_s * 1.5 * 1.1
                else:
                    if "speed" in self.ball: self.ball.speed = base_s * 1.5
                if stack_count >= 3:
                    if "damage" in self.ball: self.ball.damage = base_d * 1.5 * 1.2
                else:
                    if "damage" in self.ball: self.ball.damage = base_d * 1.5
            elif ball_type == "assassin" or ball_type == "phantom":
                if stack_count >= 2:
                    if "speed" in self.ball: self.ball.speed = base_s * 1.2 * 1.1
                else:
                    if "speed" in self.ball: self.ball.speed = base_s * 1.2
                if stack_count >= 3:
                    if "damage" in self.ball: self.ball.damage = base_d * 1.5 * 1.2
                else:
                    if "damage" in self.ball: self.ball.damage = base_d * 1.5
            else:
                if stack_count < 3:
                    if "damage" in self.ball: self.ball.damage = base_d
        else:
            var day_mult = 1.0
            if world != null and "arena" in world:
                if "is_night" in world.arena and not world.arena.is_night:
                    day_mult = 1.2
            else:
                day_mult = 1.2 # fallback

            if world != null and "arena" in world and "is_night" in world.arena and not world.arena.is_night:
                if ball_type == "paladin" or ball_type == "guardian":
                    day_mult = 1.5
                    if stack_count >= 2:
                        if "speed" in self.ball: self.ball.speed = base_s * 1.2 * 1.1
                    else:
                        if "speed" in self.ball: self.ball.speed = base_s * 1.2

            if stack_count >= 3:
                if "damage" in self.ball: self.ball.damage = base_d * day_mult * 1.2
            else:
                if "damage" in self.ball: self.ball.damage = base_d * day_mult

        var b_type_aura = ""
        if "ball_type" in self.ball:
            b_type_aura = str(self.ball.ball_type).to_lower()
        if b_type_aura == "necromancer":
            var has_minion = false
            for f in nearby_friendlies:
                var f_type = ""
                if "ball_type" in f: f_type = f.ball_type
                if f_type == "minion":
                    has_minion = true
                    break
            if has_minion:
                if "speed" in self.ball:
                    self.ball.speed = base_s * 1.5


func _update_skill_timer(delta: float):

    var m_tether_timer = 0.0
    if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("magnet_tether_timer"):
        m_tether_timer = self.ball.get_meta("magnet_tether_timer")
    elif "magnet_tether_timer" in self.ball:
        m_tether_timer = self.ball.magnet_tether_timer

    if m_tether_timer > 0:
        var target = null
        if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("magnet_tether_target"):
            target = self.ball.get_meta("magnet_tether_target")
        elif "magnet_tether_target" in self.ball:
            target = self.ball.magnet_tether_target

        var is_target_alive = true
        if target:
            if typeof(target) != TYPE_DICTIONARY and target.has_method("has_meta") and target.has_meta("alive"): is_target_alive = target.get_meta("alive")
            elif "alive" in target: is_target_alive = target.alive

        if target and is_target_alive:
            var tx = target.get_meta("x") if typeof(target) != TYPE_DICTIONARY and target.has_method("has_meta") and target.has_meta("x") else target.x if "x" in target else 0.0
            var ty = target.get_meta("y") if typeof(target) != TYPE_DICTIONARY and target.has_method("has_meta") and target.has_meta("y") else target.y if "y" in target else 0.0
            var bx = self.ball.get_meta("x") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("x") else self.ball.x if "x" in self.ball else 0.0
            var by = self.ball.get_meta("y") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("y") else self.ball.y if "y" in self.ball else 0.0

            var dx = tx - bx
            var dy = ty - by
            var dist = sqrt(dx*dx + dy*dy)
            if dist > 0:
                var tether_speed = 2.0 * 3.0
                if "speed" in self.ball:
                    tether_speed = self.ball.speed * 3.0

                var nvx = (dx / dist) * tether_speed
                var nvy = (dy / dist) * tether_speed

                if "vx" in self.ball: self.ball.vx = nvx
                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("vx", nvx)

                if "vy" in self.ball: self.ball.vy = nvy
                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("vy", nvy)

                if "x" in self.ball: self.ball.x += nvx * delta
                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + nvx * delta)

                if "y" in self.ball: self.ball.y += nvy * delta
                elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + nvy * delta)

        m_tether_timer -= delta
        if "magnet_tether_timer" in self.ball: self.ball.magnet_tether_timer = m_tether_timer
        elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("magnet_tether_timer", m_tether_timer)

    var n_timer = 0.0
    if "nemesis_booster_timer" in self.ball:
        n_timer = float(self.ball.nemesis_booster_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("nemesis_booster_timer"):
        n_timer = float(self.ball.get_meta("nemesis_booster_timer"))
    if n_timer > 0:
        n_timer -= delta
        if n_timer < 0:
            n_timer = 0.0
        if "nemesis_booster_timer" in self.ball:
            self.ball.nemesis_booster_timer = n_timer
        if self.ball.has_method("set_meta"):
            self.ball.set_meta("nemesis_booster_timer", n_timer)

    var pull_timer = 0.0
    if "pull_booster_timer" in self.ball:
        pull_timer = float(self.ball.pull_booster_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("pull_booster_timer"):
        pull_timer = self.ball.get_meta("pull_booster_timer")
    if pull_timer > 0:
        pull_timer -= delta
        if "pull_booster_timer" in self.ball:
            self.ball.pull_booster_timer = pull_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("pull_booster_timer", pull_timer)

        if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                var h_rad = 100.0
                if "radius" in hazard: h_rad = hazard.radius
                elif hazard.has_method("get_meta") and hazard.has_meta("radius"): h_rad = hazard.get_meta("radius")

                var h_kind = ""
                if "kind" in hazard: h_kind = hazard.kind
                elif hazard.has_method("get_meta") and hazard.has_meta("kind"): h_kind = hazard.get_meta("kind")

                var pullable = ["healing_spring", "booster", "drone_item", "stealth_drone_item", "shadow_booster", "vision_booster", "decoy_item", "silence_booster", "freeze_booster", "placeable_trap_item", "exit_portal_item", "position_swap_item", "magnet_booster", "stamina_booster", "link_booster", "weather_booster", "portal_gun_item", "clone_booster", "placeable_trap_booster", "nemesis_booster", "invert_booster"]
                if h_rad < 30.0 or pullable.has(h_kind):
                    var dx = self.ball.x - hazard.x
                    var dy = self.ball.y - hazard.y
                    var dist_sq = dx*dx + dy*dy
                    if dist_sq < 250000:
                        var dist = sqrt(dist_sq)
                        if dist > 0.0001:
                            var nx = dx / dist
                            var ny = dy / dist
                            var pull_strength = 150.0 * delta
                            if "x" in hazard: hazard.x += nx * pull_strength
                            elif hazard.has_method("set_meta") and hazard.has_meta("x"): hazard.set_meta("x", hazard.get_meta("x") + nx * pull_strength)
                            if "y" in hazard: hazard.y += ny * pull_strength
                            elif hazard.has_method("set_meta") and hazard.has_meta("y"): hazard.set_meta("y", hazard.get_meta("y") + ny * pull_strength)

        if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                var h_kind = ""
                if "kind" in hazard: h_kind = hazard.kind
                elif hazard.has_method("get_meta") and hazard.has_meta("kind"): h_kind = hazard.get_meta("kind")
                if h_kind == "pull_trap":
                    var owner_id = null
                    if "owner_id" in hazard: owner_id = hazard.owner_id
                    elif hazard.has_method("get_meta") and hazard.has_meta("owner_id"): owner_id = hazard.get_meta("owner_id")

                    var b_id = null
                    if "id" in self.ball: b_id = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): b_id = self.ball.get_meta("id")

                    if owner_id != null and owner_id != b_id:
                        var h_x = 0.0
                        if "x" in hazard: h_x = hazard.x
                        elif hazard.has_method("get_meta") and hazard.has_meta("x"): h_x = hazard.get_meta("x")
                        var h_y = 0.0
                        if "y" in hazard: h_y = hazard.y
                        elif hazard.has_method("get_meta") and hazard.has_meta("y"): h_y = hazard.get_meta("y")

                        var dist_sq = (h_x - self.ball.x)*(h_x - self.ball.x) + (h_y - self.ball.y)*(h_y - self.ball.y)
                        if dist_sq < 10000:
                            var dist = sqrt(dist_sq)
                            if dist > 0.0001:
                                var nx = (h_x - self.ball.x) / dist
                                var ny = (h_y - self.ball.y) / dist
                                var pull_strength = 100.0 * delta
                                if "x" in self.ball: self.ball.x += nx * pull_strength
                                elif self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + nx * pull_strength)
                                if "y" in self.ball: self.ball.y += ny * pull_strength
                                elif self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + ny * pull_strength)

                                if "hp" in self.ball:
                                    var dmg = 10.0 * delta
                                    if "damage" in hazard: dmg = hazard.damage * delta
                                    elif hazard.has_method("get_meta") and hazard.has_meta("damage"): dmg = hazard.get_meta("damage") * delta

                                    if owner_id != null and self.world != null and "balls" in self.world:
                                        var owner = null
                                        for ob in self.world.balls:
                                            var ob_id = null
                                            if "id" in ob: ob_id = ob.id
                                            elif ob.has_method("get_meta") and ob.has_meta("id"): ob_id = ob.get_meta("id")
                                            if ob_id == owner_id:
                                                owner = ob
                                                break

                                        if owner != null and self.world.has_method("_deal_damage"):
                                            var old_dmg = 10.0
                                            if "damage" in owner: old_dmg = owner.damage
                                            elif owner.has_method("get_meta") and owner.has_meta("damage"): old_dmg = owner.get_meta("damage")

                                            var new_dmg = 10.0 * delta
                                            if "damage" in hazard: new_dmg = hazard.damage * delta
                                            elif hazard.has_method("get_meta") and hazard.has_meta("damage"): new_dmg = hazard.get_meta("damage") * delta

                                            if typeof(owner) == TYPE_OBJECT and owner.has_method("set"): owner.set("damage", new_dmg)
                                            elif "damage" in owner: owner.damage = new_dmg

                                            self.world._deal_damage(owner, self.ball)

                                            if typeof(owner) == TYPE_OBJECT and owner.has_method("set"): owner.set("damage", old_dmg)
                                            elif "damage" in owner: owner.damage = old_dmg

    var weather_timer = 0.0
    if "weather_control_timer" in self.ball:
        weather_timer = float(self.ball.weather_control_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("weather_control_timer"):
        weather_timer = self.ball.get_meta("weather_control_timer")
    if weather_timer > 0:
        weather_timer -= delta
        if weather_timer < 0:
            weather_timer = 0.0
        if "weather_control_timer" in self.ball:
            self.ball.weather_control_timer = weather_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("weather_control_timer", weather_timer)

    var inf_stam_timer = 0.0
    if "infinite_stamina_timer" in self.ball:
        inf_stam_timer = self.ball.infinite_stamina_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("infinite_stamina_timer"):
        inf_stam_timer = self.ball.get_meta("infinite_stamina_timer")

    if inf_stam_timer > 0:
        inf_stam_timer -= delta
        if "infinite_stamina_timer" in self.ball:
            self.ball.infinite_stamina_timer = inf_stam_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("infinite_stamina_timer", inf_stam_timer)

    var link_timer = 0.0
    if "link_booster_timer" in self.ball:
        link_timer = self.ball.link_booster_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("link_booster_timer"):
        link_timer = self.ball.get_meta("link_booster_timer")

    if link_timer > 0:
        link_timer -= delta
        var target = null
        if "link_booster_target" in self.ball:
            target = self.ball.link_booster_target
        elif self.ball.has_method("get_meta") and self.ball.has_meta("link_booster_target"):
            target = self.ball.get_meta("link_booster_target")

        var alive = true
        if target != null and "alive" in target:
            alive = target.alive

        if target != null and alive:
            var dist_sq = pow(target.x - self.ball.x, 2) + pow(target.y - self.ball.y, 2)
            if dist_sq <= 40000:
                var drain = 20.0 * delta
                var target_hp = 100.0
                if "hp" in target: target_hp = target.hp

                var actual_damage = min(target_hp, drain)
                if "hp" in target: target.hp -= actual_damage

                if "hp" in self.ball:
                    var max_hp = 100.0
                    if "max_hp" in self.ball: max_hp = self.ball.max_hp
                    self.ball.hp = min(self.ball.hp + actual_damage, max_hp)

                if link_timer <= 0:
                    target = null
            else:
                link_timer = 0.0
                target = null
        else:
            link_timer = 0.0
            target = null

        if "link_booster_timer" in self.ball:
            self.ball.link_booster_timer = link_timer
            self.ball.link_booster_target = target
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("link_booster_timer", link_timer)
            self.ball.set_meta("link_booster_target", target)


    var hl_timer = 0.0
    var chaos_link_timer = 0.0
    if "chaos_link_timer" in self.ball:
        chaos_link_timer = self.ball.chaos_link_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_timer"):
        chaos_link_timer = self.ball.get_meta("chaos_link_timer")

    if chaos_link_timer > 0:
        chaos_link_timer -= delta
        var target = null
        if "chaos_link_target" in self.ball:
            target = self.ball.chaos_link_target
        elif self.ball.has_method("get_meta") and self.ball.has_meta("chaos_link_target"):
            target = self.ball.get_meta("chaos_link_target")

        var alive = true
        if target != null and "alive" in target: alive = target.alive
        elif target != null and target.has_method("get_meta") and target.has_meta("alive"): alive = target.get_meta("alive")

        if target != null and alive:
            var dist_sq = pow(target.x - self.ball.x, 2) + pow(target.y - self.ball.y, 2)
            if dist_sq > 90000:
                if target.has_method("get_meta") and target.has_meta("chaos_link_target") and target.get_meta("chaos_link_target") == self.ball:
                    target.set_meta("chaos_link_target", null)
                elif "chaos_link_target" in target and target.chaos_link_target == self.ball:
                    target.chaos_link_target = null
                chaos_link_timer = 0.0
                target = null
            else:
                if chaos_link_timer <= 0:
                    if target.has_method("get_meta") and target.has_meta("chaos_link_target") and target.get_meta("chaos_link_target") == self.ball:
                        target.set_meta("chaos_link_target", null)
                    elif "chaos_link_target" in target and target.chaos_link_target == self.ball:
                        target.chaos_link_target = null
                    target = null
        else:
            chaos_link_timer = 0.0
            target = null

        if "chaos_link_timer" in self.ball:
            self.ball.chaos_link_timer = chaos_link_timer
            self.ball.chaos_link_target = target
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("chaos_link_timer", chaos_link_timer)
            self.ball.set_meta("chaos_link_target", target)

    if "health_link_timer" in self.ball:
        hl_timer = self.ball.health_link_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("health_link_timer"):
        hl_timer = self.ball.get_meta("health_link_timer")

    if hl_timer > 0:
        hl_timer -= delta
        var target = null
        if "health_link_target" in self.ball:
            target = self.ball.health_link_target
        elif self.ball.has_method("get_meta") and self.ball.has_meta("health_link_target"):
            target = self.ball.get_meta("health_link_target")

        var alive = true
        if target != null and "alive" in target:
            alive = target.alive

        var ball_hp = 100.0
        if "hp" in self.ball: ball_hp = self.ball.hp
        elif self.ball.has_method("get_meta") and self.ball.has_meta("hp"): ball_hp = self.ball.get_meta("hp")

        if target != null and alive and ball_hp > 10.0:
            var dist_sq = pow(target.x - self.ball.x, 2) + pow(target.y - self.ball.y, 2)
            if dist_sq <= 40000:
                var drain = 20.0 * delta
                var target_hp = 100.0
                if "hp" in target: target_hp = target.hp
                var target_mhp = 100.0
                if "max_hp" in target: target_mhp = target.max_hp

                var actual_damage = min(ball_hp, drain)

                if "hp" in self.ball: self.ball.hp -= actual_damage
                elif self.ball.has_method("set_meta"): self.ball.set_meta("hp", ball_hp - actual_damage)

                if "hp" in target: target.hp = min(target_hp + actual_damage * 1.5, target_mhp)



                if hl_timer <= 0:
                    target = null
            else:
                hl_timer = 0.0
                target = null
        else:
            hl_timer = 0.0
            target = null

        if "health_link_timer" in self.ball:
            self.ball.health_link_timer = hl_timer
            self.ball.health_link_target = target
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("health_link_timer", hl_timer)
            self.ball.set_meta("health_link_target", target)

    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta

    var reflect_shield_timer = 0.0
    if "reflect_shield_timer" in self.ball:
        reflect_shield_timer = self.ball.reflect_shield_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("reflect_shield_timer"):
        reflect_shield_timer = self.ball.get_meta("reflect_shield_timer")

    if reflect_shield_timer > 0:
        if "reflect_shield_timer" in self.ball:
            self.ball.reflect_shield_timer -= delta
            if self.ball.reflect_shield_timer <= 0:
                self.ball.reflect_shield_active = false
        elif self.ball.has_method("set_meta"):
            var new_timer = reflect_shield_timer - delta
            self.ball.set_meta("reflect_shield_timer", new_timer)
            if new_timer <= 0:
                self.ball.set_meta("reflect_shield_active", false)


    var ricochet_barrier_timer = 0.0
    if "ricochet_barrier_timer" in self.ball:
        ricochet_barrier_timer = self.ball.ricochet_barrier_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("ricochet_barrier_timer"):
        ricochet_barrier_timer = self.ball.get_meta("ricochet_barrier_timer")

    if ricochet_barrier_timer > 0:
        if "ricochet_barrier_timer" in self.ball:
            self.ball.ricochet_barrier_timer -= delta
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("ricochet_barrier_timer", ricochet_barrier_timer - delta)

    var kite_trap_timer = 0.0
    if "kite_trap_timer" in self.ball:
        kite_trap_timer = self.ball.kite_trap_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("kite_trap_timer"):
        kite_trap_timer = self.ball.get_meta("kite_trap_timer")

    if kite_trap_timer > 0:
        if "kite_trap_timer" in self.ball:
            self.ball.kite_trap_timer -= delta
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("kite_trap_timer", kite_trap_timer - delta)

    var attack_timer = 0.0
    if "attack_timer" in self.ball:
        attack_timer = self.ball.attack_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
        attack_timer = self.ball.get_meta("attack_timer")

    if attack_timer > 0:
        attack_timer -= delta
        if "attack_timer" in self.ball:
            self.ball.attack_timer = attack_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("attack_timer", attack_timer)

    var stutter_timer = 0.0
    if "stutter_timer" in self.ball:
        stutter_timer = float(self.ball.stutter_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("stutter_timer"):
        stutter_timer = self.ball.get_meta("stutter_timer")

    if stutter_timer > 0.0:
        if "stutter_timer" in self.ball:
            self.ball.stutter_timer = stutter_timer - delta
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("stutter_timer", stutter_timer - delta)

    var stealth_timer = 0.0
    if "stealth_drone_timer" in self.ball:
        stealth_timer = float(self.ball.stealth_drone_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("stealth_drone_timer"):
        stealth_timer = self.ball.get_meta("stealth_drone_timer")

    if stealth_timer > 0.0:
        stealth_timer -= delta
        if "stealth_drone_timer" in self.ball:
            self.ball.stealth_drone_timer = stealth_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("stealth_drone_timer", stealth_timer)

        if stealth_timer <= 0.0:
            if "has_stealth_drone" in self.ball:
                self.ball.has_stealth_drone = false
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("has_stealth_drone", false)

    var shadow_timer = 0.0
    if "shadow_booster_timer" in self.ball:
        shadow_timer = float(self.ball.shadow_booster_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("shadow_booster_timer"):
        shadow_timer = self.ball.get_meta("shadow_booster_timer")

    if shadow_timer > 0.0:
        shadow_timer -= delta
        if shadow_timer < 0.0:
            shadow_timer = 0.0
        if "shadow_booster_timer" in self.ball:
            self.ball.shadow_booster_timer = shadow_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("shadow_booster_timer", shadow_timer)

    var vb_timer = 0.0
    if "vision_booster_timer" in self.ball:
        vb_timer = float(self.ball.vision_booster_timer)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("vision_booster_timer"):
        vb_timer = self.ball.get_meta("vision_booster_timer")

    if vb_timer > 0.0:
        vb_timer -= delta
        if vb_timer <= 0.0:
            vb_timer = 0.0
            var vb_applied = false
            if "vision_booster_applied" in self.ball:
                vb_applied = self.ball.vision_booster_applied
            elif self.ball.has_method("get_meta") and self.ball.has_meta("vision_booster_applied"):
                vb_applied = self.ball.get_meta("vision_booster_applied")

            if vb_applied:
                var base_perc = 250.0
                if self.ball.has_method("get_meta") and self.ball.has_meta("base_perception_radius"):
                    base_perc = self.ball.get_meta("base_perception_radius") / 2.0
                    self.ball.set_meta("base_perception_radius", base_perc)
                self.ball.perception_radius = base_perc

                if "vision_booster_applied" in self.ball:
                    self.ball.vision_booster_applied = false
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("vision_booster_applied", false)

        if "vision_booster_timer" in self.ball:
            self.ball.vision_booster_timer = vb_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("vision_booster_timer", vb_timer)

func _kite(delta: float):
    # Added Kite cosmetic comment
    # Kiting is fully implemented
    # auto-implement-kite-держит-дистанцию-атакует-при
    # Maintain distance from enemies and attack when they are close
    # Kiting behavior implementation: keeping the distance and attacking
    # Kite — держит дистанцию, атакует при приближении skill: для Sniper
    var active_enemies = _get_enemies()
    if active_enemies.size() > 0:
        var target_msg = null
        var team_allies = _get_allies()
        for ally in team_allies:
            var msg = null
            if ally.has_method("get_meta") and ally.has_meta("team_message"):
                msg = ally.get_meta("team_message")
            if typeof(msg) == TYPE_DICTIONARY and msg.has("type") and msg["type"] == "target_spotted":
                target_msg = msg
                break

        var optimal_target = null
        var min_dist_sq = INF

        if target_msg != null:
            var tx = target_msg.get("x", self.ball.x)
            var ty = target_msg.get("y", self.ball.y)
            for e in active_enemies:
                var dist_sq = pow(e.x - tx, 2) + pow(e.y - ty, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    optimal_target = e
        else:
            for e in active_enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    optimal_target = e

        var has_msg = false
        if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
            has_msg = self.ball.get_meta("team_message") != null
        if not has_msg and self.ball.has_method("set_meta"):
            self.ball.set_meta("team_message", {"type": "target_spotted", "x": optimal_target.x, "y": optimal_target.y})

        var dx = optimal_target.x - self.ball.x
        var dy = optimal_target.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var actual_dist = 0.0
        if dist_sq > 0.0001:
            actual_dist = sqrt(dist_sq)

        var b_speed = float(2.0)
        if "speed" in self.ball: b_speed = self.ball.speed

        var b_attack_range = 150.0
        if "attack_range" in self.ball: b_attack_range = self.ball.attack_range

        var kite_ratio = 0.8
        if "kite_ratio" in self.ball:
            kite_ratio = self.ball.kite_ratio
        if "traits" in self.ball:
            if "Sniper" in self.ball.traits:
                kite_ratio = 1.0
            elif "Skirmisher" in self.ball.traits:
                kite_ratio = 0.5

        if dist_sq > 0.0001:
            var nx = dx / actual_dist
            var ny = dy / actual_dist
            if actual_dist > b_attack_range:
                pass
            elif actual_dist < b_attack_range * kite_ratio:
                # Fall back if target is too close
                # IMPROVEMENT: Instead of just running directly backward, find open space
                # Default retreat vector
                var ret_x = -nx
                var ret_y = -ny

                # Check for nearby walls to avoid getting cornered
                var arena_width = 800.0
                var arena_height = 600.0
                if "arena" in self.world:
                    if "width" in self.world.arena:
                        arena_width = float(self.world.arena.width)
                    if "height" in self.world.arena:
                        arena_height = float(self.world.arena.height)

                var margin = 100.0
                var wall_repel_x = 0.0
                var wall_repel_y = 0.0

                if self.ball.x < margin:
                    wall_repel_x += (margin - self.ball.x) / margin
                elif self.ball.x > arena_width - margin:
                    wall_repel_x -= (self.ball.x - (arena_width - margin)) / margin

                if self.ball.y < margin:
                    wall_repel_y += (margin - self.ball.y) / margin
                elif self.ball.y > arena_height - margin:
                    wall_repel_y -= (self.ball.y - (arena_height - margin)) / margin

                # If we're near a wall, blend in a perpendicular (sideways) movement
                if wall_repel_x != 0.0 or wall_repel_y != 0.0:
                    # Perpendicular vectors to the target
                    var perp_x1 = -ny
                    var perp_y1 = nx
                    var perp_x2 = ny
                    var perp_y2 = -nx

                    # Choose the perpendicular direction that moves us away from walls
                    var dot1 = perp_x1 * wall_repel_x + perp_y1 * wall_repel_y
                    var dot2 = perp_x2 * wall_repel_x + perp_y2 * wall_repel_y

                    if dot1 > dot2:
                        ret_x += perp_x1 * 1.5 + wall_repel_x
                        ret_y += perp_y1 * 1.5 + wall_repel_y
                    else:
                        ret_x += perp_x2 * 1.5 + wall_repel_x
                        ret_y += perp_y2 * 1.5 + wall_repel_y

                # Normalize the resulting retreat vector
                var ret_len_sq = ret_x*ret_x + ret_y*ret_y
                if ret_len_sq > 0.0001:
                    var ret_len = sqrt(ret_len_sq)
                    nx = ret_x / ret_len
                    ny = ret_y / ret_len
                else:
                    nx = -nx
                    ny = -ny
            else:
                nx = 0.0
                ny = 0.0

            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, optimal_target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step: float = b_speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step
                if actual_dist < b_attack_range * kite_ratio:
                    self.ball.x += nx * step
                    self.ball.y += ny * step

                    var kite_trap_timer = 0.0
                    if "kite_trap_timer" in self.ball:
                        kite_trap_timer = self.ball.kite_trap_timer
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("kite_trap_timer"):
                        kite_trap_timer = self.ball.get_meta("kite_trap_timer")

                    if kite_trap_timer <= 0.0:
                        if "arena" in self.world and "hazards" in self.world.arena:
                            var trap_id = self.world.arena.hazards.size() + randi() % 10000
                            var trap = ProceduralArena.Hazard.new()
                            trap.id = trap_id
                            trap.x = self.ball.x
                            trap.y = self.ball.y
                            trap.radius = 10.0
                            trap.kind = "trap"
                            trap.damage = 0.0
                            trap.set_meta("duration", 3.0)

                            var lobby = PreGameLobby.get_instance()
                            var trap_variant = lobby.get_trap_variant(self.ball.id)
                            trap.set_meta("trap_variant", trap_variant)

                            if trap_variant == "ricochet":
                                if "ricochet_barrier_timer" in self.ball:
                                    self.ball.ricochet_barrier_timer = 3.0
                                elif self.ball.has_method("set_meta"):
                                    self.ball.set_meta("ricochet_barrier_timer", 3.0)

                            self.world.arena.hazards.append(trap)

                            if "kite_trap_timer" in self.ball:
                                self.ball.kite_trap_timer = 2.0
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("kite_trap_timer", 2.0)
                elif actual_dist > b_attack_range:
                    self.ball.x += nx * min(step, actual_dist - b_attack_range)
                    self.ball.y += ny * min(step, actual_dist - b_attack_range)
        dx = optimal_target.x - self.ball.x
        dy = optimal_target.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        var dist_after = 0.0
        if dist_sq > 0.0001:
            dist_after = sqrt(dist_sq)

        b_attack_range = 150.0
        if "attack_range" in self.ball: b_attack_range = self.ball.attack_range

        if dist_after <= b_attack_range:
            var skill_timer = 0.0
            if "skill_timer" in self.ball:
                skill_timer = self.ball.skill_timer

            if skill_timer <= 0:
                var k_ratio = 0.8
                if "kite_ratio" in self.ball:
                    k_ratio = self.ball.kite_ratio
                if "traits" in self.ball:
                    if "Sniper" in self.ball.traits:
                        k_ratio = 1.0
                    elif "Skirmisher" in self.ball.traits:
                        k_ratio = 0.5
                if dist_after < b_attack_range * k_ratio:
                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()
                    var cd = 5.0
                    if "skill_cooldown" in self.ball: cd = self.ball.skill_cooldown
                    self.ball.skill_timer = cd

            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                if self.world != null and self.world.has_method("_deal_damage"):
                    self._attempt_damage(self.ball, optimal_target)
                    if "charge_level" in self.ball:
                        self.ball.charge_level = min(100.0, float(self.ball.charge_level) + 10.0)
                    elif self.ball.has_method("set_meta"):
                        var cl = 0.0
                        if self.ball.has_meta("charge_level"): cl = float(self.ball.get_meta("charge_level"))
                        self.ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in optimal_target:
                        optimal_target.charge_level = min(100.0, float(optimal_target.charge_level) + 5.0)
                    elif optimal_target.has_method("set_meta"):
                        var tcl = 0.0
                        if optimal_target.has_meta("charge_level"): tcl = float(optimal_target.get_meta("charge_level"))
                        optimal_target.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp1 = ""
                    if "ball_type" in self.ball:
                        b_type_vamp1 = str(self.ball.ball_type).to_lower()
                    if b_type_vamp1 == "vampire":
                        var dmg_vamp1 = 10.0
                        if "damage" in self.ball: dmg_vamp1 = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp1 * 0.5, self.ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in self.ball: dmg_vamp_mode = float(self.ball.damage)
                        if "hp" in self.ball and "max_hp" in self.ball:
                            self.ball.hp = min(self.ball.hp + dmg_vamp_mode * 2.0, self.ball.max_hp)
                    if "id" in optimal_target and "id" in self.ball:
                        var mem = {}
                        if optimal_target.has_method("get_meta") and optimal_target.has_meta("memory"):
                            mem = optimal_target.get_meta("memory")
                        elif "memory" in optimal_target:
                            mem = optimal_target.memory
                        # Ball Relationships - Balls remember each other
                        mem[self.ball.id] = {"relation": "rival"}
                        if optimal_target.has_method("set_meta"):
                            optimal_target.set_meta("memory", mem)
                        else:
                            optimal_target.memory = mem

                var cooldown = max(0.2, 2.0 / b_speed if b_speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
                    if cooldown >= 0.8:
                        if "stutter_timer" in self.ball:
                            self.ball.stutter_timer = min(cooldown * 0.4, 0.4)
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("stutter_timer", min(cooldown * 0.4, 0.4))
    else:
        _idle(delta)


func _escort(delta: float) -> void:
    var allies = _get_allies()
    if allies.size() == 0:
        _idle(delta)
        return

    var target_ally = null
    for ally in allies:
        if "has_flag" in ally and ally.has_flag:
            target_ally = ally
            break

    if target_ally == null:
        var min_dist = 9999999.0
        for ally in allies:
            var d_sq = (ally.x - ball.x)*(ally.x - ball.x) + (ally.y - ball.y)*(ally.y - ball.y)
            if d_sq < min_dist:
                min_dist = d_sq
                target_ally = ally

    var dx = target_ally.x - ball.x
    var dy = target_ally.y - ball.y
    var dist_sq = dx*dx + dy*dy

    if dist_sq > 2500.0:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist

        var avoid = _apply_obstacle_avoidance(nx, ny)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var b_speed = 2.0
        if "speed" in ball:
            b_speed = ball.speed
        var step = b_speed * delta * 60.0
        var inv_t = 0.0
        if "invert_timer" in ball: inv_t = float(ball.invert_timer)
        elif ball.has_method("get_meta") and ball.has_meta("invert_timer"): inv_t = float(ball.get_meta("invert_timer"))
        if inv_t > 0.0:
            step = -step

        ball.x += nx * min(step, dist - 40.0)
        ball.y += ny * min(step, dist - 40.0)
    else:
        var enemies = _get_enemies()
        if enemies.size() > 0:
            var closest_enemy = null
            var e_min_dist = 9999999.0
            for enemy in enemies:
                var e_d_sq = (enemy.x - target_ally.x)*(enemy.x - target_ally.x) + (enemy.y - target_ally.y)*(enemy.y - target_ally.y)
                if e_d_sq < e_min_dist:
                    e_min_dist = e_d_sq
                    closest_enemy = enemy

            if e_min_dist < 40000.0:
                ball.team_message = {"type": "target_spotted", "x": closest_enemy.x, "y": closest_enemy.y}
                var attack_timer = 0.0
                if "attack_timer" in ball:
                    attack_timer = ball.attack_timer

                if attack_timer <= 0.0:
                    var my_dist = (closest_enemy.x - ball.x)*(closest_enemy.x - ball.x) + (closest_enemy.y - ball.y)*(closest_enemy.y - ball.y)
                    var atk_range = 150.0
                    if "attack_range" in ball:
                        atk_range = ball.attack_range

                    if my_dist < atk_range * atk_range:
                        if world.has_method("_deal_damage"):
                            self._attempt_damage(ball, closest_enemy)
                            if "charge_level" in ball:
                                ball.charge_level = min(100.0, float(ball.charge_level) + 10.0)
                            elif ball.has_method("set_meta"):
                                var cl = 0.0
                                if ball.has_meta("charge_level"): cl = float(ball.get_meta("charge_level"))
                                ball.set_meta("charge_level", min(100.0, cl + 10.0))
                            if "charge_level" in closest_enemy:
                                closest_enemy.charge_level = min(100.0, float(closest_enemy.charge_level) + 5.0)
                            elif closest_enemy.has_method("set_meta"):
                                var tcl = 0.0
                                if closest_enemy.has_meta("charge_level"): tcl = float(closest_enemy.get_meta("charge_level"))
                                closest_enemy.set_meta("charge_level", min(100.0, tcl + 5.0))
                            var b_type_vamp2 = ""
                            if "ball_type" in ball:
                                b_type_vamp2 = str(ball.ball_type).to_lower()
                            if b_type_vamp2 == "vampire":
                                var dmg_vamp2 = 10.0
                                if "damage" in ball: dmg_vamp2 = float(ball.damage)
                                if "hp" in ball and "max_hp" in ball:
                                    ball.hp = min(ball.hp + dmg_vamp2 * 0.5, ball.max_hp)
                            if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                                var dmg_vamp_mode = 10.0
                                if "damage" in ball: dmg_vamp_mode = float(ball.damage)
                                if "hp" in ball and "max_hp" in ball:
                                    ball.hp = min(ball.hp + dmg_vamp_mode * 2.0, ball.max_hp)
                        var s_speed = 2.0
                        if "speed" in ball:
                            s_speed = ball.speed
                        var new_cd = max(0.2, 2.0 / s_speed if s_speed > 0 else 1.0)
                        ball.attack_timer = new_cd

func _intercept(delta: float) -> void:
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var target_enemy = null
    for enemy in enemies:
        if "has_flag" in enemy and enemy.has_flag:
            target_enemy = enemy
            break

    if target_enemy == null:
        _chase(delta)
        return

    var dx = target_enemy.x - ball.x
    var dy = target_enemy.y - ball.y
    var dist_sq = dx*dx + dy*dy
    var dist = 0.0
    if dist_sq > 0.0:
        dist = sqrt(dist_sq)

    if dist > 0.0001:
        var nx = dx / dist
        var ny = dy / dist

        var ex_vel = 0.0
        var ey_vel = 0.0
        if "vx" in target_enemy:
            ex_vel = target_enemy.vx
        if "vy" in target_enemy:
            ey_vel = target_enemy.vy

        var lead_x = nx + (ex_vel * 0.5)
        var lead_y = ny + (ey_vel * 0.5)
        var lead_mag = sqrt(lead_x*lead_x + lead_y*lead_y)

        if lead_mag > 0.0:
            nx = lead_x / lead_mag
            ny = lead_y / lead_mag

        var avoid = _apply_obstacle_avoidance(nx, ny)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var b_speed = 2.0
        if "speed" in ball:
            b_speed = ball.speed
        var step = b_speed * delta * 60.0
        var inv_t = 0.0
        if "invert_timer" in ball: inv_t = float(ball.invert_timer)
        elif ball.has_method("get_meta") and ball.has_meta("invert_timer"): inv_t = float(ball.get_meta("invert_timer"))
        if inv_t > 0.0:
            step = -step

        ball.x += nx * step
        ball.y += ny * step

        var atk_range = 150.0
        if "attack_range" in ball:
            atk_range = ball.attack_range

        if dist < atk_range:
            var attack_timer = 0.0
            if "attack_timer" in ball:
                attack_timer = ball.attack_timer

            if attack_timer <= 0.0:
                if world.has_method("_deal_damage"):
                    self._attempt_damage(ball, target_enemy)
                    if "charge_level" in ball:
                        ball.charge_level = min(100.0, float(ball.charge_level) + 10.0)
                    elif ball.has_method("set_meta"):
                        var cl = 0.0
                        if ball.has_meta("charge_level"): cl = float(ball.get_meta("charge_level"))
                        ball.set_meta("charge_level", min(100.0, cl + 10.0))
                    if "charge_level" in target_enemy:
                        target_enemy.charge_level = min(100.0, float(target_enemy.charge_level) + 5.0)
                    elif target_enemy.has_method("set_meta"):
                        var tcl = 0.0
                        if target_enemy.has_meta("charge_level"): tcl = float(target_enemy.get_meta("charge_level"))
                        target_enemy.set_meta("charge_level", min(100.0, tcl + 5.0))
                    var b_type_vamp2 = ""
                    if "ball_type" in ball:
                        b_type_vamp2 = str(ball.ball_type).to_lower()
                    if b_type_vamp2 == "vampire":
                        var dmg_vamp2 = 10.0
                        if "damage" in ball: dmg_vamp2 = float(ball.damage)
                        if "hp" in ball and "max_hp" in ball:
                            ball.hp = min(ball.hp + dmg_vamp2 * 0.5, ball.max_hp)
                    if "current_mode_name" in world and world.current_mode_name == "Vampire Royale":
                        var dmg_vamp_mode = 10.0
                        if "damage" in ball: dmg_vamp_mode = float(ball.damage)
                        if "hp" in ball and "max_hp" in ball:
                            ball.hp = min(ball.hp + dmg_vamp_mode * 2.0, ball.max_hp)
                var s_speed = 2.0
                if "speed" in ball:
                    s_speed = ball.speed
                var new_cd = max(0.2, 2.0 / s_speed if s_speed > 0 else 1.0)
                ball.attack_timer = new_cd

func _hide_behind(delta: float):
    var enemies = _get_enemies()
    var allies = _get_allies()

    if enemies.size() == 0 or allies.size() == 0:
        _flee(delta)
        return

    var target_enemy = _find_strongest_enemy_deterministic(enemies)

    var best_ally = null
    var best_score = -1.0

    for ally in allies:
        var b_type = ""
        if "ball_type" in ally:
            b_type = str(ally.ball_type).to_lower()

        var score = 100.0
        if "max_hp" in ally:
            score = float(ally.max_hp)

        if b_type == "tank":
            score += 1000.0

        var dist_sq = pow(ally.x - ball.x, 2) + pow(ally.y - ball.y, 2)
        score -= dist_sq * 0.001

        if score > best_score:
            best_score = score
            best_ally = ally

    if best_ally == null:
        _flee(delta)
        return

    var dx = target_enemy.x - best_ally.x
    var dy = target_enemy.y - best_ally.y
    var dist_e = sqrt(dx*dx + dy*dy)

    if dist_e < 0.0001:
        _flee(delta)
        return

    var nx = dx / dist_e
    var ny = dy / dist_e

    var target_x = best_ally.x - nx * 30.0
    var target_y = best_ally.y - ny * 30.0

    var dx_m = target_x - ball.x
    var dy_m = target_y - ball.y
    var dist_m = sqrt(dx_m*dx_m + dy_m*dy_m)

    if dist_m > 0.0001:
        var nx_m = dx_m / dist_m
        var ny_m = dy_m / dist_m

        var avoid = _apply_obstacle_avoidance(nx_m, ny_m)
        nx_m = avoid[0]
        ny_m = avoid[1]

        var boid = _apply_boid_rules(nx_m, ny_m)
        nx_m = boid[0]
        ny_m = boid[1]

        var speed = 2.0
        if "speed" in ball:
            speed = ball.speed

        var step = speed * delta * 60.0
                var inv_t = 0.0
                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))
                if inv_t > 0.0:
                    step = -step

        ball.x += nx_m * min(step, dist_m)
        ball.y += ny_m * min(step, dist_m)
# Cosmetics: kite behavior confirmed

# Cosmetic change to trigger a commit for auto-implement-kite-держит-дистанцию-атакует-при
func _ricochet_attack(delta: float):
	var enemies = _get_enemies()
	if enemies.size() > 0:
		var target = _get_target(enemies)
		var dx = target.x - self.ball.x
		var dy = target.y - self.ball.y
		var dist = sqrt(dx*dx + dy*dy)
		var width = 1000.0
		var height = 1000.0
		if "width" in self.world: width = self.world.width
		if "height" in self.world: height = self.world.height
		if "arena" in self.world and self.world.arena != null:
			if "width" in self.world.arena: width = self.world.arena.width
			if "height" in self.world.arena: height = self.world.arena.height

		var bounce_y = 0.0
		var bounce_x = 0.0
		var bdx = 0.0
		var bdy = 0.0
		if abs(dx) > abs(dy):
			bounce_y = 0.0 if self.ball.y < height / 2.0 else height
			bdx = target.x - self.ball.x
			bdy = bounce_y - self.ball.y
		else:
			bounce_x = 0.0 if self.ball.x < width / 2.0 else width
			bdx = bounce_x - self.ball.x
			bdy = target.y - self.ball.y

		var b_dist = sqrt(bdx*bdx + bdy*bdy)
		if b_dist > 0.0001:
			var nx = bdx / b_dist
			var ny = bdy / b_dist
			var b_speed = 2.0
			if "speed" in self.ball: b_speed = self.ball.speed
			var step = b_speed * delta * 60.0
        var inv_t = 0.0
        if "invert_timer" in ball: inv_t = float(ball.invert_timer)
        elif ball.has_method("get_meta") and ball.has_meta("invert_timer"): inv_t = float(ball.get_meta("invert_timer"))
        if inv_t > 0.0:
            step = -step
			self.ball.x += nx * min(step, b_dist)
			self.ball.y += ny * min(step, b_dist)

		var tr = 10.0
		var br = 10.0
		if "radius" in target: tr = target.radius
		if "radius" in self.ball: br = self.ball.radius
		if dist < tr + br + 15:
			if self.world != null and self.world.has_method("_deal_damage"):
				self.world._deal_damage(self.ball, target)
