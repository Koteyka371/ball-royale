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

		# Evolution mechanics
		if ball.level == 5 or ball.level == 10:
			var evolutions = {
				"warrior": ["paladin", "berserker"],
				"mage": ["warlock", "necromancer"],
				"rogue": ["ninja", "assassin"],
				"tank": ["guardian", "juggernaut"],
				"ranger": ["sniper", "bounty_hunter"],
				"healer": ["monk", "druid"],
				"paladin": ["templar", "guardian"],
				"berserker": ["juggernaut", "brawler"],
				"warlock": ["chaos", "necromancer"],
				"necromancer": ["vampire", "warlock"],
				"ninja": ["phantom", "assassin"],
				"assassin": ["phantom", "ninja"],
				"guardian": ["paladin", "juggernaut"],
				"juggernaut": ["berserker", "guardian"],
				"sniper": ["bounty_hunter", "scout"],
				"bounty_hunter": ["sniper", "scout"],
				"monk": ["templar", "druid"],
				"druid": ["monk", "templar"]
			}
			var current_type = ""
			if "ball_type" in ball:
				current_type = str(ball.ball_type)

			if evolutions.has(current_type):
				var options = evolutions[current_type]
				var new_type = options[randi() % options.size()]

				if "ball_type" in ball:
					ball.ball_type = new_type
				elif typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"):
					ball.set_meta("ball_type", new_type)
				elif typeof(ball) == TYPE_DICTIONARY:
					ball["ball_type"] = new_type

				if world != null and world.has_method("add_event"):
					world.add_event("evolution", {"ball": ball.get("id"), "old_type": current_type, "new_type": new_type, "level": ball.level})

		# Apply dynamic cosmetic aura scaling
		if not ("cosmetic_aura_scale" in ball) and typeof(ball) == TYPE_OBJECT and not ball.has_meta("cosmetic_aura_scale"):
			if typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"):
				ball.set_meta("cosmetic_aura_scale", 1.0)
			elif typeof(ball) == TYPE_DICTIONARY:
				ball["cosmetic_aura_scale"] = 1.0
			else:
				ball.cosmetic_aura_scale = 1.0

		var current_scale = 1.0
		if "cosmetic_aura_scale" in ball:
			current_scale = float(ball.cosmetic_aura_scale)
		elif typeof(ball) == TYPE_OBJECT and ball.has_meta("cosmetic_aura_scale"):
			current_scale = float(ball.get_meta("cosmetic_aura_scale"))

		current_scale += 0.2

		if "cosmetic_aura_scale" in ball:
			ball.cosmetic_aura_scale = current_scale
		elif typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"):
			ball.set_meta("cosmetic_aura_scale", current_scale)
		elif typeof(ball) == TYPE_DICTIONARY:
			ball["cosmetic_aura_scale"] = current_scale

		# Change color based on level
		var colors = [[0.0, 1.0, 0.0, 0.5], [0.0, 0.0, 1.0, 0.6], [1.0, 0.0, 1.0, 0.7], [1.0, 0.0, 0.0, 0.8], [1.0, 1.0, 0.0, 1.0]]
		var c_idx = min(ball.level - 1, colors.size() - 1)
		var new_color = colors[c_idx]

		if "cosmetic_aura_color" in ball:
			ball.cosmetic_aura_color = new_color
		elif typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"):
			ball.set_meta("cosmetic_aura_color", new_color)
		elif typeof(ball) == TYPE_DICTIONARY:
			ball["cosmetic_aura_color"] = new_color

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


func _handle_reflect_bounce(original_attacker, initial_target, damage: float, bounce_chance: float = 0.5, max_bounces: int = 3, bounce_range: float = 120.0) -> void:
	if randf() > bounce_chance:
		return

	if self.world == null or not "balls" in self.world:
		return

	var current_source = original_attacker
	var hit_targets = []
	if "id" in original_attacker:
		hit_targets.append(original_attacker.id)
	if "id" in initial_target:
		hit_targets.append(initial_target.id)

	for i in range(max_bounces):
		var closest_dist = bounce_range + 1
		var next_target = null

		for other in self.world.balls:
			if not ("alive" in other and other.alive):
				continue
			var other_id = other.id if "id" in other else null
			var original_team = original_attacker.team if "team" in original_attacker else null
			var other_team = other.team if "team" in other else null
			var original_id = original_attacker.id if "id" in original_attacker else null

			if other_id != null and not (other_id in hit_targets) and other_team == original_team and other_id != original_id:
				var dx = (other.x if "x" in other else 0.0) - (current_source.x if "x" in current_source else 0.0)
				var dy = (other.y if "y" in other else 0.0) - (current_source.y if "y" in current_source else 0.0)
				var dist = sqrt(dx*dx + dy*dy)
				if dist <= bounce_range and dist < closest_dist:
					closest_dist = dist
					next_target = other

		if next_target != null:
			if "id" in next_target:
				hit_targets.append(next_target.id)
			if self.has_method("_spawn_directed_particles"):
				self._spawn_directed_particles(next_target, current_source, "chain_lightning")

			if self.world != null and self.world.has_method("_deal_damage"):
				var old_dmg = initial_target.damage if "damage" in initial_target else damage
				if "damage" in initial_target:
					initial_target.damage = damage * 0.75
				elif initial_target.has_method("set_meta"):
					initial_target.set_meta("damage", damage * 0.75)

				self.world._deal_damage(next_target, initial_target)

				if "damage" in initial_target:
					initial_target.damage = old_dmg
				elif initial_target.has_method("set_meta"):
					initial_target.set_meta("damage", old_dmg)
			elif next_target.has_method("take_damage"):
				next_target.take_damage(damage * 0.75)

			damage *= 0.75
			current_source = next_target
		else:
			break

