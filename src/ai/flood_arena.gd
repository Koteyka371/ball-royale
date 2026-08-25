extends "res://src/ai/game_modes.gd".GameMode

class_name FloodArenaMode

var whirlpool_timer = 0.0
var whirlpool_spawn_interval = 20.0
var debris_timer = 0.0
var debris_spawn_interval = 15.0
var water_slow_factor = 0.4
var water_perception_factor = 0.5
var rng = RandomNumberGenerator.new()

func _init():
    super._init()
    name = "Flood Arena"
    description = "The arena is submerged in deep water, reducing movement speed and perception for non-aquatic balls. Periodically, giant whirlpools spawn, dragging players into the center. Find buoyant floating debris to regain normal speed and stamina."
    rng.randomize()

func tick(world, balls, delta: float) -> void:
    super.tick(world, balls, delta)

    for b in balls:
        if typeof(b) == TYPE_DICTIONARY:
            if not b.get("alive", true):
                continue

            var has_debris = b.get("has_floating_debris", false)
            var debris_timer = b.get("floating_debris_timer", 0.0)

            if has_debris and debris_timer > 0:
                b["floating_debris_timer"] = debris_timer - delta
                if b["floating_debris_timer"] <= 0:
                    b["has_floating_debris"] = false
                    has_debris = false

            var is_aquatic = b.get("type", "") == "aquatic"

            if not is_aquatic and not has_debris:
                if not b.has("base_speed"):
                    b["base_speed"] = b.get("speed", 10.0)
                if not b.has("base_perception_radius"):
                    b["base_perception_radius"] = b.get("perception_radius", 100.0)

                b["speed"] = b["base_speed"] * water_slow_factor
                b["perception_radius"] = b["base_perception_radius"] * water_perception_factor
            else:
                if b.has("base_speed"):
                    b["speed"] = b["base_speed"]
                if b.has("base_perception_radius"):
                    b["perception_radius"] = b["base_perception_radius"]
        else:
            if not b.get("alive", true):
                continue

            var has_debris = b.get("has_floating_debris") if b.has_method("get") else (b.has_floating_debris if "has_floating_debris" in b else false)
            var debris_timer = b.get("floating_debris_timer") if b.has_method("get") else (b.floating_debris_timer if "floating_debris_timer" in b else 0.0)

            if has_debris and debris_timer > 0:
                b.floating_debris_timer = debris_timer - delta
                if b.floating_debris_timer <= 0:
                    b.has_floating_debris = false
                    has_debris = false

            var is_aquatic = b.get("type") == "aquatic" if b.has_method("get") else (b.type == "aquatic" if "type" in b else false)

            if not is_aquatic and not has_debris:
                if not ("base_speed" in b):
                    b.base_speed = b.get("speed") if b.has_method("get") else (b.speed if "speed" in b else 10.0)
                if not ("base_perception_radius" in b):
                    b.base_perception_radius = b.get("perception_radius") if b.has_method("get") else (b.perception_radius if "perception_radius" in b else 100.0)

                b.speed = b.base_speed * water_slow_factor
                b.perception_radius = b.base_perception_radius * water_perception_factor
            else:
                if "base_speed" in b:
                    b.speed = b.base_speed
                if "base_perception_radius" in b:
                    b.perception_radius = b.base_perception_radius

    debris_timer += delta
    if debris_timer >= debris_spawn_interval:
        debris_timer = 0.0
        _spawn_debris(world)

    whirlpool_timer += delta
    if whirlpool_timer >= whirlpool_spawn_interval:
        whirlpool_timer = 0.0
        _spawn_whirlpool(world)

    if typeof(world) == TYPE_DICTIONARY:
        if world.has("hazards"):
            var to_remove = []
            for h in world["hazards"]:
                var kind = h.get("kind", "") if typeof(h) == TYPE_DICTIONARY else (h.kind if "kind" in h else "")
                if kind == "whirlpool":
                    var life = h.get("life", 0) if typeof(h) == TYPE_DICTIONARY else (h.life if "life" in h else 0)
                    life -= delta
                    if life <= 0:
                        to_remove.append(h)
                    else:
                        if typeof(h) == TYPE_DICTIONARY:
                            h["life"] = life
                        else:
                            h.life = life
                        for b in balls:
                            if typeof(b) == TYPE_DICTIONARY:
                                if not b.get("alive", true): continue
                                var hx = h.get("x", 0) if typeof(h) == TYPE_DICTIONARY else h.x
                                var hy = h.get("y", 0) if typeof(h) == TYPE_DICTIONARY else h.y
                                var dx = hx - b.get("x", 0)
                                var dy = hy - b.get("y", 0)
                                var dist = sqrt(dx*dx + dy*dy)
                                var radius = h.get("radius", 150) if typeof(h) == TYPE_DICTIONARY else h.radius
                                if dist > 0 and dist < radius:
                                    var pull = h.get("pull_strength", 150) if typeof(h) == TYPE_DICTIONARY else h.pull_strength
                                    var force = pull * (1.0 - dist / radius)
                                    b["x"] += (dx / dist) * force * delta
                                    b["y"] += (dy / dist) * force * delta
                            else:
                                if not b.get("alive") if b.has_method("get") else (b.alive if "alive" in b else true): continue
                                var hx = h.get("x", 0) if typeof(h) == TYPE_DICTIONARY else h.x
                                var hy = h.get("y", 0) if typeof(h) == TYPE_DICTIONARY else h.y
                                var bx = b.get("x") if b.has_method("get") else (b.x if "x" in b else 0)
                                var by = b.get("y") if b.has_method("get") else (b.y if "y" in b else 0)
                                var dx = hx - bx
                                var dy = hy - by
                                var dist = sqrt(dx*dx + dy*dy)
                                var radius = h.get("radius", 150) if typeof(h) == TYPE_DICTIONARY else h.radius
                                if dist > 0 and dist < radius:
                                    var pull = h.get("pull_strength", 150) if typeof(h) == TYPE_DICTIONARY else h.pull_strength
                                    var force = pull * (1.0 - dist / radius)
                                    if "x" in b: b.x += (dx / dist) * force * delta
                                    if "y" in b: b.y += (dy / dist) * force * delta
            for h in to_remove:
                world["hazards"].erase(h)
    else:
        if "hazards" in world:
            var to_remove = []
            for h in world.hazards:
                var kind = h.get("kind", "") if typeof(h) == TYPE_DICTIONARY else (h.kind if "kind" in h else "")
                if kind == "whirlpool":
                    var life = h.get("life", 0) if typeof(h) == TYPE_DICTIONARY else (h.life if "life" in h else 0)
                    life -= delta
                    if life <= 0:
                        to_remove.append(h)
                    else:
                        if typeof(h) == TYPE_DICTIONARY:
                            h["life"] = life
                        else:
                            h.life = life
                        for b in balls:
                            if typeof(b) == TYPE_DICTIONARY:
                                if not b.get("alive", true): continue
                                var hx = h.get("x", 0) if typeof(h) == TYPE_DICTIONARY else h.x
                                var hy = h.get("y", 0) if typeof(h) == TYPE_DICTIONARY else h.y
                                var dx = hx - b.get("x", 0)
                                var dy = hy - b.get("y", 0)
                                var dist = sqrt(dx*dx + dy*dy)
                                var radius = h.get("radius", 150) if typeof(h) == TYPE_DICTIONARY else h.radius
                                if dist > 0 and dist < radius:
                                    var pull = h.get("pull_strength", 150) if typeof(h) == TYPE_DICTIONARY else h.pull_strength
                                    var force = pull * (1.0 - dist / radius)
                                    b["x"] += (dx / dist) * force * delta
                                    b["y"] += (dy / dist) * force * delta
                            else:
                                if not (b.get("alive") if b.has_method("get") else (b.alive if "alive" in b else true)): continue
                                var hx = h.get("x", 0) if typeof(h) == TYPE_DICTIONARY else h.x
                                var hy = h.get("y", 0) if typeof(h) == TYPE_DICTIONARY else h.y
                                var bx = b.get("x") if b.has_method("get") else (b.x if "x" in b else 0)
                                var by = b.get("y") if b.has_method("get") else (b.y if "y" in b else 0)
                                var dx = hx - bx
                                var dy = hy - by
                                var dist = sqrt(dx*dx + dy*dy)
                                var radius = h.get("radius", 150) if typeof(h) == TYPE_DICTIONARY else h.radius
                                if dist > 0 and dist < radius:
                                    var pull = h.get("pull_strength", 150) if typeof(h) == TYPE_DICTIONARY else h.pull_strength
                                    var force = pull * (1.0 - dist / radius)
                                    if "x" in b: b.x += (dx / dist) * force * delta
                                    if "y" in b: b.y += (dy / dist) * force * delta
            for h in to_remove:
                world.hazards.erase(h)

