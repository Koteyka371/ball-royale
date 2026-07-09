import re

with open('src/ai/game_modes.gd', 'r') as f:
    content = f.read()

# Make sure we only add it in the BattleRoyaleMode
# Let's find BattleRoyaleMode
# Add random_event_timer right after obstacle_timer in BattleRoyaleMode

parts = content.split('class BattleRoyaleMode extends GameMode:')
part1 = parts[0]
part2 = parts[1]

# In part2, replace obstacle_timer declaration
part2 = part2.replace('var obstacle_timer: float = 0.0', 'var obstacle_timer: float = 0.0\n\tvar random_event_timer: float = 0.0', 1)


loot_goblin_logic = """
		# Loot Goblin Event
		random_event_timer += delta
		if random_event_timer >= 25.0:
			random_event_timer = 0.0
			var event_type_idx = rng.randi() % 3
			var event_type = "loot_goblin"
			if event_type_idx == 1:
				event_type = "low_gravity_zone"
			elif event_type_idx == 2:
				event_type = "meteor_shower"

			if event_type == "loot_goblin":
				var new_goblin = {}
				new_goblin.id = 95000 + rng.randi() % 10000
				var arena_width = 1000.0
				var arena_height = 1000.0
				if world.has("arena") and typeof(world.arena) == TYPE_DICTIONARY:
					if world.arena.has("width"): arena_width = world.arena.width
					if world.arena.has("height"): arena_height = world.arena.height
				elif world.has("arena") and typeof(world.arena) == TYPE_OBJECT:
					if "width" in world.arena: arena_width = world.arena.width
					if "height" in world.arena: arena_height = world.arena.height

				new_goblin.x = rng.randf_range(100.0, arena_width - 100.0)
				new_goblin.y = rng.randf_range(100.0, arena_height - 100.0)
				new_goblin.vx = 0.0
				new_goblin.vy = 0.0
				new_goblin.radius = 15.0
				new_goblin.speed = 250.0
				new_goblin.damage = 0.0
				new_goblin.hp = 50.0
				new_goblin.max_hp = 50.0
				new_goblin.alive = true
				new_goblin.ball_type = "loot_goblin"
				new_goblin.team = "Goblins"

				if world.has("balls") and typeof(world.balls) == TYPE_ARRAY:
					world.balls.append(new_goblin)
					if world.has("entities") and typeof(world.entities) == TYPE_ARRAY and world.balls != world.entities:
						world.entities.append(new_goblin)

				if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
					world.add_event("loot_goblin_spawn", {"message": "A Loot Goblin has appeared! Catch it for rare boosters!"})
			elif event_type == "low_gravity_zone":
				var arena_width = 1000.0
				var arena_height = 1000.0
				if world.has("arena") and typeof(world.arena) == TYPE_DICTIONARY:
					if world.arena.has("width"): arena_width = world.arena.width
					if world.arena.has("height"): arena_height = world.arena.height
				elif world.has("arena") and typeof(world.arena) == TYPE_OBJECT:
					if "width" in world.arena: arena_width = world.arena.width
					if "height" in world.arena: arena_height = world.arena.height
				var cx = arena_width / 2.0
				var cy = arena_height / 2.0

				var h_id = 96000 + rng.randi() % 10000
				var low_grav = {
					"id": h_id,
					"x": cx,
					"y": cy,
					"radius": 50.0,
					"target_radius": 300.0,
					"kind": "low_gravity_zone",
					"damage": 0.0,
					"duration": 15.0
				}
				if world.has("arena"):
					var arena = world.arena
					if typeof(arena) == TYPE_DICTIONARY and arena.has("hazards") and typeof(arena.hazards) == TYPE_ARRAY:
						arena.hazards.append(low_grav)
					elif typeof(arena) == TYPE_OBJECT and "hazards" in arena and typeof(arena.hazards) == TYPE_ARRAY:
						arena.hazards.append(low_grav)
				if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
					world.add_event("low_gravity_zone", {"message": "A Low Gravity Zone is expanding in the center!"})
			elif event_type == "meteor_shower":
				weather = "meteor_shower"
				weather_timer = 0.0
				if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
					world.add_event("weather_change", {"weather": "meteor_shower", "message": "A sudden Meteor Shower has begun!"})

		# Update Loot Goblin Movement
		for b in balls:
			var b_alive = false
			if typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b.alive
			elif typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive

			var b_type = ""
			if typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b.ball_type
			elif typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type

			if b_alive and b_type == "loot_goblin":
				var nearest_player = null
				var min_dist = 999999.0

				var bx = 0.0
				var by = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					bx = b.x
					by = b.y
				else:
					bx = b.x
					by = b.y

				for p in balls:
					var p_alive = false
					if typeof(p) == TYPE_DICTIONARY and p.has("alive"): p_alive = p.alive
					elif typeof(p) == TYPE_OBJECT and "alive" in p: p_alive = p.alive

					var p_type = ""
					if typeof(p) == TYPE_DICTIONARY and p.has("ball_type"): p_type = p.ball_type
					elif typeof(p) == TYPE_OBJECT and "ball_type" in p: p_type = p.ball_type

					if p_alive and p_type != "spectator" and p_type != "loot_goblin":
						var px = 0.0
						var py = 0.0
						if typeof(p) == TYPE_DICTIONARY:
							px = p.x
							py = p.y
						else:
							px = p.x
							py = p.y

						var dx = px - bx
						var dy = py - by
						var dist = dx*dx + dy*dy
						if dist < min_dist:
							min_dist = dist
							nearest_player = p

				var speed = 250.0
				if typeof(b) == TYPE_DICTIONARY and b.has("speed"): speed = b.speed
				elif typeof(b) == TYPE_OBJECT and "speed" in b: speed = b.speed

				if nearest_player != null:
					var px = 0.0
					var py = 0.0
					if typeof(nearest_player) == TYPE_DICTIONARY:
						px = nearest_player.x
						py = nearest_player.y
					else:
						px = nearest_player.x
						py = nearest_player.y

					var dx = bx - px
					var dy = by - py
					var dist = sqrt(dx*dx + dy*dy)
					if dist > 0:
						var nx = dx/dist
						var ny = dy/dist
						if typeof(b) == TYPE_DICTIONARY:
							b.vx = nx * speed
							b.vy = ny * speed
						else:
							b.vx = nx * speed
							b.vy = ny * speed
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b.vx *= 0.95
						b.vy *= 0.95
					else:
						b.vx *= 0.95
						b.vy *= 0.95

				if typeof(b) == TYPE_DICTIONARY:
					b.x += b.vx * delta
					b.y += b.vy * delta
				else:
					b.x += b.vx * delta
					b.y += b.vy * delta

				var hp = 0.0
				if typeof(b) == TYPE_DICTIONARY and b.has("hp"): hp = b.hp
				elif typeof(b) == TYPE_OBJECT and "hp" in b: hp = b.hp

				if hp <= 0:
					if typeof(b) == TYPE_DICTIONARY:
						b.alive = false
					else:
						b.alive = false

					var boosters_array = null
					if typeof(world) == TYPE_DICTIONARY and world.has("boosters") and typeof(world.boosters) == TYPE_ARRAY:
						boosters_array = world.boosters
					elif typeof(world) == TYPE_OBJECT and "boosters" in world and typeof(world.boosters) == TYPE_ARRAY:
						boosters_array = world.boosters

					if boosters_array != null:
						var booster_kinds = ["damage_booster", "speed_booster", "shield_booster", "hp_booster"]
						for i in range(3):
							var b_id = 9100 + boosters_array.size() + rng.randi() % 1000
							var b_x = bx + rng.randf_range(-30, 30)
							var b_y = by + rng.randf_range(-30, 30)
							var chosen_kind = booster_kinds[rng.randi() % booster_kinds.size()]

							var dropped_booster = {
								"id": b_id,
								"x": b_x,
								"y": b_y,
								"kind": chosen_kind,
								"radius": 15.0,
								"ball_type": "booster",
								"active": true
							}
							boosters_array.append(dropped_booster)

		# Update Low Gravity Zone expansion
		var hazards_array = null
		if typeof(world) == TYPE_DICTIONARY and world.has("arena"):
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards") and typeof(world.arena.hazards) == TYPE_ARRAY:
				hazards_array = world.arena.hazards
			elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena and typeof(world.arena.hazards) == TYPE_ARRAY:
				hazards_array = world.arena.hazards
		elif typeof(world) == TYPE_OBJECT and "arena" in world:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards") and typeof(world.arena.hazards) == TYPE_ARRAY:
				hazards_array = world.arena.hazards
			elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena and typeof(world.arena.hazards) == TYPE_ARRAY:
				hazards_array = world.arena.hazards

		if hazards_array != null:
			var hazards_to_remove = []
			for h in hazards_array:
				var h_kind = ""
				if typeof(h) == TYPE_DICTIONARY and h.has("kind"): h_kind = h.kind
				elif typeof(h) == TYPE_OBJECT and "kind" in h: h_kind = h.kind

				if h_kind == "low_gravity_zone":
					var h_radius = 0.0
					if typeof(h) == TYPE_DICTIONARY and h.has("radius"): h_radius = h.radius
					elif typeof(h) == TYPE_OBJECT and "radius" in h: h_radius = h.radius

					var h_target_radius = h_radius
					if typeof(h) == TYPE_DICTIONARY and h.has("target_radius"): h_target_radius = h.target_radius
					elif typeof(h) == TYPE_OBJECT and "target_radius" in h: h_target_radius = h.target_radius

					if h_radius < h_target_radius:
						if typeof(h) == TYPE_DICTIONARY:
							h.radius += 20.0 * delta
						else:
							h.radius += 20.0 * delta

					var h_duration = 1.0
					var has_duration = false
					if typeof(h) == TYPE_DICTIONARY and h.has("duration"):
						h_duration = h.duration
						has_duration = true
					elif typeof(h) == TYPE_OBJECT and "duration" in h:
						h_duration = h.duration
						has_duration = true

					if has_duration:
						if typeof(h) == TYPE_DICTIONARY:
							h.duration -= delta
							if h.duration <= 0:
								hazards_to_remove.append(h)
						else:
							h.duration -= delta
							if h.duration <= 0:
								hazards_to_remove.append(h)

					var hx = 0.0
					var hy = 0.0
					if typeof(h) == TYPE_DICTIONARY:
						hx = h.x
						hy = h.y
					else:
						hx = h.x
						hy = h.y

					for b in balls:
						var b_alive = false
						if typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b.alive
						elif typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive

						if b_alive:
							var bx = 0.0
							var by = 0.0
							if typeof(b) == TYPE_DICTIONARY:
								bx = b.x
								by = b.y
							else:
								bx = b.x
								by = b.y

							var dist = sqrt((bx - hx)*(bx - hx) + (by - hy)*(by - hy))
							if dist < h_radius:
								var b_mass = 1.0
								if typeof(b) == TYPE_DICTIONARY and b.has("mass"): b_mass = b.mass
								elif typeof(b) == TYPE_OBJECT and "mass" in b: b_mass = b.mass

								var has_original = false
								var has_applied = false

								if typeof(b) == TYPE_DICTIONARY and b.has("_low_grav_applied"): has_applied = b._low_grav_applied
								elif typeof(b) == TYPE_OBJECT and "_low_grav_applied" in b: has_applied = b._low_grav_applied

								if not has_applied:
									if typeof(b) == TYPE_DICTIONARY:
										b._low_grav_applied = true
										b.original_mass = b_mass
										b.mass = b.original_mass * 0.5
									else:
										b._low_grav_applied = true
										b.original_mass = b_mass
										b.mass = b.original_mass * 0.5
							else:
								var has_applied = false
								if typeof(b) == TYPE_DICTIONARY and b.has("_low_grav_applied"): has_applied = b._low_grav_applied
								elif typeof(b) == TYPE_OBJECT and "_low_grav_applied" in b: has_applied = b._low_grav_applied

								if has_applied:
									var orig_mass = 1.0
									if typeof(b) == TYPE_DICTIONARY and b.has("original_mass"):
										orig_mass = b.original_mass
										b.erase("original_mass")
										b.erase("_low_grav_applied")
									elif typeof(b) == TYPE_OBJECT and "original_mass" in b:
										orig_mass = b.original_mass
										# Can't erase easily from objects, but we can set to false
										b._low_grav_applied = false

									if typeof(b) == TYPE_DICTIONARY:
										b.mass = orig_mass
									else:
										b.mass = orig_mass

			for h in hazards_to_remove:
				hazards_array.erase(h)
				for b in balls:
					var has_applied = false
					if typeof(b) == TYPE_DICTIONARY and b.has("_low_grav_applied"): has_applied = b._low_grav_applied
					elif typeof(b) == TYPE_OBJECT and "_low_grav_applied" in b: has_applied = b._low_grav_applied

					if has_applied:
						var orig_mass = 1.0
						if typeof(b) == TYPE_DICTIONARY and b.has("original_mass"):
							orig_mass = b.original_mass
							b.erase("original_mass")
							b.erase("_low_grav_applied")
						elif typeof(b) == TYPE_OBJECT and "original_mass" in b:
							orig_mass = b.original_mass
							b._low_grav_applied = false

						if typeof(b) == TYPE_DICTIONARY:
							b.mass = orig_mass
						else:
							b.mass = orig_mass
"""

# Replace match_time += delta with our logic, only replacing the first occurrence
# so we don't accidentally do it multiple times.
part2 = part2.replace('match_time += delta', 'match_time += delta\n' + loot_goblin_logic, 1)

with open('src/ai/game_modes.gd', 'w') as f:
    f.write(part1 + 'class BattleRoyaleMode extends GameMode:' + part2)
