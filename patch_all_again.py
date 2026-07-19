import re

def patch_python_modes():
    with open('src/ai/game_modes.py', 'r') as f:
        content = f.read()

    booster_kind_replacement = """            # Spawn the corresponding booster
            booster_kind = None
            if self.current_weather == "blizzard":
                if self.random.random() < 0.3: booster_kind = "snow_globe_item"
                else: booster_kind = "thermal_booster"
            elif self.current_weather == "heatwave": booster_kind = "cooling_booster"
            elif self.current_weather == "acid_rain": booster_kind = "hazmat_booster"
            elif self.current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
            elif self.current_weather == "tsunami": booster_kind = "life_jacket_booster"
            elif self.current_weather == "meteor_shower": booster_kind = "meteor_shield_booster"
            elif self.current_weather == "ice": booster_kind = "thermal_booster"
            elif self.current_weather == "earthquake": booster_kind = "seismic_booster"
            elif self.current_weather == "violent_quake": booster_kind = "seismic_booster"
            elif self.current_weather == "giant_flood": booster_kind = "life_jacket_booster"
            elif self.current_weather == "solar_eclipse": booster_kind = "vision_booster"
            elif self.current_weather == "celestial_alignment": booster_kind = "starlight_booster"

            # Also spawn rain-exclusive umbrella booster in acid rain
            if self.current_weather == "acid_rain" and hasattr(world, "boosters"):
                arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") else 1000
                arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") else 1000
                class TempBooster:
                    def __init__(self, kind, x, y):
                        self.kind = kind
                        self.x = x
                        self.y = y
                        self.active = True
                        self.radius = 15.0
                if self.random.random() < 0.5:
                    world.boosters.append(TempBooster("umbrella_booster", self.random.uniform(100, arena_w - 100), self.random.uniform(100, arena_h - 100)))"""

    old_booster_kind = """            # Spawn the corresponding booster
            booster_kind = None
            if self.current_weather == "blizzard": booster_kind = "thermal_booster"
            elif self.current_weather == "heatwave": booster_kind = "cooling_booster"
            elif self.current_weather == "acid_rain": booster_kind = "hazmat_booster"
            elif self.current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
            elif self.current_weather == "tsunami": booster_kind = "life_jacket_booster"
            elif self.current_weather == "meteor_shower": booster_kind = "meteor_shield_booster"
            elif self.current_weather == "ice": booster_kind = "thermal_booster"
            elif self.current_weather == "earthquake": booster_kind = "seismic_booster"
            elif self.current_weather == "violent_quake": booster_kind = "seismic_booster"
            elif self.current_weather == "giant_flood": booster_kind = "life_jacket_booster"
            elif self.current_weather == "solar_eclipse": booster_kind = "vision_booster"
            elif self.current_weather == "celestial_alignment": booster_kind = "starlight_booster" """

    # We replace directly but using a strong anchor to find the text
    anchor_start = content.find('            # Spawn the corresponding booster')
    if anchor_start != -1:
        anchor_end = content.find('            # Spawn a Boss / Mega-Minion', anchor_start)
        if anchor_end != -1:
            content = content[:anchor_start] + booster_kind_replacement + "\n\n" + content[anchor_end:]
            print("Patched python modes spawning")

    with open('src/ai/game_modes.py', 'w') as f:
        f.write(content)

def patch_python_action():
    with open('src/ai/action.py', 'r') as f:
        content = f.read()

    # Search for booster collection logic in _collect_booster

    old_code = """                    elif kind == "cooling_booster":
                        b_obj.cooling_booster_timer = 10.0"""

    new_code = """                    elif kind == "cooling_booster":
                        b_obj.cooling_booster_timer = 10.0
                    elif kind == "snow_globe_item":
                        b_obj.snow_globe_immunity_timer = 10.0
                    elif kind == "umbrella_booster":
                        b_obj.umbrella_booster_timer = 15.0"""

    content = content.replace(old_code, new_code, 1)

    with open('src/ai/action.py', 'w') as f:
        f.write(content)

