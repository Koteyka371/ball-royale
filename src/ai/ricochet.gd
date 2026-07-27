extends Node

var name = "Ricochet Mode"
var description = "All projectiles bounce off walls infinitely until they hit a target or their duration expires, making positioning extremely important."
var active = false

func tick(world: Dictionary, balls: Array, delta: float) -> void:
    var arena_width = 1000.0
    var arena_height = 1000.0
    if world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY:
        if world["arena"].has("width"):
            arena_width = world["arena"]["width"]
        if world["arena"].has("height"):
            arena_height = world["arena"]["height"]
    elif world.has("arena") and typeof(world["arena"]) == TYPE_OBJECT:
        if "width" in world["arena"]:
            arena_width = world["arena"].width
        if "height" in world["arena"]:
            arena_height = world["arena"].height

    var projs = []
    if world.has("projectiles"):
        projs = projs + world["projectiles"]

    var hazards = []
    if world.has("arena"):
        if typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
            hazards = world["arena"]["hazards"]
        elif typeof(world["arena"]) == TYPE_OBJECT and "hazards" in world["arena"]:
            hazards = world["arena"].hazards

    for proj in projs + hazards:
        var alive = true
        if typeof(proj) == TYPE_DICTIONARY:
            if proj.has("alive"):
                alive = proj["alive"]
            elif proj.has("hp"):
                alive = proj["hp"] > 0
        else:
            if "alive" in proj:
                alive = proj.alive
            elif "hp" in proj:
                alive = proj.hp > 0

        if not alive:
            continue

        var b_type = ""
        if typeof(proj) == TYPE_DICTIONARY:
            if proj.has("ball_type"):
                b_type = proj["ball_type"]
            elif proj.has("kind"):
                b_type = proj["kind"]
        else:
            if "ball_type" in proj:
                b_type = proj.ball_type
            elif "kind" in proj:
                b_type = proj.kind

        var is_proj = b_type in ["projectile", "spell", "fireball", "bullet", "snipe", "laser_beam"]
        if not is_proj:
            if typeof(proj) == TYPE_DICTIONARY:
                if proj.has("is_projectile") and proj["is_projectile"]:
                    is_proj = true
                elif proj.has("is_spell") and proj["is_spell"]:
                    is_proj = true
            else:
                if "is_projectile" in proj and proj.is_projectile:
                    is_proj = true
                elif "is_spell" in proj and proj.is_spell:
                    is_proj = true

        if not is_proj:
            continue

        if typeof(proj) == TYPE_DICTIONARY:
            if proj.has("bounces"):
                proj["bounces"] = 0
            if proj.has("bounces_left"):
                proj["bounces_left"] = 999
        else:
            if proj.has_method("has_meta") and proj.has_meta("bounces"):
                proj.set_meta("bounces", 0)
            elif "bounces" in proj:
                proj.bounces = 0

            if proj.has_method("has_meta") and proj.has_meta("bounces_left"):
                proj.set_meta("bounces_left", 999)
            elif "bounces_left" in proj:
                proj.bounces_left = 999

        var px = 0.0
        var py = 0.0
        var radius = 5.0
        var vx = 0.0
        var vy = 0.0

        if typeof(proj) == TYPE_DICTIONARY:
            if proj.has("x"): px = proj["x"]
            if proj.has("y"): py = proj["y"]
            if proj.has("radius"): radius = proj["radius"]
            if proj.has("vx"): vx = proj["vx"]
            if proj.has("vy"): vy = proj["vy"]
        else:
            if "x" in proj: px = proj.x
            if "y" in proj: py = proj.y
            if "radius" in proj: radius = proj.radius
            if "vx" in proj: vx = proj.vx
            if "vy" in proj: vy = proj.vy

        var bounced = false
        if px - radius < 0 and vx < 0:
            vx = -vx
            px = radius
            bounced = true
        elif px + radius > arena_width and vx > 0:
            vx = -vx
            px = arena_width - radius
            bounced = true

        if py - radius < 0 and vy < 0:
            vy = -vy
            py = radius
            bounced = true
        elif py + radius > arena_height and vy > 0:
            vy = -vy
            py = arena_height - radius
            bounced = true

        if bounced:
            if typeof(proj) == TYPE_DICTIONARY:
                proj["x"] = px
                proj["y"] = py
                proj["vx"] = vx
                proj["vy"] = vy
            else:
                proj.x = px
                proj.y = py
                proj.vx = vx
                proj.vy = vy

func setup(world: Dictionary, balls: Array) -> void:
    active = true

func teardown(world: Dictionary, balls: Array) -> void:
    active = false
