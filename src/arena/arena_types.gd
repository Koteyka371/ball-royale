class_name ArenaTypes
extends RefCounted
var boundary_states: Dictionary = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
var boundary_health: Dictionary = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}

class SwapPortal extends ProceduralArena.Hazard:
    func _init(_id: int, _x: float, _y: float, _radius: float, _target_x: float, _target_y: float, _pair_id: int):
        super(_id, _x, _y, _radius, "swap_portal", 0.0)
        set_meta("target_x", _target_x)
        set_meta("target_y", _target_y)
        set_meta("pair_id", _pair_id)

class Portal extends ProceduralArena.Hazard:
    var target_x: float
    var target_y: float

    func _init(_id: int, _x: float, _y: float, _radius: float, _target_x: float, _target_y: float):
        super(_id, _x, _y, _radius, "portal", 0.0)
        target_x = _target_x
        target_y = _target_y

class PortalArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0

		rooms.append(ProceduralArena.Room.new(50, 50, 200, 200))
		rooms.append(ProceduralArena.Room.new(w-250, 50, 200, 200))
		rooms.append(ProceduralArena.Room.new(50, h-250, 200, 200))
		rooms.append(ProceduralArena.Room.new(w-250, h-250, 200, 200))
		rooms.append(ProceduralArena.Room.new(cx-100, cy-100, 200, 200))

		hazards.append(ArenaTypes.Portal.new(0, 150.0, 150.0, 30.0, w-150.0, h-150.0))
		hazards.append(ArenaTypes.Portal.new(1, w-150.0, h-150.0, 30.0, 150.0, 150.0))

		hazards.append(ArenaTypes.Portal.new(2, w-150.0, 150.0, 30.0, 150.0, h-150.0))
		hazards.append(ArenaTypes.Portal.new(3, 150.0, h-150.0, 30.0, w-150.0, 150.0))

class ConveyorBelt extends ProceduralArena.Hazard:
    var direction_vector: Array
    var speed_magnitude: float

    func _init(_id: int, _x: float, _y: float, _radius: float, _damage: float, _dir_vec: Array, _speed: float):
        super(_id, _x, _y, _radius, "conveyor_belt", _damage)
        direction_vector = _dir_vec
        speed_magnitude = _speed

class FactoryArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()

		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0

		# Central assembly line
		rooms.append(ProceduralArena.Room.new(w * 0.1, h * 0.3, w * 0.8, h * 0.4))

		# Top and bottom side rooms
		rooms.append(ProceduralArena.Room.new(w * 0.3, h * 0.1, w * 0.4, h * 0.2))
		rooms.append(ProceduralArena.Room.new(w * 0.3, h * 0.7, w * 0.4, h * 0.2))

		# Corridors connecting side rooms to main assembly
		corridors.append(ProceduralArena.Corridor.new(cx, h * 0.2, 100, h * 0.2))
		corridors.append(ProceduralArena.Corridor.new(cx, h * 0.6, 100, h * 0.2))

		# Add conveyor belts in a loop or lines

		# Top line moving right
		hazards.append(ConveyorBelt.new(0, w*0.3, h*0.4, 60.0, 0.0, [1.0, 0.0], 200.0))
		hazards.append(ConveyorBelt.new(1, w*0.5, h*0.4, 60.0, 0.0, [1.0, 0.0], 200.0))
		hazards.append(ConveyorBelt.new(2, w*0.7, h*0.4, 60.0, 0.0, [1.0, 0.0], 200.0))

		# Bottom line moving left
		hazards.append(ConveyorBelt.new(3, w*0.7, h*0.6, 60.0, 0.0, [-1.0, 0.0], 200.0))
		hazards.append(ConveyorBelt.new(4, w*0.5, h*0.6, 60.0, 0.0, [-1.0, 0.0], 200.0))
		hazards.append(ConveyorBelt.new(5, w*0.3, h*0.6, 60.0, 0.0, [-1.0, 0.0], 200.0))


class FunnyFailsArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0

		rooms.append(ProceduralArena.Room.new(cx - 200, cy - 200, 400, 400))
		rooms.append(ProceduralArena.Room.new(cx - 700, cy - 700, 300, 300))
		rooms.append(ProceduralArena.Room.new(cx + 400, cy - 700, 300, 300))
		rooms.append(ProceduralArena.Room.new(cx - 700, cy + 400, 300, 300))
		rooms.append(ProceduralArena.Room.new(cx + 400, cy + 400, 300, 300))

		corridors.append(ProceduralArena.Corridor.new(cx - 450, cy - 600, 300, 100))
		corridors.append(ProceduralArena.Corridor.new(cx - 250, cy - 650, 100, 500))

		corridors.append(ProceduralArena.Corridor.new(cx + 150, cy - 600, 300, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 150, cy - 650, 100, 500))

		corridors.append(ProceduralArena.Corridor.new(cx - 450, cy + 500, 300, 100))
		corridors.append(ProceduralArena.Corridor.new(cx - 250, cy + 150, 100, 400))

		corridors.append(ProceduralArena.Corridor.new(cx + 150, cy + 500, 300, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 150, cy + 150, 100, 400))

		hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 50.0, "lava", 20.0))
		hazards.append(ProceduralArena.Hazard.new(1, cx - 300, cy - 600, 40.0, "lava", 20.0))
		hazards.append(ProceduralArena.Hazard.new(2, cx + 300, cy - 600, 40.0, "lava", 20.0))
		hazards.append(ProceduralArena.Hazard.new(3, cx - 300, cy + 500, 40.0, "lava", 20.0))
		hazards.append(ProceduralArena.Hazard.new(4, cx + 300, cy + 500, 40.0, "lava", 20.0))

class MetaEvolutionArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0

		# Center Room
		rooms.append(ProceduralArena.Room.new(cx - 200, cy - 200, 400, 400))
		# Top Room
		rooms.append(ProceduralArena.Room.new(cx - 150, cy - 700, 300, 300))
		# Bottom Left
		rooms.append(ProceduralArena.Room.new(cx - 700, cy + 100, 300, 300))
		# Bottom Right
		rooms.append(ProceduralArena.Room.new(cx + 400, cy + 100, 300, 300))

		# Corridors
		corridors.append(ProceduralArena.Corridor.new(cx - 50, cy - 400, 100, 200))
		corridors.append(ProceduralArena.Corridor.new(cx - 400, cy + 150, 200, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 200, cy + 150, 200, 100))

		# Hazards
		hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 30.0, "lava", 10.0))
		hazards.append(ProceduralArena.Hazard.new(1, cx - 550, cy + 250, 80.0, "lava", 40.0))
		hazards.append(ProceduralArena.Hazard.new(2, cx + 550, cy + 250, 40.0, "spikes", 30.0))
		hazards.append(ProceduralArena.Hazard.new(3, cx + 500, cy + 180, 20.0, "spikes", 30.0))
		hazards.append(ProceduralArena.Hazard.new(4, cx + 600, cy + 320, 20.0, "spikes", 30.0))


class BodyBlockArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        # A central room where the main engagement happens
        rooms.append(ProceduralArena.Room.new(cx - 400, cy - 200, 800, 400))

        # Two smaller rooms representing "ally base" and "enemy spawn"
        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 100, 200, 200)) # Left ally base
        rooms.append(ProceduralArena.Room.new(cx + 500, cy - 100, 200, 200)) # Right enemy base

        # Narrow choke point corridors connecting the bases to the center room to force body blocking
        corridors.append(ProceduralArena.Corridor.new(cx - 500, cy - 50, 100, 100))
        corridors.append(ProceduralArena.Corridor.new(cx + 400, cy - 50, 100, 100))

        # A central hazard to force players into tighter chokes
        var h0 = ProceduralArena.Hazard.new()
        h0.id = 0
        h0.x = cx
        h0.y = cy
        h0.radius = 50.0
        h0.kind = "lava"
        h0.damage = 25.0
        hazards.append(h0)

class PhysicsChainReactionsArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))

        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 200, 200, 400))
        rooms.append(ProceduralArena.Room.new(cx + 500, cy - 200, 200, 400))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy - 700, 400, 200))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy + 500, 400, 200))

        corridors.append(ProceduralArena.Corridor.new(cx - 550, cy - 100, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, cy - 100, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx - 100, cy - 550, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx - 100, cy + 250, 200, 300))

        var h0 = ProceduralArena.Hazard.new()
        h0.id = 0; h0.x = cx - 150; h0.y = cy - 150; h0.radius = 50.0; h0.kind = "spikes"; h0.damage = 30.0; hazards.append(h0)
        var h1 = ProceduralArena.Hazard.new()
        h1.id = 1; h1.x = cx + 150; h1.y = cy - 150; h1.radius = 50.0; h1.kind = "spikes"; h1.damage = 30.0; hazards.append(h1)
        var h2 = ProceduralArena.Hazard.new()
        h2.id = 2; h2.x = cx - 150; h2.y = cy + 150; h2.radius = 50.0; h2.kind = "spikes"; h2.damage = 30.0; hazards.append(h2)
        var h3 = ProceduralArena.Hazard.new()
        h3.id = 3; h3.x = cx + 150; h3.y = cy + 150; h3.radius = 50.0; h3.kind = "spikes"; h3.damage = 30.0; hazards.append(h3)
        var h4 = ProceduralArena.Hazard.new()
        h4.id = 4; h4.x = cx; h4.y = cy; h4.radius = 80.0; h4.kind = "lava"; h4.damage = 20.0; hazards.append(h4)


class BattleRoyaleShrinkingZoneArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # Central room
        rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))

        # Top-left room
        rooms.append(ProceduralArena.Room.new(50, 50, 150, 150))
        # Top-right room
        rooms.append(ProceduralArena.Room.new(w - 200, 50, 150, 150))
        # Bottom-left room
        rooms.append(ProceduralArena.Room.new(50, h - 200, 150, 150))
        # Bottom-right room
        rooms.append(ProceduralArena.Room.new(w - 200, h - 200, 150, 150))

        # Connecting corridors (top-left)
        corridors.append(ProceduralArena.Corridor.new(100, 200, 50, cy - 400))
        corridors.append(ProceduralArena.Corridor.new(100, cy - 300, cx - 300, 50))

        # Connecting corridors (top-right)
        corridors.append(ProceduralArena.Corridor.new(w - 150, 200, 50, cy - 400))
        corridors.append(ProceduralArena.Corridor.new(cx + 300, cy - 300, w - cx - 300, 50))

        # Connecting corridors (bottom-left)
        corridors.append(ProceduralArena.Corridor.new(100, cy + 250, 50, h - cy - 400))
        corridors.append(ProceduralArena.Corridor.new(100, cy + 250, cx - 300, 50))

        # Connecting corridors (bottom-right)
        corridors.append(ProceduralArena.Corridor.new(w - 150, cy + 250, 50, h - cy - 400))
        corridors.append(ProceduralArena.Corridor.new(cx + 300, cy + 250, w - cx - 300, 50))

        # 1 central hazard to discourage staying in the open
        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 80.0, "lava", 20.0))

    func update_zone(current_tick: int, delta: float) -> void:
        if current_tick != last_tick:
            last_tick = current_tick
            if safe_zone_radius > 0.0:
                safe_zone_radius -= 15.0 * delta
                if safe_zone_radius <= 0.0:
                    safe_zone_radius = 0.0

                # Black hole spawning and merging when safe zone is very small
                if safe_zone_radius <= 100.0:
                    # Spawn new black holes occasionally
                    if current_tick % 60 == 0 and randf() < 0.5:
                        var angle = randf_range(0, PI * 2)
                        var dist = randf_range(0, max(1.0, safe_zone_radius))
                        var cx = width / 2.0
                        var cy = height / 2.0
                        var hx = cx + cos(angle) * dist
                        var hy = cy + sin(angle) * dist
                        var bh_id = 20000 + (randi() % 1000)
                        if "hazards" in self:
                            bh_id += self.hazards.size()

                        var bh = ProceduralArena.Hazard.new(bh_id, hx, hy, 20.0, "black_hole", 15.0)
                        bh.duration = 1000.0
                        if "hazards" in self:
                            self.hazards.append(bh)

                    if "hazards" in self:
                        # Pull all black holes towards the center and merge them
                        var bhs = []
                        for h in self.hazards:
                            if "kind" in h and h.kind == "black_hole":
                                bhs.append(h)

                        var cx = width / 2.0
                        var cy = height / 2.0
                        for h in bhs:
                            var dx = cx - h.x
                            var dy = cy - h.y
                            var dist = sqrt(dx*dx + dy*dy)
                            if dist > 0.0001:
                                h.x += (dx/dist) * 10.0 * delta
                                h.y += (dy/dist) * 10.0 * delta

                            # Merge logic
                            for other in bhs:
                                if h.id != other.id and other.duration > 0.0 and h.duration > 0.0:
                                    var ddx = other.x - h.x
                                    var ddy = other.y - h.y
                                    var ddist2 = ddx*ddx + ddy*ddy
                                    var hr = h.radius
                                    var orad = other.radius
                                    if ddist2 < pow(hr + orad, 2) * 0.25:
                                        # Merge other into h
                                        h.radius = min(150.0, hr + orad * 0.5)
                                        h.damage = h.damage + other.damage * 0.2
                                        other.duration = 0.0 # Mark for destruction
            else:
                if current_tick % 120 == 0:
                    if has_method("_trigger_event"):
                        var event_types = ["meteor_shower", "gravity_shift", "orbital_strike", "emp_strike", "anomaly_zone"]
                        call("_trigger_event", event_types[randi() % event_types.size()], current_tick)
                    else:
                        var event_types = ["meteor_shower", "gravity_shift", "anomaly_zone"]
                        var event_type = event_types[randi() % event_types.size()]
                        if event_type == "meteor_shower":
                            for i in range(10):
                                var h_x = randf_range(50.0, width - 50.0)
                                var h_y = randf_range(50.0, height - 50.0)
                                var m_haz = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, h_x, h_y, 30.0, "meteor", 200.0)
                                m_haz.target_radius = 30.0
                                m_haz.set_meta("duration", 5.0)
                                hazards.append(m_haz)
                        elif event_type == "anomaly_zone":
                            var zone = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, width/2, height/2, width/2, "anomaly_zone", 0.0)
                            zone.set_meta("duration", 10.0)
                            hazards.append(zone)
                        elif event_type == "gravity_shift":
                            var gw = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, width/2, height/2, width/2, "gravity_well", 10.0)
                            gw.set_meta("duration", 10.0)
                            hazards.append(gw)

class HealAllyArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = self.width
        var h = self.height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))
        rooms.append(ProceduralArena.Room.new(100, 100, 300, 300))
        rooms.append(ProceduralArena.Room.new(w - 400, 100, 300, 300))
        rooms.append(ProceduralArena.Room.new(100, h - 400, 300, 300))
        rooms.append(ProceduralArena.Room.new(w - 400, h - 400, 300, 300))

        corridors.append(ProceduralArena.Corridor.new(350, 200, cx - 600, 100))
        corridors.append(ProceduralArena.Corridor.new(cx - 350, 250, 100, cy - 500))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, 200, w - cx - 600, 100))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, 250, 100, cy - 500))
        corridors.append(ProceduralArena.Corridor.new(350, h - 300, cx - 600, 100))
        corridors.append(ProceduralArena.Corridor.new(cx - 350, cy + 250, 100, h - cy - 500))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, h - 300, w - cx - 600, 100))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, cy + 250, 100, h - cy - 500))

