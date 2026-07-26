extends "res://src/ai/game_modes.gd".GameMode

func _init():
	super._init()
	name = "Hovercraft"
	description = "Friction is reduced to zero, making all balls slide uncontrollably until they hit a wall or use a dash ability."

func tick(world, balls, delta = 0.016):
	super.tick(world, balls, delta)

func apply_dynamic_traits(world, balls, delta: float) -> void:
	for b in balls:
		if typeof(b) == TYPE_DICTIONARY:
			b["is_frictionless"] = true
		elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
			b.set_meta("is_frictionless", true)
		elif "is_frictionless" in b:
			b.is_frictionless = true
