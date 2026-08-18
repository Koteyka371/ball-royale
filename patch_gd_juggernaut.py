import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

altar_tick_gd = """
		for altar in altars:
			var teams_present = {}
			for b in balls:
				var is_alive = false
				if typeof(b) == TYPE_DICTIONARY:
					is_alive = b.get("alive", false)
				else:
					is_alive = b.get("alive") if "alive" in b else false

				if is_alive and (b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else b.get("ball_type") if "ball_type" in b else "") != "spectator":
					var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("x") if "x" in b else 0.0
					var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("y") if "y" in b else 0.0
					var dist_sq = pow(bx - altar["x"], 2) + pow(by - altar["y"], 2)
					if dist_sq <= pow(altar["radius"], 2):
						var team = b.get("team", b.get("ball_type", "")) if typeof(b) == TYPE_DICTIONARY else b.get("team") if "team" in b else b.get("ball_type") if "ball_type" in b else ""
						if teams_present.has(team):
							teams_present[team] += 1
						else:
							teams_present[team] = 1

						var has_neg = false
						if typeof(b) == TYPE_DICTIONARY and b.has("inventory") and b["inventory"].has("negative_modifier"):
							has_neg = true
							b["inventory"].erase("negative_modifier")
						elif typeof(b) != TYPE_DICTIONARY and "inventory" in b and typeof(b.inventory) == TYPE_ARRAY and b.inventory.has("negative_modifier"):
							has_neg = true
							b.inventory.erase("negative_modifier")

						if has_neg:
							altar["sabotaged_by"] = team
							if world != null and typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
								world.add_event("altar_sabotaged", {"team": team})

						var saboteur = altar.get("sabotaged_by", null)
						if saboteur != null and saboteur != team:
							var cur_hp = 100.0
							if typeof(b) == TYPE_DICTIONARY and b.has("hp"):
								cur_hp = b.hp
							elif typeof(b) != TYPE_DICTIONARY and b.has_method("get_meta") and b.has_meta("hp"):
								cur_hp = b.get_meta("hp")
							elif "hp" in b:
								cur_hp = b.hp

							cur_hp = max(0.0, cur_hp - 15.0 * delta)

							if typeof(b) == TYPE_DICTIONARY:
								b["hp"] = cur_hp
							elif typeof(b) != TYPE_DICTIONARY and b.has_method("set_meta"):
								b.set_meta("hp", cur_hp)
							elif "hp" in b:
								b.hp = cur_hp

			if teams_present.size() > 0:
				var max_team = ""
				var max_val = -1
				for t in teams_present.keys():
					if teams_present[t] > max_val:
						max_val = teams_present[t]
						max_team = t

				var tie_count = 0
				for t in teams_present.keys():
					if teams_present[t] == max_val:
						tie_count += 1

				if tie_count == 1:
					if altar["owner"] == max_team:
						altar["capture_progress"] = min(100.0, altar["capture_progress"] + 20.0 * delta)
					else:
						altar["capture_progress"] -= 20.0 * delta
						if altar["capture_progress"] <= 0:
							altar["owner"] = max_team
							altar["capture_progress"] = 0.0
							var pref = "clear"
							if max_team in ["elementalist"]: pref = "thunderstorm"
							elif max_team in ["druid", "healer", "swamp"]: pref = "rain"
							elif max_team in ["rogue", "assassin", "stealth"]: pref = "fog"
							elif max_team in ["mage", "conjurer"]: pref = "snow"
							elif max_team in ["speed", "scout"]: pref = "wind"
							elif max_team in ["tank", "brawler"]: pref = "heatwave"
							elif max_team in ["swarm"]: pref = "sandstorm"
							else: pref = "thunderstorm"

							if weather != pref:
								weather = pref
								if world != null and typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
									world.add_event("weather_change", {"weather": pref})
			else:
				altar["capture_progress"] = max(0.0, altar["capture_progress"] - 5.0 * delta)
				if altar["capture_progress"] == 0:
					altar["owner"] = null
"""

jug_tick = """	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		var timer = self.get_meta("juggernaut_swap_timer") if self.has_meta("juggernaut_swap_timer") else 0.0"""
jug_tick_new = """	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)""" + altar_tick_gd + """
		var timer = self.get_meta("juggernaut_swap_timer") if self.has_meta("juggernaut_swap_timer") else 0.0"""
content = content.replace(jug_tick, jug_tick_new)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
