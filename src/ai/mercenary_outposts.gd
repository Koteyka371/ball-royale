extends "res://src/ai/game_modes.gd"

var outposts = []
var mercenary_id_counter = 5000

func _init():
    name = "Mercenary Outposts"
    description = "Players can capture mercenary outposts across the map. Once fully captured, friendly AI balls spawn periodically and help defend the capturing player."

func setup(world, balls):
    super.setup(world, balls)

    var arena_w = 1000
    if world.has("arena") and typeof(world.arena) != TYPE_DICTIONARY and "width" in world.arena:
        arena_w = world.arena.width
    elif typeof(world) == TYPE_DICTIONARY and world.has("arena_width"):
        arena_w = world.arena_width

    var arena_h = 1000
    if world.has("arena") and typeof(world.arena) != TYPE_DICTIONARY and "height" in world.arena:
        arena_h = world.arena.height
    elif typeof(world) == TYPE_DICTIONARY and world.has("arena_height"):
        arena_h = world.arena_height

    outposts = [
        {"id": 1000, "x": arena_w * 0.2, "y": arena_h * 0.2, "radius": 100.0, "owner": null, "capture_progress": 0.0, "spawn_timer": 0.0},
        {"id": 1001, "x": arena_w * 0.8, "y": arena_h * 0.8, "radius": 100.0, "owner": null, "capture_progress": 0.0, "spawn_timer": 0.0},
        {"id": 1002, "x": arena_w * 0.2, "y": arena_h * 0.8, "radius": 100.0, "owner": null, "capture_progress": 0.0, "spawn_timer": 0.0},
        {"id": 1003, "x": arena_w * 0.8, "y": arena_h * 0.2, "radius": 100.0, "owner": null, "capture_progress": 0.0, "spawn_timer": 0.0}
    ]

func apply_dynamic_traits(world, balls, delta):
    for outpost in outposts:
        var occupying_teams = []

        for b in balls:
            if typeof(b) == TYPE_DICTIONARY:
                if not b.get("alive", false) or b.get("ball_type", "") == "spectator":
                    continue
                if b.get("is_mercenary", false):
                    continue

                var dx = b.get("x", 0.0) - outpost.x
                var dy = b.get("y", 0.0) - outpost.y
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= outpost.radius:
                    var t = b.get("team", null)
                    if t != null and not occupying_teams.has(t):
                        occupying_teams.append(t)
            else:
                if not b.get("alive") or b.get("ball_type") == "spectator":
                    continue
                if b.has_method("get") and b.get("is_mercenary"):
                    continue
                elif "is_mercenary" in b and b.is_mercenary:
                    continue

                var dx = b.x - outpost.x
                var dy = b.y - outpost.y
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= outpost.radius:
                    var t = b.team
                    if t != null and not occupying_teams.has(t):
                        occupying_teams.append(t)

        if occupying_teams.size() == 1:
            var team = occupying_teams[0]
            if outpost.owner == team:
                outpost.capture_progress = 100.0
            elif outpost.owner == null:
                outpost.capture_progress += 20.0 * delta
                if outpost.capture_progress >= 100.0:
                    outpost.owner = team
                    outpost.capture_progress = 100.0
                    if world.has_method("add_event"):
                        world.add_event("outpost_captured", {"team": team, "outpost": outpost})
            else:
                outpost.capture_progress -= 20.0 * delta
                if outpost.capture_progress <= 0.0:
                    outpost.owner = null
                    outpost.capture_progress = 0.0
                    if world.has_method("add_event"):
                        world.add_event("outpost_neutralized", {"outpost": outpost})
        elif occupying_teams.size() == 0:
            if outpost.owner == null:
                outpost.capture_progress = max(0.0, outpost.capture_progress - 5.0 * delta)
            else:
                outpost.capture_progress = min(100.0, outpost.capture_progress + 5.0 * delta)

        if outpost.owner != null and outpost.capture_progress >= 100.0:
            outpost.spawn_timer += delta
            if outpost.spawn_timer >= 10.0:
                outpost.spawn_timer = 0.0
                spawn_mercenary(world, balls, outpost)

func spawn_mercenary(world, balls, outpost):
    var merc = {
        "id": mercenary_id_counter,
        "x": outpost.x,
        "y": outpost.y,
        "vx": 0.0,
        "vy": 0.0,
        "radius": 20.0,
        "hp": 100.0,
        "max_hp": 100.0,
        "alive": true,
        "ball_type": "mercenary",
        "team": outpost.owner,
        "speed": 150.0,
        "base_speed": 150.0,
        "damage": 10.0,
        "base_damage": 10.0,
        "is_mercenary": true,
        "type": "mercenary",
        "speed_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "mass": 1.0
    }
    mercenary_id_counter += 1

    balls.append(merc)

    # Optional logic if world.entities exists but world.balls is what is passed
    if typeof(world) != TYPE_DICTIONARY:
        if "entities" in world:
            world.entities.append(merc)
        if "balls" in world and not world.balls.has(merc) and balls != world.balls:
            world.balls.append(merc)

    if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
        world.add_event("mercenary_spawned", {"team": outpost.owner, "x": outpost.x, "y": outpost.y})
