import re
import sys

def modify_game_modes_gd():
    path = "src/ai/game_modes.gd"
    with open(path, "r") as f:
        content = f.read()

    orig_slippery = """				# slide more
				if "vx" in b and "vy" in b:
					b.x += float(b.vx) * delta * 0.5
					b.y += float(b.vy) * delta * 0.5"""
    repl_slippery = """				# slide more
				var si = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					si = float(b.get("slippery_immunity_timer", 0.0))
				elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"):
					if b.has_meta("slippery_immunity_timer"): si = float(b.get_meta("slippery_immunity_timer"))
					elif "slippery_immunity_timer" in b: si = float(b.slippery_immunity_timer)
				if "vx" in b and "vy" in b and si <= 0.0:
					b.x += float(b.vx) * delta * 0.5
					b.y += float(b.vy) * delta * 0.5"""
    content = content.replace(orig_slippery, repl_slippery)

    orig_rain_dash = """				# rain makes surface slippery/increases dash range but reduces steering
				b["dash_range_mult"] = 1.5
				b["steering_mult"] = 0.5"""
    repl_rain_dash = """				# rain makes surface slippery/increases dash range but reduces steering
				var si2 = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					si2 = float(b.get("slippery_immunity_timer", 0.0))
				elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"):
					if b.has_meta("slippery_immunity_timer"): si2 = float(b.get_meta("slippery_immunity_timer"))
					elif "slippery_immunity_timer" in b: si2 = float(b.slippery_immunity_timer)
				if si2 <= 0.0:
					b["dash_range_mult"] = 1.5
					b["steering_mult"] = 0.5"""
    content = content.replace(orig_rain_dash, repl_rain_dash)

    orig_ice = """				if b.has_method("set_meta"): b.set_meta("friction_multiplier", 0.1) # extremely slippery
				else: b["friction_multiplier"] = 0.1
				if "hp" in b: b.hp -= 1.0 * delta # freezing damage"""
    repl_ice = """				var fi = 0.0
				if typeof(b) == TYPE_DICTIONARY:
					fi = float(b.get("freezing_immunity_timer", 0.0))
				elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta"):
					if b.has_meta("freezing_immunity_timer"): fi = float(b.get_meta("freezing_immunity_timer"))
					elif "freezing_immunity_timer" in b: fi = float(b.freezing_immunity_timer)
				if fi <= 0.0:
					if b.has_method("set_meta"): b.set_meta("friction_multiplier", 0.1) # extremely slippery
					else: b["friction_multiplier"] = 0.1
					if "hp" in b: b.hp -= 1.0 * delta # freezing damage"""
    content = content.replace(orig_ice, repl_ice)

    orig_tick_timer = """			var w_timer = 0.0
			if "weather_immunity_timer" in b:
				w_timer = b.weather_immunity_timer
			elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("weather_immunity_timer"):
				w_timer = b.get_meta("weather_immunity_timer")
			if w_timer > 0.0:
				w_timer -= delta
				if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
					b.set_meta("weather_immunity_timer", max(0.0, w_timer))
				else:
					b.weather_immunity_timer = max(0.0, w_timer)"""
    repl_tick_timer = """			var w_timer = 0.0
			if "weather_immunity_timer" in b:
				w_timer = b.weather_immunity_timer
			elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("weather_immunity_timer"):
				w_timer = b.get_meta("weather_immunity_timer")
			if w_timer > 0.0:
				w_timer -= delta
				if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
					b.set_meta("weather_immunity_timer", max(0.0, w_timer))
				else:
					b.weather_immunity_timer = max(0.0, w_timer)

			var fi_timer = 0.0
			if "freezing_immunity_timer" in b:
				fi_timer = b.freezing_immunity_timer
			elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("freezing_immunity_timer"):
				fi_timer = b.get_meta("freezing_immunity_timer")
			if fi_timer > 0.0:
				fi_timer -= delta
				if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("freezing_immunity_timer", max(0.0, fi_timer))
				else: b.freezing_immunity_timer = max(0.0, fi_timer)

			var si_timer = 0.0
			if "slippery_immunity_timer" in b:
				si_timer = b.slippery_immunity_timer
			elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("slippery_immunity_timer"):
				si_timer = b.get_meta("slippery_immunity_timer")
			if si_timer > 0.0:
				si_timer -= delta
				if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("slippery_immunity_timer", max(0.0, si_timer))
				else: b.slippery_immunity_timer = max(0.0, si_timer)"""

    content = content.replace(orig_tick_timer, repl_tick_timer)

    with open(path, "w") as f:
        f.write(content)

modify_game_modes_gd()
