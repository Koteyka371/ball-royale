extends "res://src/ai/game_modes.gd".GameMode

func _init():
	name = "Spiderman Mode"
	description = "All balls start with a grapple hook and zero friction, relying entirely on grapple points and walls to navigate the arena."

func setup(world, balls):
	super.setup(world, balls)
	if world.has("arena") and world.arena != null:
		world.arena.base_friction = 0.0

	for b in balls:
		if not b.has("inventory"):
			b.inventory = []
		if not "grapple_hook" in b.inventory:
			b.inventory.append("grapple_hook")

		if typeof(b) == TYPE_DICTIONARY:
			b["is_frictionless"] = true
			b["friction_multiplier"] = 0.0
		elif typeof(b) == TYPE_OBJECT:
			b.set_meta("is_frictionless", true)
			if "friction_multiplier" in b:
				b.friction_multiplier = 0.0
			else:
				b.set_meta("friction_multiplier", 0.0)

func tick(world, balls, delta: float = 0.016) -> void:
	super.tick(world, balls, delta)
	for b in balls:
		if typeof(b) == TYPE_DICTIONARY:
			if not b.get("alive", false):
				continue
		else:
			if not b.get("alive"):
				continue

		if typeof(b) == TYPE_DICTIONARY:
			b["is_frictionless"] = true
		elif typeof(b) == TYPE_OBJECT:
			b.set_meta("is_frictionless", true)

		if not b.has("inventory"):
			b.inventory = []
		if not "grapple_hook" in b.inventory:
			b.inventory.append("grapple_hook")
