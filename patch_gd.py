with open("src/ai/action.gd", "r") as f:
    content = f.read()

replacement = """				if kind == "void_panel":
					var bbt = 0.0
					if "bumper_booster_timer" in self.ball: bbt = float(self.ball.bumper_booster_timer)
					elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("bumper_booster_timer"): bbt = float(self.ball.get_meta("bumper_booster_timer"))
					if bbt > 0.0:
						continue"""

content = content.replace('				if kind == "void_panel":', replacement)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