class WaitAndWatchArena extends ProceduralArena:
	func generate() -> void:
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = float(width)
		var h = float(height)
		var cx = w / 2.0
		var cy = h / 2.0

		rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))
		rooms.append(ProceduralArena.Room.new(cx - 150, 50, 300, 200))
		rooms.append(ProceduralArena.Room.new(cx - 150, h - 250, 300, 200))
		rooms.append(ProceduralArena.Room.new(50, cy - 150, 200, 300))
		rooms.append(ProceduralArena.Room.new(w - 250, cy - 150, 200, 300))

		corridors.append(ProceduralArena.Corridor.new(cx - 50, 250, 100, cy - 550))
		corridors.append(ProceduralArena.Corridor.new(cx - 50, cy + 300, 100, h - 550 - cy))
		corridors.append(ProceduralArena.Corridor.new(250, cy - 50, cx - 550, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 300, cy - 50, w - 550 - cx, 100))

		var h0 = ProceduralArena.Hazard.new(); h0.id = 0; h0.x = cx; h0.y = cy; h0.radius = 100.0; h0.kind = "lava"; h0.damage = 20.0; hazards.append(h0)
		var h1 = ProceduralArena.Hazard.new(); h1.id = 1; h1.x = cx - 150; h1.y = cy - 150; h1.radius = 50.0; h1.kind = "spikes"; h1.damage = 30.0; hazards.append(h1)
		var h2 = ProceduralArena.Hazard.new(); h2.id = 2; h2.x = cx + 150; h2.y = cy - 150; h2.radius = 50.0; h2.kind = "spikes"; h2.damage = 30.0; hazards.append(h2)
		var h3 = ProceduralArena.Hazard.new(); h3.id = 3; h3.x = cx - 150; h3.y = cy + 150; h3.radius = 50.0; h3.kind = "spikes"; h3.damage = 30.0; hazards.append(h3)
		var h4 = ProceduralArena.Hazard.new(); h4.id = 4; h4.x = cx + 150; h4.y = cy + 150; h4.radius = 50.0; h4.kind = "spikes"; h4.damage = 30.0; hazards.append(h4)

class EscortArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0
		rooms.append(ProceduralArena.Room.new(cx - 200, h - 400, 400, 300))
		rooms.append(ProceduralArena.Room.new(cx - 200, 100, 400, 300))
		corridors.append(ProceduralArena.Corridor.new(cx - 100, 400, 200, h - 800))
		var h1 = ProceduralArena.Hazard.new(); h1.id = 0; h1.x = cx - 150; h1.y = cy; h1.radius = 40.0; h1.kind = "lava"; h1.damage = 10.0; hazards.append(h1)
		var h2 = ProceduralArena.Hazard.new(); h2.id = 1; h2.x = cx + 150; h2.y = cy; h2.radius = 40.0; h2.kind = "lava"; h2.damage = 10.0; hazards.append(h2)


class TargetStrongArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))
        rooms.append(ProceduralArena.Room.new(cx - 500.0, cy - 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx + 300.0, cy - 100.0, 200.0, 200.0))

        corridors.append(ProceduralArena.Corridor.new(cx - 350.0, cy - 50.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 250.0, cy - 50.0, 100.0, 100.0))

        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 50.0, "lava", 25.0))


