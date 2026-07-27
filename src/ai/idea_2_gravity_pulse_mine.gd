extends Node

var mode_name = "Gravity Pulse Mine Mode"
var description = "A rare drop hazard that periodically pulsates, pushing away enemies in a large radius but pulling in allies."
var spawn_timer = 0.0
var spawn_interval = 15.0

func setup(world, balls):
	pass

func tick(world, balls, delta=0.016):
	spawn_timer += delta

	if spawn_timer >= spawn_interval:
		spawn_timer = 0.0
		if world.get("arena") != null and world.arena.get("hazards") != null:
			var w = 1000.0
			var h = 1000.0
			if world.arena.get("width") != null:
				w = world.arena.width
			if world.arena.get("height") != null:
				h = world.arena.height

			var h_x = randf_range(100, w - 100)
			var h_y = randf_range(100, h - 100)

			var owner_team = "blue"
			var valid_balls = []
			for b in balls:
				if b.get("alive", true) and b.get("team") != null:
					valid_balls.append(b)
			if valid_balls.size() > 0:
				owner_team = valid_balls[randi() % valid_balls.size()].get("team", "blue")

			var mine = {
				"id": randi() % 900000 + 100000,
				"x": h_x,
				"y": h_y,
				"radius": 20.0,
				"kind": "idea_2_gravity_pulse_mine",
				"duration": 20.0,
				"damage": 0.0,
				"active": true,
				"team": owner_team,
				"pulse_timer": 0.0,
				"pulse_interval": 2.0,
				"pulse_radius": 250.0
			}
			world.arena.hazards.append(mine)

	if world.get("arena") != null and world.arena.get("hazards") != null:
		var hazards_to_remove = []
		for hazard in world.arena.hazards:
			if hazard.get("kind", "") == "idea_2_gravity_pulse_mine" and hazard.get("active", true):
				hazard["duration"] = hazard.get("duration", 20.0) - delta
				if hazard["duration"] <= 0:
					hazard["active"] = false
					hazards_to_remove.append(hazard)
					continue

				hazard["pulse_timer"] = hazard.get("pulse_timer", 0.0) + delta
				if hazard["pulse_timer"] >= hazard.get("pulse_interval", 2.0):
					hazard["pulse_timer"] -= hazard.get("pulse_interval", 2.0)

					var pulse_radius = hazard.get("pulse_radius", 250.0)
					var mine_team = hazard.get("team")

					for b in balls:
						if not b.get("alive", true):
							continue

						var dx = b.get("x", 0.0) - hazard.get("x", 0.0)
						var dy = b.get("y", 0.0) - hazard.get("y", 0.0)
						var dist_sq = dx * dx + dy * dy

						if dist_sq > 0 and dist_sq <= pulse_radius * pulse_radius:
							var dist = sqrt(dist_sq)
							var nx = dx / dist
							var ny = dy / dist

							var b_team = b.get("team")
							var strength = 200.0

							if b_team == mine_team:
								b["vx"] = b.get("vx", 0.0) - nx * strength
								b["vy"] = b.get("vy", 0.0) - ny * strength
							else:
								b["vx"] = b.get("vx", 0.0) + nx * strength
								b["vy"] = b.get("vy", 0.0) + ny * strength

		for hazard in hazards_to_remove:
			var index = world.arena.hazards.find(hazard)
			if index != -1:
				world.arena.hazards.remove_at(index)
