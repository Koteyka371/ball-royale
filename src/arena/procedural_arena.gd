class_name ProceduralArena
extends RefCounted

var width: float
var height: float
var num_rooms: int
var rooms: Array = []
var corridors: Array = []
var hazards: Array = []
var rng: RandomNumberGenerator

var safe_zone_radius: float
var safe_zone_center: Array
var last_tick: int = -1
var danger_grid: Dictionary = {}

class Hazard:
    var id: int
    var x: float
    var y: float
    var radius: float
    var target_radius: float
    var kind: String
    var damage: float
    var active: bool

    func _init(_id: int, _x: float, _y: float, _radius: float, _kind: String, _damage: float):
        id = _id
        x = _x
        y = _y
        radius = _radius
        target_radius = _radius
        kind = _kind
        damage = _damage
        active = true
        set_meta("active", true)

class Room:
    var x: float
    var y: float
    var width: float
    var height: float

    func _init(_x: float, _y: float, _w: float, _h: float):
        x = _x
        y = _y
        width = _w
        height = _h

class Corridor:
    var x: float
    var y: float
    var width: float
    var height: float

    func _init(_x: float, _y: float, _w: float, _h: float):
        x = _x
        y = _y
        width = _w
        height = _h

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
    width = _arena_size
    height = _arena_size
    num_rooms = _num_rooms
    rng = RandomNumberGenerator.new()
    if _seed != null:
        rng.seed = _seed
    else:
        rng.randomize()

    safe_zone_radius = width * 0.7
    safe_zone_center = [width / 2.0, height / 2.0]
    last_tick = -1

    generate()

