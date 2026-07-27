extends "res://src/ai/game_modes.gd"

var pulse_timer: float = 0.0

func _init() -> void:
	name = "Magnet Ball"
	description = "Players get magnetized with positive or negative charges. Opposite charges attract and same charges repel."

func setup(world, balls) -> void:
	super.setup(world, balls)

	if not ("hazards" in world.arena):
		world.arena.hazards = []

	var has_magnetizer = false
	for h in world.arena.hazards:
		var h_kind = ""
		if typeof(h) == TYPE_DICTIONARY:
			h_kind = h.get("kind", "")
		else:
			h_kind = h.get("kind") if "kind" in h else ""

		if h_kind == "magnetizer":
			has_magnetizer = true
			break

	if not has_magnetizer:
		var hazard = {
			"kind": "magnetizer",
			"x": 500.0,
			"y": 500.0,
			"radius": 50.0,
			"damage": 0.0
		}
		world.arena.hazards.append(hazard)

func apply_dynamic_traits(world, balls, delta) -> void:
	super.apply_dynamic_traits(world, balls, delta)

	pulse_timer += delta
	var needs_reroll = false
	if pulse_timer > 5.0:
		pulse_timer = 0.0
		needs_reroll = true

	for b in balls:
		if b.get("alive") == true and b.get("ball_type") != "spectator":
			if needs_reroll or not b.has_meta("magnet_charge"):
				# 0 = false, 1 = true
				var charge = -1 if randi() % 2 == 0 else 1
				b.set_meta("magnet_charge", charge)
				if world.has_method("add_event") and needs_reroll:
					world.add_event("magnet_charge_changed", {"ball_id": b.get("id"), "charge": charge})

	for i in range(balls.size()):
		var b1 = balls[i]
		if not b1.get("alive") or b1.get("ball_type") == "spectator":
			continue

		for j in range(i + 1, balls.size()):
			var b2 = balls[j]
			if not b2.get("alive") or b2.get("ball_type") == "spectator":
				continue

			var dx = b2.x - b1.x
			var dy = b2.y - b1.y
			var dist = sqrt(dx*dx + dy*dy)

			if dist > 0 and dist < 400.0:
				var c1 = b1.get_meta("magnet_charge") if b1.has_meta("magnet_charge") else 0
				var c2 = b2.get_meta("magnet_charge") if b2.has_meta("magnet_charge") else 0

				if c1 == 0 or c2 == 0:
					continue

				var force = 500.0 * (1.0 - dist / 400.0) * delta

				var fx = 0.0
				var fy = 0.0
				if c1 == c2: # repel
					fx = -dx / dist * force
					fy = -dy / dist * force
				else: # attract
					fx = dx / dist * force
					fy = dy / dist * force

				b1.x += fx
				b1.y += fy
				b2.x -= fx
				b2.y -= fy

func tick(world, balls, delta=0.016) -> void:
	super.tick(world, balls, delta)
