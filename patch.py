import re
import sys

def modify_python_game_modes():
    path = "src/ai/game_modes.py"
    with open(path, "r") as f:
        content = f.read()

    # ExtremeWeatherMode.tick() modification
    repl = """
            # Spawn the corresponding booster
            booster_kind = None
            if self.current_weather == "blizzard": booster_kind = self.random.choice(["thermal_booster", "snow_globe_booster"])
            elif self.current_weather == "heatwave": booster_kind = "cooling_booster"
            elif self.current_weather == "acid_rain": booster_kind = self.random.choice(["hazmat_booster", "umbrella_booster"])
            elif self.current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
            elif self.current_weather == "tsunami": booster_kind = "life_jacket_booster"
            elif self.current_weather == "meteor_shower": booster_kind = "meteor_shield_booster"
            elif self.current_weather == "ice": booster_kind = "thermal_booster"
            elif self.current_weather == "earthquake": booster_kind = "seismic_booster"
            elif self.current_weather == "violent_quake": booster_kind = "seismic_booster"
            elif self.current_weather == "giant_flood": booster_kind = "life_jacket_booster"
            elif self.current_weather == "solar_eclipse": booster_kind = "vision_booster"
            elif self.current_weather == "celestial_alignment": booster_kind = "starlight_booster"
    """

    orig = """
            # Spawn the corresponding booster
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
            elif self.current_weather == "celestial_alignment": booster_kind = "starlight_booster"
    """
    content = content.replace(orig, repl)

    with open(path, "w") as f:
        f.write(content)

def modify_gd_game_modes():
    path = "src/ai/game_modes.gd"
    with open(path, "r") as f:
        content = f.read()

    # ExtremeWeatherMode.tick() modification
    repl = """
			var booster_kind = ""
			if current_weather == "blizzard": booster_kind = ["thermal_booster", "snow_globe_booster"][randi() % 2]
			elif current_weather == "heatwave": booster_kind = "cooling_booster"
			elif current_weather == "acid_rain": booster_kind = ["hazmat_booster", "umbrella_booster"][randi() % 2]
			elif current_weather == "hurricane": booster_kind = "heavy_anchor_booster"
			elif current_weather == "tsunami": booster_kind = "life_jacket_booster"
			elif current_weather == "ice": booster_kind = "thermal_booster"
			elif current_weather == "earthquake": booster_kind = "seismic_booster"
			elif current_weather == "violent_quake": booster_kind = "seismic_booster"
			elif current_weather == "giant_flood": booster_kind = "life_jacket_booster"
			elif current_weather == "solar_eclipse": booster_kind = "vision_booster"
			elif current_weather == "celestial_alignment": booster_kind = "starlight_booster"
    """

    orig = """
			var booster_kind = ""
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
			elif current_weather == "celestial_alignment": booster_kind = "starlight_booster"
    """
    content = content.replace(orig, repl)

    with open(path, "w") as f:
        f.write(content)

modify_python_game_modes()
modify_gd_game_modes()