class BallGeneticsArena extends ProceduralArena:
	func generate() -> void:
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = width
		var h = height
		var cx = w / 2.0
		var cy = h / 2.0

		rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))

		rooms.append(ProceduralArena.Room.new(cx - 600.0, cy - 600.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(cx + 400.0, cy - 600.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(cx - 600.0, cy + 400.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(cx + 400.0, cy + 400.0, 200.0, 200.0))

		corridors.append(ProceduralArena.Corridor.new(cx - 450.0, cy - 450.0, 100.0, 200.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 350.0, cy - 450.0, 100.0, 200.0))
		corridors.append(ProceduralArena.Corridor.new(cx - 450.0, cy + 250.0, 100.0, 200.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 350.0, cy + 250.0, 100.0, 200.0))

		hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 50.0, "lava", 10.0))


class FleeArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0
		rooms.append(ProceduralArena.Room.new(cx - 200, cy - 200, 400, 400))
		rooms.append(ProceduralArena.Room.new(50, cy - 100, 200, 200))
		rooms.append(ProceduralArena.Room.new(w - 250, cy - 100, 200, 200))
		rooms.append(ProceduralArena.Room.new(cx - 100, 50, 200, 200))
		rooms.append(ProceduralArena.Room.new(cx - 100, h - 250, 200, 200))
		corridors.append(ProceduralArena.Corridor.new(200, cy - 50, cx - 350, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 150, cy - 50, w - cx - 350, 100))
		corridors.append(ProceduralArena.Corridor.new(cx - 50, 200, 100, cy - 350))
		corridors.append(ProceduralArena.Corridor.new(cx - 50, cy + 150, 100, h - cy - 350))
		var h1 = ProceduralArena.Hazard.new(); h1.id = 0; h1.x = cx; h1.y = cy; h1.radius = 100.0; h1.kind = "lava"; h1.damage = 20.0; hazards.append(h1)

class NeuralBallArena extends ProceduralArena:
	func generate():
		self.rooms.clear()
		self.corridors.clear()
		self.hazards.clear()
		var w = self.width
		var h = self.height

		# Input Layer
		self.rooms.append(ProceduralArena.Room.new(w * 0.1, h * 0.2, 150.0, 150.0))
		self.rooms.append(ProceduralArena.Room.new(w * 0.1, h * 0.5, 150.0, 150.0))
		self.rooms.append(ProceduralArena.Room.new(w * 0.1, h * 0.8, 150.0, 150.0))

		# Hidden Layer
		self.rooms.append(ProceduralArena.Room.new(w * 0.5, h * 0.2, 150.0, 150.0))
		self.rooms.append(ProceduralArena.Room.new(w * 0.5, h * 0.5, 150.0, 150.0))
		self.rooms.append(ProceduralArena.Room.new(w * 0.5, h * 0.8, 150.0, 150.0))

		# Output Layer
		self.rooms.append(ProceduralArena.Room.new(w * 0.8, h * 0.35, 150.0, 150.0))
		self.rooms.append(ProceduralArena.Room.new(w * 0.8, h * 0.65, 150.0, 150.0))

		# Corridors
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.1 + 100.0, h * 0.2 + 50.0, w * 0.4, 50.0))
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.1 + 100.0, h * 0.5 + 50.0, w * 0.4, 50.0))
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.1 + 100.0, h * 0.8 + 50.0, w * 0.4, 50.0))
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.5 + 100.0, h * 0.2 + 50.0, w * 0.3, 50.0))
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.5 + 100.0, h * 0.8 + 50.0, w * 0.3, 50.0))

		self.corridors.append(ProceduralArena.Corridor.new(w * 0.8 + 50.0, h * 0.2 + 50.0, 50.0, h * 0.15 + 50.0))
		self.corridors.append(ProceduralArena.Corridor.new(w * 0.8 + 50.0, h * 0.65 + 50.0, 50.0, h * 0.15 + 50.0))

		# Hazards
		var h1 = ProceduralArena.Hazard.new()
		h1.id = 0
		h1.x = w * 0.5 + 75.0
		h1.y = h * 0.35 + 75.0
		h1.radius = 30.0
		h1.kind = "spikes"
		h1.damage = 20.0
		self.hazards.append(h1)
		var h2 = ProceduralArena.Hazard.new()
		h2.id = 1
		h2.x = w * 0.5 + 75.0
		h2.y = h * 0.65 + 75.0
		h2.radius = 30.0
		h2.kind = "lava"
		h2.damage = 50.0
		self.hazards.append(h2)


class BlackHoleArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = width
		var h = height
		var cx = w / 2.0
		var cy = h / 2.0
		rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))
		rooms.append(ProceduralArena.Room.new(50.0, 50.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(w - 250.0, 50.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(50.0, h - 250.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(w - 250.0, h - 250.0, 200.0, 200.0))
		corridors.append(ProceduralArena.Corridor.new(100.0, 200.0, 100.0, cy - 400.0))
		corridors.append(ProceduralArena.Corridor.new(100.0, cy - 300.0, cx - 300.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(w - 200.0, 200.0, 100.0, cy - 400.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 200.0, cy - 300.0, w - cx - 300.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(100.0, cy + 200.0, 100.0, h - cy - 400.0))
		corridors.append(ProceduralArena.Corridor.new(100.0, cy + 200.0, cx - 300.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(w - 200.0, cy + 200.0, 100.0, h - cy - 400.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 200.0, cy + 200.0, w - cx - 300.0, 100.0))
		var h0 = ProceduralArena.Hazard.new(0, cx, cy, 200.0, "black_hole", 30.0)
		hazards.append(h0)


class ThunderstormArena extends ProceduralArena:
	var lightning_timer = 0.0
	var strike_interval = 2.0

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func update_zone(current_tick: int, delta: float) -> void:
		super.update_zone(current_tick, delta)
		lightning_timer += delta
		if lightning_timer >= strike_interval:
			lightning_timer = 0.0
			var x = randf_range(50.0, width - 50.0)
			var y = randf_range(50.0, height - 50.0)
			var h_id = 9000 + hazards.size() + (randi() % 1000)
			var lightning = ProceduralArena.Hazard.new(h_id, x, y, 60.0, "lightning", 300.0)
			lightning.set_meta("target_radius", 60.0)
			lightning.set_meta("duration", 0.5)
			hazards.append(lightning)

		var surviving_hazards = []
		for h in hazards:
			if h.kind == "lightning":
				var duration = h.get_meta("duration", 0.0)
				duration -= delta
				h.set_meta("duration", duration)
				if duration > 0:
					surviving_hazards.append(h)
			else:
				surviving_hazards.append(h)
		hazards = surviving_hazards


class PinballArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))
        rooms.append(ProceduralArena.Room.new(50.0, cy - 100.0, 150.0, 400.0))
        rooms.append(ProceduralArena.Room.new(w - 200.0, cy - 100.0, 150.0, 400.0))

        corridors.append(ProceduralArena.Corridor.new(200.0, cy + 100.0, cx - 300.0 - 200.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, cy + 100.0, w - 200.0 - (cx + 300.0), 100.0))

        for i in range(12):
            var bx = cx + randf_range(-250.0, 250.0)
            var by = cy + randf_range(-250.0, 250.0)
            hazards.append(ProceduralArena.Hazard.new(hazards.size(), bx, by, 30.0, "bumper", 0.0))

        var f_left = ProceduralArena.Hazard.new(hazards.size(), cx - 150.0, cy + 200.0, 50.0, "pinball_flipper", 10.0)
        f_left.set_meta("flipper_side", "left")
        f_left.set_meta("flip_timer", 0.0)
        hazards.append(f_left)

        var f_right = ProceduralArena.Hazard.new(hazards.size(), cx + 150.0, cy + 200.0, 50.0, "pinball_flipper", 10.0)
        f_right.set_meta("flipper_side", "right")
        f_right.set_meta("flip_timer", 0.0)
        hazards.append(f_right)

    func update_zone(current_tick: int, delta: float) -> void:
        super.update_zone(current_tick, delta)
        for h in hazards:
            if h.kind == "pinball_flipper":
                var ft = 0.0
                if h.has_meta("flip_timer"):
                    ft = h.get_meta("flip_timer")

                if ft > 0:
                    h.set_meta("flip_timer", ft - delta)
                else:
                    if randf() < 0.05:
                        h.set_meta("flip_timer", 0.5)


class SpringArena extends ProceduralArena:
	func _init(size: float = 2000.0, seed_val = null):
		super._init(size, seed_val)
		generate()

	func generate():
		super.generate()
		var w = width
		var h = height

		# Add numerous bounce pads
		for i in range(15):
			var x = randf_range(100.0, w - 100.0)
			var y = randf_range(100.0, h - 100.0)
			var h_id = 3500 + hazards.size()
			var radius = randf_range(40.0, 70.0)
			var pad = ProceduralArena.Hazard.new(h_id, x, y, radius, "bounce_pad", 0.0)
			pad.set_meta("vx", randf_range(-10.0, 10.0))
			pad.set_meta("vy", randf_range(-10.0, 10.0))
			hazards.append(pad)

class IceArena extends ProceduralArena:
	func _init(arena_size: float = 2000.0, seed_val = null).(arena_size, 5, seed_val):
		self.is_snowing = true
		self.weather = "ice"
		self.base_friction = 0.2

	func generate():
		.generate()
		var cx = self.width / 2.0
		var cy = self.height / 2.0
		for i in range(5):
			var hx = randf_range(cx - 300.0, cx + 300.0)
			var hy = randf_range(cy - 300.0, cy + 300.0)
			var radius = randf_range(150.0, 300.0)
			var h = ProceduralArena.Hazard.new(self.hazards.size() + 500, hx, hy, radius, "ice_patches", 0.0)
			self.hazards.append(h)


class PlatformerArena extends ProceduralArena:
	func _init(size: float = 2000.0, seed_val = null):
		super(10000.0, 1, seed_val)
		self.height = 1000.0
		self.name = "platformer"

	func generate():
		super.generate()
		rooms.clear()
		corridors.clear()
		hazards.clear()
		rooms.append(ProceduralArena.Room.new(0.0, 400.0, 500.0, 200.0))
		for i in range(1, 15):
			var x = i * 650.0
			rooms.append(ProceduralArena.Room.new(x, 400.0, 400.0, 200.0))
			if i % 2 == 0:
				hazards.append(ProceduralArena.Hazard.new(100+i, x - 125.0, 500.0, 20.0, "grapple_node", 0.0))
			else:
				hazards.append(ProceduralArena.Hazard.new(200+i, x - 200.0, 450.0, 40.0, "bounce_pad", 0.0))

const ARENAS = [
	"platformer",
	"falling_panels",
	"ice",
    "spring",
    "shrinking_hazards",

	"thunderstorm",
	"thick_fog",
	"black_hole",
	"neural_ball",
	"flee",
	"ball_genetics",
	"funny_fails",
	"escort",
	"wait_and_watch",
    "battle_royale_shrinking_zone",
	"emotional_contagion",
	"body_block",
	"meta_evolution",
    "swarm_intelligence",
    "avoid_trap",
    "kite",
    "procedural",
	"time_distortion",
    "cross",
    "ring",
    "four_rooms",
    "grid",
    "labyrinth",
    "hazard_pit",
    "duel",
    "long_corridor",
    "zigzag",
    "fortress",
    "split",
    "flank",
    "group_attack",
    "choke_point",
    "use_shield",
    "retreat_to_ally",
    "health_link",
    "buff_ally",
    "aggressive_chase",
    "comebacks",
    "circle_strafe",
    "epic_kills",
    "reposition",
    "ai_commentary",
	"ball_relationships",
    "clutch_plays",
    "collect_booster",
    "finals_1v1",
    "team_wipes",
    "ambush",
    "physics_chain_reactions",
    "target_strong",
    "day_night",
    "pinball"
]


class DayNightArena extends ProceduralArena:
    var is_night = false
    var night_ratio = 0.0
    var day_night_timer = 0.0
    var phase_duration = 10.0
    var is_eclipse = false
    var eclipse_timer = 0.0
    var time_until_eclipse = 30.0

    func _init(size: float = 2000.0, seed_val = null):
        super(size, 5, seed_val)
        if rng != null:
            time_until_eclipse = rng.randf_range(20.0, 40.0)
        else:
            time_until_eclipse = randf_range(20.0, 40.0)

    func generate():
        super.generate()
        is_eclipse = false
        eclipse_timer = 0.0
        if rng != null:
            time_until_eclipse = rng.randf_range(20.0, 40.0)
        else:
            time_until_eclipse = randf_range(20.0, 40.0)

    func update_zone(current_tick: int, delta: float) -> void:
        super.update_zone(current_tick, delta)
        day_night_timer += delta
        if day_night_timer >= phase_duration:
            day_night_timer = 0.0
            is_night = not is_night

        if is_night:
            night_ratio = day_night_timer / max(0.1, phase_duration)
        else:
            night_ratio = 0.0

        if is_eclipse:
            eclipse_timer -= delta
            if eclipse_timer <= 0:
                is_eclipse = false
                if rng != null:
                    time_until_eclipse = rng.randf_range(20.0, 40.0)
                else:
                    time_until_eclipse = randf_range(20.0, 40.0)
        else:
            time_until_eclipse -= delta
            if time_until_eclipse <= 0:
                is_eclipse = true
                eclipse_timer = 10.0

class ThickFogArena extends ProceduralArena:
	var is_foggy = false
	var is_raining = false
	var is_sandstorming = false
	var is_snowing = false
	var fog_timer = 0.0
	var phase_duration = 20.0

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func update_zone(current_tick: int, delta: float) -> void:
		super.update_zone(current_tick, delta)
		fog_timer += delta
		if fog_timer >= phase_duration:
			fog_timer = 0.0
			is_foggy = not is_foggy

class SummerArena extends ProceduralArena:
	var is_heatwave = true

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func generate() -> void:
		super.generate()
		# Add sun flares
		for i in range(4):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 5000 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(30.0, 80.0), "sun_flare", 15.0))
		# Add sand traps
		for i in range(5):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 5100 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(50.0, 100.0), "sand_trap", 0.0))

	func update_zone(current_tick: int, delta: float) -> void:
		super.update_zone(current_tick, delta)
		if is_heatwave and current_tick % 300 == 0 and randf() < 0.3:
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 15000 + hazards.size()
			var hw = ProceduralArena.Hazard.new(h_id, x, y, 100.0, "localized_heatwave", 0.0)
			hw.set_meta("duration", 10.0)
			hazards.append(hw)

		for h in hazards:
			if h.kind == "localized_heatwave":
				var dur = h.get_meta("duration") - delta
				h.set_meta("duration", dur)
				if dur <= 0:
					if h.has_method("set_meta"):
						h.set_meta("active", false)
					if "active" in h:
						h.active = false



