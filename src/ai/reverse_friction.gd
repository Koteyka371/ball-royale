extends RefCounted

const GameMode = preload("res://src/ai/game_modes.gd").GameMode

class ReverseFrictionMode extends GameMode:
	var acceleration_rate = 0.5 # 50% increase per second

	func _init() -> void:
		name = "Reverse Friction"
		description = "Balls continuously accelerate as long as they are moving, turning the arena into a high-speed ping-pong match. Collisions deal extra damage based on speed."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		for b in balls:
			var alive = false
			if "alive" in b: alive = b.alive
			elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("alive"): alive = b.get_meta("alive")
			elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): alive = b.alive

			var b_type = ""
			if "ball_type" in b: b_type = b.ball_type
			elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("ball_type"): b_type = b.get_meta("ball_type")
			elif typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b.ball_type

			if alive and b_type != "spectator":
				var vx = 0.0
				var vy = 0.0
				if "vx" in b: vx = b.vx
				elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vx"): vx = b.get_meta("vx")
				elif typeof(b) == TYPE_DICTIONARY and b.has("vx"): vx = b.vx

				if "vy" in b: vy = b.vy
				elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("vy"): vy = b.get_meta("vy")
				elif typeof(b) == TYPE_DICTIONARY and b.has("vy"): vy = b.vy

				if abs(vx) > 0.1 or abs(vy) > 0.1:
					var new_vx = vx * (1.0 + acceleration_rate * delta)
					var new_vy = vy * (1.0 + acceleration_rate * delta)

					if typeof(b) == TYPE_OBJECT:
						if "vx" in b:
							b.vx = new_vx
							b.vy = new_vy
						elif b.has_method("set_meta"):
							b.set_meta("vx", new_vx)
							b.set_meta("vy", new_vy)
					elif typeof(b) == TYPE_DICTIONARY:
						b["vx"] = new_vx
						b["vy"] = new_vy
