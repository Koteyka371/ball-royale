extends Node

const GameMode = preload("res://src/ai/game_modes.gd").GameMode

class MirrorWorldMode extends GameMode:
	var mirror_timer: float = 0.0
	var is_mirrored: bool = false
	var mirror_duration: float = 5.0
	var normal_duration: float = 10.0

	func _init():
		name = "Mirror World"
		description = "Creates a temporary mirror version of the map."

	func tick(world: Dictionary, balls: Array, delta: float = 0.016):
		super.tick(world, balls, delta)
		mirror_timer += delta

		if not is_mirrored and mirror_timer >= normal_duration:
			is_mirrored = true
			mirror_timer = 0.0
			_mirror_world(world, balls)
		elif is_mirrored and mirror_timer >= mirror_duration:
			is_mirrored = false
			mirror_timer = 0.0
			_mirror_world(world, balls)

	func _mirror_world(world: Dictionary, balls: Array):
		var arena_width = 1000.0
		if world.has("arena") and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("width"):
				arena_width = float(world.arena.width)
			elif typeof(world.arena) == TYPE_OBJECT and "width" in world.arena:
				arena_width = float(world.arena.width)

		var center_x = arena_width / 2.0

		if world.has("arena") and world.arena != null:
			var hazards = []
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
				hazards = world.arena.hazards
			elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
				hazards = world.arena.hazards

			for hazard in hazards:
				if typeof(hazard) == TYPE_DICTIONARY:
					if hazard.has("x"):
						hazard.x = center_x + (center_x - hazard.x)
					if hazard.has("vx"):
						hazard.vx = -hazard.vx
				elif typeof(hazard) == TYPE_OBJECT:
					if "x" in hazard:
						hazard.x = center_x + (center_x - hazard.x)
					if "vx" in hazard:
						hazard.vx = -hazard.vx

			var boosters = []
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("boosters"):
				boosters = world.arena.boosters
			elif typeof(world.arena) == TYPE_OBJECT and "boosters" in world.arena:
				boosters = world.arena.boosters

			for booster in boosters:
				if typeof(booster) == TYPE_DICTIONARY:
					if booster.has("x"):
						booster.x = center_x + (center_x - booster.x)
					if booster.has("vx"):
						booster.vx = -booster.vx
				elif typeof(booster) == TYPE_OBJECT:
					if "x" in booster:
						booster.x = center_x + (center_x - booster.x)
					if "vx" in booster:
						booster.vx = -booster.vx

		if world.has("projectiles"):
			for p in world.projectiles:
				if typeof(p) == TYPE_DICTIONARY:
					if p.has("x"):
						p.x = center_x + (center_x - p.x)
					if p.has("vx"):
						p.vx = -p.vx
					if p.has("target_x"):
						p.target_x = center_x + (center_x - p.target_x)
				elif typeof(p) == TYPE_OBJECT:
					if "x" in p:
						p.x = center_x + (center_x - p.x)
					if "vx" in p:
						p.vx = -p.vx
					if "target_x" in p:
						p.target_x = center_x + (center_x - p.target_x)

		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				if b.has("x"):
					b.x = center_x + (center_x - b.x)
				if b.has("vx"):
					b.vx = -b.vx
			elif typeof(b) == TYPE_OBJECT:
				if "x" in b:
					b.x = center_x + (center_x - b.x)
				if "vx" in b:
					b.vx = -b.vx
