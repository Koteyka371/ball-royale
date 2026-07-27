extends Node

var name = "Mercenary Outposts"
var description = "Capture outposts to spawn friendly mercenaries."
var active = false
var active_timer = 0.0

func _init():
    pass

func setup(world, balls):
    if not ("hazards" in world.arena):
        world.arena.hazards = []

    var has_outpost = false
    for h in world.arena.hazards:
        if typeof(h) == TYPE_DICTIONARY and h.get("kind", "") == "mercenary_outpost":
            has_outpost = true
            break
        elif typeof(h) == TYPE_OBJECT and h.get("kind") == "mercenary_outpost":
            has_outpost = true
            break

    if not has_outpost:
        world.arena.hazards.append({
            "kind": "mercenary_outpost",
            "x": 300.0,
            "y": 300.0,
            "radius": 80.0,
            "capture_progress": 0.0,
            "capture_threshold": 10.0,
            "owner_id": null,
            "owner_team": null,
            "spawn_timer": 0.0,
            "spawn_interval": 5.0
        })
        world.arena.hazards.append({
            "kind": "mercenary_outpost",
            "x": 700.0,
            "y": 700.0,
            "radius": 80.0,
            "capture_progress": 0.0,
            "capture_threshold": 10.0,
            "owner_id": null,
            "owner_team": null,
            "spawn_timer": 0.0,
            "spawn_interval": 5.0
        })

func apply_dynamic_traits(world, balls, delta):
    for b in balls:
        var b_type = ""
        var alive = false
        var b_team = null
        var b_x = 0.0
        var b_y = 0.0
        var owner_id = null
        var perception = 400.0
        var speed = 120.0

        if typeof(b) == TYPE_DICTIONARY:
            b_type = b.get("ball_type", "")
            alive = b.get("alive", true)
            b_team = b.get("team", null)
            b_x = b.get("x", 0.0)
            b_y = b.get("y", 0.0)
            owner_id = b.get("owner_id", null)
            perception = b.get("perception_radius", 400.0)
            speed = b.get("speed", 120.0)
        else:
            b_type = b.ball_type if "ball_type" in b else ""
            alive = b.alive if "alive" in b else true
            b_team = b.team if "team" in b else null
            b_x = b.x
            b_y = b.y
            owner_id = b.owner_id if "owner_id" in b else null
            perception = b.perception_radius if "perception_radius" in b else 400.0
            speed = b.speed if "speed" in b else 120.0

        if b_type == "mercenary" and alive:
            var closest_enemy = null
            var closest_dist = 999999.0

            for other in balls:
                var o_alive = false
                var o_team = null
                var o_type = ""
                var o_x = 0.0
                var o_y = 0.0

                if typeof(other) == TYPE_DICTIONARY:
                    o_alive = other.get("alive", true)
                    o_team = other.get("team", null)
                    o_type = other.get("ball_type", "")
                    o_x = other.get("x", 0.0)
                    o_y = other.get("y", 0.0)
                else:
                    o_alive = other.alive if "alive" in other else true
                    o_team = other.team if "team" in other else null
                    o_type = other.ball_type if "ball_type" in other else ""
                    o_x = other.x
                    o_y = other.y

                if o_alive and o_team != b_team and o_type != "spectator":
                    var dx = b_x - o_x
                    var dy = b_y - o_y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_enemy = other

            var vx = 0.0
            var vy = 0.0

            if closest_enemy != null and closest_dist < perception:
                var o_x = 0.0
                var o_y = 0.0
                if typeof(closest_enemy) == TYPE_DICTIONARY:
                    o_x = closest_enemy.get("x", 0.0)
                    o_y = closest_enemy.get("y", 0.0)
                else:
                    o_x = closest_enemy.x
                    o_y = closest_enemy.y

                var dx = o_x - b_x
                var dy = o_y - b_y
                var mag = sqrt(dx*dx + dy*dy)
                if mag > 0:
                    vx = (dx / mag) * speed
                    vy = (dy / mag) * speed
            else:
                var owner = null
                for other in balls:
                    var o_id = null
                    if typeof(other) == TYPE_DICTIONARY:
                        o_id = other.get("id", null)
                    else:
                        o_id = other.id if "id" in other else null

                    if o_id != null and o_id == owner_id:
                        owner = other
                        break

                if owner != null:
                    var o_x = 0.0
                    var o_y = 0.0
                    if typeof(owner) == TYPE_DICTIONARY:
                        o_x = owner.get("x", 0.0)
                        o_y = owner.get("y", 0.0)
                    else:
                        o_x = owner.x
                        o_y = owner.y

                    var dx = o_x - b_x
                    var dy = o_y - b_y
                    var mag = sqrt(dx*dx + dy*dy)
                    if mag > 100:
                        vx = (dx / mag) * speed
                        vy = (dy / mag) * speed

            if typeof(b) == TYPE_DICTIONARY:
                b["vx"] = vx
                b["vy"] = vy
                b["x"] = b_x + vx * delta
                b["y"] = b_y + vy * delta
            else:
                b.vx = vx
                b.vy = vy
                b.x = b_x + vx * delta
                b.y = b_y + vy * delta