def patch_gd_modes():
    with open('src/ai/game_modes.gd', 'r') as f:
        content = f.read()

    new_booster_kind = """			var booster_kind = ""
			if current_weather == "blizzard":
				if randf() < 0.3:
					booster_kind = "snow_globe_item"
				else:
					booster_kind = "thermal_booster"
			elif current_weather == "heatwave": booster_kind = "cooling_booster"
			elif current_weather == "acid_rain": booster_kind = "hazmat_booster"
			elif current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
			elif current_weather == "tsunami": booster_kind = "life_jacket_booster"
			elif current_weather == "ice": booster_kind = "thermal_booster"
			elif current_weather == "earthquake": booster_kind = "seismic_booster"
			elif current_weather == "violent_quake": booster_kind = "seismic_booster"
			elif current_weather == "giant_flood": booster_kind = "life_jacket_booster"
			elif current_weather == "solar_eclipse": booster_kind = "vision_booster"
			elif current_weather == "celestial_alignment": booster_kind = "starlight_booster"

			if current_weather == "acid_rain" and world != null and "boosters" in world:
				var arena_w = 1000
				var arena_h = 1000
				if "arena" in world and world.arena != null:
					if "width" in world.arena: arena_w = world.arena.width
					if "height" in world.arena: arena_h = world.arena.height
				if randf() < 0.5:
					world.boosters.append({"kind": "umbrella_booster", "x": randf_range(100, arena_w - 100), "y": randf_range(100, arena_h - 100), "active": true, "radius": 15.0})"""

    anchor_start = content.find('			var booster_kind = ""')
    if anchor_start != -1:
        anchor_end = content.find('			var boss_map = {', anchor_start)
        if anchor_end != -1:
            content = content[:anchor_start] + new_booster_kind + "\n\n" + content[anchor_end:]
            print("Patched gd modes spawning")

    with open('src/ai/game_modes.gd', 'w') as f:
        f.write(content)

def patch_gd_action():
    with open('src/ai/action.gd', 'r') as f:
        content = f.read()

    # Search for booster collection logic in _collect_booster

    old_code = """					elif kind == "cooling_booster":
						if typeof(b_obj) == TYPE_DICTIONARY:
							b_obj["cooling_booster_timer"] = 10.0
						elif b_obj.has_method("set_meta"):
							b_obj.set_meta("cooling_booster_timer", 10.0)
						else:
							b_obj.cooling_booster_timer = 10.0"""

    new_code = """					elif kind == "cooling_booster":
						if typeof(b_obj) == TYPE_DICTIONARY:
							b_obj["cooling_booster_timer"] = 10.0
						elif b_obj.has_method("set_meta"):
							b_obj.set_meta("cooling_booster_timer", 10.0)
						else:
							b_obj.cooling_booster_timer = 10.0
					elif kind == "snow_globe_item":
						if typeof(b_obj) == TYPE_DICTIONARY:
							b_obj["snow_globe_immunity_timer"] = 10.0
						elif b_obj.has_method("set_meta"):
							b_obj.set_meta("snow_globe_immunity_timer", 10.0)
						else:
							b_obj.snow_globe_immunity_timer = 10.0
					elif kind == "umbrella_booster":
						if typeof(b_obj) == TYPE_DICTIONARY:
							b_obj["umbrella_booster_timer"] = 15.0
						elif b_obj.has_method("set_meta"):
							b_obj.set_meta("umbrella_booster_timer", 15.0)
						else:
							b_obj.umbrella_booster_timer = 15.0"""

    content = content.replace(old_code, new_code, 1)

    with open('src/ai/action.gd', 'w') as f:
        f.write(content)


patch_python_modes()
patch_python_action()
patch_gd_modes()
patch_gd_action()
print("Done patching all.")
