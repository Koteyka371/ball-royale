import re

with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

# Fix b.get(..., default) -> b.get(prop) and handle default manually or just use 'in' checks
# Or simply get with a default by using `b.get("base_radius") if b.get("base_radius") != null else 15.0`
# Let's fix this in both setup and apply_dynamic_traits

fixed_mode_class = """class GiantBouncyRoyaleMode extends GameMode:
	func _init():
		super._init()
		self.name = "Giant Bouncy Royale"
		self.description = "All balls have double size and double bounce physics, causing massive chaotic collisions and ricochets. Arena boundaries are replaced by bouncy forcefields."

	func setup(world, balls):
		super.setup(world, balls)
		for b in balls:
			if typeof(b) == TYPE_OBJECT:
				var alive = true
				if b.get("alive") != null:
					alive = b.get("alive")
				var b_type = b.get("ball_type")
				if not alive or b_type == "spectator":
					continue
				var base_rad = 15.0
				if b.get("base_radius") != null:
					base_rad = b.get("base_radius")
				b.set("radius", base_rad * 2.0)
			elif typeof(b) == TYPE_DICTIONARY:
				if not b.get("alive", true) or b.get("ball_type", "") == "spectator":
					continue
				b["radius"] = b.get("base_radius", 15.0) * 2.0

	func apply_dynamic_traits(world, balls, delta):
		for b in balls:
			if typeof(b) == TYPE_OBJECT:
				var alive = true
				if b.get("alive") != null:
					alive = b.get("alive")
				var b_type = b.get("ball_type")
				if not alive or b_type == "spectator":
					continue
				var base_rad = 15.0
				if b.get("base_radius") != null:
					base_rad = b.get("base_radius")
				b.set("radius", base_rad * 2.0)
			elif typeof(b) == TYPE_DICTIONARY:
				if not b.get("alive", true) or b.get("ball_type", "") == "spectator":
					continue
				b["radius"] = b.get("base_radius", 15.0) * 2.0
"""

# replace the old mode class definition with the fixed one
text = re.sub(
    r'class GiantBouncyRoyaleMode extends GameMode:[\s\S]*?(?=var GAME_MODES = \{)',
    fixed_mode_class + '\n',
    text
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
