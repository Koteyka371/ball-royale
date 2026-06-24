class_name BasicArena
extends RefCounted

var width: float
var height: float
var rng: RandomNumberGenerator

var safe_zone_radius: float
var safe_zone_center: Array
var last_tick: int = -1
var danger_grid: Dictionary = {}

func _init(_arena_size: float = 2000.0, _seed = null):
    width = _arena_size
    height = _arena_size
    rng = RandomNumberGenerator.new()
    if _seed != null:
        rng.seed = _seed
    else:
        rng.randomize()

    safe_zone_radius = width * 0.7
    safe_zone_center = [width / 2.0, height / 2.0]
    last_tick = -1

func get_random_spawn_point(radius: float) -> Array:
    return [rng.randf_range(radius, width - radius), rng.randf_range(radius, height - radius)]

func is_point_inside(x: float, y: float, radius: float) -> bool:
    return radius <= x and x <= width - radius and radius <= y and y <= height - radius

func clamp_position(x: float, y: float, radius: float) -> Array:
    var bounced = false
    var new_x = x
    var new_y = y

    if x < radius:
        new_x = radius
        bounced = true
    elif x > width - radius:
        new_x = width - radius
        bounced = true

    if y < radius:
        new_y = radius
        bounced = true
    elif y > height - radius:
        new_y = height - radius
        bounced = true

    return [new_x, new_y, bounced]

func update_zone(current_tick: int, delta: float) -> void:
    if current_tick != last_tick:
        last_tick = current_tick
        safe_zone_radius -= 10.0 * delta
        if safe_zone_radius < 50.0:
            safe_zone_radius = 50.0
