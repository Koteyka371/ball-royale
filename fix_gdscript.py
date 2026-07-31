import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

# Find the start of the first AlternatingZoneMode class
first_idx = content.find("class AlternatingZoneMode extends GameMode:")

# Cut the content right before the first AlternatingZoneMode definition
content = content[:first_idx]

# Define the complete correct class block
new_class = """class AlternatingZoneMode extends GameMode:
	var zone_x: float = 500.0
	var zone_y: float = 500.0
	var zone_radius: float = 150.0
	var phase_duration: float = 5.0
	var phase_timer: float = 5.0
	var is_healing_phase: bool = true
	var heal_rate: float = 20.0
	var damage_rate: float = 20.0

	func _init() -> void:
		super._init()
		name = "Alternating Zone"
		description = "A central zone that alternates between healing players and damaging them every 5 seconds."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		var arena_width = 1000.0
		var arena_height = 1000.0
		if typeof(world) == TYPE_DICTIONARY and ("arena" in world):
			var arena = world.get("arena")
			if typeof(arena) == TYPE_DICTIONARY:
				arena_width = float(arena.get("width", 1000.0))
				arena_height = float(arena.get("height", 1000.0))
			elif typeof(arena) == TYPE_OBJECT:
				arena_width = float(arena.get("width") if "width" in arena else 1000.0)
				arena_height = float(arena.get("height") if "height" in arena else 1000.0)
		elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = float(world.arena.get("width", 1000.0))
				arena_height = float(world.arena.get("height", 1000.0))
			else:
				arena_width = float(world.arena.get("width") if "width" in world.arena else 1000.0)
				arena_height = float(world.arena.get("height") if "height" in world.arena else 1000.0)
		zone_x = arena_width / 2.0
		zone_y = arena_height / 2.0
		phase_timer = phase_duration
		is_healing_phase = true

	func tick(world, balls: Array, delta: float) -> void:
		super.tick(world, balls, delta)

		phase_timer -= delta
		if phase_timer <= 0:
			phase_timer = phase_duration
			is_healing_phase = not is_healing_phase
			var phase_name = "Healing" if is_healing_phase else "Damaging"
			if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
				world.add_event("alternating_zone_phase", {"message": "Zone changed to " + phase_name + " Phase!"})
			elif typeof(world) == TYPE_DICTIONARY and "events" in world:
				world["events"].append({"type": "alternating_zone_phase", "data": {"message": "Zone changed to " + phase_name + " Phase!"}})

		for b in balls:
			var is_alive = false
			if typeof(b) == TYPE_DICTIONARY and b.get("alive", false): is_alive = true
			elif typeof(b) == TYPE_OBJECT and b.get("alive"): is_alive = true

			var b_type = ""
			if typeof(b) == TYPE_DICTIONARY: b_type = b.get("ball_type", "")
			elif typeof(b) == TYPE_OBJECT: b_type = b.get("ball_type")

			if is_alive and b_type != "spectator":
				var bx = 0.0
				var by = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					bx = float(b.get("x", 0.0))
					by = float(b.get("y", 0.0))
				else:
					bx = float(b.get("x"))
					by = float(b.get("y"))

				var dist = sqrt((bx - zone_x) * (bx - zone_x) + (by - zone_y) * (by - zone_y))
				if dist <= zone_radius:
					if is_healing_phase:
						var max_hp = 100.0
						if typeof(b) == TYPE_DICTIONARY: max_hp = float(b.get("max_hp", 100.0))
						else: max_hp = float(b.get("max_hp"))

						var current_hp = 0.0
						if typeof(b) == TYPE_DICTIONARY: current_hp = float(b.get("hp", 100.0))
						else: current_hp = float(b.get("hp"))

						var new_hp = min(current_hp + heal_rate * delta, max_hp)
						if typeof(b) == TYPE_DICTIONARY: b["hp"] = new_hp
						else: b.set("hp", new_hp)

						if typeof(b) == TYPE_DICTIONARY: b["in_healing_zone"] = true
						else:
							if b.get_script() != null and "in_healing_zone" in b:
								b.set("in_healing_zone", true)
							else:
								b.set_meta("in_healing_zone", true)
					else:
						if typeof(world) == TYPE_OBJECT and world.has_method("_deal_damage"):
							world._deal_damage(null, b, damage_rate * delta)
						else:
							var current_hp = 0.0
							if typeof(b) == TYPE_DICTIONARY: current_hp = float(b.get("hp", 100.0))
							else: current_hp = float(b.get("hp"))

							if typeof(b) == TYPE_DICTIONARY: b["hp"] = current_hp - (damage_rate * delta)
							else: b.set("hp", current_hp - (damage_rate * delta))
"""

content = content + new_class + "\n"
with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
