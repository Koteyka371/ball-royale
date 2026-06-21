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

class Hazard:
    var id: int
    var x: float
    var y: float
    var radius: float
    var kind: String
    var damage: float

    func _init(_id: int, _x: float, _y: float, _radius: float, _kind: String, _damage: float):
        id = _id
        x = _x
        y = _y
        radius = _radius
        kind = _kind
        damage = _damage

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
        var kind = "spikes"
        if rng.randf() > 0.5:
            kind = "lava"

        var radius = 0.0
        var damage = 0.0
        if kind == "spikes":
            radius = rng.randf_range(15.0, 30.0)
            damage = 20.0
        else:
            radius = rng.randf_range(30.0, 60.0)
            damage = 50.0

        var spawn_pt = get_random_spawn_point(radius)
        hazards.append(ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage))

func get_random_spawn_point(radius: float) -> Array:
    if rooms.size() == 0:
        return [rng.randf_range(radius, width - radius), rng.randf_range(radius, height - radius)]
    var room = rooms[rng.randi_range(0, rooms.size() - 1)]
    return [rng.randf_range(room.x + radius, room.x + room.width - radius),
            rng.randf_range(room.y + radius, room.y + room.height - radius)]

func is_point_inside(x: float, y: float, radius: float) -> bool:
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

    return [nearest_x, nearest_y, true]


func update_zone(current_tick: int, delta: float) -> void:
    if current_tick != last_tick:
        last_tick = current_tick
        safe_zone_radius -= 10.0 * delta
        if safe_zone_radius < 50.0:
            safe_zone_radius = 50.0

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


class TargetWeakArena extends ProceduralArena:
    func generate():
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w = width
        var h = height
        var cx = w / 2.0
        var cy = h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300.0, cy - 300.0, 600.0, 600.0))

        rooms.append(ProceduralArena.Room.new(50.0, 50.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(w - 200.0, 50.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(50.0, h - 200.0, 150.0, 150.0))
        rooms.append(ProceduralArena.Room.new(w - 200.0, h - 200.0, 150.0, 150.0))

        corridors.append(ProceduralArena.Corridor.new(200.0, 100.0, cx - 300.0 - 200.0, 50.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, 100.0, w - 200.0 - (cx + 300.0), 50.0))
        corridors.append(ProceduralArena.Corridor.new(200.0, h - 150.0, cx - 300.0 - 200.0, 50.0))
        corridors.append(ProceduralArena.Corridor.new(cx + 300.0, h - 150.0, w - 200.0 - (cx + 300.0), 50.0))
