import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

exec_start = content.find('func execute(strategy: String, delta: float):')
assert exec_start != -1

timer_logic_gd = """
	if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
		if self.ball.has_meta("gravity_boots_timer"):
			var gb_timer = self.ball.get_meta("gravity_boots_timer")
			if gb_timer > 0.0:
				self.ball.set_meta("gravity_boots_timer", max(0.0, gb_timer - delta))
				if self.ball.get_meta("gravity_boots_timer") <= 0.0:
					if self.ball.has_meta("inventory"):
						var inv = self.ball.get_meta("inventory")
						if inv.has("gravity_boots"):
							inv.erase("gravity_boots")
							self.ball.set_meta("inventory", inv)
	elif typeof(self.ball) == TYPE_DICTIONARY:
		if self.ball.has("gravity_boots_timer"):
			var gb_timer = self.ball.gravity_boots_timer
			if gb_timer > 0.0:
				self.ball.gravity_boots_timer = max(0.0, gb_timer - delta)
				if self.ball.gravity_boots_timer <= 0.0:
					if self.ball.has("inventory"):
						var inv = self.ball.inventory
						if inv.has("gravity_boots"):
							inv.erase("gravity_boots")
							self.ball.inventory = inv
	if "gravity_boots_timer" in self.ball and typeof(self.ball) == TYPE_OBJECT:
		if self.ball.gravity_boots_timer > 0.0:
			self.ball.gravity_boots_timer = max(0.0, self.ball.gravity_boots_timer - delta)
			if self.ball.gravity_boots_timer <= 0.0:
				if "inventory" in self.ball:
					var inv = self.ball.inventory
					if inv.has("gravity_boots"):
						inv.erase("gravity_boots")
						self.ball.inventory = inv
"""

nl = content.find('\n', exec_start)
content = content[:nl+1] + timer_logic_gd + content[nl+1:]

old_coll_gd = """			elif "kind" in nearest and nearest.kind == "gravity_boots":
				var inv = []
				if "inventory" in self.ball: inv = self.ball.inventory
				elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
				inv.append("gravity_boots")
				if "inventory" in self.ball: self.ball.inventory = inv
				elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)"""

new_coll_gd = """			elif "kind" in nearest and nearest.kind == "gravity_boots":
				var inv = []
				if "inventory" in self.ball: inv = self.ball.inventory
				elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
				if not inv.has("gravity_boots"):
					inv.append("gravity_boots")
				if "inventory" in self.ball: self.ball.inventory = inv
				elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
				if "gravity_boots_timer" in self.ball: self.ball.gravity_boots_timer = 15.0
				elif self.ball.has_method("set_meta"): self.ball.set_meta("gravity_boots_timer", 15.0)
				elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["gravity_boots_timer"] = 15.0"""

content = content.replace(old_coll_gd, new_coll_gd)

with open("src/ai/action.gd", "w") as f:
    f.write(content)

print("patched action.gd temp")