func generate():
    var attempts = 0
    while rooms.size() < num_rooms and attempts < 1000:
        attempts += 1
        var max_size = min(600.0, width / 2.0)
        var rw = rng.randf_range(200.0, max_size)
        var rh = rng.randf_range(200.0, max_size)
        var rx = rng.randf_range(50.0, width - rw - 50.0)
        var ry = rng.randf_range(50.0, height - rh - 50.0)

        var overlap = false
        for r in rooms:
            if not (rx + rw + 50.0 < r.x or rx > r.x + r.width + 50.0 or ry + rh + 50.0 < r.y or ry > r.y + r.height + 50.0):
                overlap = true
                break

        if not overlap:
            rooms.append(ProceduralArena.Room.new(rx, ry, rw, rh))

    if rooms.size() == 0:
        return

    var connected = [rooms[0]]
    var unconnected = []
    for i in range(1, rooms.size()):
        unconnected.append(rooms[i])

    while unconnected.size() > 0:
        var best_dist = INF
        var best_r1 = null
        var best_r2 = null
        var best_idx = -1

        for c_room in connected:
            var c_cx = c_room.x + c_room.width / 2.0
            var c_cy = c_room.y + c_room.height / 2.0
            for i in range(unconnected.size()):
                var u_room = unconnected[i]
                var u_cx = u_room.x + u_room.width / 2.0
                var u_cy = u_room.y + u_room.height / 2.0
                var dist = (c_cx - u_cx) * (c_cx - u_cx) + (c_cy - u_cy) * (c_cy - u_cy)
                if dist < best_dist:
                    best_dist = dist
                    best_r1 = c_room
                    best_r2 = u_room
                    best_idx = i

        if best_r1 == null or best_r2 == null:
            break

        var r1 = best_r1
        var r2 = best_r2

        var c1x = r1.x + r1.width / 2.0
        var c1y = r1.y + r1.height / 2.0
        var c2x = r2.x + r2.width / 2.0
        var c2y = r2.y + r2.height / 2.0

        if rng.randf() < 0.5:
            corridors.append(ProceduralArena.Corridor.new(min(c1x, c2x) - 25.0, c1y - 25.0, abs(c2x - c1x) + 50.0, 50.0))
            corridors.append(ProceduralArena.Corridor.new(c2x - 25.0, min(c1y, c2y) - 25.0, 50.0, abs(c2y - c1y) + 50.0))
        else:
            corridors.append(ProceduralArena.Corridor.new(c1x - 25.0, min(c1y, c2y) - 25.0, 50.0, abs(c2y - c1y) + 50.0))
            corridors.append(ProceduralArena.Corridor.new(min(c1x, c2x) - 25.0, c2y - 25.0, abs(c2x - c1x) + 50.0, 50.0))

        connected.append(r2)
        unconnected.remove_at(best_idx)

    var num_hazards = num_rooms * 2
    for i in range(num_hazards):
        var r = rng.randf()
        var kind = "spikes"
        if r < 0.25:
            kind = "lava"
        elif r < 0.34:
            kind = "hidden_mine"
        elif r < 0.35:
            kind = "fake_booster"
        elif r < 0.4:
            kind = "decoy_item"
        elif r < 0.42:
            kind = "clone_booster"
        elif r < 0.43:
            kind = "invert_booster"
        elif r < 0.44:
            kind = "portal_gun_item"
        elif r < 0.45:
            kind = "silence_booster"
        elif r < 0.46:
            kind = "freeze_booster"
        elif r < 0.5:
            kind = "stamina_booster"
        elif r < 0.55:
            kind = "weather_booster"
        elif r < 0.75:
            kind = "proximity_trap"
        elif r < 0.9:
            kind = "spinning_laser"
        elif r < 0.92:
            kind = "hidden_trap"
        elif r < 0.96:
            kind = "magnet"
        elif r < 0.98:
            kind = "bumper"
        elif r < 0.985:
            kind = "quicksand"
        elif r < 0.990:
            kind = "magnet_booster"
        elif r < 0.992:
            kind = "material_magnet_booster"
        elif r < 0.995:
            kind = "breakable_wall"
        elif r < 0.997:
            kind = "tornado"
        elif r < 0.999:
            kind = "lightning_storm"
        elif r < 0.9995:
            kind = "stealth_zone"
        elif r < 0.9997:
            kind = "stamina_drain_zone"
        elif r < 0.9998:
            kind = "slip_zone"
        elif r < 0.99982:
            kind = "frictionless_zone"
        elif r < 0.99985:
            kind = "vortex"
        elif r < 0.9999:
            kind = "tall_grass"
        else:
            kind = "switch"

        var radius = 15.0
        var damage = 20.0
        if kind == "spikes":
            radius = rng.randf_range(15.0, 30.0)
            damage = 20.0
        elif kind == "lava":
            radius = rng.randf_range(30.0, 60.0)
            damage = 50.0
        elif kind == "proximity_trap":
            radius = rng.randf_range(20.0, 40.0)
            damage = 30.0
        elif kind == "hidden_trap":
            radius = rng.randf_range(20.0, 35.0)
            damage = 15.0
        elif kind == "magnet":
            radius = rng.randf_range(25.0, 45.0)
            damage = 0.0
            var new_hazard = ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage)
            new_hazard.set_meta("polarity", 1 if rng.randf() > 0.5 else -1)
            hazards.append(new_hazard)
            continue

        elif kind == "bumper":
            radius = rng.randf_range(30.0, 60.0)
            damage = 0.0
            var s = get_random_spawn_point(radius)
            var new_hazard = Hazard.new(i, s[0], s[1], radius, kind, damage)
            if rng.randf() < 0.4:
                var powerups = ["heal", "speed", "shield", "stamina"]
                new_hazard.set_meta("powerup_type", powerups[rng.randi() % powerups.size()])
            if kind == "breakable_wall":
                new_hazard.set_meta("hp", 100.0)
            if rng.randf() < 0.5:
                var target = null
                if hazards.size() > 0:
                    target = hazards[rng.randi_range(0, hazards.size() - 1)]
                if target != null:
                    new_hazard.set_meta("target_hazard_id", target.id)
                    new_hazard.set_meta("orbit_angle", rng.randf_range(0.0, PI * 2))
                    new_hazard.set_meta("orbit_radius", target.radius + radius + rng.randf_range(10.0, 50.0))
                    new_hazard.set_meta("orbit_speed", rng.randf_range(1.0, 3.0))
            else:
                var angle = rng.randf_range(0.0, PI * 2)
                var speed = rng.randf_range(50.0, 150.0)
                new_hazard.set_meta("vx", cos(angle) * speed)
                new_hazard.set_meta("vy", sin(angle) * speed)
            hazards.append(new_hazard)
            continue
        elif kind == "quicksand":
            radius = rng.randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "magnet_booster" or kind == "material_magnet_booster":
            radius = 15.0
            damage = 0.0
        elif kind == "breakable_wall":
            radius = rng.randf_range(30.0, 60.0)
            damage = 0.0
        elif kind == "switch":
            radius = 20.0
            damage = 0.0
        elif kind == "hidden_mine":
            radius = 15.0
            damage = 30.0
        elif kind == "silence_booster":
            radius = 15.0
            damage = 0.0
        elif kind == "freeze_booster":
            radius = 15.0
            damage = 0.0
        elif kind == "link_booster":
            radius = 15.0
            damage = 0.0
        elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "material_magnet_booster" or kind == "clone_booster" or kind == "invert_booster" or kind == "freeze_booster" or kind == "reverse_gravity_booster":
            radius = 15.0
            damage = 0.0
        elif kind == "stealth_zone":
            radius = randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "tornado":
            radius = rng.randf_range(30.0, 60.0)
            damage = 15.0
        elif kind == "lightning_storm":
            radius = rng.randf_range(30.0, 60.0)
            damage = 0.0
        elif kind == "tether_trap":
            radius = rng.randf_range(50.0, 100.0)
            damage = 0.0
        elif kind == "stamina_drain_zone":
            radius = rng.randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "slip_zone":
            radius = rng.randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "frictionless_zone":
            radius = rng.randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "tall_grass":
            radius = rng.randf_range(30.0, 60.0)
            damage = 5.0
        elif kind == "vortex":
            radius = 80.0
            damage = 20.0
        elif kind == "spinning_laser":
            radius = rng.randf_range(100.0, 150.0)
            damage = 100.0
        else:
            radius = 15.0
            damage = 50.0

        var spawn_pt = get_random_spawn_point(radius)
        hazards.append(ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage))

    # Generate guaranteed paired portals
    var num_portals = max(1, num_rooms / 2)
    for p in range(num_portals):
        var p1_id = hazards.size() + 5000 + p*2
        var p2_id = hazards.size() + 5000 + p*2 + 1

        var p1_pt = get_random_spawn_point(30.0)
        var p2_pt = get_random_spawn_point(30.0)

        var portal1 = ProceduralArena.Hazard.new(p1_id, p1_pt[0], p1_pt[1], 30.0, "portal", 0.0)
        portal1.set_meta("target_x", p2_pt[0])
        portal1.set_meta("target_y", p2_pt[1])

        var portal2 = ProceduralArena.Hazard.new(p2_id, p2_pt[0], p2_pt[1], 30.0, "portal", 0.0)
        var is_two_way = randf() < 0.5
        if is_two_way:
            portal2.set_meta("target_x", p1_pt[0])
            portal2.set_meta("target_y", p1_pt[1])

        var bh_hazards = []
        for h in hazards:
            if h.kind == "black_hole":
                bh_hazards.append(h)
        if bh_hazards.size() > 0 and randf() < 0.3:
            var target_bh = bh_hazards[randi() % bh_hazards.size()]
            portal1.set_meta("target_hazard_id", target_bh.id)
            if is_two_way:
                portal2.set_meta("target_hazard_id", target_bh.id)

        hazards.append(portal1)
        hazards.append(portal2)

        # Generate guaranteed paired swap portals
        var num_swap_portals = max(1, num_rooms / 2)
        for p in range(num_swap_portals):
            var sp1_id = hazards.size() + 8000 + p*2
            var sp2_id = hazards.size() + 8000 + p*2 + 1

            var sp1_pt = get_random_spawn_point(30.0)
            var sp2_pt = get_random_spawn_point(30.0)

            var sp1 = ProceduralArena.Hazard.new(sp1_id, sp1_pt[0], sp1_pt[1], 30.0, "swap_portal", 0.0)
            sp1.set_meta("target_x", sp2_pt[0])
            sp1.set_meta("target_y", sp2_pt[1])
            sp1.set_meta("pair_id", sp2_id)

            var sp2 = ProceduralArena.Hazard.new(sp2_id, sp2_pt[0], sp2_pt[1], 30.0, "swap_portal", 0.0)
            sp2.set_meta("target_x", sp1_pt[0])
            sp2.set_meta("target_y", sp1_pt[1])
            sp2.set_meta("pair_id", sp1_id)

            hazards.append(sp1)
            hazards.append(sp2)
        # Generate guaranteed paired wormholes
        var num_wormholes = max(1, num_rooms / 2)
        for p in range(num_wormholes):
            var w1_id = hazards.size() + 9000 + p*2
            var w2_id = hazards.size() + 9000 + p*2 + 1

            var w1_pt = get_random_spawn_point(30.0)
            var w2_pt = get_random_spawn_point(30.0)

            var w1 = ProceduralArena.Hazard.new(w1_id, w1_pt[0], w1_pt[1], 30.0, "wormhole", 0.0)
            w1.set_meta("target_x", w2_pt[0])
            w1.set_meta("target_y", w2_pt[1])

            var w2 = ProceduralArena.Hazard.new(w2_id, w2_pt[0], w2_pt[1], 30.0, "wormhole", 0.0)
            w2.set_meta("target_x", w1_pt[0])
            w2.set_meta("target_y", w1_pt[1])

            hazards.append(w1)
            hazards.append(w2)


    # Generate random one-way teleporters
    var num_oneway_teleporters = max(1, num_rooms / 2)
    for t in range(num_oneway_teleporters):
        var t_id = hazards.size() + 6500 + t
        var tx_pt = get_random_spawn_point(25.0)
        var target_pt = get_random_spawn_point(25.0)
        var teleporter = ProceduralArena.Hazard.new(t_id, tx_pt[0], tx_pt[1], 25.0, "one_way_teleporter", 0.0)
        teleporter.set_meta("target_x", target_pt[0])
        teleporter.set_meta("target_y", target_pt[1])
        teleporter.set_meta("change_timer", 5.0)
        hazards.append(teleporter)

    # Generate random teleporter pads
    var num_teleporters = max(2, num_rooms)
    if num_teleporters % 2 != 0:
        num_teleporters += 1

    var teleporters = []
    for t in range(num_teleporters):
        var t_id = hazards.size() + 6000 + t
        var t_pt = get_random_spawn_point(25.0)
        var teleporter = ProceduralArena.Hazard.new(t_id, t_pt[0], t_pt[1], 25.0, "teleporter", 0.0)
        teleporters.append(teleporter)

    # Link them in pairs
    for i in range(0, teleporters.size(), 2):
        var t1 = teleporters[i]
        var t2 = teleporters[i+1]
        t1.set_meta("target_x", t2.x)
        t1.set_meta("target_y", t2.y)
        t2.set_meta("target_x", t1.x)
        t2.set_meta("target_y", t1.y)

        hazards.append(t1)
        hazards.append(t2)

