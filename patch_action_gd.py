with open("src/ai/action.gd", "r") as f:
    content = f.read()

old_block = """		var has_breach = false
		if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("breach_charge_active"):
			has_breach = self.ball.get_meta("breach_charge_active")
		elif "breach_charge_active" in self.ball:
			has_breach = self.ball.breach_charge_active

		if has_breach:
			if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
				var hazards_to_remove_breach = []
				for h in self.world.arena.hazards:
					if typeof(h) == TYPE_DICTIONARY and h.has("kind") and (h.kind == "bumper" or h.kind == "breakable_wall"):
						var dx = float(h.x) - float(self.ball.x)
						var dy = float(h.y) - float(self.ball.y)
						var dist = sqrt(dx*dx + dy*dy)
						var h_rad = 10.0
						if h.has("radius"): h_rad = float(h.radius)
						var b_rad = 10.0
						if "radius" in self.ball: b_rad = float(self.ball.radius)
						if dist < b_rad + h_rad + 10.0:
							hazards_to_remove_breach.append(h)
					elif typeof(h) == TYPE_OBJECT and "kind" in h and (h.kind == "bumper" or h.kind == "breakable_wall"):
						var dx = float(h.x) - float(self.ball.x)
						var dy = float(h.y) - float(self.ball.y)
						var dist = sqrt(dx*dx + dy*dy)
						var h_rad = 10.0
						if "radius" in h: h_rad = float(h.radius)
						var b_rad = 10.0
						if "radius" in self.ball: b_rad = float(self.ball.radius)
						if dist < b_rad + h_rad + 10.0:
							hazards_to_remove_breach.append(h)

				if hazards_to_remove_breach.size() > 0:
					for h in hazards_to_remove_breach:
						var idx = self.world.arena.hazards.find(h)
						if idx != -1:
							self.world.arena.hazards.remove_at(idx)
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
						self.ball.set_meta("breach_charge_active", false)
					if "breach_charge_active" in self.ball:
						self.ball.breach_charge_active = false
"""

new_block = """		var has_breach = false
		if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("breach_charge_active"):
			has_breach = self.ball.get_meta("breach_charge_active")
		elif "breach_charge_active" in self.ball:
			has_breach = self.ball.breach_charge_active

		if has_breach:
			if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
				var disabled_any = false
				for h in self.world.arena.hazards:
					if typeof(h) == TYPE_DICTIONARY and h.has("kind") and (h.kind == "bumper" or h.kind == "breakable_wall"):
						var dx = float(h.x) - float(self.ball.x)
						var dy = float(h.y) - float(self.ball.y)
						var dist = sqrt(dx*dx + dy*dy)
						var h_rad = 10.0
						if h.has("radius"): h_rad = float(h.radius)
						var b_rad = 10.0
						if "radius" in self.ball: b_rad = float(self.ball.radius)
						if dist < b_rad + h_rad + 10.0:
							h["emp_disabled_timer"] = 15.0
							disabled_any = true
					elif typeof(h) == TYPE_OBJECT and "kind" in h and (h.kind == "bumper" or h.kind == "breakable_wall"):
						var dx = float(h.x) - float(self.ball.x)
						var dy = float(h.y) - float(self.ball.y)
						var dist = sqrt(dx*dx + dy*dy)
						var h_rad = 10.0
						if "radius" in h: h_rad = float(h.radius)
						var b_rad = 10.0
						if "radius" in self.ball: b_rad = float(self.ball.radius)
						if dist < b_rad + h_rad + 10.0:
							if h.has_method("set_meta"):
								h.set_meta("emp_disabled_timer", 15.0)
							if "emp_disabled_timer" in h:
								h.emp_disabled_timer = 15.0
							disabled_any = true

				if disabled_any:
					if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
						self.ball.set_meta("breach_charge_active", false)
					if "breach_charge_active" in self.ball:
						self.ball.breach_charge_active = false
"""

content = content.replace(old_block, new_block)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
