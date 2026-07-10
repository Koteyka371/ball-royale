import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

anomaly_class_gd = """class PhysicsAnomalyEventMode extends GameMode:
	var event_timer = 0.0
	var event_active = false
	var event_duration = 0.0
	var cx = 500.0
	var cy = 500.0

	func _init():
		super._init()
		self.name = "Physics Anomaly Event"
		self.description = "A random event that alters the physics of the arena. Projectiles curve, movement speed is affected depending on the direction of travel relative to the anomaly's center."

	func tick(world: Object, balls: Array, delta: float = 0.016) -> void:
		if not event_active:
			event_timer += delta

		if not event_active and event_timer > 20.0:
			if randf() < 0.2:
				event_active = true
				event_duration = 15.0
				event_timer = 0.0
				if world.has_method("add_event"):
					world.add_event("physics_anomaly", {"active": true, "message": "Physics Anomaly detected! Projectiles curve and movement is distorted!"})
			else:
				event_timer = 0.0

		if "arena" in world and typeof(world.arena) != TYPE_DICTIONARY:
			var w = 1000.0
			var h = 1000.0
			if "width" in world.arena:
				w = world.arena.width
			elif world.arena.has_method("get"):
				w = world.arena.get("width")
			if "height" in world.arena:
				h = world.arena.height
			elif world.arena.has_method("get"):
				h = world.arena.get("height")
			cx = w / 2.0
			cy = h / 2.0
		elif "arena" in world and typeof(world.arena) == TYPE_DICTIONARY:
			cx = world.arena.get("width", 1000.0) / 2.0
			cy = world.arena.get("height", 1000.0) / 2.0

		if event_active:
			event_duration -= delta
			if event_duration <= 0:
				event_active = false
				event_timer = 0.0
				if world.has_method("add_event"):
					world.add_event("physics_anomaly", {"active": false})

			for b in balls:
				var alive = true
				if "alive" in b: alive = b.alive
				elif b.has_method("get"): alive = b.get("alive")
				if not alive: continue

				var bx = cx
				var by = cy
				if "x" in b: bx = b.x
				elif b.has_method("get"): bx = b.get("x")
				if "y" in b: by = b.y
				elif b.has_method("get"): by = b.get("y")

				var dx = cx - bx
				var dy = cy - by
				var dist = sqrt(dx*dx + dy*dy)

				var vx = 0.0
				var vy = 0.0
				if "vx" in b: vx = b.vx
				elif b.has_method("get"): vx = b.get("vx")
				if "vy" in b: vy = b.vy
				elif b.has_method("get"): vy = b.get("vy")

				var speed_sq = vx*vx + vy*vy
				if speed_sq > 0.01 and dist > 0.01:
					var ndx = dx / dist
					var ndy = dy / dist
					var spd = sqrt(speed_sq)
					var nvx = vx / spd
					var nvy = vy / spd

					var dot = ndx * nvx + ndy * nvy
					var speed_mod = 1.0 + (dot * 0.5)

					if typeof(b) == TYPE_DICTIONARY:
						b["physics_anomaly_speed_mod"] = speed_mod
					elif b.has_method("set_meta"):
						b.set_meta("physics_anomaly_speed_mod", speed_mod)
					else:
						b.physics_anomaly_speed_mod = speed_mod
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b["physics_anomaly_speed_mod"] = 1.0
					elif b.has_method("set_meta"):
						b.set_meta("physics_anomaly_speed_mod", 1.0)
					else:
						b.physics_anomaly_speed_mod = 1.0
		else:
			for b in balls:
				if typeof(b) == TYPE_DICTIONARY and b.has("physics_anomaly_speed_mod"):
					b.erase("physics_anomaly_speed_mod")
				elif typeof(b) != TYPE_DICTIONARY and b.has_method("has_meta") and b.has_meta("physics_anomaly_speed_mod"):
					b.remove_meta("physics_anomaly_speed_mod")

"""

content = content.replace("var GAME_MODES = {", anomaly_class_gd + "\nvar GAME_MODES = {")
content = content.replace('"reverse_gravity_event": ReverseGravityEventMode.new(),', '"reverse_gravity_event": ReverseGravityEventMode.new(),\n	"physics_anomaly_event": PhysicsAnomalyEventMode.new(),')

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
print("Updated src/ai/game_modes.gd")
