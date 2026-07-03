import re

with open('src/ai/game_modes.gd', 'r') as f:
    text = f.read()

search_mud_gd = """                if self.weather == "rain" and randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var mud = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 60.0, "quicksand", 0.0)
                    mud.set_meta("duration", 15.0)
                    world.arena.hazards.append(mud)"""

replace_mud_gd = """                var arena_name = "unknown"
                if "arena" in world and world.arena != null:
                    arena_name = str(world.arena.get_script().resource_path).to_lower()
                var is_dirt_sand = false
                if "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name:
                    is_dirt_sand = true
                elif "arena" in world and "is_sandstorming" in world.arena and world.arena.is_sandstorming:
                    is_dirt_sand = true

                if is_dirt_sand and self.weather == "rain" and randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var mud = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 60.0, "quicksand", 0.0)
                    mud.set_meta("duration", 15.0)
                    world.arena.hazards.append(mud)"""

if search_mud_gd in text:
    text = text.replace(search_mud_gd, replace_mud_gd)
    print("Replaced mud gd")
else:
    print("Could not find mud gd")


search_rain_gd = """                elif self.weather == "rain":
			if "speed" in b: b.speed = base_spd * 0.8
			if "damage" in b: b.damage = base_dmg"""

replace_rain_gd = """                elif self.weather == "rain":
			var has_wt = false
			var bt = ""
			if "ball_type" in b: bt = str(b.ball_type).to_lower()
			elif b.has_method("get_meta") and b.has_meta("ball_type"): bt = str(b.get_meta("ball_type")).to_lower()
			if "water" in bt or "swamp" in bt: has_wt = true
			var tr = []
			if "traits" in b: tr = b.traits
			elif b.has_method("get_meta") and b.has_meta("traits"): tr = b.get_meta("traits")
			if typeof(tr) == TYPE_ARRAY:
				for t in tr:
					if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
						has_wt = true
			if "speed" in b:
				if has_wt: b.speed = base_spd
				else: b.speed = base_spd * 0.8
			if "damage" in b: b.damage = base_dmg"""

if search_rain_gd in text:
    text = text.replace(search_rain_gd, replace_rain_gd)
    print("Replaced rain gd")
else:
    print("Could not find rain gd block")

with open('src/ai/game_modes.gd', 'w') as f:
    f.write(text)
