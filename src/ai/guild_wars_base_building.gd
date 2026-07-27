extends "res://src/ai/game_modes.gd"

var active_defenses: Array = []

func _init() -> void:
    name = "Guild Wars"
    description = "Attack enemy guild bases while defending your own."

func setup(world, balls: Array) -> void:
    active_defenses.clear()

    var defenses = []
    if typeof(world) == TYPE_DICTIONARY and "guild_defenses" in world: defenses = world.guild_defenses
    elif typeof(world) == TYPE_OBJECT and "guild_defenses" in world: defenses = world.guild_defenses

    for d in defenses:
        var d_type = ""
        var d_x = 0.0
        var d_y = 0.0
        var d_hp = 100.0
        var d_team = "defender"

        if typeof(d) == TYPE_DICTIONARY:
            d_type = d.get("type", "")
            d_x = d.get("x", 0.0)
            d_y = d.get("y", 0.0)
            d_hp = d.get("hp", 100.0)
            d_team = d.get("team", "defender")

        var radius = 20.0
        if d_type == "turret": radius = 30.0
        elif d_type == "wall": radius = 50.0

        var defense_obj = {
            "type": d_type,
            "x": d_x,
            "y": d_y,
            "hp": d_hp,
            "max_hp": d_hp,
            "radius": radius,
            "team": d_team,
            "cooldown": 0.0,
            "alive": true
        }
        active_defenses.append(defense_obj)

func tick(world, balls: Array, delta: float = 0.016) -> void:
    for d in active_defenses:
        if not d.alive: continue

        if d.type == "turret":
            d.cooldown -= delta
            if d.cooldown <= 0.0:
                var target = null
                var min_dist = 500.0

                for b in balls:
                    var b_alive = false
                    var b_team = null

                    if typeof(b) == TYPE_DICTIONARY:
                        b_alive = b.get("alive", false)
                        b_team = b.get("team", null)
                    elif typeof(b) == TYPE_OBJECT:
                        b_alive = b.get("alive") if "alive" in b else false
                        b_team = b.get("team") if "team" in b else null

                    if b_alive and b_team != d.team:
                        var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.get("x") if "x" in b else 0.0)
                        var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.get("y") if "y" in b else 0.0)

                        var dx = b_x - d.x
                        var dy = b_y - d.y
                        var dist = sqrt(dx*dx + dy*dy)

                        if dist < min_dist:
                            min_dist = dist
                            target = b

                if target != null:
                    if typeof(target) == TYPE_OBJECT and target.has_method("take_damage"):
                        target.take_damage(50.0)
                    else:
                        var hp = target.get("hp", 0.0) if typeof(target) == TYPE_DICTIONARY else (target.get("hp") if "hp" in target else 0.0)
                        hp -= 50.0
                        if typeof(target) == TYPE_DICTIONARY:
                            target["hp"] = hp
                            if hp <= 0.0: target["alive"] = false
                        else:
                            target.set("hp", hp)
                            if hp <= 0.0: target.set("alive", false)

                    d.cooldown = 1.0

        elif d.type == "trap":
            for b in balls:
                var b_alive = false
                var b_team = null

                if typeof(b) == TYPE_DICTIONARY:
                    b_alive = b.get("alive", false)
                    b_team = b.get("team", null)
                elif typeof(b) == TYPE_OBJECT:
                    b_alive = b.get("alive") if "alive" in b else false
                    b_team = b.get("team") if "team" in b else null

                if b_alive and b_team != d.team:
                    var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.get("x") if "x" in b else 0.0)
                    var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.get("y") if "y" in b else 0.0)
                    var b_radius = b.get("radius", 20.0) if typeof(b) == TYPE_DICTIONARY else (b.get("radius") if "radius" in b else 20.0)

                    var dx = b_x - d.x
                    var dy = b_y - d.y
                    var dist = sqrt(dx*dx + dy*dy)

                    if dist < d.radius + b_radius:
                        if typeof(b) == TYPE_OBJECT and b.has_method("take_damage"):
                            b.take_damage(200.0)
                        else:
                            var hp = b.get("hp", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.get("hp") if "hp" in b else 0.0)
                            hp -= 200.0
                            if typeof(b) == TYPE_DICTIONARY:
                                b["hp"] = hp
                                if hp <= 0.0: b["alive"] = false
                            else:
                                b.set("hp", hp)
                                if hp <= 0.0: b.set("alive", false)

                        d.alive = false
                        break

    var remaining = []
    for d in active_defenses:
        if d.alive:
            remaining.append(d)
    active_defenses = remaining
