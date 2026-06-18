class_name ProceduralArena
extends RefCounted

var width: float
var height: float
var num_rooms: int
var rooms: Array = []
var corridors: Array = []
var rng: RandomNumberGenerator

var safe_zone_radius: float
var safe_zone_center: Array
var last_tick: int = -1

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
            rooms.append(Room.new(rx, ry, rw, rh))

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
            corridors.append(Corridor.new(min(c1x, c2x) - 25.0, c1y - 25.0, abs(c2x - c1x) + 50.0, 50.0))
            corridors.append(Corridor.new(c2x - 25.0, min(c1y, c2y) - 25.0, 50.0, abs(c2y - c1y) + 50.0))
        else:
            corridors.append(Corridor.new(c1x - 25.0, min(c1y, c2y) - 25.0, 50.0, abs(c2y - c1y) + 50.0))
            corridors.append(Corridor.new(min(c1x, c2x) - 25.0, c2y - 25.0, abs(c2x - c1x) + 50.0, 50.0))

        connected.append(r2)
        unconnected.remove_at(best_idx)

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