func tick(world, balls, delta=0.016):
    if not ("hazards" in world.arena):
        return

    if active:
        active_timer -= delta
        if active_timer <= 0.0:
            active = false

    var new_mercs = []

    for h in world.arena.hazards:
        var is_outpost = false
        if typeof(h) == TYPE_DICTIONARY and h.get("kind", "") == "mercenary_outpost":
            is_outpost = true
        elif typeof(h) == TYPE_OBJECT and h.get("kind") == "mercenary_outpost":
            is_outpost = true

        if is_outpost:
            var progress = 0.0
            var threshold = 10.0
            var radius = 80.0
            var owner_id = null
            var owner_team = null
            var h_x = 0.0
            var h_y = 0.0
            var spawn_timer = 0.0
            var spawn_interval = 5.0

            if typeof(h) == TYPE_DICTIONARY:
                progress = h.get("capture_progress", 0.0)
                threshold = h.get("capture_threshold", 10.0)
                radius = h.get("radius", 80.0)
                owner_id = h.get("owner_id", null)
                owner_team = h.get("owner_team", null)
                h_x = h.get("x", 0.0)
                h_y = h.get("y", 0.0)
                spawn_timer = h.get("spawn_timer", 0.0)
                spawn_interval = h.get("spawn_interval", 5.0)
            else:
                progress = h.get("capture_progress") if "capture_progress" in h else 0.0
                threshold = h.get("capture_threshold") if "capture_threshold" in h else 10.0
                radius = h.get("radius") if "radius" in h else 80.0
                owner_id = h.get("owner_id") if "owner_id" in h else null
                owner_team = h.get("owner_team") if "owner_team" in h else null
                h_x = h.get("x") if "x" in h else 0.0
                h_y = h.get("y") if "y" in h else 0.0
                spawn_timer = h.get("spawn_timer") if "spawn_timer" in h else 0.0
                spawn_interval = h.get("spawn_interval") if "spawn_interval" in h else 5.0

            if progress < threshold:
                var capturing_balls = []
                for b in balls:
                    var alive = true
                    var b_type = ""
                    var b_x = 0.0
                    var b_y = 0.0
                    if typeof(b) == TYPE_DICTIONARY:
                        alive = b.get("alive", true)
                        b_type = b.get("ball_type", "")
                        b_x = b.get("x", 0.0)
                        b_y = b.get("y", 0.0)
                    else:
                        alive = b.alive if "alive" in b else true
                        b_type = b.ball_type if "ball_type" in b else ""
                        b_x = b.x
                        b_y = b.y

                    if alive and b_type != "spectator" and b_type != "mercenary":
                        var dx = b_x - h_x
                        var dy = b_y - h_y
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist < radius:
                            capturing_balls.append(b)

                if capturing_balls.size() == 1:
                    var cb = capturing_balls[0]
                    var cb_id = null
                    var cb_team = null
                    if typeof(cb) == TYPE_DICTIONARY:
                        cb_id = cb.get("id", null)
                        cb_team = cb.get("team", null)
                    else:
                        cb_id = cb.id if "id" in cb else null
                        cb_team = cb.team if "team" in cb else null

                    if owner_id != cb_id:
                        owner_id = cb_id
                        owner_team = cb_team
                        progress = 0.0
                        if typeof(h) == TYPE_DICTIONARY:
                            h["owner_id"] = cb_id
                            h["owner_team"] = cb_team
                        else:
                            h.owner_id = cb_id
                            h.owner_team = cb_team

                    progress += delta
                    if progress >= threshold:
                        progress = threshold

                    if typeof(h) == TYPE_DICTIONARY:
                        h["capture_progress"] = progress
                    else:
                        h.capture_progress = progress
            else:
                spawn_timer += delta
                if spawn_timer >= spawn_interval:
                    spawn_timer = 0.0
                    var merc = {
                        "id": randi() % 1000000,
                        "x": h_x,
                        "y": h_y,
                        "vx": 0.0,
                        "vy": 0.0,
                        "radius": 20.0,
                        "mass": 1.0,
                        "hp": 100.0,
                        "max_hp": 100.0,
                        "alive": true,
                        "ball_type": "mercenary",
                        "type": "mercenary",
                        "team": owner_team,
                        "owner_id": owner_id,
                        "speed": 120.0,
                        "base_speed": 120.0,
                        "damage": 15.0,
                        "base_damage": 15.0,
                        "speed_multiplier": 1.0,
                        "damage_multiplier": 1.0,
                        "perception_radius": 400.0,
                        "base_perception_radius": 400.0
                    }
                    new_mercs.append(merc)
                if typeof(h) == TYPE_DICTIONARY:
                    h["spawn_timer"] = spawn_timer
                else:
                    h.spawn_timer = spawn_timer

    if new_mercs.size() > 0:
        for m in new_mercs:
            balls.append(m)

    apply_dynamic_traits(world, balls, delta)
