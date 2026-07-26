extends "res://src/ai/game_modes.gd".GameMode

class_name MirrorIllusionMode

var illusions = {}

func _init():
    super._init()
    name = "Mirror Illusion"
    description = "A game mode where every ball has a harmless mirror illusion on the opposite side of the arena that moves symmetrically, confusing opponents and absorbing single-target projectiles."
    illusions = {}

func setup(world, balls):
    super.setup(world, balls)
    illusions = {}

    if typeof(world) == TYPE_DICTIONARY:
        if not world.has("entities"):
            world["entities"] = []
    else:
        if not "entities" in world:
            world.entities = []

func tick(world, balls, delta = 0.016):
    super.tick(world, balls, delta)

    var arena_w = 1000.0
    var arena_h = 1000.0

    if world != null:
        if typeof(world) == TYPE_DICTIONARY and world.has("arena") and world["arena"] != null:
            var arena = world["arena"]
            if typeof(arena) == TYPE_DICTIONARY:
                arena_w = arena.get("width", 1000.0)
                arena_h = arena.get("height", 1000.0)
            else:
                if "width" in arena: arena_w = arena.width
                if "height" in arena: arena_h = arena.height
        elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
            var arena = world.arena
            if typeof(arena) == TYPE_DICTIONARY:
                arena_w = arena.get("width", 1000.0)
                arena_h = arena.get("height", 1000.0)
            else:
                if "width" in arena: arena_w = arena.width
                if "height" in arena: arena_h = arena.height

    var active_ball_ids = {}

    for b in balls:
        var b_id = null
        var b_type = null
        var is_alive = false
        var bx = arena_w / 2.0
        var by = arena_h / 2.0
        var bvx = 0.0
        var bvy = 0.0
        var br = 10.0
        var team = "unknown"
        var mass = 1.0

        if typeof(b) == TYPE_DICTIONARY:
            b_id = b.get("id", null)
            b_type = b.get("ball_type", null)
            is_alive = b.get("alive", false)
            bx = b.get("x", bx)
            by = b.get("y", by)
            bvx = b.get("vx", 0.0)
            bvy = b.get("vy", 0.0)
            br = b.get("radius", 10.0)
            team = b.get("team", b_type if b_type != null else "unknown")
            mass = b.get("mass", 1.0)
        else:
            if "id" in b: b_id = b.id
            if "ball_type" in b: b_type = b.ball_type
            if "alive" in b: is_alive = b.alive
            if "x" in b: bx = b.x
            if "y" in b: by = b.y
            if "vx" in b: bvx = b.vx
            if "vy" in b: bvy = b.vy
            if "radius" in b: br = b.radius

            if "team" in b:
                team = b.team
            elif b_type != null:
                team = b_type

            if "mass" in b: mass = b.mass

        if b_id == null or b_type == "spectator":
            continue

        if not is_alive:
            continue

        active_ball_ids[b_id] = true

        if not illusions.has(b_id):
            var illusion = {
                "id": "illusion_" + str(b_id),
                "is_illusion": true,
                "alive": true,
                "x": arena_w - bx,
                "y": arena_h - by,
                "vx": -bvx,
                "vy": -bvy,
                "radius": br,
                "team": team,
                "ball_type": "illusion",
                "hp": 1.0,
                "max_hp": 1.0,
                "speed_multiplier": 1.0,
                "damage_multiplier": 1.0,
                "speed": 0.0,
                "base_speed": 0.0,
                "mass": mass
            }
            illusions[b_id] = illusion

            if typeof(world) == TYPE_DICTIONARY:
                if world.has("entities"):
                    world["entities"].append(illusion)
                elif world.has("balls"):
                    world["balls"].append(illusion)
            else:
                if "entities" in world:
                    world.entities.append(illusion)
                elif "balls" in world:
                    world.balls.append(illusion)

        var illusion = illusions[b_id]
        illusion["x"] = arena_w - bx
        illusion["y"] = arena_h - by
        illusion["vx"] = -bvx
        illusion["vy"] = -bvy
        illusion["radius"] = br
        illusion["team"] = team
        illusion["alive"] = true

    var keys_to_remove = []
    for b_id in illusions.keys():
        if not active_ball_ids.has(b_id):
            keys_to_remove.append(b_id)

    for b_id in keys_to_remove:
        var illusion = illusions[b_id]
        illusion["alive"] = false

        if typeof(world) == TYPE_DICTIONARY:
            if world.has("entities") and world["entities"].has(illusion):
                world["entities"].erase(illusion)
            elif world.has("balls") and world["balls"].has(illusion):
                world["balls"].erase(illusion)
        else:
            if "entities" in world and world.entities.has(illusion):
                world.entities.erase(illusion)
            elif "balls" in world and world.balls.has(illusion):
                world.balls.erase(illusion)

        illusions.erase(b_id)

    var hazards = null
    if typeof(world) == TYPE_DICTIONARY and world.has("arena") and world["arena"] != null:
        var arena = world["arena"]
        if typeof(arena) == TYPE_DICTIONARY and arena.has("hazards"):
            hazards = arena["hazards"]
        elif typeof(arena) != TYPE_DICTIONARY and "hazards" in arena:
            hazards = arena.hazards
    elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
        var arena = world.arena
        if typeof(arena) == TYPE_DICTIONARY and arena.has("hazards"):
            hazards = arena["hazards"]
        elif typeof(arena) != TYPE_DICTIONARY and "hazards" in arena:
            hazards = arena.hazards

    if hazards != null:
        var hazards_to_remove = []
        for h in hazards:
            var h_active = true
            var hx = 0.0
            var hy = 0.0
            var hr = 10.0
            var h_team = null

            if typeof(h) == TYPE_DICTIONARY:
                h_active = h.get("active", true)
                hx = h.get("x", 0.0)
                hy = h.get("y", 0.0)
                hr = h.get("radius", 10.0)
                h_team = h.get("team", null)
            else:
                if "active" in h: h_active = h.active
                if "x" in h: hx = h.x
                if "y" in h: hy = h.y
                if "radius" in h: hr = h.radius
                if "team" in h: h_team = h.team

            if not h_active:
                continue

            for illusion in illusions.values():
                if not illusion["alive"]:
                    continue

                if h_team != null and h_team == illusion["team"]:
                    continue

                var dx = hx - illusion["x"]
                var dy = hy - illusion["y"]
                var dist = sqrt(dx * dx + dy * dy)

                if dist < hr + illusion["radius"]:
                    hazards_to_remove.append(h)
                    break

        for h in hazards_to_remove:
            if typeof(h) == TYPE_DICTIONARY:
                h["active"] = false
            else:
                if "active" in h: h.active = false

            if typeof(hazards) == TYPE_ARRAY and hazards.has(h):
                hazards.erase(h)
