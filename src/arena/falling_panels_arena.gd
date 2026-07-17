class_name FallingPanelsArena
extends ProceduralArena

var panel_size: float = 400.0
var panels: Array = []
var drop_timer: float = 0.0
var drop_interval: float = 10.0

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
	super(_arena_size, _num_rooms, _seed)

func generate() -> void:
	super.generate()
	rooms.clear()
	corridors.clear()
	hazards.clear()

	var cols = int(ceil(width / panel_size))
	var rows = int(ceil(height / panel_size))

	panels.clear()
	for i in range(cols):
		for j in range(rows):
			panels.append({
				"col": i,
				"row": j,
				"x": i * panel_size,
				"y": j * panel_size,
				"width": panel_size,
				"height": panel_size,
				"state": "normal",
				"timer": 0.0
			})

func update_zone(current_tick: int, delta: float) -> void:
	var is_new_tick = current_tick != last_tick
	super.update_zone(current_tick, delta)

	if is_new_tick:
		drop_timer += delta

		if drop_timer >= drop_interval:
			drop_timer = 0.0
			var normal_panels = []
			for p in panels:
				if p.state == "normal":
					normal_panels.append(p)

			if normal_panels.size() > 0:
				var panel = normal_panels[randi() % normal_panels.size()]
				panel.state = "glowing"
				panel.timer = 3.0

		for p in panels:
			if p.state == "glowing":
				p.timer -= delta
				if p.timer <= 0.0:
					p.state = "fallen"
					var cx = p.x + panel_size / 2.0
					var cy = p.y + panel_size / 2.0
					var radius = panel_size / 2.0

					var h_id = -10000 - hazards.size()
					var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
					if ProceduralArenaScript and ProceduralArenaScript.has_source_code():
						var new_hazard = ProceduralArenaScript.Hazard.new(h_id, cx, cy, radius, "void_panel", 10000.0)
						hazards.append(new_hazard)
					else:
						var new_hazard = {
							"id": h_id,
							"x": cx,
							"y": cy,
							"radius": radius,
							"kind": "void_panel",
							"damage": 10000.0,
							"active": true
						}
						hazards.append(new_hazard)

func is_point_inside(px: float, py: float, radius: float) -> bool:
	return super.is_point_inside(px, py, radius)