func _attempt_damage(attacker, target) -> void:

	var target_b_type = ""
	if "ball_type" in target: target_b_type = str(target.ball_type)
	if target_b_type != "shield_drone":
		var world_ref = self.world
		if world_ref != null and world_ref.has_method("get_nearby_entities"):
			var nearby = world_ref.get_nearby_entities(target, 150.0)
			if typeof(nearby) == TYPE_DICTIONARY and nearby.has("allies"):
				var pm_ref = null
				if "profile_manager" in world_ref: pm_ref = world_ref.profile_manager
				for a in nearby["allies"]:
					var a_type = ""
					if "ball_type" in a: a_type = str(a.ball_type)
					var a_hp = 0.0
					if "hp" in a: a_hp = float(a.hp)
					var a_alive = false
					if "alive" in a: a_alive = bool(a.alive)
					if a_type == "shield_drone" and a_hp > 0 and a_alive:
						var is_n = false
						if pm_ref != null and pm_ref.has_method("is_nemesis") and target_b_type != "" and a_type != "":
							is_n = pm_ref.is_nemesis(target_b_type, a_type)
						if not is_n:
							var original_dmg = 10.0
							if "damage" in attacker: original_dmg = float(attacker.damage)
							if a.has_method("take_damage"):
								a.take_damage(original_dmg)
							elif typeof(a) != TYPE_DICTIONARY and a.has_method("set_meta"):
								a.set_meta("hp", a_hp - original_dmg)
							else:
								a.hp -= original_dmg
							return
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

	var target_es = false
	if "energy_shield_active" in target and target.energy_shield_active:
		target_es = true
	elif target.has_method("has_meta") and target.has_meta("energy_shield_active") and target.get_meta("energy_shield_active"):
		target_es = true

	if target_es:
		var a_x = 0.0
		if "x" in attacker: a_x = float(attacker.x)
		var a_y = 0.0
		if "y" in attacker: a_y = float(attacker.y)
		var t_x = 0.0
		if "x" in target: t_x = float(target.x)
		var t_y = 0.0
		if "y" in target: t_y = float(target.y)
		var dx = a_x - t_x
		var dy = a_y - t_y
		var dist = sqrt(dx*dx + dy*dy)
		var a_rad = 10.0
		if "radius" in attacker: a_rad = float(attacker.radius)
		var t_rad = 10.0
		if "radius" in target: t_rad = float(target.radius)

		var reflection_mult = 0.5
		if dist > (a_rad + t_rad + 20.0):
			reflection_mult = 1.5

		var dmg = 10.0
		if "damage" in attacker: dmg = float(attacker.damage)
		var refl_dmg = dmg * reflection_mult

		if attacker.has_method("take_damage"):
			attacker.take_damage(refl_dmg)
		elif "hp" in attacker:
			if typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("set_meta"):
				attacker.set_meta("hp", attacker.hp - refl_dmg)
			else:
				attacker.hp -= refl_dmg
		return

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
		var bonus_cap = 0.0
		if "bonus_reflect_shield_capacity" in attacker: bonus_cap = attacker.bonus_reflect_shield_capacity
		elif attacker.has_method("get_meta") and attacker.has_meta("bonus_reflect_shield_capacity"): bonus_cap = attacker.get_meta("bonus_reflect_shield_capacity")
		shield_cap = max(shield_cap, target_max_hp * 0.5 + bonus_cap)

		if "reflect_shield_active" in attacker: attacker.reflect_shield_active = true
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_active", true)

		if "reflect_shield_capacity" in attacker: attacker.reflect_shield_capacity = shield_cap
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_capacity", shield_cap)

		var bonus_dur = 0.0
		if "bonus_reflect_shield_duration" in attacker: bonus_dur = attacker.bonus_reflect_shield_duration
		elif attacker.has_method("get_meta") and attacker.has_meta("bonus_reflect_shield_duration"): bonus_dur = attacker.get_meta("bonus_reflect_shield_duration")
		if "reflect_shield_timer" in attacker: attacker.reflect_shield_timer = 5.0 + bonus_dur
		elif attacker.has_method("set_meta"): attacker.set_meta("reflect_shield_timer", 5.0 + bonus_dur)

	else:
		if is_nemesis_active:
			if "damage" in attacker:
				attacker.damage = original_damage * 1.2

		var b_type_attacker = ""
		if "ball_type" in attacker:
			b_type_attacker = str(attacker.ball_type).to_lower()
		elif attacker.has_method("get_meta") and attacker.has_meta("ball_type"):
			b_type_attacker = str(attacker.get_meta("ball_type")).to_lower()

		var target_is_bounty = false
		if "is_bounty" in target and target.is_bounty:
			target_is_bounty = true
		elif target.has_method("get_meta") and target.has_meta("is_bounty") and target.get_meta("is_bounty"):
			target_is_bounty = true

		var target_high_threat = false
		if "high_threat" in target and target.high_threat:
			target_high_threat = true
		elif target.has_method("get_meta") and target.has_meta("high_threat") and target.get_meta("high_threat"):
			target_high_threat = true

		if b_type_attacker == "bounty_hunter" and (target_is_bounty or target_high_threat):
			if "damage" in attacker:
				attacker.damage = original_damage * 2.0

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

				self._handle_reflect_bounce(attacker, target, damage_to_reflect)

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

		var leech_timer = 0.0
		if "leech_booster_timer" in attacker: leech_timer = float(attacker.leech_booster_timer)
		elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("get_meta") and attacker.has_meta("leech_booster_timer"): leech_timer = float(attacker.get_meta("leech_booster_timer"))

		if leech_timer > 0.0:
			if "leech_seed_timer" in target: target.leech_seed_timer = 5.0
			elif typeof(target) != TYPE_DICTIONARY and target.has_method("set_meta"): target.set_meta("leech_seed_timer", 5.0)

			var a_id = null
			if "id" in attacker: a_id = attacker.id
			elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("get_meta") and attacker.has_meta("id"): a_id = attacker.get_meta("id")

			if "leech_seed_attacker_id" in target: target.leech_seed_attacker_id = a_id
			elif typeof(target) != TYPE_DICTIONARY and target.has_method("set_meta"): target.set_meta("leech_seed_attacker_id", a_id)

		var weather = ""
		if self.world != null and "game_mode" in self.world and self.world.game_mode != null and "weather" in self.world.game_mode:
			weather = str(self.world.game_mode.weather)
		if weather == "magnetic_storm":
			var chain_radius = 100.0
			var chain_chance = 0.5
			if randf() < chain_chance:
				var chain_damage = original_damage * 0.5
				var nearby_entities = []

				var tx = 0.0
				var ty = 0.0
				if "x" in target: tx = float(target.x)
				elif target.has_method("get_meta"): tx = float(target.get_meta("x"))
				if "y" in target: ty = float(target.y)
				elif target.has_method("get_meta"): ty = float(target.get_meta("y"))

				var target_id = null
				if "id" in target: target_id = target.id
				elif target.has_method("get_meta") and target.has_meta("id"): target_id = target.get_meta("id")

				var attacker_id = null
				if "id" in attacker: attacker_id = attacker.id
				elif attacker.has_method("get_meta") and attacker.has_meta("id"): attacker_id = attacker.get_meta("id")

				if "balls" in self.world:
					for b in self.world.balls:
						var b_alive = false
						if "alive" in b and b.alive: b_alive = true
						elif b.has_method("get_meta") and b.has_meta("alive") and b.get_meta("alive"): b_alive = true

						var b_id = null
						if "id" in b: b_id = b.id
						elif b.has_method("get_meta") and b.has_meta("id"): b_id = b.get_meta("id")

						if b_alive and b_id != target_id and b_id != attacker_id:
							var bx = 0.0
							var by = 0.0
							if "x" in b: bx = float(b.x)
							elif b.has_method("get_meta"): bx = float(b.get_meta("x"))
							if "y" in b: by = float(b.y)
							elif b.has_method("get_meta"): by = float(b.get_meta("y"))

							var d_sq = (bx - tx)*(bx - tx) + (by - ty)*(by - ty)
							if d_sq <= chain_radius * chain_radius:
								nearby_entities.append({"d_sq": d_sq, "entity": b})

				if "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
					for h in self.world.arena.hazards:
						var h_active = true
						if "active" in h: h_active = bool(h.active)
						elif h.has_method("get_meta") and h.has_meta("active"): h_active = bool(h.get_meta("active"))

						var h_id = null
						if "id" in h: h_id = h.id
						elif h.has_method("get_meta") and h.has_meta("id"): h_id = h.get_meta("id")

						if h_active and h_id != target_id:
							var hx = 0.0
							var hy = 0.0
							if "x" in h: hx = float(h.x)
							elif h.has_method("get_meta"): hx = float(h.get_meta("x"))
							if "y" in h: hy = float(h.y)
							elif h.has_method("get_meta"): hy = float(h.get_meta("y"))

							var d_sq = (hx - tx)*(hx - tx) + (hy - ty)*(hy - ty)
							if d_sq <= chain_radius * chain_radius:
								nearby_entities.append({"d_sq": d_sq, "entity": h})

				if nearby_entities.size() > 0:
					var closest_ent = nearby_entities[0]
					for i in range(1, nearby_entities.size()):
						if nearby_entities[i].d_sq < closest_ent.d_sq:
							closest_ent = nearby_entities[i]

					var next_target = closest_ent.entity
					var old_dmg = original_damage
					if "damage" in attacker: attacker.damage = chain_damage

					if self.world != null and self.world.has_method("_deal_damage"):
						self.world._deal_damage(attacker, next_target)
					elif "hp" in next_target:
						if typeof(next_target) != TYPE_DICTIONARY and next_target.has_method("set_meta"):
							next_target.set_meta("hp", float(next_target.hp) - chain_damage)
						else:
							next_target.hp -= chain_damage

					if "damage" in attacker: attacker.damage = old_dmg

					if self.has_method("_spawn_skill_particles"):
						self._spawn_skill_particles("lightning")

		if (is_nemesis_active or b_type_attacker == "bounty_hunter") and "damage" in attacker:
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
		var target_stun = 0.0
		if "stun_timer" in target:
			target_stun = target.stun_timer
		elif typeof(target) == TYPE_OBJECT and target.has_meta("stun_timer"):
			target_stun = target.get_meta("stun_timer")
		target_stun = max(target_stun, 0.2)
		if "stun_timer" in target:
			target.stun_timer = target_stun
		elif typeof(target) == TYPE_OBJECT and target.has_method("set_meta"):
			target.set_meta("stun_timer", target_stun)

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

							self._handle_reflect_bounce(attacker, next_entity, damage_to_reflect)

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

						var ne_stun = 0.0
						if "stun_timer" in next_entity:
							ne_stun = next_entity.stun_timer
						elif typeof(next_entity) == TYPE_OBJECT and next_entity.has_meta("stun_timer"):
							ne_stun = next_entity.get_meta("stun_timer")
						ne_stun = max(ne_stun, 0.2)
						if "stun_timer" in next_entity:
							next_entity.stun_timer = ne_stun
						elif typeof(next_entity) == TYPE_OBJECT and next_entity.has_method("set_meta"):
							next_entity.set_meta("stun_timer", ne_stun)
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
												var b_emp_imm = 0.0
												if "emp_immunity_timer" in b: b_emp_imm = b.emp_immunity_timer
												elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("emp_immunity_timer"): b_emp_imm = b.get_meta("emp_immunity_timer")
												elif typeof(b) == TYPE_DICTIONARY and b.has("emp_immunity_timer"): b_emp_imm = b.get("emp_immunity_timer")

												if b_emp_imm <= 0:
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
	var is_active_clone = false
	if self.ball.has_method("get_meta") and self.ball.get_meta("is_active_clone"): is_active_clone = true
	elif "is_active_clone" in self.ball and self.ball.is_active_clone: is_active_clone = true

	var is_alive_ac = true
	if "alive" in self.ball: is_alive_ac = self.ball.alive
	elif self.ball.has_method("get_meta") and self.ball.has_meta("alive"): is_alive_ac = self.ball.get_meta("alive")

	if is_active_clone and is_alive_ac:
		var mimic_timer = 0.0
		if self.ball.has_method("get_meta") and self.ball.has_meta("mimic_timer"): mimic_timer = self.ball.get_meta("mimic_timer")
		elif "mimic_timer" in self.ball: mimic_timer = self.ball.mimic_timer

		mimic_timer -= delta

		if self.ball.has_method("set_meta"): self.ball.set_meta("mimic_timer", mimic_timer)
		elif "mimic_timer" in self.ball: self.ball.mimic_timer = mimic_timer

		var hp_ac = 1.0
		if "hp" in self.ball: hp_ac = self.ball.hp

		if mimic_timer <= 0 or hp_ac <= 0:
			if "alive" in self.ball: self.ball.alive = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)
			return

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

		var o_alive = true
		if owner != null:
			if "alive" in owner: o_alive = owner.alive
			elif owner.has_method("get_meta") and owner.has_meta("alive"): o_alive = owner.get_meta("alive")

		if owner != null and o_alive:
			if "current_action" in owner: strategy = owner.current_action
		else:
			if "alive" in self.ball: self.ball.alive = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)
			return

	if typeof(self.ball) == TYPE_DICTIONARY:
		self.ball["is_frictionless"] = false
	elif self.ball.has_method("set_meta"):
		self.ball.set_meta("is_frictionless", false)

	var leech_booster_t = 0.0
	if "leech_booster_timer" in self.ball: leech_booster_t = float(self.ball.leech_booster_timer)
	elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("get_meta") and self.ball.has_meta("leech_booster_timer"): leech_booster_t = float(self.ball.get_meta("leech_booster_timer"))

	if leech_booster_t > 0.0:
		var new_l = max(0.0, leech_booster_t - delta)
		if "leech_booster_timer" in self.ball: self.ball.leech_booster_timer = new_l
		elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("leech_booster_timer", new_l)

	var leech_seed_t = 0.0
	if "leech_seed_timer" in self.ball: leech_seed_t = float(self.ball.leech_seed_timer)
	elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("get_meta") and self.ball.has_meta("leech_seed_timer"): leech_seed_t = float(self.ball.get_meta("leech_seed_timer"))

	if leech_seed_t > 0.0:
		var new_ls = max(0.0, leech_seed_t - delta)
		if "leech_seed_timer" in self.ball: self.ball.leech_seed_timer = new_ls
		elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("leech_seed_timer", new_ls)

		var a_id = null
		if "leech_seed_attacker_id" in self.ball: a_id = self.ball.leech_seed_attacker_id
		elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("get_meta") and self.ball.has_meta("leech_seed_attacker_id"): a_id = self.ball.get_meta("leech_seed_attacker_id")

		var attacker = null
		if a_id != null and self.world != null and "balls" in self.world:
			for b in self.world.balls:
				var bid = null
				if "id" in b: bid = b.id
				elif typeof(b) != TYPE_DICTIONARY and b.has_method("get_meta") and b.has_meta("id"): bid = b.get_meta("id")

				var balive = false
				if "alive" in b: balive = b.alive
				elif typeof(b) != TYPE_DICTIONARY and b.has_method("get_meta") and b.has_meta("alive"): balive = b.get_meta("alive")

				if str(bid) == str(a_id) and balive:
					attacker = b
					break

		if attacker != null:
			var drain = 5.0 * delta
			var cur_hp = 0.0
			if "hp" in self.ball: cur_hp = float(self.ball.hp)
			elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("get_meta") and self.ball.has_meta("hp"): cur_hp = float(self.ball.get_meta("hp"))

			var n_hp = cur_hp - drain
			if "hp" in self.ball: self.ball.hp = n_hp
			elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("hp", n_hp)

			var atk_cur_hp = 0.0
			if "hp" in attacker: atk_cur_hp = float(attacker.hp)
			elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("get_meta") and attacker.has_meta("hp"): atk_cur_hp = float(attacker.get_meta("hp"))

			var atk_max = 100.0
			if "max_hp" in attacker: atk_max = float(attacker.max_hp)
			elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("get_meta") and attacker.has_meta("max_hp"): atk_max = float(attacker.get_meta("max_hp"))

			var a_nhp = min(atk_max, atk_cur_hp + drain)
			if "hp" in attacker: attacker.hp = a_nhp
			elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("set_meta"): attacker.set_meta("hp", a_nhp)

			if n_hp <= 0.0:
				if "alive" in self.ball: self.ball.alive = false
				elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)


	var glitch_time = 0.0
	if typeof(self.ball) == TYPE_DICTIONARY:
		if "glitch_timer" in self.ball: glitch_time = self.ball.glitch_timer
	else:
		if self.ball.has_method("has_meta") and self.ball.has_meta("glitch_timer"):
			glitch_time = self.ball.get_meta("glitch_timer")
		elif "glitch_timer" in self.ball:
			glitch_time = self.ball.glitch_timer

	if glitch_time > 0.0:
		glitch_time -= delta
		if typeof(self.ball) == TYPE_DICTIONARY:
			self.ball["glitch_timer"] = glitch_time
		else:
			if self.ball.has_method("set_meta"):
				self.ball.set_meta("glitch_timer", glitch_time)
			elif "glitch_timer" in self.ball:
				self.ball.glitch_timer = glitch_time
		if randf() < 0.2:
			var strats = ["flee", "wander"]
			strategy = strats[randi() % strats.size()]

	# Track state history for time_rewind
	if typeof(self.ball) == TYPE_DICTIONARY:
		if not self.ball.has("state_history"):
			self.ball["state_history"] = []
		var hp_val = 100.0
		if self.ball.has("hp"): hp_val = float(self.ball["hp"])
		self.ball["state_history"].push_back({"x": float(self.ball.get("x", 0.0)), "y": float(self.ball.get("y", 0.0)), "hp": hp_val})
		if self.ball["state_history"].size() > 180:
			self.ball["state_history"].pop_front()
	else:
		if not self.ball.has_method("has_meta") or not self.ball.has_meta("state_history"):
			if self.ball.has_method("set_meta"):
				self.ball.set_meta("state_history", [])
		if self.ball.has_method("has_meta") and self.ball.has_meta("state_history"):
			var history = self.ball.get_meta("state_history")
			var hp_val = 100.0
			if "hp" in self.ball: hp_val = float(self.ball.hp)
			history.push_back({"x": float(self.ball.x), "y": float(self.ball.y), "hp": hp_val})
			if history.size() > 180:
				history.pop_front()
			self.ball.set_meta("state_history", history)


    if self.ball.has_method("remove_meta") and self.ball.has_meta("_chrono_slow"):
        self.ball.remove_meta("_chrono_slow")
    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("_chrono_slow"):
        self.ball.erase("_chrono_slow")

    var mirror_timer = 0.0
    if "mirror_stance_timer" in self.ball:
        mirror_timer = self.ball.mirror_stance_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("mirror_stance_timer"):
        mirror_timer = self.ball.get_meta("mirror_stance_timer")

    if mirror_timer > 0:
        mirror_timer -= delta
        if "mirror_stance_timer" in self.ball:
            self.ball.mirror_stance_timer = mirror_timer
        else:
            self.ball.set_meta("mirror_stance_timer", mirror_timer)

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("_chrono_slow", 0.5)
        elif typeof(self.ball) == TYPE_DICTIONARY:
            self.ball["_chrono_slow"] = 0.5


    var is_orbiting_accelerator = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("is_orbiting_accelerator"):
        is_orbiting_accelerator = self.ball.get_meta("is_orbiting_accelerator")
    elif "is_orbiting_accelerator" in self.ball:
        is_orbiting_accelerator = self.ball.is_orbiting_accelerator

    if is_orbiting_accelerator:
        var hazard_x = self.ball.x
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("orbit_center_x"):
            hazard_x = self.ball.get_meta("orbit_center_x")
        elif "orbit_center_x" in self.ball:
            hazard_x = self.ball.orbit_center_x

        var hazard_y = self.ball.y
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("orbit_center_y"):
            hazard_y = self.ball.get_meta("orbit_center_y")
        elif "orbit_center_y" in self.ball:
            hazard_y = self.ball.orbit_center_y

        var orbit_radius = 50.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("orbit_radius"):
            orbit_radius = self.ball.get_meta("orbit_radius")
        elif "orbit_radius" in self.ball:
            orbit_radius = self.ball.orbit_radius

        var orbit_speed = 0.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("orbit_speed"):
            orbit_speed = self.ball.get_meta("orbit_speed")
        elif "orbit_speed" in self.ball:
            orbit_speed = self.ball.orbit_speed

        var orbit_angle = 0.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("orbit_angle"):
            orbit_angle = self.ball.get_meta("orbit_angle")
        elif "orbit_angle" in self.ball:
            orbit_angle = self.ball.orbit_angle

        orbit_speed += 10.0 * delta
        orbit_angle += orbit_speed * delta

        var new_x = hazard_x + cos(orbit_angle) * orbit_radius
        var new_y = hazard_y + sin(orbit_angle) * orbit_radius

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("orbit_speed", orbit_speed)
            self.ball.set_meta("orbit_angle", orbit_angle)
            self.ball.x = new_x
            self.ball.y = new_y
        else:
            self.ball.orbit_speed = orbit_speed
            self.ball.orbit_angle = orbit_angle
            if typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["x"] = new_x
                self.ball["y"] = new_y
            else:
                self.ball.x = new_x
                self.ball.y = new_y

        if orbit_speed > 30.0:
            var eject_angle = randf() * 2.0 * PI
            var eject_dist = 2000.0
            var fly_tx = new_x + cos(eject_angle) * eject_dist
            var fly_ty = new_y + sin(eject_angle) * eject_dist
            var fly_t = max(0.5, eject_dist / 1500.0)

            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                self.ball.set_meta("is_orbiting_accelerator", false)
                self.ball.set_meta("is_flying", true)
                self.ball.set_meta("fly_target_x", fly_tx)
                self.ball.set_meta("fly_target_y", fly_ty)
                self.ball.set_meta("fly_timer", fly_t)
            else:
                self.ball.is_orbiting_accelerator = false
                self.ball.is_flying = true
                self.ball.fly_target_x = fly_tx
                self.ball.fly_target_y = fly_ty
                self.ball.fly_timer = fly_t
        return

    var is_flying = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("is_flying"):
        is_flying = self.ball.get_meta("is_flying")
    elif "is_flying" in self.ball:
        is_flying = self.ball.is_flying

    if is_flying:
        var fly_timer = 0.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("fly_timer"):
            fly_timer = self.ball.get_meta("fly_timer")
        elif "fly_timer" in self.ball:
            fly_timer = self.ball.fly_timer

        if fly_timer > 0:
            fly_timer -= delta
            var tx = self.ball.x
            var ty = self.ball.y
            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta"):
                self.ball.set_meta("fly_timer", fly_timer)
                if self.ball.has_meta("fly_target_x"): tx = self.ball.get_meta("fly_target_x")
                if self.ball.has_meta("fly_target_y"): ty = self.ball.get_meta("fly_target_y")
                var current_immunity = 0.0
                if self.ball.has_meta("zone_immunity_timer"): current_immunity = self.ball.get_meta("zone_immunity_timer")
                self.ball.set_meta("zone_immunity_timer", max(current_immunity, 0.1))
            else:
                self.ball.fly_timer = fly_timer
                if "fly_target_x" in self.ball: tx = self.ball.fly_target_x
                if "fly_target_y" in self.ball: ty = self.ball.fly_target_y
                var current_immunity = 0.0
                if "zone_immunity_timer" in self.ball: current_immunity = self.ball.zone_immunity_timer
                self.ball.zone_immunity_timer = max(current_immunity, 0.1)

            var dx = tx - self.ball.x
            var dy = ty - self.ball.y
            var dist = sqrt(dx*dx + dy*dy)
            if dist > 5.0:
                var speed = 2000.0 * delta
                self.ball.x += (dx / dist) * min(speed, dist)
                self.ball.y += (dy / dist) * min(speed, dist)
            if fly_timer <= 0:
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                    self.ball.set_meta("is_flying", false)
                else:
                    self.ball.is_flying = false
        else:
            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                self.ball.set_meta("is_flying", false)
            else:
                self.ball.is_flying = false
        return



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

	var is_decoy_clone = false
	if self.ball.has_method("get_meta") and self.ball.has_meta("is_decoy_clone") and self.ball.get_meta("is_decoy_clone"): is_decoy_clone = true
	elif "is_decoy_clone" in self.ball and self.ball.is_decoy_clone: is_decoy_clone = true

	if is_decoy_clone:
		var is_exploded = false
		if self.ball.has_method("get_meta") and self.ball.has_meta("_exploded") and self.ball.get_meta("_exploded"): is_exploded = true
		elif "_exploded" in self.ball and self.ball._exploded: is_exploded = true

		if not is_exploded:
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
				if "_exploded" in self.ball: self.ball._exploded = true
				elif self.ball.has_method("set_meta"): self.ball.set_meta("_exploded", true)
				if "alive" in self.ball: self.ball.alive = false
				elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)
				if "hp" in self.ball: self.ball.hp = 0.0
				elif self.ball.has_method("set_meta"): self.ball.set_meta("hp", 0.0)

				var bx_self = 0.0
				if "x" in self.ball: bx_self = self.ball.x
				elif self.ball.has_method("get_meta") and self.ball.has_meta("x"): bx_self = self.ball.get_meta("x")
				var by_self = 0.0
				if "y" in self.ball: by_self = self.ball.y
				elif self.ball.has_method("get_meta") and self.ball.has_meta("y"): by_self = self.ball.get_meta("y")

				if world != null and "events" in world:
					world.events.append({'type': 'explosion', 'data': {'x': bx_self, 'y': by_self, 'radius': 120.0}})
				if world != null and "balls" in world:
					var my_team = ""
					if "team" in self.ball: my_team = self.ball.team
					elif self.ball.has_method("get_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
					elif "ball_type" in self.ball: my_team = self.ball.ball_type
					elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): my_team = self.ball.get_meta("ball_type")

					for b in world.balls:
						var b_alive = true
						if "alive" in b: b_alive = b.alive
						elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
						var b_team = ""
						if "team" in b: b_team = b.team
						elif b.has_method("get_meta") and b.has_meta("team"): b_team = b.get_meta("team")
						elif "ball_type" in b: b_team = b.ball_type
						elif b.has_method("get_meta") and b.has_meta("ball_type"): b_team = b.get_meta("ball_type")

						if b_alive and b_team != my_team:
							var bx = 0.0
							if "x" in b: bx = b.x
							elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
							var by = 0.0
							if "y" in b: by = b.y
							elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

							var dist = sqrt(pow(bx_self - bx, 2) + pow(by_self - by, 2))
							if dist <= 120.0:
								if b.has_method("take_damage"):
									b.take_damage(50.0)
								else:
									var bh = 0.0
									if "hp" in b: bh = b.hp
									elif b.has_method("get_meta") and b.has_meta("hp"): bh = b.get_meta("hp")
									bh -= 50.0
									if "hp" in b: b.hp = bh
									elif b.has_method("set_meta"): b.set_meta("hp", bh)
									if bh <= 0.0:
										if "alive" in b: b.alive = false
										elif b.has_method("set_meta"): b.set_meta("alive", false)
				return

	var is_alive_mine_decoy = true
	if "alive" in self.ball: is_alive_mine_decoy = self.ball.alive
	elif self.ball.has_method("get_meta") and self.ball.has_meta("alive"): is_alive_mine_decoy = self.ball.get_meta("alive")

	if is_decoy_clone and is_alive_mine_decoy:
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
		self._clamp_position()
		return

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
			if "is_mimic_clone" in self.ball: self.ball.is_mimic_clone = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("is_mimic_clone", false)
			if "is_mimic_charging" in self.ball: self.ball.is_mimic_charging = true
			elif self.ball.has_method("set_meta"): self.ball.set_meta("is_mimic_charging", true)
			if "mimic_charge_timer" in self.ball: self.ball.mimic_charge_timer = 3.0
			elif self.ball.has_method("set_meta"): self.ball.set_meta("mimic_charge_timer", 3.0)
			var max_hp = 100.0
			if "max_hp" in self.ball: max_hp = self.ball.max_hp
			elif self.ball.has_method("get_meta") and self.ball.has_meta("max_hp"): max_hp = self.ball.get_meta("max_hp")
			if "hp" in self.ball: self.ball.hp = max_hp
			elif self.ball.has_method("set_meta"): self.ball.set_meta("hp", max_hp)
			if "alive" in self.ball: self.ball.alive = true
			elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", true)
			if "is_illusion" in self.ball: self.ball.is_illusion = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("is_illusion", false)
			return
		else:
			self._clamp_position()
			return

	var is_mimic_charging = false
	if self.ball.has_method("get_meta") and self.ball.has_meta("is_mimic_charging"): is_mimic_charging = self.ball.get_meta("is_mimic_charging")
	elif "is_mimic_charging" in self.ball and self.ball.is_mimic_charging: is_mimic_charging = true


	var is_alive_mine_charge = true
	if "alive" in self.ball: is_alive_mine_charge = self.ball.alive
	elif self.ball.has_method("get_meta") and self.ball.has_meta("alive"): is_alive_mine_charge = self.ball.get_meta("alive")
	if is_mimic_charging and is_alive_mine_charge:
		var nearest_enemy = null
		var min_dist = 999999.0
		var my_team = ""
		if "team" in self.ball: my_team = self.ball.team
		elif self.ball.has_method("get_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
		elif "ball_type" in self.ball: my_team = self.ball.ball_type
		elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): my_team = self.ball.get_meta("ball_type")
		if world != null and "balls" in world:
			for b in world.balls:
				var b_alive = true
				if "alive" in b: b_alive = b.alive
				elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
				var b_team = ""
				if "team" in b: b_team = b.team
				elif b.has_method("get_meta") and b.has_meta("team"): b_team = b.get_meta("team")
				elif "ball_type" in b: b_team = b.ball_type
				elif b.has_method("get_meta") and b.has_meta("ball_type"): b_team = b.get_meta("ball_type")
				if b_alive and b_team != my_team:
					var bx = 0.0
					var by = 0.0
					if "x" in b: bx = b.x
					elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
					if "y" in b: by = b.y
					elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")
					var mx = 0.0
					var my = 0.0
					if "x" in self.ball: mx = self.ball.x
					elif self.ball.has_method("get_meta") and self.ball.has_meta("x"): mx = self.ball.get_meta("x")
					if "y" in self.ball: my = self.ball.y
					elif self.ball.has_method("get_meta") and self.ball.has_meta("y"): my = self.ball.get_meta("y")
					var dist = sqrt((mx - bx) * (mx - bx) + (my - by) * (my - by))
					if dist < min_dist:
						min_dist = dist
						nearest_enemy = b

		var detonate = false
		if nearest_enemy != null:
			var speed = 300.0
			if "base_speed" in self.ball: speed = self.ball.base_speed * 1.5
			elif self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"): speed = self.ball.get_meta("base_speed") * 1.5
			if min_dist > 0.0001:
				var bx = 0.0
				var by = 0.0
				if "x" in nearest_enemy: bx = nearest_enemy.x
				elif nearest_enemy.has_method("get_meta") and nearest_enemy.has_meta("x"): bx = nearest_enemy.get_meta("x")
				if "y" in nearest_enemy: by = nearest_enemy.y
				elif nearest_enemy.has_method("get_meta") and nearest_enemy.has_meta("y"): by = nearest_enemy.get_meta("y")
				var mx = 0.0
				var my = 0.0
				if "x" in self.ball: mx = self.ball.x
				elif self.ball.has_method("get_meta") and self.ball.has_meta("x"): mx = self.ball.get_meta("x")
				if "y" in self.ball: my = self.ball.y
				elif self.ball.has_method("get_meta") and self.ball.has_meta("y"): my = self.ball.get_meta("y")
				var dx = bx - mx
				var dy = by - my
				var cvx = (dx / min_dist) * speed
				var cvy = (dy / min_dist) * speed
				if "vx" in self.ball: self.ball.vx = cvx
				elif self.ball.has_method("set_meta"): self.ball.set_meta("vx", cvx)
				if "vy" in self.ball: self.ball.vy = cvy
				elif self.ball.has_method("set_meta"): self.ball.set_meta("vy", cvy)
				if "x" in self.ball: self.ball.x += cvx * delta
				elif self.ball.has_method("set_meta"): self.ball.set_meta("x", self.ball.get_meta("x") + cvx * delta)
				if "y" in self.ball: self.ball.y += cvy * delta
				elif self.ball.has_method("set_meta"): self.ball.set_meta("y", self.ball.get_meta("y") + cvy * delta)
			if min_dist <= 30.0:
				detonate = true
		else:
			detonate = true

		var m_charge = 3.0
		if "mimic_charge_timer" in self.ball: m_charge = self.ball.mimic_charge_timer
		elif self.ball.has_method("get_meta") and self.ball.has_meta("mimic_charge_timer"): m_charge = self.ball.get_meta("mimic_charge_timer")
		m_charge -= delta
		if "mimic_charge_timer" in self.ball: self.ball.mimic_charge_timer = m_charge
		elif self.ball.has_method("set_meta"): self.ball.set_meta("mimic_charge_timer", m_charge)
		if m_charge <= 0:
			detonate = true

		if detonate:
			if "alive" in self.ball: self.ball.alive = false
			elif self.ball.has_method("set_meta"): self.ball.set_meta("alive", false)
			if "hp" in self.ball: self.ball.hp = 0.0
			elif self.ball.has_method("set_meta"): self.ball.set_meta("hp", 0.0)
			if world != null and "balls" in world:
				for b in world.balls:
					var b_alive = true
					if "alive" in b: b_alive = b.alive
					elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
					var b_team = ""
					if "team" in b: b_team = b.team
					elif b.has_method("get_meta") and b.has_meta("team"): b_team = b.get_meta("team")
					elif "ball_type" in b: b_team = b.ball_type
					elif b.has_method("get_meta") and b.has_meta("ball_type"): b_team = b.get_meta("ball_type")
					if b_alive and b_team != my_team:
						var bx = 0.0
						var by = 0.0
						if "x" in b: bx = b.x
						elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
						if "y" in b: by = b.y
						elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")
						var mx = 0.0
						var my = 0.0
						if "x" in self.ball: mx = self.ball.x
						elif self.ball.has_method("get_meta") and self.ball.has_meta("x"): mx = self.ball.get_meta("x")
						if "y" in self.ball: my = self.ball.y
						elif self.ball.has_method("get_meta") and self.ball.has_meta("y"): my = self.ball.get_meta("y")
						var d = sqrt((mx - bx) * (mx - bx) + (my - by) * (my - by))
						if d <= 60.0:
							if b.has_method("take_damage"):
								b.take_damage(20.0)
							else:
								var bhp = 100.0
								if "hp" in b: bhp = b.hp
								elif b.has_method("get_meta") and b.has_meta("hp"): bhp = b.get_meta("hp")
								bhp -= 20.0
								if "hp" in b: b.hp = bhp
								elif b.has_method("set_meta"): b.set_meta("hp", bhp)
								if bhp <= 0.0:
									if "alive" in b: b.alive = false
									elif b.has_method("set_meta"): b.set_meta("alive", false)
				var mx = 0.0
				var my = 0.0
				if "x" in self.ball: mx = self.ball.x
				elif self.ball.has_method("get_meta") and self.ball.has_meta("x"): mx = self.ball.get_meta("x")
				if "y" in self.ball: my = self.ball.y
				elif self.ball.has_method("get_meta") and self.ball.has_meta("y"): my = self.ball.get_meta("y")
				if world != null and "events" in world:
					world.events.append({"type": "explosion", "data": {"x": mx, "y": my, "radius": 60.0}})
				elif world != null and world.has_method("add_event"):
					world.add_event("explosion", {"x": mx, "y": my, "radius": 60.0})
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

		var cascade_timer = -1.0
		if "clone_cascade_timer" in self.ball: cascade_timer = self.ball.clone_cascade_timer
		elif self.ball.has_method("get_meta") and self.ball.has_meta("clone_cascade_timer"): cascade_timer = self.ball.get_meta("clone_cascade_timer")

		if cascade_timer >= 0.0:
			cascade_timer -= delta
			if "clone_cascade_timer" in self.ball: self.ball.clone_cascade_timer = cascade_timer
			elif self.ball.has_method("set_meta"): self.ball.set_meta("clone_cascade_timer", cascade_timer)

			if cascade_timer <= 0.0:
				triggered = true

		if not triggered and world != null and "balls" in world:
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

					if b_alive:
						var is_enemy = b_team != my_team
						var bx = 0.0
						var by = 0.0
						if "x" in b: bx = b.x
						elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
						if "y" in b: by = b.y
						elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

						var d_sq = pow(self.ball.x - bx, 2) + pow(self.ball.y - by, 2)
						if d_sq <= aoe_radius * aoe_radius:
							if is_enemy:
								var original_damage = 0.0
								if "damage" in self.ball: original_damage = self.ball.damage
								if "damage" in self.ball: self.ball.damage = aoe_damage
								self._attempt_damage(self.ball, b)
								if "damage" in self.ball: self.ball.damage = original_damage
							else:
								var is_b_clone = false
								if b.has_method("get_meta") and b.get_meta("is_clone"): is_b_clone = true
								elif "is_clone" in b and b.is_clone: is_b_clone = true

								if is_b_clone and (typeof(b) != typeof(self.ball) or (typeof(b) == typeof(self.ball) and b != self.ball)):
									var b_cascade = -1.0
									if "clone_cascade_timer" in b: b_cascade = b.clone_cascade_timer
									elif b.has_method("get_meta") and b.has_meta("clone_cascade_timer"): b_cascade = b.get_meta("clone_cascade_timer")

									if b_cascade < 0.0:
										if "clone_cascade_timer" in b: b.clone_cascade_timer = 0.25
										elif b.has_method("set_meta"): b.set_meta("clone_cascade_timer", 0.25)

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
		if inv.has("nemesis_compass_item"):
			if self.world != null and "profile_manager" in self.world and self.world.profile_manager != null:
				var pm = self.world.profile_manager
				if pm.has_method("is_nemesis"):
					var min_dist_sq = 999999999.0
					var nemesis = null
					if "balls" in self.world:
						for other in self.world.balls:
							var o_id = -1
							if "id" in other: o_id = other.id
							var my_id = -2
							if "id" in self.ball: my_id = self.ball.id
							var o_hp = 0.0
							if "hp" in other: o_hp = float(other.hp)
							elif other.has_method("get_meta") and other.has_meta("hp"): o_hp = float(other.get_meta("hp"))
							if o_id != my_id and o_hp > 0:
								var o_type = ""
								if "ball_type" in other: o_type = str(other.ball_type)
								var my_type = ""
								if "ball_type" in self.ball: my_type = str(self.ball.ball_type)
								if my_type != "" and o_type != "" and pm.is_nemesis(my_type, o_type):
									var ox = 0.0
									var oy = 0.0
									if "x" in other: ox = float(other.x)
									if "y" in other: oy = float(other.y)
									var dist_sq = pow(ox - self.ball.x, 2) + pow(oy - self.ball.y, 2)
									if dist_sq < min_dist_sq:
										min_dist_sq = dist_sq
										nemesis = other
					if nemesis != null:
						if "events" in self.world:
							var nx = 0.0
							var ny = 0.0
							if "x" in nemesis: nx = float(nemesis.x)
							if "y" in nemesis: ny = float(nemesis.y)
							var my_id_e = -1
							if "id" in self.ball: my_id_e = self.ball.id
							self.world.events.append({"type": "nemesis_compass", "data": {"target_x": nx, "target_y": ny, "owner_id": my_id_e}})
							self.world.events.append({"type": "visual_effect", "data": {"type": "line", "x": self.ball.x, "y": self.ball.y, "tx": nx, "ty": ny, "color": "red"}})
			inv.erase("nemesis_compass_item")
			self.ball.set_meta("inventory", inv)

	if (strategy == "flee" or strategy == "defend" or strategy == "attack") and self.ball.has_meta("inventory"):
		var inv = self.ball.get_meta("inventory")
		if inv.has("weather_scanner"):
			if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
				var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
				var scanner = ProceduralArenaScript.Hazard.new(self.world.arena.hazards.size() + (randi() % 10000), self.ball.x, self.ball.y, 15.0, "weather_scanner", 0.0)
				scanner.set_meta("duration", 30.0)
				if "id" in self.ball: scanner.set_meta("owner_id", self.ball.id)
				if "team" in self.ball: scanner.set_meta("team", self.ball.team)
				self.world.arena.hazards.append(scanner)
				inv.erase("weather_scanner")
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
					var aw = 800.0
					if "width" in arena: aw = arena.width
					var ah = 600.0
					if "height" in arena: ah = arena.height

					var px1 = self.ball.x
					var py1 = self.ball.y
					var d_left = px1
					var d_right = aw - px1
					var d_top = py1
					var d_bottom = ah - py1
					var min_d = min(min(d_left, d_right), min(d_top, d_bottom))
					if min_d == d_left: px1 = 0.0
					elif min_d == d_right: px1 = aw
					elif min_d == d_top: py1 = 0.0
					else: py1 = ah

					var p1 = load("res://src/arena/procedural_arena.gd").Hazard.new(p1_id, px1, py1, 30.0, "teleporter", 0.0)
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

					target_x = max(0.0, min(aw, target_x))
					target_y = max(0.0, min(ah, target_y))

					d_left = target_x
					d_right = aw - target_x
					d_top = target_y
					d_bottom = ah - target_y
					min_d = min(min(d_left, d_right), min(d_top, d_bottom))
					if min_d == d_left: target_x = 0.0
					elif min_d == d_right: target_x = aw
					elif min_d == d_top: target_y = 0.0
					else: target_y = ah

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
	# Gravity Well and Repulsor Hazard Logic
	if world != null and "arena" in world and "hazards" in world.arena:
		var current_tick = world.get("tick", 0)
		for hazard in world.arena.hazards:
			var kind = hazard.get("kind", "")
			var is_active = hazard.get("active", true)
			if (kind == "gravity_well" or kind == "repulsor") and is_active:
				var hx = float(hazard.x)
				var hy = float(hazard.y)

				if typeof(hazard) == TYPE_OBJECT:
					if (not hazard.has_meta("last_booster_pull_tick") or hazard.get_meta("last_booster_pull_tick") != current_tick):
						hazard.set_meta("last_booster_pull_tick", current_tick)
				elif typeof(hazard) == TYPE_DICTIONARY:
					if (not hazard.has("last_booster_pull_tick") or hazard["last_booster_pull_tick"] != current_tick):
						hazard["last_booster_pull_tick"] = current_tick
					if "boosters" in world:
						for b in world.boosters:
							var bx = float(b.x) if typeof(b) != TYPE_DICTIONARY else float(b["x"])
							var by = float(b.y) if typeof(b) != TYPE_DICTIONARY else float(b["y"])
							var bdx = hx - bx
							var bdy = hy - by
							var bdist_sq = bdx * bdx + bdy * bdy
							var radius = float(hazard.get("radius", 50.0))
							var eff_radius = radius * 3.0
							if bdist_sq > 0.0001 and bdist_sq < eff_radius * eff_radius:
								var bdist = sqrt(bdist_sq)
								var mdist = 10.0
								if bdist > 10.0:
									mdist = bdist
								var force = (eff_radius / mdist) * 50.0 * delta
								if force > bdist * 0.5:
									force = bdist * 0.5
								var bnx = bdx / bdist
								var bny = bdy / bdist
								if kind == "gravity_well":
									var is_inverted = false
									if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("is_inverted"):
										is_inverted = hazard.get_meta("is_inverted")
									elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("is_inverted"):
										is_inverted = hazard["is_inverted"]

									if is_inverted:
										if typeof(b) == TYPE_DICTIONARY:
											b["x"] -= bnx * force * 3.0
											b["y"] -= bny * force * 3.0
										else:
											b.x -= bnx * force * 3.0
											b.y -= bny * force * 3.0
									else:
										if typeof(b) == TYPE_DICTIONARY:
											b["x"] += bnx * force
											b["y"] += bny * force
										else:
											b.x += bnx * force
											b.y += bny * force
								else:
									if typeof(b) == TYPE_DICTIONARY:
										b["x"] -= bnx * force
										b["y"] -= bny * force
									else:
										b.x -= bnx * force
										b.y -= bny * force

				var anchor_timer = 0.0
				if "anchor_booster_timer" in self.ball:
					anchor_timer = float(self.ball.anchor_booster_timer)
				elif self.ball.has_method("has_meta") and self.ball.has_meta("anchor_booster_timer"):
					anchor_timer = float(self.ball.get_meta("anchor_booster_timer"))

				if anchor_timer <= 0.0:
					var dx = hx - float(self.ball.x)
					var dy = hy - float(self.ball.y)
					var dist_sq = dx * dx + dy * dy
					var radius = float(hazard.get("radius", 50.0))
					var eff_radius = radius * 3.0
					if dist_sq > 0.0001 and dist_sq < eff_radius * eff_radius:
						var dist = sqrt(dist_sq)
						var mdist = 10.0
						if dist > 10.0:
							mdist = dist
						var force = (eff_radius / mdist) * 50.0 * delta
						if force > dist * 0.5:
							force = dist * 0.5
						var nx = dx / dist
						var ny = dy / dist
						if kind == "gravity_well":
							var is_inverted = false
							if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("is_inverted"):
								is_inverted = hazard.get_meta("is_inverted")
							elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("is_inverted"):
								is_inverted = hazard["is_inverted"]

							if is_inverted:
								if typeof(self.ball) == TYPE_DICTIONARY:
									self.ball["x"] -= nx * force * 3.0
									self.ball["y"] -= ny * force * 3.0
								else:
									self.ball.x -= nx * force * 3.0
									self.ball.y -= ny * force * 3.0
							else:
								if typeof(self.ball) == TYPE_DICTIONARY:
									self.ball["x"] += nx * force
									self.ball["y"] += ny * force
									if hazard.get("damage", 0.0) > 0.0 and dist_sq < radius * radius:
										self.ball["hp"] -= float(hazard.get("damage", 0.0)) * delta
										if self.ball["hp"] <= 0:
											self.ball["hp"] = 0
											self.ball["alive"] = false
											self.ball["killer"] = "gravity_well"
								else:
									self.ball.x += nx * force
									self.ball.y += ny * force
									if hazard.get("damage", 0.0) > 0.0 and dist_sq < radius * radius:
										self.ball.hp -= float(hazard.get("damage", 0.0)) * delta
										if self.ball.hp <= 0:
											self.ball.hp = 0
											self.ball.alive = false
											self.ball.killer = "gravity_well"
						else:
							if typeof(self.ball) == TYPE_DICTIONARY:
								self.ball["x"] -= nx * force
								self.ball["y"] -= ny * force
							else:
								self.ball.x -= nx * force
								self.ball.y -= ny * force

	if world != null and "arena" in world and "hazards" in world.arena:
		for hazard in world.arena.hazards:
			if hazard.get("kind") == "shrapnel":
				if "duration" in hazard and hazard.duration > 0:
					hazard.duration -= delta
					if hazard.duration <= 0:
						hazard.duration = 0.0
				if "x" in hazard and "vx" in hazard: hazard.x += hazard.vx * delta
				if "y" in hazard and "vy" in hazard: hazard.y += hazard.vy * delta
				if "vx" in hazard: hazard.vx *= (1.0 - 2.0 * delta)
				if "vy" in hazard: hazard.vy *= (1.0 - 2.0 * delta)

				var h_rad = hazard.radius if "radius" in hazard else 5.0
				var b_rad = self.ball.radius if "radius" in self.ball else (self.ball.get_meta("radius") if self.ball.has_method("has_meta") and self.ball.has_meta("radius") else 10.0)
				var bx = self.ball.x if "x" in self.ball else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else 0.0)
				var by = self.ball.y if "y" in self.ball else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else 0.0)
				var hx = hazard.x if "x" in hazard else 0.0
				var hy = hazard.y if "y" in hazard else 0.0

				var dist = sqrt(pow(bx - hx, 2) + pow(by - hy, 2))
				if dist <= h_rad + b_rad:
					if self.ball.has_method("take_damage"):
						var dmg = hazard.damage if "damage" in hazard else 10.0
						self.ball.take_damage(dmg * delta)

			elif hazard.get("kind") == "vampiric_puddle":
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
	var emp_timer = 0.0
	if self.ball.has_method("get_meta") and self.ball.has_meta("empowerment_boost_timer"):
		emp_timer = float(self.ball.get_meta("empowerment_boost_timer"))
	if emp_timer > 0:
		emp_timer -= delta
		self.ball.set_meta("empowerment_boost_timer", emp_timer)
		if emp_timer <= 0:
			self.ball.set_meta("empowerment_boost_timer", 0.0)
			if self.ball.has_method("get_meta") and self.ball.has_meta("base_damage_multiplier"):
				self.ball["damage_multiplier"] = float(self.ball.get_meta("base_damage_multiplier"))
			var b_speed = 100.0
			if "base_speed" in self.ball: b_speed = float(self.ball.base_speed)
			self.ball["speed"] = b_speed

	# Empowerment Matrix logic
	if world != null and "arena" in world and "hazards" in world.arena:
		for hazard in world.arena.hazards:
			if hazard.get("kind") == "empowerment_matrix":
				var my_rad = 10.0
				if "radius" in self.ball:
					my_rad = float(self.ball.radius)
				var dist = sqrt((self.ball.x - hazard.x) * (self.ball.x - hazard.x) + (self.ball.y - hazard.y) * (self.ball.y - hazard.y))
				var h_rad = 50.0
				if "radius" in hazard: h_rad = float(hazard.radius)
				if dist <= h_rad + my_rad:
					var owner_team = hazard.get("owner_team")
					if owner_team == null:
						var owner_id = hazard.get("owner_id")
						if owner_id != null:
							if "balls" in world:
								for b in world.balls:
									if b.get("id") == owner_id:
										owner_team = b.get("team")
										if owner_team == null:
											owner_team = b.get("ball_type")
											if owner_team == null:
												owner_team = ""
										hazard["owner_team"] = owner_team
										break
					if owner_team != null:
						var my_team = self.ball.get("team")
						if my_team == null:
							my_team = self.ball.get("ball_type")
							if my_team == null:
								my_team = ""

						if owner_team == my_team:
							# Ally: boost speed and damage
							self.ball.set_meta("empowerment_boost_timer", 0.5)
							var base_speed = 100.0
							if "base_speed" in self.ball: base_speed = float(self.ball.base_speed)
							self.ball["speed"] = base_speed * 1.5
							if not (self.ball.has_method("has_meta") and self.ball.has_meta("base_damage_multiplier")):
								var dmg_mult = 1.0
								if "damage_multiplier" in self.ball: dmg_mult = float(self.ball.damage_multiplier)
								self.ball.set_meta("base_damage_multiplier", dmg_mult)
							self.ball["damage_multiplier"] = float(self.ball.get_meta("base_damage_multiplier")) * 1.5
						else:
							# Enemy: slow
							self.ball.set_meta("empowerment_boost_timer", 0.5)
							var base_speed = 100.0
							if "base_speed" in self.ball: base_speed = float(self.ball.base_speed)
							self.ball["speed"] = base_speed * 0.5

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

        if self.world != null and self.world.has_method("add_event"):
            var enemies = self._get_enemies()
            var hazards = []
            if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                hazards = self.world.arena.hazards
            var items = []
            if self.world != null and "arena" in self.world and self.world.arena != null and "items" in self.world.arena:
                items = self.world.arena.items
            var boosters = []
            if self.world != null and "boosters" in self.world:
                boosters = self.world.boosters

            if enemies.size() > 0 or hazards.size() > 0 or items.size() > 0 or boosters.size() > 0:
                var weather_is_thunderstorm = false
                if self.world != null:
                    if "arena" in self.world and self.world.arena != null and "weather" in self.world.arena and self.world.arena.weather == "thunderstorm":
                        weather_is_thunderstorm = true
                    elif "game_mode" in self.world and self.world.game_mode != null and "weather" in self.world.game_mode and self.world.game_mode.weather == "thunderstorm":
                        weather_is_thunderstorm = true

                var chain_range = 150.0
                if weather_is_thunderstorm:
                    chain_range = 300.0
                var chain_range_sq = chain_range * chain_range

                var jump_count = 0
                var current_target = self.ball
                var hit_entities = []
                hit_entities.append(self.ball)

                while jump_count < 3:
                    var nearby = []
                    var ct_x = current_target.x if "x" in current_target else current_target.get_meta("x") if typeof(current_target) == TYPE_OBJECT and current_target.has_meta("x") else current_target["x"]
                    var ct_y = current_target.y if "y" in current_target else current_target.get_meta("y") if typeof(current_target) == TYPE_OBJECT and current_target.has_meta("y") else current_target["y"]
                    for e in enemies:
                        if not hit_entities.has(e):
                            var dist_sq = pow(e.x - ct_x, 2) + pow(e.y - ct_y, 2)
                            if dist_sq < chain_range_sq:
                                nearby.append({"dist": dist_sq, "entity": e, "type": "enemy"})
                    for h in hazards:
                        if not hit_entities.has(h):
                            var is_active = true
                            if "active" in h: is_active = h.active
                            if is_active:
                                var dist_sq = pow(h.x - ct_x, 2) + pow(h.y - ct_y, 2)
                                if dist_sq < chain_range_sq:
                                    var t_var = ""
                                    if typeof(h) == TYPE_OBJECT and h.has_meta("trap_variant"): t_var = h.get_meta("trap_variant")
                                    if t_var == "emp_trap":
                                        nearby.append({"dist": -999999.0 + dist_sq, "entity": h, "type": "hazard"})
                                    else:
                                        nearby.append({"dist": dist_sq, "entity": h, "type": "hazard"})
                    for b in boosters:
                        if not hit_entities.has(b):
                            var dist_sq = pow(b.x - ct_x, 2) + pow(b.y - ct_y, 2)
                            if dist_sq < chain_range_sq:
                                nearby.append({"dist": dist_sq, "entity": b, "type": "booster"})
                    for it in items:
                        if not hit_entities.has(it):
                            var dist_sq = pow(it.x - ct_x, 2) + pow(it.y - ct_y, 2)
                            if dist_sq < chain_range_sq:
                                nearby.append({"dist": dist_sq, "entity": it, "type": "item"})

                    if self.world != null and "arena" in self.world and self.world.arena != null:
                        var aw = 2000.0
                        var ah = 2000.0
                        if "width" in self.world.arena: aw = self.world.arena.width
                        if "height" in self.world.arena: ah = self.world.arena.height
                        var walls = [{"x": 0.0, "y": ct_y, "name": "left_wall"}, {"x": aw, "y": ct_y, "name": "right_wall"}, {"x": ct_x, "y": 0.0, "name": "top_wall"}, {"x": ct_x, "y": ah, "name": "bottom_wall"}]
                        for w in walls:
                            if not hit_entities.has(w["name"]):
                                var dist_sq = pow(w["x"] - ct_x, 2) + pow(w["y"] - ct_y, 2)
                                if dist_sq < chain_range_sq:
                                    nearby.append({"dist": dist_sq, "entity": w, "type": "wall"})

                    if nearby.size() == 0:
                        break

                    nearby.sort_custom(func(a, b): return a["dist"] < b["dist"])
                    var next_entity = nearby[0]["entity"]
                    var e_type = nearby[0]["type"]

                    var tx = next_entity["x"] if e_type == "wall" else next_entity.x
                    var ty = next_entity["y"] if e_type == "wall" else next_entity.y

                    self.world.add_event("visual_effect", {"type": "line", "x": ct_x, "y": ct_y, "tx": tx, "ty": ty, "color": "yellow"})

                    if e_type == "wall":
                        hit_entities.append(next_entity["name"])
                        # Create an object to act as the current target for next iteration
                        var temp_target = RefCounted.new()
                        temp_target.set_meta("x", tx)
                        temp_target.set_meta("y", ty)
                        current_target = temp_target
                    else:
                        hit_entities.append(next_entity)
                        current_target = next_entity

                    jump_count += 1

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
        var b_type_slip = my_ball.get("ball_type") if typeof(my_ball) == TYPE_OBJECT or (typeof(my_ball) == TYPE_DICTIONARY and my_ball.has("ball_type")) else ""
        if world.arena.get("is_snowing") == true and not is_wind_riding_f and b_type_slip != "snow_yeti":
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

    var in_anomaly_zone = false
    if world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
        for h in world.arena.hazards:
            var h_kind = h.kind if "kind" in h else (h.get_meta("kind") if h.has_method("has_meta") and h.has_meta("kind") else "")
            if h_kind == "anomaly_zone":
                var hx = h.x if "x" in h else h.get_meta("x")
                var hy = h.y if "y" in h else h.get_meta("y")
                var hr = h.radius if "radius" in h else h.get_meta("radius")
                var active = h.active if "active" in h else (h.get_meta("active") if h.has_method("has_meta") and h.has_meta("active") else true)
                if active:
                    var dx = hx - my_ball.x
                    var dy = hy - my_ball.y
                    if dx*dx + dy*dy <= hr*hr:
                        in_anomaly_zone = true
                        break
    if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
        my_ball.set_meta("in_anomaly_zone", in_anomaly_zone)
    elif typeof(my_ball) == TYPE_DICTIONARY:
        my_ball["in_anomaly_zone"] = in_anomaly_zone

    var gm = null
    if world != null and "game_mode" in world:
        gm = world.game_mode
    var is_zero_gravity = false
    if in_anomaly_zone:
        is_zero_gravity = true
    elif gm != null:
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

        var cosmetic_val = ""
        if "cosmetic" in my_ball:
            cosmetic_val = str(my_ball.cosmetic).to_lower().replace(" ", "_")
        elif my_ball.has_method("get_meta") and my_ball.has_meta("cosmetic"):
            cosmetic_val = str(my_ball.get_meta("cosmetic")).to_lower().replace(" ", "_")

        if cosmetic_val == "magnetic_boots":
            base_s *= 0.9

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
        var is_night = false
        var is_lunar = false
        if self.world != null and "arena" in self.world:
            if "is_night" in self.world.arena:
                is_night = self.world.arena.is_night
            if "is_lunar_eclipse" in self.world.arena:
                is_lunar = self.world.arena.is_lunar_eclipse

        if self.world != null and "arena" in self.world and ("is_night" in self.world.arena or "is_lunar_eclipse" in self.world.arena):
            var b_type_action = ""
            if "ball_type" in my_ball:
                b_type_action = str(my_ball.ball_type).to_lower()

            if is_lunar:
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
                elif b_type_action == "paladin" or b_type_action == "guardian":
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed") * 1.2
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.5
                else:
                    if "speed" in my_ball:
                        my_ball.speed = my_ball.get_meta("base_speed")
                    if "damage" in my_ball:
                        my_ball.damage = my_ball.get_meta("base_damage") * 1.2
            elif is_night:
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

        # Apply global eclipse effect across all strategies early in the tick
        if self.world != null and "arena" in self.world and "is_eclipse" in self.world.arena and self.world.arena.is_eclipse:
            if "damage" in my_ball:
                my_ball.damage *= 2.0

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

        var sc_timer = 0.0
        if my_ball.has_method("has_meta") and my_ball.has_meta("supercharge_timer"):
            sc_timer = float(my_ball.get_meta("supercharge_timer"))
        elif "supercharge_timer" in my_ball:
            sc_timer = float(my_ball.supercharge_timer)

        if sc_timer > 0.0:
            if "speed" in my_ball:
                my_ball.speed *= 1.5
            if "damage" in my_ball:
                my_ball.damage *= 1.5

        var burst_timer = 0.0
        if my_ball.has_method("has_meta") and my_ball.has_meta("stamina_speed_burst_timer"):
            burst_timer = my_ball.get_meta("stamina_speed_burst_timer")
        elif "stamina_speed_burst_timer" in my_ball:
            burst_timer = my_ball.stamina_speed_burst_timer

        if burst_timer > 0.0:
            if my_ball.has_method("set_meta"):
                my_ball.set_meta("stamina_speed_burst_timer", burst_timer - delta)
            elif "stamina_speed_burst_timer" in my_ball:
                my_ball.stamina_speed_burst_timer = burst_timer - delta

            if "speed" in my_ball:
                var b_speed = 2.0
                if my_ball.has_method("has_meta") and my_ball.has_meta("base_speed"):
                    b_speed = my_ball.get_meta("base_speed")
                elif "base_speed" in my_ball:
                    b_speed = my_ball.base_speed

                var can_burst = true
                var s_timer = 0.0
                var sl_timer = 0.0

                if my_ball.has_method("has_meta") and my_ball.has_meta("stutter_timer"):
                    s_timer = my_ball.get_meta("stutter_timer")
                elif "stutter_timer" in my_ball:
                    s_timer = float(my_ball.stutter_timer)

                if my_ball.has_method("has_meta") and my_ball.has_meta("slow_timer"):
                    sl_timer = my_ball.get_meta("slow_timer")
                elif "slow_timer" in my_ball:
                    sl_timer = float(my_ball.slow_timer)

                if s_timer > 0.0 or sl_timer > 0.0:
                    can_burst = false

                if can_burst:
                    my_ball.speed = b_speed * 1.5

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
        # Check for elite minion evolution
        var is_elite_minion = false
        if self.ball.has_method("has_meta") and self.ball.has_meta("is_elite_minion"):
            is_elite_minion = self.ball.get_meta("is_elite_minion")

        if not is_elite_minion:
            var survival_time = 0.0
            if self.ball.has_method("has_meta") and self.ball.has_meta("survival_time"):
                survival_time = self.ball.get_meta("survival_time")
            survival_time += delta
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("survival_time", survival_time)

            var kills = 0
            if "kills" in self.ball:
                kills = self.ball.kills
            elif self.ball.has_method("has_meta") and self.ball.has_meta("kills"):
                kills = self.ball.get_meta("kills")

            if survival_time > 30.0 or kills >= 1:
                is_elite_minion = true
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("is_elite_minion", true)
                var max_hp = 40.0
                if "max_hp" in self.ball:
                    self.ball.max_hp *= 2.0
                    max_hp = self.ball.max_hp
                self.ball.hp = max_hp
                if "damage" in self.ball:
                    self.ball.damage *= 1.5
                if "base_damage" in self.ball:
                    self.ball.base_damage *= 1.5
                if "ball_type" in self.ball:
                    self.ball.ball_type = "elite_minion"
                if "add_event" in self.world:
                    self.world.add_event("minion_evolution", {"minion_id": self.ball.id})

        if is_elite_minion:
            # Autonomous ranged attack for elite minion
            var ranged_attack_timer = 2.0
            if self.ball.has_method("has_meta") and self.ball.has_meta("ranged_attack_timer"):
                ranged_attack_timer = self.ball.get_meta("ranged_attack_timer")
            ranged_attack_timer -= delta
            if ranged_attack_timer <= 0:
                ranged_attack_timer = 2.0
                var enemies = []
                if "balls" in self.world:
                    for b in self.world.balls:
                        var b_team = ""
                        if typeof(b) == TYPE_DICTIONARY and "team" in b: b_team = b.team
                        elif "team" in b: b_team = b.team

                        var my_team = ""
                        if "team" in self.ball: my_team = self.ball.team

                        var b_alive = true
                        if typeof(b) == TYPE_DICTIONARY and "alive" in b: b_alive = b.alive
                        elif "alive" in b: b_alive = b.alive

                        if b_team != my_team and b_alive:
                            enemies.append(b)
                if enemies.size() > 0:
                    var closest_enemy = enemies[0]
                    var b_x = closest_enemy.x if typeof(closest_enemy) != TYPE_DICTIONARY else closest_enemy.x
                    var b_y = closest_enemy.y if typeof(closest_enemy) != TYPE_DICTIONARY else closest_enemy.y
                    var min_dist = sqrt(pow(b_x - self.ball.x, 2) + pow(b_y - self.ball.y, 2))

                    for b in enemies:
                        var ex = b.x if typeof(b) != TYPE_DICTIONARY else b.x
                        var ey = b.y if typeof(b) != TYPE_DICTIONARY else b.y
                        var dist = sqrt(pow(ex - self.ball.x, 2) + pow(ey - self.ball.y, 2))
                        if dist < min_dist:
                            min_dist = dist
                            closest_enemy = b

                    if min_dist < 200:
                        var dmg = 5.0
                        if "damage" in self.ball:
                            dmg = self.ball.damage * 0.5
                        if typeof(closest_enemy) == TYPE_DICTIONARY:
                            closest_enemy.hp -= dmg
                        else:
                            closest_enemy.hp -= dmg
                        if "add_event" in self.world:
                            var c_id = closest_enemy.id if typeof(closest_enemy) != TYPE_DICTIONARY else closest_enemy.id
                            self.world.add_event("ranged_attack", {"attacker_id": self.ball.id, "target_id": c_id})

            if self.ball.has_method("set_meta"):
                self.ball.set_meta("ranged_attack_timer", ranged_attack_timer)

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
        else:
            var owner_id = null
            if "owner_id" in my_ball:
                owner_id = my_ball.owner_id
            elif my_ball.has_method("get_meta") and my_ball.has_meta("owner_id"):
                owner_id = my_ball.get_meta("owner_id")

            if owner_id != null and world != null and "balls" in world:
                var owner = null
                for b in world.balls:
                    var b_id = null
                    if "id" in b: b_id = b.id
                    elif b.has_method("get_meta") and b.has_meta("id"): b_id = b.get_meta("id")

                    var b_alive = true
                    if "alive" in b: b_alive = b.alive
                    elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                    if b_id == owner_id and b_alive:
                        owner = b
                        break

                if owner != null:
                    var is_turret = false
                    if "is_turret" in my_ball: is_turret = my_ball.is_turret
                    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_turret"): is_turret = my_ball.get_meta("is_turret")

                    if is_turret:
                        self._chase(delta)
                        return

                    var is_orbiting = false
                    if "is_orbiting" in my_ball: is_orbiting = my_ball.is_orbiting
                    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_orbiting"): is_orbiting = my_ball.get_meta("is_orbiting")

                    var is_mirroring = false
                    if "is_mirroring" in my_ball: is_mirroring = my_ball.is_mirroring
                    elif my_ball.has_method("get_meta") and my_ball.has_meta("is_mirroring"): is_mirroring = my_ball.get_meta("is_mirroring")

                    if is_orbiting:
                        var spd = 4.0
                        if "speed" in my_ball: spd = float(my_ball.speed)
                        var orbit_speed = spd * 0.5

                        var orbit_angle = 0.0
                        if "orbit_angle" in my_ball: orbit_angle = my_ball.orbit_angle
                        elif my_ball.has_method("get_meta") and my_ball.has_meta("orbit_angle"): orbit_angle = my_ball.get_meta("orbit_angle")

                        orbit_angle += orbit_speed * delta

                        if "orbit_angle" in my_ball: my_ball.orbit_angle = orbit_angle
                        elif my_ball.has_method("set_meta"): my_ball.set_meta("orbit_angle", orbit_angle)

                        var radius = 30.0
                        my_ball.x = owner.x + cos(orbit_angle) * radius
                        my_ball.y = owner.y + sin(orbit_angle) * radius
                    elif is_mirroring:
                        var mx = null
                        var my = null
                        if "mirror_center_x" in my_ball:
                            mx = my_ball.mirror_center_x
                            my = my_ball.mirror_center_y
                        elif my_ball.has_method("get_meta") and my_ball.has_meta("mirror_center_x"):
                            mx = my_ball.get_meta("mirror_center_x")
                            my = my_ball.get_meta("mirror_center_y")

                        if mx == null:
                            mx = (owner.x + my_ball.x) / 2.0
                            my = (owner.y + my_ball.y) / 2.0
                            if "mirror_center_x" in my_ball:
                                my_ball.mirror_center_x = mx
                                my_ball.mirror_center_y = my
                            elif my_ball.has_method("set_meta"):
                                my_ball.set_meta("mirror_center_x", mx)
                                my_ball.set_meta("mirror_center_y", my)

                        my_ball.x = mx - (owner.x - mx)
                        my_ball.y = my - (owner.y - my)

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
                                    var b_decoy_type = b.decoy_type if "decoy_type" in b else (b.get_meta("decoy_type") if b.has_method("has_meta") and b.has_meta("decoy_type") else "")
                                    if b_decoy_type == "stun_trap":
                                        if "stutter_timer" in other:
                                            other.stutter_timer += 5.0
                                        elif other.has_method("set_meta") and other.has_meta("stutter_timer"):
                                            other.set_meta("stutter_timer", other.get_meta("stutter_timer") + 5.0)
                                        elif other.has_method("set_meta"):
                                            other.set_meta("stutter_timer", 5.0)
                                    elif b_decoy_type == "explosive":
                                        if "hp" in other:
                                            other.hp -= explosion_damage
                                        if "stutter_timer" in other:
                                            other.stutter_timer += 2.0
                                        elif other.has_method("set_meta") and other.has_meta("stutter_timer"):
                                            other.set_meta("stutter_timer", other.get_meta("stutter_timer") + 2.0)
                                        elif other.has_method("set_meta"):
                                            other.set_meta("stutter_timer", 2.0)
                                    else:
                                        if "hp" in other:
                                            other.hp -= explosion_damage
                                        if "stutter_timer" in other:
                                            other.stutter_timer += 2.0
                                        elif other.has_method("set_meta") and other.has_meta("stutter_timer"):
                                            other.set_meta("stutter_timer", other.get_meta("stutter_timer") + 2.0)
                                        elif other.has_method("set_meta"):
                                            other.set_meta("stutter_timer", 2.0)

                                    if "hp" in other:
                                        var rng = RandomNumberGenerator.new()
                                        rng.randomize()
                                        var b_type = b.ball_type if "ball_type" in b else (b.get_meta("ball_type") if b.has_method("has_meta") and b.has_meta("ball_type") else "")
                                        var b_team_check = b.team if "team" in b else (b.get_meta("team") if b.has_method("has_meta") and b.has_meta("team") else "")

                                        if b_type == "trickster" or b_team_check == "trickster":
                                            if "stutter_timer" in other:
                                                other.stutter_timer += 1.5
                                            elif other.has_method("set_meta") and other.has_meta("stutter_timer"):
                                                other.set_meta("stutter_timer", other.get_meta("stutter_timer") + 1.5)
                                            elif other.has_method("set_meta"):
                                                other.set_meta("stutter_timer", 1.5)

                                            if world != null and "events" in world:
                                                world.events.append({"type": "visual_effect", "data": {"type": "noise", "x": other.x, "y": other.y, "intensity": 0.5}})

                                                for i in range(4):
                                                    var angle = rng.randf_range(0.0, 2.0 * PI)
                                                    var tx = other.x + cos(angle) * 150.0
                                                    var ty = other.y + sin(angle) * 150.0
                                                    world.events.append({
                                                        "type": "visual_effect",
                                                        "data": {
                                                            "type": "fragmentation_projectile",
                                                            "x": b.x,
                                                            "y": b.y,
                                                            "tx": tx,
                                                            "ty": ty,
                                                            "bounce": true,
                                                            "color": "purple"
                                                        }
                                                    })

                                            if rng.randf() < 0.3:
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

                        var pull_radius = 150.0
                        if "balls" in world:
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
                                    var dx_other = other.x - b.x
                                    var dy_other = other.y - b.y
                                    var dist_other = sqrt(dx_other*dx_other + dy_other*dy_other)
                                    if dist_other <= pull_radius and dist_other > 0.0001:
                                        var pull_strength = 60.0
                                        other.x -= (dx_other/dist_other) * pull_strength
                                        other.y -= (dy_other/dist_other) * pull_strength

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

            var b_is_mimic_charging = false
            if "is_mimic_charging" in b: b_is_mimic_charging = b.is_mimic_charging
            elif b.has_method("get_meta") and b.has_meta("is_mimic_charging"): b_is_mimic_charging = b.get_meta("is_mimic_charging")
            if b_is_illusion and not b_is_mimic_clone and not b_is_mimic_charging:
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


    var has_hazard_immunity = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("hazard_immunity_timer") and self.ball.get_meta("hazard_immunity_timer") > 0:
        has_hazard_immunity = true
        var t = self.ball.get_meta("hazard_immunity_timer") - delta
        if t < 0: t = 0
        self.ball.set_meta("hazard_immunity_timer", t)
    elif "hazard_immunity_timer" in self.ball and self.ball.get("hazard_immunity_timer", 0) > 0:
        has_hazard_immunity = true
        self.ball.hazard_immunity_timer -= delta
        if self.ball.hazard_immunity_timer < 0:
            self.ball.hazard_immunity_timer = 0.0

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
            var ball_r = 10.0
            if "radius" in self.ball: ball_r = self.ball.radius
            elif self.ball.has_method("get_radius"): ball_r = self.ball.get_radius()
            if dist >= r - ball_r - 0.01:
                var is_immune = false
                if self.ball.has_meta("zone_immunity_timer") and self.ball.get_meta("zone_immunity_timer") > 0:
                    is_immune = true

                if not is_immune:
                    var zone_damage = 200.0 * delta
                    if self.ball.has_method("take_damage") and not has_hazard_immunity:
                        self.ball.take_damage(zone_damage)
                    elif "hp" in self.ball and not has_hazard_immunity:
                        self.ball.hp -= zone_damage
                        if self.ball.hp <= 0:
                            self.ball.alive = false


        var has_hazard_immunity = false
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("hazard_immunity_timer") and self.ball.get_meta("hazard_immunity_timer") > 0:
            has_hazard_immunity = true
            var t = self.ball.get_meta("hazard_immunity_timer") - delta
            if t < 0: t = 0
            self.ball.set_meta("hazard_immunity_timer", t)
        elif "hazard_immunity_timer" in self.ball and self.ball.hazard_immunity_timer > 0:
            has_hazard_immunity = true
            self.ball.hazard_immunity_timer -= delta
            if self.ball.hazard_immunity_timer < 0:
                self.ball.hazard_immunity_timer = 0.0

        if "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                if hazard.kind == "temporal_rift":
			continue
                if hazard.kind in ["explosive_barrel", "volatile_barrel"]:
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
                            if h_id != oh_id and other_hazard.kind in ["explosive_barrel", "volatile_barrel"]:
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
                            if hazard.kind == "volatile_barrel":
                                var h_arena = world.get("arena") if world.has_method("get") else world.get("arena", null)
                                if h_arena and typeof(h_arena) == TYPE_OBJECT and h_arena.has_method("get") and h_arena.get("hazards"):
                                    for oh in h_arena.get("hazards"):
                                        var h_id2 = hazard.get_instance_id() if typeof(hazard) == TYPE_OBJECT else hash(hazard)
                                        var oh_id2 = oh.get_instance_id() if typeof(oh) == TYPE_OBJECT else hash(oh)
                                        if h_id2 != oh_id2 and ("kind" in oh and oh.kind == "volatile_barrel"):
                                            var oh_exploded = oh.get_meta("is_exploded") if oh.has_meta("is_exploded") else false
                                            if not oh_exploded:
                                                var dx_oh = oh.x - hazard.x
                                                var dy_oh = oh.y - hazard.y
                                                if sqrt(dx_oh*dx_oh + dy_oh*dy_oh) < hazard.radius * 6:
                                                    oh.set_meta("is_exploded", true)
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
                    elif hazard.kind == "swap_trap":
                        var valid_targets = []
                        if "balls" in self.world:
                            var my_team = ""
                            if "team" in self.ball: my_team = self.ball.team
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
                            elif "ball_type" in self.ball: my_team = self.ball.ball_type
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): my_team = self.ball.get_meta("ball_type")

                            for b in self.world.balls:
                                if _get_id(b) != _get_id(self.ball):
                                    var b_alive = true
                                    var is_decoy = false
                                    if typeof(b) == TYPE_DICTIONARY:
                                        b_alive = b.get("alive", true)
                                        is_decoy = b.get("is_decoy", false)
                                    else:
                                        b_alive = b.alive if "alive" in b else true
                                        is_decoy = b.is_decoy if "is_decoy" in b else false
                                        if not is_decoy and b.has_method("get_meta") and b.has_meta("is_decoy"):
                                            is_decoy = b.get_meta("is_decoy")

                                    if b_alive and not is_decoy:
                                        var b_team = ""
                                        if typeof(b) == TYPE_DICTIONARY:
                                            b_team = b.get("team", b.get("ball_type", ""))
                                        else:
                                            if "team" in b: b_team = b.team
                                            elif b.has_method("get_meta") and b.has_meta("team"): b_team = b.get_meta("team")
                                            elif "ball_type" in b: b_team = b.ball_type
                                            elif b.has_method("get_meta") and b.has_meta("ball_type"): b_team = b.get_meta("ball_type")

                                        if b_team != my_team:
                                            valid_targets.append(b)

                            if valid_targets.size() == 0:
                                for b in self.world.balls:
                                    if _get_id(b) != _get_id(self.ball):
                                        var b_alive = true
                                        var is_decoy = false
                                        if typeof(b) == TYPE_DICTIONARY:
                                            b_alive = b.get("alive", true)
                                            is_decoy = b.get("is_decoy", false)
                                        else:
                                            b_alive = b.alive if "alive" in b else true
                                            is_decoy = b.is_decoy if "is_decoy" in b else false
                                            if not is_decoy and b.has_method("get_meta") and b.has_meta("is_decoy"):
                                                is_decoy = b.get_meta("is_decoy")

                                        if b_alive and not is_decoy:
                                            valid_targets.append(b)

                            if valid_targets.size() > 0:
                                var rng_target = valid_targets[self.world.math.randi() % valid_targets.size()]

                                var current_tick = 0
                                if "tick" in self.world: current_tick = self.world.tick

                                if typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["last_teleport_tick"] = current_tick
                                elif self.ball.has_method("set_meta"):
                                    self.ball.set_meta("last_teleport_tick", current_tick)
                                elif "last_teleport_tick" in self.ball:
                                    self.ball.last_teleport_tick = current_tick

                                if typeof(rng_target) == TYPE_DICTIONARY:
                                    rng_target["last_teleport_tick"] = current_tick
                                elif rng_target.has_method("set_meta"):
                                    rng_target.set_meta("last_teleport_tick", current_tick)
                                elif "last_teleport_tick" in rng_target:
                                    rng_target.last_teleport_tick = current_tick

                                var temp_x = _get_x(self.ball)
                                var temp_y = _get_y(self.ball)
                                var target_x = _get_x(rng_target)
                                var target_y = _get_y(rng_target)

                                _set_x(self.ball, target_x)
                                _set_y(self.ball, target_y)
                                _set_x(rng_target, temp_x)
                                _set_y(rng_target, temp_y)

                                if "events" in self.world:
                                    self.world.events.append({
                                        "type": "swap",
                                        "source": _get_id(self.ball),
                                        "target": _get_id(rng_target),
                                        "x": target_x,
                                        "y": target_y
                                    })

                        if typeof(hazard) == TYPE_DICTIONARY:
                            hazard["duration"] = 0.0
                        else:
                            hazard.duration = 0.0
                    elif hazard.kind == "trap":
                        var current_tick = 0
                        if "tick" in self.world:
                        current_tick = self.world.tick

                    var h_trap_variant = "normal"
                    if hazard.has_meta("trap_variant"):
                        h_trap_variant = hazard.get_meta("trap_variant")

                    if h_trap_variant == "hologram":
                        var hologram_spawned = false
                        if hazard.has_meta("hologram_spawned"):
                            hologram_spawned = hazard.get_meta("hologram_spawned")

                        if not hologram_spawned:
                            hazard.set_meta("hologram_spawned", true)
                            hazard.set_meta("duration", 0.0)
                                var target_to_clone = null
                                var nearest_dist = 9999999.0

                                if "boosters" in self.world:
                                    for b in self.world.boosters:
                                        var bx = 0.0
                                        if "x" in b: bx = float(b.x)
                                        elif typeof(b) != TYPE_DICTIONARY and b.has_method("get_meta") and b.has_meta("x"): bx = float(b.get_meta("x"))

                                        var by = 0.0
                                        if "y" in b: by = float(b.y)
                                        elif typeof(b) != TYPE_DICTIONARY and b.has_method("get_meta") and b.has_meta("y"): by = float(b.get_meta("y"))

                                        var d_sq = (bx - hazard.x)*(bx - hazard.x) + (by - hazard.y)*(by - hazard.y)
                                        if d_sq < nearest_dist:
                                            nearest_dist = d_sq
                                            target_to_clone = b

                            if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                                for h in self.world.arena.hazards:
                                    var hkind = ""
                                    if "kind" in h: hkind = h.kind
                                    elif typeof(h) != TYPE_DICTIONARY and h.has_method("get_meta") and h.has_meta("kind"): hkind = h.get_meta("kind")

                                    if hkind == "healing_spring":
                                        var hx = 0.0
                                        if "x" in h: hx = float(h.x)
                                        elif typeof(h) != TYPE_DICTIONARY and h.has_method("get_meta") and h.has_meta("x"): hx = float(h.get_meta("x"))

                                        var hy = 0.0
                                        if "y" in h: hy = float(h.y)
                                        elif typeof(h) != TYPE_DICTIONARY and h.has_method("get_meta") and h.has_meta("y"): hy = float(h.get_meta("y"))

                                        var d_sq = (hx - hazard.x)*(hx - hazard.x) + (hy - hazard.y)*(hy - hazard.y)
                                        if d_sq < nearest_dist:
                                            nearest_dist = d_sq
                                            target_to_clone = h

                            if target_to_clone == null:
                                if "balls" in self.world:
                                    for b in self.world.balls:
                                        var bid = null
                                        if "id" in b: bid = b.id
                                        elif b.has_method("get_meta") and b.has_meta("id"): bid = b.get_meta("id")

                                        var hid = null
                                        if "owner_id" in hazard: hid = hazard.owner_id
                                        elif hazard.has_method("get_meta") and hazard.has_meta("owner_id"): hid = hazard.get_meta("owner_id")

                                        if bid != null and bid == hid:
                                            target_to_clone = b
                                            break

                            if target_to_clone != null:
                                var holo = null
                                if typeof(target_to_clone) == TYPE_DICTIONARY:
                                    holo = target_to_clone.duplicate(true)
                                elif target_to_clone.has_method("duplicate"):
                                    holo = target_to_clone.duplicate()
                                else:
                                    holo = target_to_clone

                                var n_id = randi() % 90000 + 10000
                                if "next_id" in self.world:
                                    n_id = self.world.next_id
                                    self.world.next_id += 1

                                if "id" in holo: holo.id = n_id
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("id", n_id)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["id"] = n_id

                                if "x" in holo: holo.x = hazard.x
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("x", hazard.x)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["x"] = hazard.x

                                if "y" in holo: holo.y = hazard.y
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("y", hazard.y)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["y"] = hazard.y

                                if "hp" in holo: holo.hp = 10.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("hp", 10.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["hp"] = 10.0

                                if "max_hp" in holo: holo.max_hp = 10.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("max_hp", 10.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["max_hp"] = 10.0

                                if "is_hologram" in holo: holo.is_hologram = true
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("is_hologram", true)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["is_hologram"] = true

                                if "hologram_timer" in holo: holo.hologram_timer = 10.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("hologram_timer", 10.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["hologram_timer"] = 10.0

                                if "skill" in holo: holo.skill = null
                                elif typeof(holo) == TYPE_DICTIONARY: holo["skill"] = null
                                if "active_skill" in holo: holo.active_skill = null
                                elif typeof(holo) == TYPE_DICTIONARY: holo["active_skill"] = null
                                if "SKILL" in holo: holo.SKILL = null
                                elif typeof(holo) == TYPE_DICTIONARY: holo["SKILL"] = null

                                if "vx" in holo: holo.vx = 0.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("vx", 0.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["vx"] = 0.0

                                if "vy" in holo: holo.vy = 0.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("vy", 0.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["vy"] = 0.0

                                if "damage" in holo: holo.damage = 0.0
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("damage", 0.0)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["damage"] = 0.0

                                if "alive" in holo: holo.alive = true
                                elif typeof(holo) != TYPE_DICTIONARY and holo.has_method("set_meta"): holo.set_meta("alive", true)
                                elif typeof(holo) == TYPE_DICTIONARY: holo["alive"] = true

                                self.world.balls.append(holo)

                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                            hazard.set_meta("last_updated_tick", current_tick)

                            var has_spawned = false
                            if hazard.has_meta("hologram_spawned"):
                                has_spawned = hazard.get_meta("hologram_spawned")

                            if not has_spawned:
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
                elif hazard.kind == "portal" or hazard.kind == "teleporter" or hazard.kind == "one_way_teleporter" or hazard.kind == "wormhole" or hazard.kind == "quantum_teleporter":
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
                        var cooldown = 10
                        if hazard.kind == "quantum_teleporter":
                            cooldown = 30
                        if current_tick - last_teleport > cooldown:
                            if hazard.kind == "quantum_teleporter":
                                if hazard.has_meta("target_x") and hazard.has_meta("target_y"):
                                    var old_x = self.ball.x
                                    var old_y = self.ball.y
                                    self.ball.x = hazard.get_meta("target_x")
                                    self.ball.y = hazard.get_meta("target_y")

                                    if self.world.get("events") != null:
                                        var eff = {"type": "visual_effect", "data": {"x": old_x, "y": old_y, "target_x": self.ball.x, "target_y": self.ball.y, "kind": "quantum_trail"}}
                                        self.world.events.append(eff)

                                    if self.ball.has_method("set_meta"):
                                        self.ball.set_meta("last_teleport_tick", current_tick)
                                    break
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
                elif hazard.kind == "slip_zone":
                    var active = true
                    if hazard.has_method("get_meta") and hazard.has_meta("active"):
                        active = hazard.get_meta("active")
                    elif "active" in hazard:
                        active = hazard.active
                    if active:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq < hazard.radius * hazard.radius:
                            if "vx" in self.ball and "vy" in self.ball:
                                self.ball.x += self.ball.vx * delta
                                self.ball.y += self.ball.vy * delta
                            var base_s = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_s = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_s = self.ball.base_speed
                            self.ball.speed = base_s * 0.01
                            if self.ball.has_method("set_meta"):
                                self.ball.set_meta("is_slipping", true)
                elif hazard.kind == "frictionless_zone":
                    var active = true
                    if hazard.has_method("get_meta") and hazard.has_meta("active"):
                        active = hazard.get_meta("active")
                    elif "active" in hazard:
                        active = hazard.active
                    if active:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq < hazard.radius * hazard.radius:
                            if "vx" in self.ball and "vy" in self.ball:
                                self.ball.x += self.ball.vx * delta
                                self.ball.y += self.ball.vy * delta
                            var base_s = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_s = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_s = self.ball.base_speed
                            self.ball.speed = base_s * 0.001
                            if typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["is_frictionless"] = true
                            elif self.ball.has_method("set_meta"):
                                self.ball.set_meta("is_frictionless", true)
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

                elif hazard.kind == "fire_zone":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    var hr = hazard.radius
                    if dist_sq < hr * hr:
                        if "hp" in self.ball:
                            var dmg = 5.0 * delta
                            if "damage" in hazard: dmg = hazard.damage * delta
                            self.ball.hp -= dmg
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                                self.ball.hp = 0
                                if "killer" in self.ball:
                                    self.ball.killer = "fire_zone"
                elif hazard.kind == "quicksand":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta
                        if self.ball.has_method("take_damage") and not has_hazard_immunity:
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball and not has_hazard_immunity:
                            self.ball.hp -= hd
                            if self.ball.hp <= 0:
                                self.ball.alive = false

                        var has_wt = false
                        var bt = ""
                        if "ball_type" in self.ball: bt = str(self.ball.ball_type).to_lower()
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): bt = str(self.ball.get_meta("ball_type")).to_lower()
                        if "water" in bt or "swamp" in bt: has_wt = true
                        var tr = []
                        if "traits" in self.ball: tr = self.ball.traits
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("traits"): tr = self.ball.get_meta("traits")
                        if typeof(tr) == TYPE_ARRAY:
                            for t in tr:
                                if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
                                    has_wt = true

                        # Occasional slow debuff that lingers
                        if not has_wt:
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
                            else:
                                self.ball.quicksand_debuff_timer = debuff_timer

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.is_in_quicksand = true
                elif hazard.kind == "vortex":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var dist = sqrt(dist_sq)
                        if dist > 0.1:
                            var nx = dx / dist
                            var ny = dy / dist
                            var pull_strength = 50.0 * delta
                            if "x" in self.ball: self.ball.x += nx * pull_strength
                            elif self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + nx * pull_strength)
                            if "y" in self.ball: self.ball.y += ny * pull_strength
                            elif self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + ny * pull_strength)

                        var dmg = 10.0 * delta
                        if "damage" in hazard: dmg = hazard.damage * delta
                        elif hazard.has_method("get_meta") and hazard.has_meta("damage"): dmg = hazard.get_meta("damage") * delta

                        if "hp" in self.ball:
                            self.ball.hp -= dmg
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                                self.ball.hp = 0
                                if "killer" in self.ball:
                                    self.ball.killer = "vortex"

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("_chrono_slow", 0.5)
                        elif typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_chrono_slow"] = 0.5
                elif hazard.kind == "singularity":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var dist = sqrt(dist_sq)
                        if dist > 0.1:
                            var nx = dx / dist
                            var ny = dy / dist
                            var pull_strength = 80.0 * delta
                            if "x" in self.ball: self.ball.x += nx * pull_strength
                            elif self.ball.has_method("set_meta") and self.ball.has_meta("x"): self.ball.set_meta("x", self.ball.get_meta("x") + nx * pull_strength)
                            if "y" in self.ball: self.ball.y += ny * pull_strength
                            elif self.ball.has_method("set_meta") and self.ball.has_meta("y"): self.ball.set_meta("y", self.ball.get_meta("y") + ny * pull_strength)

                        var dmg = 30.0 * delta
                        if "damage" in hazard: dmg = hazard.damage * delta
                        elif hazard.has_method("get_meta") and hazard.has_meta("damage"): dmg = hazard.get_meta("damage") * delta

                        if "hp" in self.ball:
                            self.ball.hp -= dmg
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                                self.ball.hp = 0
                                if "killer" in self.ball:
                                    self.ball.killer = "singularity"

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("_chrono_slow", 0.4)
                        elif typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_chrono_slow"] = 0.4
                elif hazard.kind == "sinkhole":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta
                        if self.ball.has_method("take_damage") and not has_hazard_immunity:
                            self.ball.take_damage(hd)
                        elif "hp" in self.ball and not has_hazard_immunity:
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

                            if self.ball.has_method("take_damage") and not has_hazard_immunity:
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball and not has_hazard_immunity:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            # push AWAY from hazard
                            var nx = -dx / dist
                            var ny = -dy / dist
                            var push_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta

                            var cosmetic_val = ""
                            if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("cosmetic"):
                                cosmetic_val = str(self.ball["cosmetic"]).to_lower().replace(" ", "_")
                            elif typeof(self.ball) == TYPE_OBJECT and "cosmetic" in self.ball:
                                cosmetic_val = str(self.ball.cosmetic).to_lower().replace(" ", "_")
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("cosmetic"):
                                cosmetic_val = str(self.ball.get_meta("cosmetic")).to_lower().replace(" ", "_")

                            if cosmetic_val == "magnetic_boots":
                                push_strength *= 0.5

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

                            if self.ball.has_method("take_damage") and not has_hazard_immunity:
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball and not has_hazard_immunity:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    self.ball.alive = false

                        if dist_sq > 0.0001:
                            var dist = sqrt(dist_sq)
                            var nx = -dx / dist
                            var ny = -dy / dist
                            var push_strength = (hazard.radius * 2.0 / max(10.0, dist)) * 50.0 * delta

                            var cosmetic_val = ""
                            if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("cosmetic"):
                                cosmetic_val = str(self.ball["cosmetic"]).to_lower().replace(" ", "_")
                            elif typeof(self.ball) == TYPE_OBJECT and "cosmetic" in self.ball:
                                cosmetic_val = str(self.ball.cosmetic).to_lower().replace(" ", "_")
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("cosmetic"):
                                cosmetic_val = str(self.ball.get_meta("cosmetic")).to_lower().replace(" ", "_")

                            if cosmetic_val == "magnetic_boots":
                                push_strength *= 0.5

                            self.ball.x += nx * push_strength
                            self.ball.y += ny * push_strength
                elif hazard.kind == "gravity_well":
                    # Cosmetics: gravity anomaly already implemented
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy

                    # Random pairing logic
                    var has_paired_checked = false
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("paired_checked"):
                        has_paired_checked = true
                    elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("paired_checked"):
                        has_paired_checked = true

                    if not has_paired_checked:
                        if typeof(hazard) == TYPE_OBJECT:
                            hazard.set_meta("paired_checked", true)
                        else:
                            hazard["paired_checked"] = true

                        var has_paired_id = false
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("paired_id"):
                            has_paired_id = true
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("paired_id"):
                            has_paired_id = true

                        if not has_paired_id and randf() < 0.3:
                            var other_gws = []
                            for h in self.world.arena.hazards:
                                var h_kind = ""
                                if typeof(h) == TYPE_OBJECT:
                                    h_kind = h.kind if "kind" in h else ""
                                else:
                                    h_kind = h.get("kind", "")

                                var h_id = -1
                                if typeof(h) == TYPE_OBJECT:
                                    h_id = h.id if "id" in h else -1
                                else:
                                    h_id = h.get("id", -1)

                                var h_paired = false
                                if typeof(h) == TYPE_OBJECT and h.has_meta("paired_checked"):
                                    h_paired = true
                                elif typeof(h) == TYPE_DICTIONARY and h.has("paired_checked"):
                                    h_paired = true

                                var haz_id = -1
                                if typeof(hazard) == TYPE_OBJECT:
                                    haz_id = hazard.id if "id" in hazard else -1
                                else:
                                    haz_id = hazard.get("id", -1)

                                if h_kind == "gravity_well" and h_id != haz_id and not h_paired:
                                    other_gws.append(h)

                            if other_gws.size() > 0:
                                var selected_pair = other_gws[randi() % other_gws.size()]
                                var selected_id = -1
                                if typeof(selected_pair) == TYPE_OBJECT:
                                    selected_id = selected_pair.id if "id" in selected_pair else -1
                                else:
                                    selected_id = selected_pair.get("id", -1)

                                var haz_id2 = -1
                                if typeof(hazard) == TYPE_OBJECT:
                                    haz_id2 = hazard.id if "id" in hazard else -1
                                else:
                                    haz_id2 = hazard.get("id", -1)

                                if typeof(hazard) == TYPE_OBJECT:
                                    hazard.set_meta("paired_id", selected_id)
                                else:
                                    hazard["paired_id"] = selected_id

                                if typeof(selected_pair) == TYPE_OBJECT:
                                    selected_pair.set_meta("paired_id", haz_id2)
                                    selected_pair.set_meta("paired_checked", true)
                                else:
                                    selected_pair["paired_id"] = haz_id2
                                    selected_pair["paired_checked"] = true

                    if dist_sq < hazard.radius * hazard.radius:
                        # Wormhole teleport logic
                        var current_tick = 0
                        if typeof(self.world) == TYPE_OBJECT:
                            current_tick = self.world.tick if "tick" in self.world else 0
                        else:
                            current_tick = self.world.get("tick", 0)

                        var last_teleport = -100
                        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("last_teleport_tick"):
                            last_teleport = self.ball.get_meta("last_teleport_tick")
                        elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("last_teleport_tick"):
                            last_teleport = self.ball["last_teleport_tick"]
                        elif typeof(self.ball) == TYPE_OBJECT and "last_teleport_tick" in self.ball:
                            last_teleport = self.ball.last_teleport_tick

                        var h_paired_id = null
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("paired_id"):
                            h_paired_id = hazard.get_meta("paired_id")
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("paired_id"):
                            h_paired_id = hazard["paired_id"]

                        if h_paired_id != null and (current_tick - last_teleport > 20):
                            var target_pair = null
                            for h in self.world.arena.hazards:
                                var curr_id = -1
                                if typeof(h) == TYPE_OBJECT:
                                    curr_id = h.id if "id" in h else -1
                                else:
                                    curr_id = h.get("id", -1)

                                if curr_id == h_paired_id:
                                    target_pair = h
                                    break
                            if target_pair != null:
                                var angle = randf() * 2.0 * PI
                                var pair_radius = 50.0
                                if typeof(target_pair) == TYPE_OBJECT:
                                    pair_radius = target_pair.radius if "radius" in target_pair else 50.0
                                else:
                                    pair_radius = target_pair.get("radius", 50.0)

                                var launch_dist = pair_radius + 30.0

                                if typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["x"] = target_pair.x + cos(angle) * launch_dist
                                    self.ball["y"] = target_pair.y + sin(angle) * launch_dist
                                    self.ball["last_teleport_tick"] = current_tick
                                else:
                                    self.ball.x = target_pair.x + cos(angle) * launch_dist
                                    self.ball.y = target_pair.y + sin(angle) * launch_dist
                                    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                        self.ball.set_meta("last_teleport_tick", current_tick)
                                    else:
                                        self.ball.last_teleport_tick = current_tick

                                var temp_damage = 5.0
                                if typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["hp"] -= temp_damage
                                    if self.ball["hp"] <= 0:
                                        self.ball["hp"] = 0
                                        self.ball["alive"] = false
                                else:
                                    if self.ball.has_method("take_damage") and not has_hazard_immunity:
                                        self.ball.take_damage(temp_damage)
                                    elif "hp" in self.ball and not has_hazard_immunity:
                                        self.ball.hp -= temp_damage
                                        if self.ball.hp <= 0:
                                            self.ball.hp = 0
                                            self.ball.alive = false

                                if "events" in self.world:
                                    var eff = {}
                                    eff["type"] = "visual_effect"
                                    var b_x = 0
                                    var b_y = 0
                                    if typeof(self.ball) == TYPE_OBJECT:
                                        b_x = self.ball.x if "x" in self.ball else 0
                                        b_y = self.ball.y if "y" in self.ball else 0
                                    else:
                                        b_x = self.ball.get("x", 0)
                                        b_y = self.ball.get("y", 0)
                                    eff["data"] = {"x": b_x, "y": b_y, "kind": "teleport"}
                                    self.world.events.append(eff)
                                continue

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

                            if self.ball.has_method("take_damage") and not has_hazard_immunity:
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball and not has_hazard_immunity:
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
                elif hazard.kind in ["black_hole", "massive_black_hole", "tornado", "local_tornado", "portal", "teleporter", "one_way_teleporter", "swap_portal", "lightning_storm"]:
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

                        var h_lifetime = 0.0
                        if hazard.has_meta("lifetime"):
                            h_lifetime = hazard.get_meta("lifetime")

                        if hazard.kind in ["black_hole", "massive_black_hole"] and h_lifetime >= 10.0:
                            hazard.set_meta("duration", 0.0)

                            if "events" in self.world:
                                self.world.events.append({"type": "explosion", "x": hazard.x, "y": hazard.y})

                            var balls_list = []
                            if "balls" in self.world: balls_list = self.world.balls

                            for b in balls_list:
                                var is_alive = false
                                if "alive" in b: is_alive = b.alive
                                elif typeof(b) == TYPE_OBJECT and b.has_method("get"): is_alive = b.get("alive")

                                if is_alive:
                                    var bdx = hazard.x - b.x
                                    var bdy = hazard.y - b.y
                                    var bdist_sq = bdx * bdx + bdy * bdy
                                    var blast_radius = hazard.radius * 6.0

                                    if bdist_sq < blast_radius * blast_radius and bdist_sq > 0.0001:
                                        var bdist = sqrt(bdist_sq)
                                        var bnx = bdx / bdist
                                        var bny = bdy / bdist

                                        if typeof(b) == TYPE_OBJECT and b.has_method("take_damage"):
                                            b.take_damage(500.0)
                                        elif "hp" in b:
                                            b.hp -= 500.0
                                            if b.hp <= 0:
                                                b.hp = 0
                                                b.alive = false
                                                if "killer" in b: b.killer = "black_hole_explosion"

                                        var push_strength = 2000.0
                                        var has_vx = false
                                        if "vx" in b: has_vx = true
                                        elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vx"): has_vx = true
                                        var has_vy = false
                                        if "vy" in b: has_vy = true
                                        elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vy"): has_vy = true

                                        if has_vx and has_vy:
                                            var b_vx = 0.0
                                            if "vx" in b: b.vx -= bnx * push_strength
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"):
                                                b_vx = b.get_meta("vx")
                                                b.set_meta("vx", b_vx - bnx * push_strength)
                                            var b_vy = 0.0
                                            if "vy" in b: b.vy -= bny * push_strength
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"):
                                                b_vy = b.get_meta("vy")
                                                b.set_meta("vy", b_vy - bny * push_strength)
                                        else:
                                            b.x -= bnx * push_strength * delta
                                            b.y -= bny * push_strength * delta

                        var h_dur = 1.0
                        if hazard.has_meta("duration"): h_dur = hazard.get_meta("duration")

                        if h_dur > 0 and hazard.kind in ["black_hole", "massive_black_hole", "tornado", "local_tornado"] and "boosters" in self.world:
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
                                    if hazard.kind in ["black_hole", "massive_black_hole"] and hazard.has_meta("lifetime"):
                                        lifetime_mult = 1.0 + (hazard.get_meta("lifetime") / 10.0)
                                    var bpull_strength = (hazard.radius * 2.0 / bmin_dist) * 50.0 * delta * lifetime_mult
                                    b.x += bnx * bpull_strength
                                    b.y += bny * bpull_strength
                                    if hazard.kind in ["black_hole", "massive_black_hole"]:
                                        var has_vx = false
                                        if "vx" in b: has_vx = true
                                        elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vx"): has_vx = true
                                        var has_vy = false
                                        if "vy" in b: has_vy = true
                                        elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vy"): has_vy = true

                                        if has_vx and has_vy:
                                            var b_vx = 0.0
                                            if "vx" in b: b_vx = b.vx
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"): b_vx = b.get_meta("vx")
                                            var b_vy = 0.0
                                            if "vy" in b: b_vy = b.vy
                                            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"): b_vy = b.get_meta("vy")

                                            var speed = sqrt(b_vx * b_vx + b_vy * b_vy)
                                            if speed > 20.0:
                                                var slingshot_strength = bpull_strength * 2.0 / delta
                                                var dot = bnx * b_vx + bny * b_vy
                                                if dot > -speed * 0.8:
                                                    if "vx" in b: b.vx += bnx * slingshot_strength * delta
                                                    elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("vx", b_vx + bnx * slingshot_strength * delta)
                                                    if "vy" in b: b.vy += bny * slingshot_strength * delta
                                                    elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("vy", b_vy + bny * slingshot_strength * delta)
                                    if hazard.kind in ["tornado", "local_tornado"]:
                                        var tx = -bny
                                        var ty = bnx
                                        var orbital_strength = bpull_strength * 1.5
                                        b.x += tx * orbital_strength
                                        b.y += ty * orbital_strength

                    var h_dur = 1.0
                    if hazard.has_meta("duration"): h_dur = hazard.get_meta("duration")

                    if h_dur > 0 and hazard.kind in ["black_hole", "massive_black_hole", "tornado", "local_tornado"]:
                        var dx = hazard.x - self.ball.x
                        var dy = hazard.y - self.ball.y
                        var dist_sq = dx * dx + dy * dy
                        if dist_sq > 0.0001:
                            var lifetime_mult = 1.0
                            if hazard.kind in ["black_hole", "massive_black_hole"] and hazard.has_meta("lifetime"):
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
                            if hazard.kind in ["black_hole", "massive_black_hole"]:
                                var has_vx = false
                                if "vx" in self.ball: has_vx = true
                                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("vx"): has_vx = true
                                var has_vy = false
                                if "vy" in self.ball: has_vy = true
                                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("vy"): has_vy = true

                                if has_vx and has_vy:
                                    var b_vx = 0.0
                                    if "vx" in self.ball: b_vx = self.ball.vx
                                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"): b_vx = self.ball.get_meta("vx")
                                    var b_vy = 0.0
                                    if "vy" in self.ball: b_vy = self.ball.vy
                                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"): b_vy = self.ball.get_meta("vy")

                                    var speed = sqrt(b_vx * b_vx + b_vy * b_vy)
                                    if speed > 20.0:
                                        var slingshot_strength = pull_strength * 2.0 / delta
                                        var dot = nx * b_vx + ny * b_vy
                                        if dot > -speed * 0.8:
                                            if "vx" in self.ball: self.ball.vx += nx * slingshot_strength * delta
                                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("vx", b_vx + nx * slingshot_strength * delta)
                                            if "vy" in self.ball: self.ball.vy += ny * slingshot_strength * delta
                                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("vy", b_vy + ny * slingshot_strength * delta)
                            if hazard.kind in ["tornado", "local_tornado"]:
                                var tx = -ny
                                var ty = nx
                                var orbital_strength = pull_strength * 1.5
                                self.ball.x += tx * orbital_strength
                                self.ball.y += ty * orbital_strength

