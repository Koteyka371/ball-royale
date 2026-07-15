import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

acid_rain_block_search = """			elif current_weather == "acid_rain":
				if not has_hazmat:
					b.damage = b.get_meta("base_damage") * 1.5
					b.hp -= 10.0 * delta"""

acid_rain_block_replace = """			elif current_weather == "acid_rain":
				if randf() < 0.2 * delta and world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
					var HazardObj = load("res://src/arena/procedural_arena.gd").Hazard
					var h_id = 9500 + world.arena.hazards.size() + (randi() % 1000)
					var arena_w = world.arena.width if "width" in world.arena else 1000
					var arena_h = world.arena.height if "height" in world.arena else 1000
					var np = HazardObj.new(h_id, randf_range(50, arena_w - 50), randf_range(50, arena_h - 50), 40.0, "neutralizing_puddle", 0.0)
					np.duration = 10.0
					world.arena.hazards.append(np)

				if not has_hazmat:
					b.damage = b.get_meta("base_damage") * 1.5
					var b_type = b.get("ball_type") if typeof(b) == TYPE_DICTIONARY else b.ball_type
					if typeof(b_type) == TYPE_STRING: b_type = b_type.to_lower()
					var traits = b.get("traits") if typeof(b) == TYPE_DICTIONARY else (b.traits if "traits" in b else [])
					if typeof(traits) != TYPE_ARRAY: traits = []
					var is_metal = false
					if typeof(b_type) == TYPE_STRING and ("metal" in b_type or "armor" in b_type):
						is_metal = true
					if "metal" in traits or "armor" in traits:
						is_metal = true

					if is_metal:
						if typeof(b) == TYPE_DICTIONARY:
							if not b.has("base_max_hp"): b["base_max_hp"] = float(b.get("max_hp", 100.0))
							b["max_hp"] = max(1.0, b["max_hp"] - 5.0 * delta)
							if b["hp"] > b["max_hp"]: b["hp"] = b["max_hp"]
							b["defense_multiplier"] = b.get("defense_multiplier", 1.0) * 0.9
						else:
							if not b.has_meta("base_max_hp"): b.set_meta("base_max_hp", b.max_hp if "max_hp" in b else 100.0)
							b.max_hp = max(1.0, b.max_hp - 5.0 * delta)
							if b.hp > b.max_hp: b.hp = b.max_hp
							var cur_def = b.defense_multiplier if "defense_multiplier" in b else (b.get_meta("defense_multiplier") if b.has_meta("defense_multiplier") else 1.0)
							if "defense_multiplier" in b: b.defense_multiplier = cur_def * 0.9
							elif b.has_method("set_meta"): b.set_meta("defense_multiplier", cur_def * 0.9)
					else:
						b.hp -= 10.0 * delta"""

if acid_rain_block_search in content:
    content = content.replace(acid_rain_block_search, acid_rain_block_replace)
    with open("src/ai/game_modes.gd", "w") as f:
        f.write(content)
    print("Replaced successfully in src/ai/game_modes.gd")
else:
    print("Block not found in src/ai/game_modes.gd")