func _spawn_debris(world) -> void:
    if typeof(world) == TYPE_DICTIONARY:
        if not world.has("boosters"):
            return

        var arena = world.get("arena", {})
        var max_x = arena.get("width", 800.0)
        var max_y = arena.get("height", 600.0)

        var x = rng.randf_range(50, max_x - 50)
        var y = rng.randf_range(50, max_y - 50)

        var debris = {
            "x": x,
            "y": y,
            "type": "floating_debris",
            "radius": 15.0,
            "active": true
        }
        world["boosters"].append(debris)
    else:
        if not ("boosters" in world):
            return

        var arena = world.get("arena") if world.has_method("get") else (world.arena if "arena" in world else null)
        var max_x = arena.get("width") if arena and arena.has_method("get") else (arena.width if arena and "width" in arena else 800.0)
        var max_y = arena.get("height") if arena and arena.has_method("get") else (arena.height if arena and "height" in arena else 600.0)

        var x = rng.randf_range(50, max_x - 50)
        var y = rng.randf_range(50, max_y - 50)

        var debris = {
            "x": x,
            "y": y,
            "type": "floating_debris",
            "radius": 15.0,
            "active": true
        }
        world.boosters.append(debris)

func _spawn_whirlpool(world) -> void:
    if typeof(world) == TYPE_DICTIONARY:
        if not world.has("hazards"):
            return

        var arena = world.get("arena", {})
        var max_x = arena.get("width", 800.0)
        var max_y = arena.get("height", 600.0)

        var x = rng.randf_range(150, max_x - 150)
        var y = rng.randf_range(150, max_y - 150)

        var whirlpool = {
            "x": x,
            "y": y,
            "kind": "whirlpool",
            "radius": 150.0,
            "pull_strength": 150.0,
            "active": true,
            "life": 10.0
        }
        world["hazards"].append(whirlpool)
    else:
        if not ("hazards" in world):
            return

        var arena = world.get("arena") if world.has_method("get") else (world.arena if "arena" in world else null)
        var max_x = arena.get("width") if arena and arena.has_method("get") else (arena.width if arena and "width" in arena else 800.0)
        var max_y = arena.get("height") if arena and arena.has_method("get") else (arena.height if arena and "height" in arena else 600.0)

        var x = rng.randf_range(150, max_x - 150)
        var y = rng.randf_range(150, max_y - 150)

        var whirlpool = {
            "x": x,
            "y": y,
            "kind": "whirlpool",
            "radius": 150.0,
            "pull_strength": 150.0,
            "active": true,
            "life": 10.0
        }
        world.hazards.append(whirlpool)
