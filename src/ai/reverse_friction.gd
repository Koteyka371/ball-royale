extends GameMode
class_name ReverseFrictionMode

func _init() -> void:
	name = "Reverse Friction Mode"
	description = "Balls continuously accelerate as long as they are moving, turning the arena into a high-speed ping-pong match. Collisions deal extra damage based on speed."

func setup(world, balls: Array) -> void:
	super.setup(world, balls)
	if typeof(world) == TYPE_OBJECT and not "dead_balls" in world:
		world.dead_balls = []
	elif typeof(world) == TYPE_DICTIONARY and not world.has("dead_balls"):
		world["dead_balls"] = []

	for b in balls:
		var base_damage = 10.0
		if "base_damage" in b:
			base_damage = b.base_damage
		elif "damage" in b:
			base_damage = b.damage

		var base_speed = 100.0
		if "base_speed" in b:
			base_speed = b.base_speed
		elif "speed" in b:
			base_speed = b.speed

		if typeof(b) == TYPE_OBJECT:
			b.set_meta("base_damage", base_damage)
			b.set_meta("base_speed", base_speed)
			b.set_meta("is_frictionless", true)
			if not "base_damage" in b:
				b.base_damage = base_damage
			if not "base_speed" in b:
				b.base_speed = base_speed
			b.is_frictionless = true
		elif typeof(b) == TYPE_DICTIONARY:
			b["base_damage"] = base_damage
			b["base_speed"] = base_speed
			b["is_frictionless"] = true

func tick(world, balls: Array, delta: float = 0.016) -> void:
	super.tick(world, balls, delta)
	for b in balls:
		var alive = false
		if "alive" in b:
			alive = b.alive
		elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("alive"):
			alive = b.get_meta("alive")
		elif typeof(b) == TYPE_DICTIONARY and b.has("alive"):
			alive = b["alive"]

		if alive:
			var vx = 0.0
			var vy = 0.0
			if "vx" in b:
				vx = b.vx
			elif typeof(b) == TYPE_DICTIONARY and b.has("vx"):
				vx = b["vx"]

			if "vy" in b:
				vy = b.vy
			elif typeof(b) == TYPE_DICTIONARY and b.has("vy"):
				vy = b["vy"]

			if typeof(b) == TYPE_OBJECT:
				b.is_frictionless = true
				if b.has_method("set_meta"):
					b.set_meta("is_frictionless", true)
			elif typeof(b) == TYPE_DICTIONARY:
				b["is_frictionless"] = true

			var velocity_sq = vx * vx + vy * vy
			if velocity_sq > 1.0:
				var velocity = sqrt(velocity_sq)
				var acceleration = 50.0 * delta

				vx += (vx / velocity) * acceleration
				vy += (vy / velocity) * acceleration

				if "vx" in b:
					b.vx = vx
				elif typeof(b) == TYPE_DICTIONARY:
					b["vx"] = vx

				if "vy" in b:
					b.vy = vy
				elif typeof(b) == TYPE_DICTIONARY:
					b["vy"] = vy

				var current_speed = sqrt(vx * vx + vy * vy)

				var base_speed = 100.0
				if "base_speed" in b:
					base_speed = b.base_speed
				elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("base_speed"):
					base_speed = b.get_meta("base_speed")
				elif typeof(b) == TYPE_DICTIONARY and b.has("base_speed"):
					base_speed = b["base_speed"]

				var speed_ratio = 1.0
				if base_speed > 0:
					speed_ratio = current_speed / base_speed

				if speed_ratio < 1.0:
					speed_ratio = 1.0
				speed_ratio = min(speed_ratio, 5.0)

				var base_damage = 10.0
				if "base_damage" in b:
					base_damage = b.base_damage
				elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("base_damage"):
					base_damage = b.get_meta("base_damage")
				elif typeof(b) == TYPE_DICTIONARY and b.has("base_damage"):
					base_damage = b["base_damage"]

				if "damage" in b:
					b.damage = base_damage * speed_ratio
				elif typeof(b) == TYPE_DICTIONARY:
					b["damage"] = base_damage * speed_ratio
			else:
				var base_damage = 10.0
				if "base_damage" in b:
					base_damage = b.base_damage
				elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("base_damage"):
					base_damage = b.get_meta("base_damage")
				elif typeof(b) == TYPE_DICTIONARY and b.has("base_damage"):
					base_damage = b["base_damage"]

				if "damage" in b:
					b.damage = base_damage
				elif typeof(b) == TYPE_DICTIONARY:
					b["damage"] = base_damage
