import sys

def patch_gd_game_modes():
    filepath = "src/ai/game_modes.gd"
    with open(filepath, 'r') as f:
        content = f.read()

    search_str1 = """                elif self.weather == "sandstorm":
                    if "speed" in b: b.speed = base_spd * 0.7
                    if "damage" in b: b.damage = base_dmg
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 0.5)
                        b.set_meta("steering_mult", 0.5)
                        b.set_meta("attack_accuracy", 0.5)
                        var sand_timer = 0.0
                        if b.has_meta("sandstorm_timer"):
                            sand_timer = b.get_meta("sandstorm_timer")
                        sand_timer += delta
                        if sand_timer >= 1.0:
                            sand_timer = 0.0
                            if "hp" in b and not is_earth:
                                b.hp -= 1.0
                        b.set_meta("sandstorm_timer", sand_timer)
                    if randf() < 0.05 * delta and not is_earth:
                        if "hp" in b:
                            b.hp -= 20.0"""

    replace_str1 = """                elif self.weather == "sandstorm":
                    var near_shelter_or_flare = false
                    if world != null and "arena" in world and "hazards" in world.arena:
                        for h in world.arena.hazards:
                            var h_kind = ""
                            if "kind" in h: h_kind = h.kind
                            if h_kind == "shelter" or h_kind == "flare":
                                var hx = 0.0
                                var hy = 0.0
                                var hr = 0.0
                                if "x" in h: hx = h.x
                                if "y" in h: hy = h.y
                                if "radius" in h: hr = h.radius
                                if pow(hx - b.x, 2) + pow(hy - b.y, 2) <= pow(hr, 2):
                                    near_shelter_or_flare = true
                                    break

                    if not near_shelter_or_flare:
                        if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
                        elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
                        else: b.perception_radius = 250.0 * 0.3

                    if "speed" in b: b.speed = base_spd * 0.7
                    if "damage" in b: b.damage = base_dmg
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 0.5)
                        b.set_meta("steering_mult", 0.5)
                        b.set_meta("attack_accuracy", 0.5)
                        var sand_timer = 0.0
                        if b.has_meta("sandstorm_timer"):
                            sand_timer = b.get_meta("sandstorm_timer")
                        sand_timer += delta
                        if sand_timer >= 1.0:
                            sand_timer = 0.0
                            if "hp" in b and not is_earth:
                                b.hp -= 1.0
                        b.set_meta("sandstorm_timer", sand_timer)
                    if randf() < 0.05 * delta and not is_earth:
                        if "hp" in b:
                            b.hp -= 20.0"""

    search_str2 = """				elif weather == "sandstorm":
					if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "dust_mask")
					elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "dust_mask"
					var b_type = ""
					if typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b["ball_type"]
					elif typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type
					if b_type == "sand_elemental":
						if "speed" in b: b.speed = base_spd * 1.2
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 1.0)
							b.set_meta("steering_mult", 1.0)
						if "attack_accuracy" in b: b.attack_accuracy = 1.0
					else:
						if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
						elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
						else: b.perception_radius = 250.0 * 0.3
						if "speed" in b: b.speed = base_spd * 0.7
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 0.5)
							b.set_meta("steering_mult", 0.5)
						var bt = b_type
						if bt in ["trickster", "phantom", "mimic"]:
							if b.has_method("set_meta") and b.has_method("get_meta"):
								var mtimer = 0.0
								if b.has_meta("mirage_timer"): mtimer = b.get_meta("mirage_timer")
								mtimer += delta
								if mtimer >= 5.0: mtimer = 0.0
								b.set_meta("mirage_timer", mtimer)
						if b.has_method("set_meta") and b.has_method("get_meta"):
							var sand_timer = 0.0
							if b.has_meta("sandstorm_timer"): sand_timer = b.get_meta("sandstorm_timer")
							sand_timer += delta
							if sand_timer >= 1.0:
								sand_timer = 0.0
								if "hp" in b: b.hp -= 1.0
							b.set_meta("sandstorm_timer", sand_timer)
						if randf() < 0.05 * delta:
							if "hp" in b: b.hp -= 20.0
						if "attack_accuracy" in b: b.attack_accuracy = 0.5"""

    replace_str2 = """				elif weather == "sandstorm":
					if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "dust_mask")
					elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "dust_mask"
					var b_type = ""
					if typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b["ball_type"]
					elif typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type

					var b_traits = []
					if typeof(b) == TYPE_DICTIONARY and b.has("traits"): b_traits = b["traits"]
					elif typeof(b) == TYPE_OBJECT and "traits" in b: b_traits = b.traits
					var is_earth = b_type in ["tank", "druid", "juggernaut", "sand_elemental"] or "earth" in b_traits

					var near_shelter_or_flare = false
					if world != null and "arena" in world and "hazards" in world.arena:
						for h in world.arena.hazards:
							var h_kind = ""
							if "kind" in h: h_kind = h.kind
							if h_kind == "shelter" or h_kind == "flare":
								var hx = 0.0
								var hy = 0.0
								var hr = 0.0
								if "x" in h: hx = h.x
								if "y" in h: hy = h.y
								if "radius" in h: hr = h.radius
								var bx = 0.0
								var by = 0.0
								if typeof(b) == TYPE_DICTIONARY:
									if b.has("x"): bx = b["x"]
									if b.has("y"): by = b["y"]
								elif typeof(b) == TYPE_OBJECT:
									if "x" in b: bx = b.x
									if "y" in b: by = b.y
								if pow(hx - bx, 2) + pow(hy - by, 2) <= pow(hr, 2):
									near_shelter_or_flare = true
									break

					if b_type == "sand_elemental":
						if "speed" in b: b.speed = base_spd * 1.2
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 1.0)
							b.set_meta("steering_mult", 1.0)
						if "attack_accuracy" in b: b.attack_accuracy = 1.0
					else:
						if not near_shelter_or_flare:
							if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
							elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
							else: b.perception_radius = 250.0 * 0.3

						if "speed" in b: b.speed = base_spd * 0.7
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 0.5)
							b.set_meta("steering_mult", 0.5)
						var bt = b_type
						if bt in ["trickster", "phantom", "mimic"]:
							if b.has_method("set_meta") and b.has_method("get_meta"):
								var mtimer = 0.0
								if b.has_meta("mirage_timer"): mtimer = b.get_meta("mirage_timer")
								mtimer += delta
								if mtimer >= 5.0: mtimer = 0.0
								b.set_meta("mirage_timer", mtimer)
						if b.has_method("set_meta") and b.has_method("get_meta"):
							var sand_timer = 0.0
							if b.has_meta("sandstorm_timer"): sand_timer = b.get_meta("sandstorm_timer")
							sand_timer += delta
							if sand_timer >= 1.0:
								sand_timer = 0.0
								if "hp" in b and not is_earth: b.hp -= 1.0
							b.set_meta("sandstorm_timer", sand_timer)
						if randf() < 0.05 * delta and not is_earth:
							if "hp" in b: b.hp -= 20.0
						if "attack_accuracy" in b: b.attack_accuracy = 0.5"""

    if search_str1 in content and search_str2 in content:
        content = content.replace(search_str1, replace_str1)
        content = content.replace(search_str2, replace_str2)
        with open(filepath, 'w') as f:
            f.write(content)
        print("Updated GDScript game modes successfully.")
    else:
        print("Failed to find search_str in GDScript file.")

patch_gd_game_modes()
