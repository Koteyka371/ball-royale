import sys

def patch_file():
    with open('src/ai/game_modes.gd', 'r') as f:
        content = f.read()

    new_class = """
class ReverseDualPayloadMode extends GameMode:
	var payload_red
	var payload_blue

	func _init() -> void:
		name = "Reverse Dual Payload"
		description = "Each team pushes the enemy's payload to the opposing goal. Standing near your own payload deals damage."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		var valid_balls = []
		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				if b.get("ball_type", "") != "spectator":
					valid_balls.append(b)
			else:
				if b.get("ball_type") != "spectator":
					valid_balls.append(b)

		var mid = valid_balls.size() / 2
		var red_team = []
		var blue_team = []

		for i in range(valid_balls.size()):
			var b = valid_balls[i]
			if i < mid:
				if typeof(b) == TYPE_DICTIONARY:
					b["team"] = "Red"
				else:
					b.set("team", "Red")
				red_team.append(b)
			else:
				if typeof(b) == TYPE_DICTIONARY:
					b["team"] = "Blue"
				else:
					b.set("team", "Blue")
				blue_team.append(b)

		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				arena_width = world.arena.get("width")
				arena_height = world.arena.get("height")

		class PayloadObj:
			var ball_type = "payload"
			var is_payload = true
			var speed = 0.0
			var base_speed = 0.0
			var damage = 0.0
			var base_damage = 0.0
			var max_hp = 10000.0
			var hp = 10000.0
			var x = 0.0
			var y = 0.0
			var alive = true
			var team = ""
			var radius = 20.0
			var is_invulnerable = true

		if red_team.size() > 0:
			payload_red = PayloadObj.new()
			payload_red.x = arena_width - 100.0
			payload_red.y = arena_height / 2.0
			payload_red.team = "Red"
			balls.append(payload_red)

		if blue_team.size() > 0:
			payload_blue = PayloadObj.new()
			payload_blue.x = 100.0
			payload_blue.y = arena_height / 2.0
			payload_blue.team = "Blue"
			balls.append(payload_blue)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		var arena_width = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
			else:
				arena_width = world.arena.get("width")

		if payload_red != null and payload_red.alive:
			var pushers = 0
			for b in balls:
				if typeof(b) == TYPE_DICTIONARY:
					if b.get("ball_type", "") == "spectator" or not b.get("alive", false) or b.get("is_payload", false):
						continue
					var dx = b.get("x", 0) - payload_red.x
					var dy = b.get("y", 0) - payload_red.y
					if sqrt(dx*dx + dy*dy) <= 150.0:
						var team = b.get("team", "")
						if team == "Blue":
							pushers += 1
						elif team == "Red":
							b["hp"] = b.get("hp", 100.0) - 15.0 * delta
							if b["hp"] <= 0:
								b["alive"] = false
				else:
					if b.get("ball_type") == "spectator" or not b.get("alive") or b.get("is_payload"):
						continue
					var dx = b.get("x") - payload_red.x
					var dy = b.get("y") - payload_red.y
					if sqrt(dx*dx + dy*dy) <= 150.0:
						var team = b.get("team")
						if team == "Blue":
							pushers += 1
						elif team == "Red":
							b.set("hp", b.get("hp") - 15.0 * delta)
							if b.get("hp") <= 0:
								b.set("alive", false)

			if pushers > 0:
				var speed_mult = 1.0 + ((pushers - 1) * 0.5)
				payload_red.x -= 50.0 * delta * pushers * speed_mult
				if payload_red.x < 50.0:
					payload_red.x = 50.0

		if payload_blue != null and payload_blue.alive:
			var pushers = 0
			for b in balls:
				if typeof(b) == TYPE_DICTIONARY:
					if b.get("ball_type", "") == "spectator" or not b.get("alive", false) or b.get("is_payload", false):
						continue
					var dx = b.get("x", 0) - payload_blue.x
					var dy = b.get("y", 0) - payload_blue.y
					if sqrt(dx*dx + dy*dy) <= 150.0:
						var team = b.get("team", "")
						if team == "Red":
							pushers += 1
						elif team == "Blue":
							b["hp"] = b.get("hp", 100.0) - 15.0 * delta
							if b["hp"] <= 0:
								b["alive"] = false
				else:
					if b.get("ball_type") == "spectator" or not b.get("alive") or b.get("is_payload"):
						continue
					var dx = b.get("x") - payload_blue.x
					var dy = b.get("y") - payload_blue.y
					if sqrt(dx*dx + dy*dy) <= 150.0:
						var team = b.get("team")
						if team == "Red":
							pushers += 1
						elif team == "Blue":
							b.set("hp", b.get("hp") - 15.0 * delta)
							if b.get("hp") <= 0:
								b.set("alive", false)

			if pushers > 0:
				var speed_mult = 1.0 + ((pushers - 1) * 0.5)
				payload_blue.x += 50.0 * delta * pushers * speed_mult
				if payload_blue.x > arena_width - 50.0:
					payload_blue.x = arena_width - 50.0

	func check_winner(world, balls: Array):
		var arena_width = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
			else:
				arena_width = world.arena.get("width")

		var red_reached = false
		var blue_reached = false

		if payload_red != null and payload_red.x <= 100.0:
			red_reached = true
		if payload_blue != null and payload_blue.x >= arena_width - 100.0:
			blue_reached = true

		if red_reached and blue_reached:
			return "Draw"
		elif red_reached:
			return "Blue"
		elif blue_reached:
			return "Red"

		return null


"""
    content = content.replace("class DualPayloadMode extends GameMode:", new_class + "class DualPayloadMode extends GameMode:", 1)

    dict_entry = '\t"reverse_dual_payload": ReverseDualPayloadMode.new(),\n\t"dual_payload": DualPayloadMode.new(),'
    content = content.replace('\t"dual_payload": DualPayloadMode.new(),', dict_entry, 1)

    with open('src/ai/game_modes.gd', 'w') as f:
        f.write(content)

if __name__ == "__main__":
    patch_file()
