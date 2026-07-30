import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

content = content.replace(
    '''var bpull_strength = (hazard.radius * 2.0 * radius_mult / bmin_dist) * 50.0 * delta * lifetime_mult''',
    '''var bpull_strength = (hazard.radius * 2.0 * radius_mult / bmin_dist) * 50.0 * delta * lifetime_mult
									if hazard.kind in ["tornado", "supercell_tornado", "local_tornado", "firenado", "local_firenado", "poison_tornado", "local_poison_tornado"]:
										var mass = 1.0
										if "mass" in b: mass = float(b.mass)
										elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("mass"): mass = float(b.get_meta("mass"))
										elif typeof(b) == TYPE_DICTIONARY and b.has("mass"): mass = float(b["mass"])
										if mass < 0.1: mass = 0.1
										bpull_strength = bpull_strength / mass'''
)

content = content.replace(
    '''var pull_strength = (hazard.radius * 2.0 * radius_mult / min_dist) * 50.0 * delta * lifetime_mult''',
    '''var pull_strength = (hazard.radius * 2.0 * radius_mult / min_dist) * 50.0 * delta * lifetime_mult
							if hazard.kind in ["tornado", "supercell_tornado", "local_tornado", "firenado", "local_firenado", "poison_tornado", "local_poison_tornado"]:
								var mass = 1.0
								if "mass" in self.ball: mass = float(self.ball.mass)
								elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("mass"): mass = float(self.ball.get_meta("mass"))
								elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("mass"): mass = float(self.ball["mass"])
								if mass < 0.1: mass = 0.1
								pull_strength = pull_strength / mass'''
)

content = content.replace(
    '''var pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta''',
    '''var pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta
                        if hazard.kind in ["tornado", "supercell_tornado", "local_tornado", "firenado", "local_firenado", "poison_tornado", "local_poison_tornado"]:
                            var mass = 1.0
                            if "mass" in self.ball: mass = float(self.ball.mass)
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("mass"): mass = float(self.ball.get_meta("mass"))
                            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("mass"): mass = float(self.ball["mass"])
                            if mass < 0.1: mass = 0.1
                            pull_strength = pull_strength / mass'''
)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
