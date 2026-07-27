extends "res://src/ai/game_modes.gd".GameMode

var arena_width = 800.0
var arena_height = 600.0

func _init():
    super._init()
    name = "Kinetic Battery"
    description = "Balls deal no direct damage. Moving and bouncing charges a battery that unleashes a devastating shockwave."

func setup(world, balls):
    if typeof(world) == TYPE_OBJECT and world.get("arena") != null:
        var arena = world.get("arena")
        if typeof(arena) == TYPE_OBJECT:
            arena_width = arena.get("width") if arena.get("width") != null else 800.0
            arena_height = arena.get("height") if arena.get("height") != null else 600.0
        elif typeof(arena) == TYPE_DICTIONARY:
            arena_width = arena.get("width", 800.0)
            arena_height = arena.get("height", 600.0)
    elif typeof(world) == TYPE_DICTIONARY and world.has("arena"):
        var arena = world["arena"]
        if typeof(arena) == TYPE_DICTIONARY:
            arena_width = arena.get("width", 800.0)
            arena_height = arena.get("height", 600.0)

func tick(world, balls, delta=0.016):
    for b in balls:
        if typeof(b) == TYPE_OBJECT:
            if not b.get("alive") or b.get("ball_type") == "spectator":
                continue

            b.set("damage", 0.0)
            b.set("base_damage", 0.0)

            var charge = b.get("kinetic_charge") if b.get("kinetic_charge") != null else 0.0
            var vx = b.get("vx") if b.get("vx") != null else 0.0
            var vy = b.get("vy") if b.get("vy") != null else 0.0
            var speed = sqrt(vx*vx + vy*vy)

            charge += speed * delta * 0.1

            var radius = b.get("radius") if b.get("radius") != null else 15.0
            var x = b.get("x") if b.get("x") != null else 0.0
            var y = b.get("y") if b.get("y") != null else 0.0

            var prev_vx = b.get_meta("prev_vx") if b.has_meta("prev_vx") else vx
            var prev_vy = b.get_meta("prev_vy") if b.has_meta("prev_vy") else vy

            var bounced = false
            if (x <= radius or x >= arena_width - radius) and vx * prev_vx < 0:
                bounced = true
            if (y <= radius or y >= arena_height - radius) and vy * prev_vy < 0:
                bounced = true

            if bounced:
                charge += 20.0

            b.set_meta("prev_vx", vx)
            b.set_meta("prev_vy", vy)

            if charge >= 100.0:
                charge = 0.0
                if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
                    world.add_event("explosion", {
                        "x": x, "y": y,
                        "radius": 200.0,
                        "damage": 100.0,
                        "color": "cyan"
                    })
                elif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
                    world["add_event"].call("explosion", {
                        "x": x, "y": y,
                        "radius": 200.0,
                        "damage": 100.0,
                        "color": "cyan"
                    })

                for other in balls:
                    if typeof(other) == TYPE_OBJECT:
                        if not other.get("alive") or other.get("ball_type") == "spectator" or other == b:
                            continue
                        if other.get("team") != b.get("team"):
                            var ox = other.get("x") if other.get("x") != null else 0.0
                            var oy = other.get("y") if other.get("y") != null else 0.0
                            var dist_sq = (x - ox)*(x - ox) + (y - oy)*(y - oy)
                            if dist_sq <= 200.0 * 200.0:
                                var hp = other.get("hp") if other.get("hp") != null else 100.0
                                other.set("hp", hp - 100.0)
                                if other.get("hp") <= 0:
                                    other.set("alive", false)
                    elif typeof(other) == TYPE_DICTIONARY:
                        if not other.get("alive", false) or other.get("ball_type") == "spectator" or other == b:
                            continue
                        if other.get("team") != b.get("team"):
                            var ox = other.get("x", 0.0)
                            var oy = other.get("y", 0.0)
                            var dist_sq = (x - ox)*(x - ox) + (y - oy)*(y - oy)
                            if dist_sq <= 200.0 * 200.0:
                                var hp = other.get("hp", 100.0)
                                other["hp"] = hp - 100.0
                                if other["hp"] <= 0:
                                    other["alive"] = false
            b.set("kinetic_charge", charge)

        elif typeof(b) == TYPE_DICTIONARY:
            if not b.get("alive", false) or b.get("ball_type", "") == "spectator":
                continue

            b["damage"] = 0.0
            b["base_damage"] = 0.0

            var charge = b.get("kinetic_charge", 0.0)
            var vx = b.get("vx", 0.0)
            var vy = b.get("vy", 0.0)
            var speed = sqrt(vx*vx + vy*vy)

            charge += speed * delta * 0.1

            var radius = b.get("radius", 15.0)
            var x = b.get("x", 0.0)
            var y = b.get("y", 0.0)

            var prev_vx = b.get("meta_prev_vx", vx)
            var prev_vy = b.get("meta_prev_vy", vy)

            var bounced = false
            if (x <= radius or x >= arena_width - radius) and vx * prev_vx < 0:
                bounced = true
            if (y <= radius or y >= arena_height - radius) and vy * prev_vy < 0:
                bounced = true

            if bounced:
                charge += 20.0

            b["meta_prev_vx"] = vx
            b["meta_prev_vy"] = vy

            if charge >= 100.0:
                charge = 0.0
                if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
                    world.add_event("explosion", {
                        "x": x, "y": y,
                        "radius": 200.0,
                        "damage": 100.0,
                        "color": "cyan"
                    })
                elif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
                    world["add_event"].call("explosion", {
                        "x": x, "y": y,
                        "radius": 200.0,
                        "damage": 100.0,
                        "color": "cyan"
                    })

                for other in balls:
                    if typeof(other) == TYPE_OBJECT:
                        if not other.get("alive") or other.get("ball_type") == "spectator" or other == b:
                            continue
                        if other.get("team") != b.get("team"):
                            var ox = other.get("x") if other.get("x") != null else 0.0
                            var oy = other.get("y") if other.get("y") != null else 0.0
                            var dist_sq = (x - ox)*(x - ox) + (y - oy)*(y - oy)
                            if dist_sq <= 200.0 * 200.0:
                                var hp = other.get("hp") if other.get("hp") != null else 100.0
                                other.set("hp", hp - 100.0)
                                if other.get("hp") <= 0:
                                    other.set("alive", false)
                    elif typeof(other) == TYPE_DICTIONARY:
                        if not other.get("alive", false) or other.get("ball_type") == "spectator" or other == b:
                            continue
                        if other.get("team") != b.get("team", ""):
                            var ox = other.get("x", 0.0)
                            var oy = other.get("y", 0.0)
                            var dist_sq = (x - ox)*(x - ox) + (y - oy)*(y - oy)
                            if dist_sq <= 200.0 * 200.0:
                                var hp = other.get("hp", 100.0)
                                other["hp"] = hp - 100.0
                                if other["hp"] <= 0:
                                    other["alive"] = false
            b["kinetic_charge"] = charge