class WaterArena extends ProceduralArena:
	var is_water_theme = true
	func _init(arena_size: float = 2000.0, seed_val = null):
		super(arena_size, 5, seed_val)
	func generate():
		super.generate()
		# Add whirlpools
		for i in range(5):
			var x = rng.randf_range(100.0, width - 100.0)
			var y = rng.randf_range(100.0, height - 100.0)
			var h_id = 6000 + hazards.size()
			var whirlpool = preload("res://src/arena/procedural_arena.gd").Hazard.new(h_id, x, y, rng.randf_range(50.0, 100.0), "whirlpool", 10.0)
			hazards.append(whirlpool)

class LavaArena extends ProceduralArena:
	var is_lava_theme = true

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func generate() -> void:
		super.generate()
		for i in range(5):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 1000 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(30.0, 80.0), "lava", 15.0))

class NeonArena extends ProceduralArena:
	var is_neon_theme = true

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func generate() -> void:
		super.generate()
		for i in range(5):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 2000 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(40.0, 60.0), "bounce_pad", 0.0))

class AutumnArena extends ProceduralArena:
	var is_windy = true

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func generate() -> void:
		super.generate()
		for i in range(3):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 3000 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(50.0, 100.0), "tornado", 5.0))

	func update_zone(current_tick: int, delta: float) -> void:
		super.update_zone(current_tick, delta)
		if is_windy and current_tick % 300 == 0 and randf() < 0.5:
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 17000 + hazards.size()
			var ProceduralArena = load("res://src/arena/procedural_arena.gd")
			var tornado = ProceduralArena.Hazard.new(h_id, x, y, randf_range(50.0, 100.0), "tornado", 5.0)
			tornado.set_meta("duration", 15.0)
			tornado.set_meta("vx", randf_range(-100.0, 100.0))
			tornado.set_meta("vy", randf_range(-100.0, 100.0))
			hazards.append(tornado)