func get_random_spawn_point(radius: float) -> Array:
    if rooms.size() == 0:
        return [rng.randf_range(radius, width - radius), rng.randf_range(radius, height - radius)]
    var room = rooms[rng.randi_range(0, rooms.size() - 1)]
    return [rng.randf_range(room.x + radius, room.x + room.width - radius),
            rng.randf_range(room.y + radius, room.y + room.height - radius)]

func is_point_inside(x: float, y: float, radius: float) -> bool:
    var sz_cx = safe_zone_center[0]
    var sz_cy = safe_zone_center[1]
    var dist = sqrt((x - sz_cx)*(x - sz_cx) + (y - sz_cy)*(y - sz_cy))
    if dist > max(0.0, safe_zone_radius - radius):
        return false
    for r in rooms:
        if r.x + radius <= x and x <= r.x + r.width - radius and r.y + radius <= y and y <= r.y + r.height - radius:
            return true
    for c in corridors:
        if c.x + radius <= x and x <= c.x + c.width - radius and c.y + radius <= y and y <= c.y + c.height - radius:
            return true
    return false

func clamp_position(x: float, y: float, radius: float) -> Array:
    if is_point_inside(x, y, radius):
        return [x, y, false]

    var min_dist = INF
    var nearest_x = x
    var nearest_y = y

    for r in rooms:
        var cx = max(r.x + radius, min(x, r.x + r.width - radius))
        var cy = max(r.y + radius, min(y, r.y + r.height - radius))
        var dist = (cx - x)*(cx - x) + (cy - y)*(cy - y)
        if dist < min_dist:
            min_dist = dist
            nearest_x = cx
            nearest_y = cy

    for c in corridors:
        var cx = max(c.x + radius, min(x, c.x + c.width - radius))
        var cy = max(c.y + radius, min(y, c.y + c.height - radius))
        var dist = (cx - x)*(cx - x) + (cy - y)*(cy - y)
        if dist < min_dist:
            min_dist = dist
            nearest_x = cx
            nearest_y = cy

    var sz_cx = safe_zone_center[0]
    var sz_cy = safe_zone_center[1]
    var sz_dist = sqrt((nearest_x - sz_cx)*(nearest_x - sz_cx) + (nearest_y - sz_cy)*(nearest_y - sz_cy))

    if sz_dist > max(0.0, safe_zone_radius - radius):
        if sz_dist > 0.0001:
            var dir_x = (nearest_x - sz_cx) / sz_dist
            var dir_y = (nearest_y - sz_cy) / sz_dist
            nearest_x = sz_cx + dir_x * max(0.0, safe_zone_radius - radius)
            nearest_y = sz_cy + dir_y * max(0.0, safe_zone_radius - radius)
        else:
            nearest_x = sz_cx
            nearest_y = sz_cy

    return [nearest_x, nearest_y, true]


