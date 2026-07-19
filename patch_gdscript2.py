import re

def patch_gd():
    with open('src/ai/game_modes.gd', 'r') as f:
        content = f.read()

    # Apply changes missing from git diff

    old_booster_kind = """			var booster_kind = ""
			if current_weather == "blizzard": booster_kind = "thermal_booster"
			elif current_weather == "heatwave": booster_kind = "cooling_booster"
			elif current_weather == "acid_rain": booster_kind = "hazmat_booster"
			elif current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
			elif current_weather == "tsunami": booster_kind = "life_jacket_booster"
			elif current_weather == "ice": booster_kind = "thermal_booster"
			elif current_weather == "earthquake": booster_kind = "seismic_booster"
			elif current_weather == "violent_quake": booster_kind = "seismic_booster"
			elif current_weather == "giant_flood": booster_kind = "life_jacket_booster"
			elif current_weather == "solar_eclipse": booster_kind = "vision_booster"
			elif current_weather == "celestial_alignment": booster_kind = "starlight_booster" """

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
					world.boosters.append({"kind": "umbrella_booster", "x": randf_range(100, arena_w - 100), "y": randf_range(100, arena_h - 100), "active": true, "radius": 15.0}) """

    content = content.replace(old_booster_kind, new_booster_kind, 1)

    old_acid_rain = """			elif current_weather == "acid_rain":
				if randf() < 0.2 * delta and world != null and "arena" in world and "hazards" in world.arena:"""

    new_acid_rain = """			elif current_weather == "acid_rain":
				var has_umbrella = b.has_meta("umbrella_booster_timer") and b.get_meta("umbrella_booster_timer") > 0.0
				if has_umbrella:
					if b.has_method("set_meta"):
						b.set_meta("is_slipping", false)
					else:
						b.is_slipping = false
				if randf() < 0.2 * delta and world != null and "arena" in world and "hazards" in world.arena:"""

    content = content.replace(old_acid_rain, new_acid_rain, 1)

    with open('src/ai/game_modes.gd', 'w') as f:
        f.write(content)

patch_gd()
print("Done patching game_modes.gd")