class WinterArena extends ProceduralArena:
	var is_snowing = true

	func _init(size: float = 2000.0, seed_val = null):
		super(size, 5, seed_val)

	func generate() -> void:
		super.generate()
		# Add ice patches
		for i in range(5):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 4000 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, randf_range(40.0, 120.0), "ice_patch", 0.0))
		# Add snowman decoys
		for i in range(3):
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 4100 + hazards.size()
			hazards.append(ProceduralArena.Hazard.new(h_id, x, y, 20.0, "snowman_decoy", 0.0))

	func update_zone(current_tick: int, delta: float) -> void:
		super.update_zone(current_tick, delta)
		if is_snowing and current_tick % 300 == 0 and randf() < 0.3:
			var x = randf_range(100, width - 100)
			var y = randf_range(100, height - 100)
			var h_id = 16000 + hazards.size()
			var bz = ProceduralArena.Hazard.new(h_id, x, y, 120.0, "localized_blizzard", 0.0)
			bz.set_meta("duration", 12.0)
			hazards.append(bz)

		for h in hazards:
			if h.kind == "localized_blizzard":
				var dur = h.get_meta("duration") - delta
				h.set_meta("duration", dur)
				if dur <= 0:
					if h.has_method("set_meta"):
						h.set_meta("active", false)
					if "active" in h:
						h.active = false



class TimeDistortionArena extends ProceduralArena:
	func generate() -> void:
		super.generate()
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = width
		var h = height
		var cx = w / 2.0
		var cy = h / 2.0

		rooms.append(ProceduralArena.Room.new(cx - 200.0, cy - 200.0, 400.0, 400.0))
		hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 200.0, "chrono_anomaly", 0.0))

class ShiftingBoundariesArena extends ProceduralArena:
	var min_x: float = 0.0
	var min_y: float = 0.0
	var max_x: float = 2000.0
	var max_y: float = 2000.0

	var target_min_x: float = 0.0
	var target_min_y: float = 0.0
	var target_max_x: float = 2000.0
	var target_max_y: float = 2000.0

	var shift_speed: float = 50.0

	func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
		super(_arena_size, _num_rooms, _seed)
		min_x = 0.0
		min_y = 0.0
		max_x = width
		max_y = height
		target_min_x = 0.0
		target_min_y = 0.0
		target_max_x = width
		target_max_y = height
		shift_speed = 50.0

	func generate() -> void:
		super.generate()
		_pick_new_targets()

	func _pick_new_targets() -> void:
		var min_size = 500.0
		target_min_x = randf_range(0.0, width - min_size)
		target_max_x = randf_range(target_min_x + min_size, width)

		target_min_y = randf_range(0.0, height - min_size)
		target_max_y = randf_range(target_min_y + min_size, height)

	func update_zone(current_tick: int, delta: float) -> void:
		var is_new_tick = current_tick != last_tick
		super.update_zone(current_tick, delta)

		if is_new_tick:
			var step = shift_speed * delta

			var move_towards = func(current: float, target: float, max_step: float) -> float:
				if current < target:
					return min(current + max_step, target)
				elif current > target:
					return max(current - max_step, target)
				return current

			min_x = move_towards.call(min_x, target_min_x, step)
			max_x = move_towards.call(max_x, target_max_x, step)
			min_y = move_towards.call(min_y, target_min_y, step)
			max_y = move_towards.call(max_y, target_max_y, step)

			if min_x == target_min_x and max_x == target_max_x and min_y == target_min_y and max_y == target_max_y:
				_pick_new_targets()

			for hazard in hazards:
				hazard.x = max(min_x + hazard.radius, min(max_x - hazard.radius, hazard.x))
				hazard.y = max(min_y + hazard.radius, min(max_y - hazard.radius, hazard.y))

			if "platforms" in self:
				for p in self.platforms:
					var pw_half = p.width / 2.0
					var ph_half = p.height / 2.0
					p.x = max(min_x + pw_half, min(max_x - pw_half, p.x))
					p.y = max(min_y + ph_half, min(max_y - ph_half, p.y))

	func is_point_inside(px: float, py: float, radius: float) -> bool:
		if not (min_x + radius <= px and px <= max_x - radius and min_y + radius <= py and py <= max_y - radius):
			return false
		return super.is_point_inside(px, py, radius)

	func clamp_position(px: float, py: float, radius: float) -> Array:
		var bounced = false
		var new_x = px
		var new_y = py

		if new_x < min_x + radius:
			new_x = min_x + radius
			bounced = true
		elif new_x > max_x - radius:
			new_x = max_x - radius
			bounced = true

		if new_y < min_y + radius:
			new_y = min_y + radius
			bounced = true
		elif new_y > max_y - radius:
			new_y = max_y - radius
			bounced = true

		var res = super.clamp_position(new_x, new_y, radius)
		var res_x = res[0]
		var res_y = res[1]
		var proc_bounced = res[2]

		var final_x = max(min_x + radius, min(max_x - radius, res_x))
		var final_y = max(min_y + radius, min(max_y - radius, res_y))

		if final_x != res_x or final_y != res_y:
			proc_bounced = true

		return [final_x, final_y, bounced or proc_bounced]