func update_zone(current_tick: int, delta: float) -> void:
    if current_tick != last_tick:
        if "hazards" in self:
            for hazard in hazards:
                if hazard.kind == "sinkhole" or hazard.kind == "massive_sinkhole":
                    hazard.radius += 2.0 * delta
                    for other_hazard in hazards:
                        if hazard.id == other_hazard.id:
                            continue
                        var dist = Vector2(hazard.x, hazard.y).distance_to(Vector2(other_hazard.x, other_hazard.y))
                        if dist < hazard.radius + other_hazard.radius:
                            if other_hazard.kind == "quicksand":
                                hazard.kind = "massive_sinkhole"
                                hazard.radius += other_hazard.radius * 0.5
                                if other_hazard.has_method("set_meta"):
                                    other_hazard.set_meta("active", false)
                                else:
                                    other_hazard.active = false
                            elif other_hazard.kind != "sinkhole" and other_hazard.kind != "massive_sinkhole":
                                var is_active = true
                                if other_hazard.has_method("has_meta") and other_hazard.has_meta("active"):
                                    is_active = other_hazard.get_meta("active")
                                elif "active" in other_hazard:
                                    is_active = other_hazard.active

                                if is_active:
                                    hazard.radius += other_hazard.radius * 0.1
                                    if other_hazard.has_method("set_meta"):
                                        other_hazard.set_meta("active", false)
                                    else:
                                        other_hazard.active = false

            for hazard in hazards:
                if hazard.kind == "slip_zone":
                    if not "active_timer" in hazard:
                        if hazard.has_method("set_meta"):
                            hazard.set_meta("active_timer", 0.0)
                            hazard.set_meta("active", true)
                        else:
                            hazard.active_timer = 0.0
                            hazard.active = true

                    var timer = hazard.get_meta("active_timer") if hazard.has_method("get_meta") and hazard.has_meta("active_timer") else hazard.get("active_timer")
                    timer += delta
                    if timer >= 5.0:
                        timer = 0.0
                        var active = hazard.get_meta("active") if hazard.has_method("get_meta") and hazard.has_meta("active") else hazard.get("active")
                        if hazard.has_method("set_meta"):
                            hazard.set_meta("active", not active)
                        else:
                            hazard.active = not active

                    if hazard.has_method("set_meta"):
                        hazard.set_meta("active_timer", timer)
                    else:
                        hazard.active_timer = timer
            for hazard in hazards:
                if hazard.kind == "magnet":
                    for other_hazard in hazards:
                        var h_id = hazard.get_instance_id() if typeof(hazard) == TYPE_OBJECT else hash(hazard)
                        var oh_id = other_hazard.get_instance_id() if typeof(other_hazard) == TYPE_OBJECT else hash(other_hazard)
                        if h_id == oh_id:
                            continue
                        if other_hazard.kind == "explosive_barrel" or other_hazard.kind == "flare":
                            var hx_diff = hazard.x - other_hazard.x
                            var hy_diff = hazard.y - other_hazard.y
                            var hdist_sq = hx_diff * hx_diff + hy_diff * hy_diff
                            var eff_rad = hazard.radius * 3.0
                            if hdist_sq > 0.0001 and hdist_sq < eff_rad * eff_rad:
                                var hdist = sqrt(hdist_sq)
                                var hnx = hx_diff / hdist
                                var hny = hy_diff / hdist
                                var h_min_dist = hdist
                                if h_min_dist < 10.0:
                                    h_min_dist = 10.0
                                var pull_strength = (eff_rad / h_min_dist) * 150.0 * delta
                                pull_strength = min(pull_strength, hdist * 0.5)

                                other_hazard.x += hnx * pull_strength
                                other_hazard.y += hny * pull_strength

                                var other_rad = other_hazard.radius if "radius" in other_hazard else 10.0
                                if hdist < hazard.radius + other_rad:
                                    if other_hazard.kind == "explosive_barrel":
                                        var is_exploded = other_hazard.is_exploded if "is_exploded" in other_hazard else false
                                        if not is_exploded:
                                            if typeof(other_hazard) == TYPE_OBJECT and not other_hazard is Dictionary:
                                                if other_hazard.has_method("set_meta"):
                                                    other_hazard.set("is_exploded", true)
                                                    if "radius" in other_hazard:
                                                        other_hazard.radius = other_hazard.radius * 3.0
                                                    if "damage" in other_hazard:
                                                        other_hazard.damage = other_hazard.damage * 2.0
                                            else:
                                                other_hazard["is_exploded"] = true
                                                if other_hazard.has("radius"):
                                                    other_hazard["radius"] = other_hazard["radius"] * 3.0
                                                if other_hazard.has("damage"):
                                                    other_hazard["damage"] = other_hazard["damage"] * 2.0
                                    elif other_hazard.kind == "flare":
                                        var is_active = other_hazard.active if "active" in other_hazard else true
                                        if is_active:
                                            if typeof(other_hazard) == TYPE_OBJECT and not other_hazard is Dictionary:
                                                if other_hazard.has_method("set_meta"):
                                                    other_hazard.set("active", false)
                                                    other_hazard.set("duration", 0.0)
                                            else:
                                                other_hazard["active"] = false
                                                other_hazard["duration"] = 0.0

                                            if typeof(hazard) == TYPE_OBJECT and not hazard is Dictionary:
                                                if hazard.has_method("set_meta"):
                                                    hazard.set("kind", "fire_zone")
                                                    if "radius" in hazard: hazard.radius = hazard.radius * 2.0
                                                    if "damage" in hazard: hazard.damage = hazard.damage * 3.0
                                                    if not "duration" in hazard: hazard.set("duration", 10.0)
                                            else:
                                                hazard["kind"] = "fire_zone"
                                                if hazard.has("radius"): hazard["radius"] = hazard["radius"] * 2.0
                                                if hazard.has("damage"): hazard["damage"] = hazard["damage"] * 3.0
                                                if not hazard.has("duration"): hazard["duration"] = 10.0
        last_tick = current_tick

        var has_mbh = false
        if "hazards" in self:
            for h in hazards:
                if h.kind == "massive_black_hole":
                    has_mbh = true
                    break

        if safe_zone_radius > 0.0:
            if has_mbh:
                safe_zone_radius -= 50.0 * delta
            else:
                safe_zone_radius -= 10.0 * delta
            if safe_zone_radius <= 0.0:
                safe_zone_radius = 0.0
        else:
            if current_tick % 300 == 0:
                var angle = randf_range(0, PI * 2)
                var drop_dist = safe_zone_radius + randf_range(-20.0, 100.0)
                var cx = safe_zone_center.x if typeof(safe_zone_center) == TYPE_VECTOR2 else safe_zone_center[0]
                var cy = safe_zone_center.y if typeof(safe_zone_center) == TYPE_VECTOR2 else safe_zone_center[1]
                var sx = cx + cos(angle) * drop_dist
                var sy = cy + sin(angle) * drop_dist

                sx = max(50.0, min(width - 50.0, sx))
                sy = max(50.0, min(height - 50.0, sy))

                var item_kinds = ["healing_spring", "damage_link", "emp_burst", "nemesis_booster", "stamina_booster", "vision_booster", "reverse_gravity_booster", "material_magnet_booster"]
                var item_kind = item_kinds[randi() % item_kinds.size()]

                var item_id = 9000 + hazards.size() + (randi() % 1000)
                var drop = Hazard.new(item_id, sx, sy, 20.0, item_kind, 0.0)
                hazards.append(drop)

            if current_tick % 120 == 0:
                if has_method("_trigger_event"):
                    var event_types = ["meteor_shower", "gravity_shift", "orbital_strike", "massive_black_hole_event"]
                    call("_trigger_event", event_types[randi() % event_types.size()], current_tick)
                else:
                    var event_types = ["meteor_shower", "gravity_shift"]
                    var event_type = event_types[randi() % event_types.size()]
                    if event_type == "meteor_shower":
                        for i in range(10):
                            var h_x = randf_range(50.0, width - 50.0)
                            var h_y = randf_range(50.0, height - 50.0)
                            var m_haz = Hazard.new(hazards.size() + (randi() % 9000) + 1000, h_x, h_y, 30.0, "meteor", 200.0)
                            m_haz.target_radius = 30.0
                            m_haz.set_meta("duration", 5.0)
                            hazards.append(m_haz)
                    elif event_type == "anomaly_zone":
                        var h_id = 6000 + hazards.size()
                        var zone = Hazard.new(h_id, width/2, height/2, 400.0, "anomaly_zone", 0.0)
                        zone.target_radius = 400.0
                        zone.set_meta("duration", 10.0)
                        hazards.append(zone)
                    elif event_type == "gravity_shift":
                        var gw = Hazard.new(hazards.size() + (randi() % 9000) + 1000, width/2, height/2, width/2, "gravity_well", 10.0)
                        gw.set_meta("duration", 10.0)
                        hazards.append(gw)

        var new_craters = []
        for h in hazards:
            if h.has_method("has_meta") and h.has_meta("frozen_timer"):
                var ft = h.get_meta("frozen_timer")
                if ft > 0:
                    h.set_meta("frozen_timer", ft - delta)
                    continue

            if "kind" in h and h.kind == "flare":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
            elif "kind" in h and h.kind == "weather_scanner":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
            elif "kind" in h and h.kind == "orbital_strike":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.kind = "orbital_strike_active"
                        h.set_meta("duration", 0.5)
                        h.damage = 1000.0
            elif "kind" in h and h.kind == "lightning_strike":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        if h.has_method("set_meta"):
                            h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
            elif "kind" in h and h.kind == "bumper":
                if h.has_meta("target_hazard_id"):
                    var t_id = h.get_meta("target_hazard_id")
                    var target = null
                    for th in hazards:
                        if th.id == t_id:
                            target = th
                            break
                    if target != null:
                        var cur_angle = h.get_meta("orbit_angle") if h.has_meta("orbit_angle") else 0.0
                        var o_speed = h.get_meta("orbit_speed") if h.has_meta("orbit_speed") else 1.0
                        var o_rad = h.get_meta("orbit_radius") if h.has_meta("orbit_radius") else 50.0
                        cur_angle += o_speed * delta
                        h.set_meta("orbit_angle", cur_angle)
                        h.x = target.x + cos(cur_angle) * o_rad
                        h.y = target.y + sin(cur_angle) * o_rad
                else:
                    if h.has_meta("vx") and h.has_meta("vy"):
                        h.x += h.get_meta("vx") * delta
                        h.y += h.get_meta("vy") * delta
                        if h.x < 0 or h.x > width:
                            h.set_meta("vx", h.get_meta("vx") * -1.0)
                        if h.y < 0 or h.y > height:
                            h.set_meta("vy", h.get_meta("vy") * -1.0)

            elif "kind" in h and h.kind == "one_way_teleporter":
                if h.has_meta("change_timer"):
                    var ct = h.get_meta("change_timer") - delta
                    if ct <= 0:
                        ct = 5.0
                        var new_target = get_random_spawn_point(25.0)
                        h.set_meta("target_x", new_target[0])
                        h.set_meta("target_y", new_target[1])
                    h.set_meta("change_timer", ct)
            elif "kind" in h and h.kind in ["tornado", "lightning_storm"]:
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        if h.has_method("set_meta"):
                            h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
                if h.has_meta("vx") and h.has_meta("vy"):
                    h.x += h.get_meta("vx") * delta
                    h.y += h.get_meta("vy") * delta
                    if h.x < 0 or h.x > width:
                        h.set_meta("vx", h.get_meta("vx") * -1.0)
                    if h.y < 0 or h.y > height:
                        h.set_meta("vy", h.get_meta("vy") * -1.0)
            elif "kind" in h and h.kind == "tornado_warning":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        if h.has_method("set_meta"):
                            h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
                        var HazardClass = load("res://src/arena/procedural_arena.gd").Hazard
                        var tornado = HazardClass.new(8000 + hazards.size() + (randi() % 1000), h.x, h.y, h.radius, "tornado", 20.0)
                        tornado.set_meta("duration", 5.0)
                        tornado.set_meta("vx", randf_range(-100.0, 100.0))
                        tornado.set_meta("vy", randf_range(-100.0, 100.0))
                        new_craters.append(tornado)
            elif "kind" in h and (h.kind == "fire_ring" or h.kind == "poison_nova"):
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
                    else:
                        var shrink_rate = 50.0
                        if h.has_meta("shrink_rate"):
                            shrink_rate = h.get_meta("shrink_rate")
                        h.radius = max(0.0, h.radius - shrink_rate * delta)
            elif "kind" in h and h.kind == "orbital_strike_active":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        if h.has_method("set_meta"):
                            h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
            elif "kind" in h and h.kind == "fire_zone":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
            elif "kind" in h and h.kind == "meteor":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    h.set_meta("duration", dur)
                    if dur <= 0:
                        h.set_meta("active", false)
                        if "active" in h:
                            h.active = false
                        var crater_id = 6000 + hazards.size() + new_craters.size() + (randi() % 1000)
                        var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
                        var crater = ProceduralArenaScript.Hazard.new(crater_id, h.x, h.y, h.radius * 1.5, "crater", 10.0)
                        new_craters.append(crater)

                        var fire_id = 7000 + hazards.size() + new_craters.size() + (randi() % 1000)
                        var fire_zone = ProceduralArenaScript.Hazard.new(fire_id, h.x, h.y, h.radius * 1.8, "fire_zone", 50.0)
                        fire_zone.set_meta("duration", 10.0)
                        new_craters.append(fire_zone)

                        var crater_size = h.radius * 3.0
                        var new_room = ProceduralArenaScript.Room.new(h.x - crater_size/2, h.y - crater_size/2, crater_size, crater_size)
                        rooms.append(new_room)
                        if has_method("queue_redraw"):
                            call("queue_redraw")
            elif h.id >= 1000 and h.radius < h.target_radius:
                h.radius += (h.target_radius / 600.0) * delta * 60.0
                if h.radius > h.target_radius:
                    h.radius = h.target_radius

        var active_hazards = []
        for h in hazards:
            var is_active = true
            if "active" in h:
                is_active = h.active
            elif h.has_method("has_meta") and h.has_meta("active"):
                is_active = h.get_meta("active")

            if is_active:
                active_hazards.append(h)
        for c in new_craters:
            active_hazards.append(c)
        hazards = active_hazards

        if current_tick % 60 == 0:
            if randf() < 0.1:
                var x = randf_range(50, width - 50)
                var y = randf_range(50, height - 50)
                var h_id = 2500 + hazards.size() + (randi() % 1000)
                var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
                var meteor = ProceduralArenaScript.Hazard.new(h_id, x, y, 30.0, "meteor", 200.0)
                meteor.target_radius = 30.0
                meteor.set_meta("duration", 5.0)
                hazards.append(meteor)

        if current_tick % 600 == 0:
            var new_hazards = []
            for h in hazards:
                if h.id < 1000:
                    new_hazards.append(h)
            hazards = new_hazards

            var event_types = ["meteor_shower", "gravity_shift", "moving_walls", "orbital_strike", "fire_ring", "anomaly_zone", "massive_black_hole_event", "none"]
            var event_type = event_types[randi() % event_types.size()]
            if event_type != "none":
                _trigger_event(event_type, current_tick)

            var num_zones = (randi() % 3) + 1
            for i in range(num_zones):
                var x = randf_range(200, width - 200)
                var y = randf_range(200, height - 200)
                var t_radius = randf_range(100.0, 250.0)
                var h_id = 1000 + hazards.size()
                var h = ProceduralArena.Hazard.new(h_id, x, y, 10.0, "trap", 100.0)
                h.target_radius = t_radius
                if randf() < 0.1:
                    h.kind = "drone_item"
                    h.damage = 0.0
                elif randf() < 0.1:
                    h.kind = "breakable_wall"
                    h.damage = 0.0
                    h.set_meta("hp", 100.0)
                elif randf() < 0.05:
                    h.kind = "launch_pad"
                    h.damage = 0.0
                    h.set_meta("target_x", randf_range(200.0, width - 200.0))
                    h.set_meta("target_y", randf_range(200.0, height - 200.0))
                elif randf() < 0.1:
                    h.kind = "bounce_pad"
                    h.damage = 0.0
                elif randf() < 0.1:
                    h.kind = "explosive_barrel"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "stealth_drone_item"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "shadow_booster"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "decoy_item"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "silence_booster"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "freeze_booster"
                    h.damage = 0.0
                elif randf() < 0.10:
                    h.kind = "placeable_trap_item"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "exit_portal_item"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "position_swap_item"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "portal_gun_item"
                    h.damage = 0.0
                elif randf() < 0.15:
                    h.kind = "quicksand"
                    h.damage = 10.0
                elif randf() < 0.10:
                    h.kind = "sinkhole"
                    h.damage = 5.0
                elif randf() < 0.05:
                    h.kind = "orbital_accelerator"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "loadout_fragment"
                    h.damage = 0.0
                elif randf() < 0.05:
                    h.kind = "decoy_spawner"
                    h.damage = 0.0
                elif randf() < 0.2:
                    h.kind = "gravity_well"
                    h.damage = 0.0
                hazards.append(h)

        if current_tick % 10 == 0:
            _update_danger_grid()

class CollectBoosterArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # 9 rooms in a 3x3 grid
        # Top row
        rooms.append(ProceduralArena.Room.new(cx - 400.0, cy - 400.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx - 100.0, cy - 400.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx + 200.0, cy - 400.0, 200.0, 200.0))
        # Middle row
        rooms.append(ProceduralArena.Room.new(cx - 400.0, cy - 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx - 100.0, cy - 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx + 200.0, cy - 100.0, 200.0, 200.0))
        # Bottom row
        rooms.append(ProceduralArena.Room.new(cx - 400.0, cy + 200.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx - 100.0, cy + 200.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(cx + 200.0, cy + 200.0, 200.0, 200.0))

        # 12 corridors connecting them
        # Horizontal corridors
        corridors.append(ProceduralArena.Corridor.new(cx - 200.0, cy - 350.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 100.0, cy - 350.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx - 200.0, cy - 50.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 100.0, cy - 50.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx - 200.0, cy + 250.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 100.0, cy + 250.0, 100.0, 100.0))

        # Vertical corridors
        corridors.append(ProceduralArena.Corridor.new(cx - 350.0, cy - 200.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx - 50.0, cy - 200.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 250.0, cy - 200.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx - 350.0, cy + 100.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx - 50.0, cy + 100.0, 100.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 250.0, cy + 100.0, 100.0, 100.0))

        # Central hazard
        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 40.0, "lava", 25.0))


class AvoidTrapArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        rooms.append(ProceduralArena.Room.new(100.0, 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(600.0, 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(350.0, 400.0, 200.0, 200.0))
        corridors.append(ProceduralArena.Corridor.new(300.0, 150.0, 300.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(150.0, 300.0, 100.0, 200.0))
        corridors.append(ProceduralArena.Corridor.new(150.0, 450.0, 200.0, 100.0))
        hazards.append(ProceduralArena.Hazard.new(0, 400.0, 200.0, 30.0, "spikes", 20.0))
        hazards.append(ProceduralArena.Hazard.new(1, 450.0, 200.0, 30.0, "lava", 50.0))
        hazards.append(ProceduralArena.Hazard.new(2, 500.0, 200.0, 30.0, "spikes", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, 200.0, 400.0, 30.0, "lava", 50.0))
        hazards.append(ProceduralArena.Hazard.new(4, 450.0, 500.0, 40.0, "lava", 50.0))

class Finals1v1Arena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))
        rooms.append(ProceduralArena.Room.new(100.0, cy - 100.0, 200.0, 200.0))
        rooms.append(ProceduralArena.Room.new(w - 300.0, cy - 100.0, 200.0, 200.0))

        corridors.append(ProceduralArena.Corridor.new(250.0, cy - 50.0, 500.0, 100.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 250.0, cy - 50.0, 500.0, 100.0))

        hazards.append(ProceduralArena.Hazard.new(0, cx - 200.0, cy - 200.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(1, cx + 200.0, cy - 200.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(2, cx - 200.0, cy + 200.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, cx + 200.0, cy + 200.0, 30.0, "lava", 20.0))

class RepositionArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # Central room
        rooms.append(ProceduralArena.Room.new(cx - 200.0, cy - 200.0, 400.0, 400.0))
        # Top room
        rooms.append(ProceduralArena.Room.new(cx - 100.0, 100.0, 200.0, 200.0))
        # Bottom room
        rooms.append(ProceduralArena.Room.new(cx - 100.0, h - 300.0, 200.0, 200.0))
        # Left room
        rooms.append(ProceduralArena.Room.new(100.0, cy - 100.0, 200.0, 200.0))
        # Right room
        rooms.append(ProceduralArena.Room.new(w - 300.0, cy - 100.0, 200.0, 200.0))

        # Top corridor
        corridors.append(ProceduralArena.Corridor.new(cx - 50.0, 300.0, 100.0, cy - 200.0 - 300.0))
        # Bottom corridor
        corridors.append(ProceduralArena.Corridor.new(cx - 50.0, cy + 200.0, 100.0, h - 300.0 - (cy + 200.0)))
        # Left corridor
        corridors.append(ProceduralArena.Corridor.new(300.0, cy - 50.0, cx - 200.0 - 300.0, 100.0))
        # Right corridor
        corridors.append(ProceduralArena.Corridor.new(cx + 200.0, cy - 50.0, w - 300.0 - (cx + 200.0), 100.0))

        # Central hazard
        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 100.0, "lava", 15.0))

class AICommentaryArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = width
		var h = height
		var cx = w / 2.0
		var cy = h / 2.0

		# Central battle room for commentary
		rooms.append(ProceduralArena.Room.new(cx - 400.0, cy - 400.0, 800.0, 800.0))

		# 4 Viewing/Spawn rooms
		rooms.append(ProceduralArena.Room.new(100.0, 100.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(w - 300.0, 100.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(100.0, h - 300.0, 200.0, 200.0))
		rooms.append(ProceduralArena.Room.new(w - 300.0, h - 300.0, 200.0, 200.0))

		# Connecting corridors
		corridors.append(ProceduralArena.Corridor.new(200.0, 200.0, cx - 600.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(cx - 450.0, 200.0, 100.0, cy - 600.0))

		corridors.append(ProceduralArena.Corridor.new(cx + 400.0, 200.0, cx - 600.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 350.0, 200.0, 100.0, cy - 600.0))

		corridors.append(ProceduralArena.Corridor.new(200.0, cy + 350.0, cx - 600.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(cx - 450.0, cy + 350.0, 100.0, cy - 600.0))

		corridors.append(ProceduralArena.Corridor.new(cx + 400.0, cy + 350.0, cx - 600.0, 100.0))
		corridors.append(ProceduralArena.Corridor.new(cx + 350.0, cy + 350.0, 100.0, cy - 600.0))

		# Central hazards for exciting moments
		var h1 = ProceduralArena.Hazard.new(0, cx - 150.0, cy - 150.0, 50.0, "lava", 20.0)
		hazards.append(h1)

		var h2 = ProceduralArena.Hazard.new(1, cx + 150.0, cy + 150.0, 50.0, "lava", 20.0)
		hazards.append(h2)

class BallRelationshipsArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # Central meeting room
        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))

        # 4 Spawn rooms
        rooms.append(ProceduralArena.Room.new(50.0, 50.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(w - 350.0, 50.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(50.0, h - 350.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(w - 350.0, h - 350.0, 300.0, 300.0))

        # Connecting corridors
        # Top-Left to Center
        corridors.append(ProceduralArena.Corridor.new(150.0, 350.0, 100.0, cy - 650.0))
        corridors.append(ProceduralArena.Corridor.new(150.0, cy - 300.0, cx - 450.0, 100.0))
        # Top-Right to Center
        corridors.append(ProceduralArena.Corridor.new(w - 250.0, 350.0, 100.0, cy - 650.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, cy - 300.0, w - cx - 550.0, 100.0))
        # Bottom-Left to Center
        corridors.append(ProceduralArena.Corridor.new(150.0, cy + 200.0, 100.0, h - cy - 550.0))
        corridors.append(ProceduralArena.Corridor.new(150.0, cy + 200.0, cx - 450.0, 100.0))
        # Bottom-Right to Center
        corridors.append(ProceduralArena.Corridor.new(w - 250.0, cy + 200.0, 100.0, h - cy - 550.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, cy + 200.0, w - cx - 550.0, 100.0))

        # 4 central hazards
        hazards.append(ProceduralArena.Hazard.new(0, cx - 150.0, cy - 150.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(1, cx + 150.0, cy - 150.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(2, cx - 150.0, cy + 150.0, 30.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, cx + 150.0, cy + 150.0, 30.0, "lava", 20.0))


class ClutchPlaysArena:
    extends ProceduralArena

    func _init(size: float = 2000.0, seed_val = null):
        super(size, 5, seed_val)

    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()

        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # Central room
        rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))

        # Safe zones
        rooms.append(ProceduralArena.Room.new(50, 50, 200, 200))
        rooms.append(ProceduralArena.Room.new(w - 250, 50, 200, 200))
        rooms.append(ProceduralArena.Room.new(50, h - 250, 200, 200))
        rooms.append(ProceduralArena.Room.new(w - 250, h - 250, 200, 200))

        # Corridors
        corridors.append(ProceduralArena.Corridor.new(100, 200, 100, cy - 400))
        corridors.append(ProceduralArena.Corridor.new(100, cy - 300, cx - 300, 100))

        corridors.append(ProceduralArena.Corridor.new(w - 200, 200, 100, cy - 400))
        corridors.append(ProceduralArena.Corridor.new(cx + 200, cy - 300, w - cx - 300, 100))

        corridors.append(ProceduralArena.Corridor.new(100, cy + 200, 100, h - cy - 400))
        corridors.append(ProceduralArena.Corridor.new(100, cy + 200, cx - 300, 100))

        corridors.append(ProceduralArena.Corridor.new(w - 200, cy + 200, 100, h - cy - 400))
        corridors.append(ProceduralArena.Corridor.new(cx + 200, cy + 200, w - cx - 300, 100))

        # Hazards
        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 100.0, "lava", 30.0))
        hazards.append(ProceduralArena.Hazard.new(1, cx - 150, cy - 150, 50.0, "spikes", 20.0))
        hazards.append(ProceduralArena.Hazard.new(2, cx + 150, cy - 150, 50.0, "spikes", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, cx - 150, cy + 150, 50.0, "spikes", 20.0))
        hazards.append(ProceduralArena.Hazard.new(4, cx + 150, cy + 150, 50.0, "spikes", 20.0))


class TeamWipesArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(100.0, cy - 300.0, 400.0, 600.0))
        rooms.append(ProceduralArena.Room.new(w - 500.0, cy - 300.0, 400.0, 600.0))
        rooms.append(ProceduralArena.Room.new(cx - 400.0, cy - 400.0, 800.0, 800.0))

        corridors.append(ProceduralArena.Corridor.new(450.0, cy - 200.0, 200.0, 400.0))
        corridors.append(ProceduralArena.Corridor.new(w - 650.0, cy - 200.0, 200.0, 400.0))

        hazards.append(ProceduralArena.Hazard.new(0, cx - 200.0, cy - 200.0, 40.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(1, cx + 200.0, cy - 200.0, 40.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(2, cx - 200.0, cy + 200.0, 40.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, cx + 200.0, cy + 200.0, 40.0, "lava", 20.0))


class SwarmIntelligenceArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # 3x3 grid of 9 rooms, 400x400 each
        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 700, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy - 700, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx + 300, cy - 700, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 200, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy - 200, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx + 300, cy - 200, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx - 700, cy + 300, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy + 300, 400, 400))
        rooms.append(ProceduralArena.Room.new(cx + 300, cy + 300, 400, 400))

        # 12 connecting corridors, 300x300 to overlap 50px
        # Horizontal
        corridors.append(ProceduralArena.Corridor.new(cx - 350, cy - 650, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx + 150, cy - 650, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx - 350, cy - 150, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx + 150, cy - 150, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx - 350, cy + 350, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx + 150, cy + 350, 200, 300))

        # Vertical
        corridors.append(ProceduralArena.Corridor.new(cx - 650, cy - 350, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx - 150, cy - 350, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx + 350, cy - 350, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx - 650, cy + 150, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx - 150, cy + 150, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx + 350, cy + 150, 300, 200))

        # 4 central hazards
        hazards.append(ProceduralArena.Hazard.new(0, cx - 100, cy - 100, 40.0, "spikes", 25.0))
        hazards.append(ProceduralArena.Hazard.new(1, cx + 100, cy - 100, 40.0, "spikes", 25.0))
        hazards.append(ProceduralArena.Hazard.new(2, cx - 100, cy + 100, 40.0, "spikes", 25.0))
        hazards.append(ProceduralArena.Hazard.new(3, cx + 100, cy + 100, 40.0, "spikes", 25.0))

class EmotionalContagionArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))
        rooms.append(ProceduralArena.Room.new(100.0, 100.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(w - 400.0, 100.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(100.0, h - 400.0, 300.0, 300.0))
        rooms.append(ProceduralArena.Room.new(w - 400.0, h - 400.0, 300.0, 300.0))

        corridors.append(ProceduralArena.Corridor.new(200.0, 350.0, 100.0, cy - 600.0))
        corridors.append(ProceduralArena.Corridor.new(w - 300.0, 350.0, 100.0, cy - 600.0))
        corridors.append(ProceduralArena.Corridor.new(200.0, cy + 250.0, 100.0, h - cy - 600.0))
        corridors.append(ProceduralArena.Corridor.new(w - 300.0, cy + 250.0, 100.0, h - cy - 600.0))

        hazards.append(ProceduralArena.Hazard.new(0, 250.0, 250.0, 50.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(1, w - 250.0, 250.0, 50.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(2, 250.0, h - 250.0, 50.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(3, w - 250.0, h - 250.0, 50.0, "lava", 20.0))
        hazards.append(ProceduralArena.Hazard.new(4, cx - 150.0, cy - 150.0, 40.0, "spikes", 30.0))
        hazards.append(ProceduralArena.Hazard.new(5, cx + 150.0, cy - 150.0, 40.0, "spikes", 30.0))
        hazards.append(ProceduralArena.Hazard.new(6, cx - 150.0, cy + 150.0, 40.0, "spikes", 30.0))
        hazards.append(ProceduralArena.Hazard.new(7, cx + 150.0, cy + 150.0, 40.0, "spikes", 30.0))

class AmbushArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        # 1 central combat zone
        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))

        # 4 hiding spots (alcoves) in the corners
        rooms.append(ProceduralArena.Room.new(50.0, 50.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(w - 200.0, 50.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(50.0, h - 200.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(w - 200.0, h - 200.0, 150.0, 150.0))

        # Narrow corridors connecting hiding spots to the center
        corridors.append(ProceduralArena.Corridor.new(100.0, 200.0, 50.0, cy - 400.0))
        corridors.append(ProceduralArena.Corridor.new(100.0, cy - 300.0, cx - 300.0, 50.0))

        corridors.append(ProceduralArena.Corridor.new(w - 150.0, 200.0, 50.0, cy - 400.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, cy - 300.0, w - cx - 300.0, 50.0))

        corridors.append(ProceduralArena.Corridor.new(100.0, cy + 250.0, 50.0, h - cy - 400.0))
        corridors.append(ProceduralArena.Corridor.new(100.0, cy + 250.0, cx - 300.0, 50.0))

        corridors.append(ProceduralArena.Corridor.new(w - 150.0, cy + 250.0, 50.0, h - cy - 400.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, cy + 250.0, w - cx - 300.0, 50.0))

        # 1 central hazard to discourage staying in the open
        hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 80.0, "lava", 20.0))


func _trigger_event(event_type: String, current_tick: int) -> void:
    if event_type == "orbital_strike":
        var h_id = 5000 + hazards.size()
        var strike = ProceduralArena.Hazard.new(h_id, width/2, height/2, 400.0, "orbital_strike", 0.0)
        strike.target_radius = 400.0
        strike.set_meta("duration", 3.0)
        hazards.append(strike)
    elif event_type == "meteor_shower":
        var num_meteors = (randi() % 11) + 5
        for i in range(num_meteors):
            var x = randf_range(50, width - 50)
            var y = randf_range(50, height - 50)
            var h_id = 2000 + hazards.size() + (randi() % 1000)
            var meteor = ProceduralArena.Hazard.new(h_id, x, y, 30.0, "meteor", 200.0)
            meteor.target_radius = 30.0
            meteor.set_meta("duration", 5.0)
            hazards.append(meteor)
    elif event_type == "anomaly_zone":
        var h_id = 6000 + hazards.size()
        var zone = ProceduralArena.Hazard.new(h_id, width/2, height/2, 400.0, "anomaly_zone", 0.0)
        zone.target_radius = 400.0
        zone.set_meta("duration", 10.0)
        hazards.append(zone)
    elif event_type == "massive_black_hole_event":
        var h_id = 9000 + hazards.size()
        var mbh = ProceduralArena.Hazard.new(h_id, width/2, height/2, 100.0, "massive_black_hole", 10.0)
        mbh.target_radius = 500.0
        mbh.set_meta("duration", 20.0)
        mbh.set_meta("pull_strength", 100.0)
        hazards.append(mbh)
    elif event_type == "gravity_shift":
        var h_id = 3000 + hazards.size()
        var gw = ProceduralArena.Hazard.new(h_id, width/2, height/2, width/2, "gravity_well", 0.0)
        gw.target_radius = width/2
        gw.set_meta("duration", 10.0)
        hazards.append(gw)
    elif event_type == "moving_walls":
        var h_id = 4000 + hazards.size()
        var wall = ProceduralArena.Hazard.new(h_id, width/2, height/2, 100.0, "laser_wall", 50.0)
        wall.target_radius = width
        wall.set_meta("duration", 8.0)
        hazards.append(wall)
    elif event_type == "fire_ring":
        var h_id = 4500 + hazards.size()
        var ring = ProceduralArena.Hazard.new(h_id, width/2, height/2, 500.0, "fire_ring", 40.0)
        ring.target_radius = 0.0
        ring.set_meta("duration", 10.0)
        ring.set_meta("shrink_rate", 500.0 / 10.0)
        hazards.append(ring)

func _update_danger_grid() -> void:
    danger_grid.clear()

    for h in hazards:
        var grid_x = int(h.x / 100)
        var grid_y = int(h.y / 100)
        var r_cells = int(h.radius / 100) + 1
        for i in range(grid_x - r_cells, grid_x + r_cells + 1):
            for j in range(grid_y - r_cells, grid_y + r_cells + 1):
                var cx = i * 100 + 50
                var cy = j * 100 + 50
                var dist = sqrt((cx - h.x)*(cx - h.x) + (cy - h.y)*(cy - h.y))
                if dist <= h.radius + 50:
                    var key = str(i) + "," + str(j)
                    var current = 0.0
                    if danger_grid.has(key):
                        current = danger_grid[key]
                    danger_grid[key] = current + (h.damage / 10.0)

    var grid_w = int(width / 100) + 1
    var grid_h = int(height / 100) + 1
    for i in range(grid_w):
        for j in range(grid_h):
            var cx = i * 100 + 50
            var cy = j * 100 + 50
            var dist_to_center = sqrt((cx - safe_zone_center[0])*(cx - safe_zone_center[0]) + (cy - safe_zone_center[1])*(cy - safe_zone_center[1]))
            if dist_to_center > safe_zone_radius:
                var key = str(i) + "," + str(j)
                var current = 0.0
                if danger_grid.has(key):
                    current = danger_grid[key]
                danger_grid[key] = current + 5.0
