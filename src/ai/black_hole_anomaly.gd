extends Node

var mode_name = "Black Hole Anomaly"
var description = "Periodically, a massive gravity well appears that sucks in projecticles and items, changing weapon trajectories and creating a dangerous pull effect."

var anomaly_timer = 10.0
var active_timer = 0.0
var active = false
var anomaly_x = 500.0
var anomaly_y = 500.0
var radius = 300.0
var pull_strength = 200.0
var random = RandomNumberGenerator.new()

func setup(world, balls):
	anomaly_timer = 10.0
	active_timer = 0.0
	active = false
	random.randomize()
	if world.get("arena") != null:
		var arena = world.arena
		var arena_width = arena.get("width") if arena.get("width") != null else 1000
		var arena_height = arena.get("height") if arena.get("height") != null else 1000
		anomaly_x = random.randf_range(200, arena_width - 200)
		anomaly_y = random.randf_range(200, arena_height - 200)

func tick(world, balls, delta=0.016):
	if not active:
		anomaly_timer -= delta
		if anomaly_timer <= 0:
			active = true
			active_timer = 5.0
			if world.get("arena") != null:
				var arena = world.arena
				var arena_width = arena.get("width") if arena.get("width") != null else 1000
				var arena_height = arena.get("height") if arena.get("height") != null else 1000
				anomaly_x = random.randf_range(200, arena_width - 200)
				anomaly_y = random.randf_range(200, arena_height - 200)
			if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
				world.add_event("anomaly_spawn", {"message": "A Black Hole Anomaly has appeared!"})
	else:
		active_timer -= delta
		if active_timer <= 0:
			active = false
			anomaly_timer = 10.0
			if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
				world.add_event("anomaly_despawn", {"message": "The Black Hole Anomaly has dissipated."})
			return

		var entities = []
		if world.get("arena") != null and typeof(world.arena) == TYPE_OBJECT and world.arena.get("hazards") != null:
			for h in world.arena.hazards:
				entities.append(h)
		if world.get("boosters") != null:
			for b in world.boosters:
				entities.append(b)
		if world.get("projectiles") != null:
			for p in world.projectiles:
				entities.append(p)
		for b in balls:
			var b_type = b["ball_type"] if typeof(b) == TYPE_DICTIONARY else b.get("ball_type")
			if b_type == "projectile":
				entities.append(b)

		for entity in entities:
			var ex = entity["x"] if typeof(entity) == TYPE_DICTIONARY else entity.get("x")
			var ey = entity["y"] if typeof(entity) == TYPE_DICTIONARY else entity.get("y")

			if ex == null or ey == null:
				continue

			var dx = anomaly_x - ex
			var dy = anomaly_y - ey
			var dist = sqrt(dx*dx + dy*dy)

			if dist > 0 and dist < radius:
				var pull_force = (pull_strength * (1.0 - (dist / radius))) * delta

				if typeof(entity) == TYPE_DICTIONARY:
					if entity.has("vx"):
						entity["vx"] += (dx / dist) * pull_force
						entity["vy"] += (dy / dist) * pull_force
					else:
						entity["x"] += (dx / dist) * pull_force
						entity["y"] += (dy / dist) * pull_force
				else:
					if entity.get("vx") != null and entity.get("vy") != null:
						entity.set("vx", entity.get("vx") + (dx / dist) * pull_force)
						entity.set("vy", entity.get("vy") + (dy / dist) * pull_force)
					else:
						entity.set("x", entity.get("x") + (dx / dist) * pull_force)
						entity.set("y", entity.get("y") + (dy / dist) * pull_force)
