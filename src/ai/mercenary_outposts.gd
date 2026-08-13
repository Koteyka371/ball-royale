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
            "spawn_timer": 0.0,
            "spawn_interval": 5.0
        })
        world.arena.hazards.append({
            "kind": "mercenary_outpost",
            "x": 700.0,
            "y": 700.0,
            "radius": 80.0,
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
            var vx = 0.0
            var vy = 0.0

            if owner_id != null:
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
            else:
                var camp = null
                var closest_camp_dist = 999999.0
                if "hazards" in world.arena:
                    for h in world.arena.hazards:
                        var h_kind = ""
                        var h_x = 0.0
                        var h_y = 0.0
                        if typeof(h) == TYPE_DICTIONARY:
                            h_kind = h.get("kind", "")
                            h_x = h.get("x", 0.0)
                            h_y = h.get("y", 0.0)
                        else:
                            h_kind = h.kind if "kind" in h else ""
                            h_x = h.x if "x" in h else 0.0
                            h_y = h.y if "y" in h else 0.0

                        if h_kind == "mercenary_outpost":
                            var dist = sqrt((h_x - b_x)*(h_x - b_x) + (h_y - b_y)*(h_y - b_y))
                            if dist < closest_camp_dist:
                                closest_camp_dist = dist
                                camp = h

                if camp != null:
                    var c_x = 0.0
                    var c_y = 0.0
                    if typeof(camp) == TYPE_DICTIONARY:
                        c_x = camp.get("x", 0.0)
                        c_y = camp.get("y", 0.0)
                    else:
                        c_x = camp.x if "x" in camp else 0.0
                        c_y = camp.y if "y" in camp else 0.0

                    var dx = c_x - b_x
                    var dy = c_y - b_y
                    var dist_to_camp = sqrt(dx*dx + dy*dy)
                    if dist_to_camp > 100:
                        if dist_to_camp > 0:
                            vx = (dx / dist_to_camp) * (speed * 0.5)
                            vy = (dy / dist_to_camp) * (speed * 0.5)
                    else:
                        if randf() < 0.05:
                            var angle = randf() * 2 * PI
                            vx = cos(angle) * (speed * 0.3)
                            vy = sin(angle) * (speed * 0.3)
                        elif typeof(b) == TYPE_DICTIONARY:
                            vx = b.get("vx", 0.0)
                            vy = b.get("vy", 0.0)
                        else:
                            vx = b.vx if "vx" in b else 0.0
                            vy = b.vy if "vy" in b else 0.0

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

    for b in balls:
        var p_cooldown = b.get("purchase_cooldown", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.purchase_cooldown if "purchase_cooldown" in b else 0.0)
        if p_cooldown > 0.0:
            p_cooldown -= delta
            if p_cooldown < 0.0:
                p_cooldown = 0.0

            if typeof(b) == TYPE_DICTIONARY:
                b["purchase_cooldown"] = p_cooldown
            else:
                if b.has_method("set_meta"): b.set_meta("purchase_cooldown", p_cooldown)
                else: b.purchase_cooldown = p_cooldown

    # Merc duration logic
    for b in balls:
        var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else "")
        var alive = b.get("alive", true) if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else true)

        if b_type == "mercenary" and alive:
            var h_timer = b.get("hire_timer", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.hire_timer if "hire_timer" in b else 0.0)
            if h_timer > 0.0:
                h_timer -= delta
                if h_timer <= 0.0:
                    if typeof(b) == TYPE_DICTIONARY:
                        b["owner_id"] = null
                        b["team"] = null
                        b["hire_timer"] = 0.0
                    else:
                        if b.has_method("set_meta"):
                            b.set_meta("owner_id", null)
                            b.set_meta("team", null)
                            b.set_meta("hire_timer", 0.0)
                        else:
                            b.owner_id = null
                            b.team = null
                            b.hire_timer = 0.0
                else:
                    if typeof(b) == TYPE_DICTIONARY:
                        b["hire_timer"] = h_timer
                    else:
                        if b.has_method("set_meta"): b.set_meta("hire_timer", h_timer)
                        else: b.hire_timer = h_timer

    # Hire logic
    for b in balls:
        var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else "")
        var b_alive = b.get("alive", true) if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else true)
        if b_type != "mercenary" and b_type != "spectator" and b_alive:
            var p_cooldown = b.get("purchase_cooldown", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.purchase_cooldown if "purchase_cooldown" in b else 0.0)
            if p_cooldown <= 0.0:
                for m in balls:
                    var m_type = m.get("ball_type", "") if typeof(m) == TYPE_DICTIONARY else (m.ball_type if "ball_type" in m else "")
                    var m_alive = m.get("alive", true) if typeof(m) == TYPE_DICTIONARY else (m.alive if "alive" in m else true)
                    var m_owner = m.get("owner_id", null) if typeof(m) == TYPE_DICTIONARY else (m.owner_id if "owner_id" in m else null)

                    if m_type == "mercenary" and m_alive and m_owner == null:
                        var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.x if "x" in b else 0.0)
                        var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.y if "y" in b else 0.0)
                        var b_r = b.get("radius", 20.0) if typeof(b) == TYPE_DICTIONARY else (b.radius if "radius" in b else 20.0)

                        var m_x = m.get("x", 0.0) if typeof(m) == TYPE_DICTIONARY else (m.x if "x" in m else 0.0)
                        var m_y = m.get("y", 0.0) if typeof(m) == TYPE_DICTIONARY else (m.y if "y" in m else 0.0)
                        var m_r = m.get("radius", 20.0) if typeof(m) == TYPE_DICTIONARY else (m.radius if "radius" in m else 20.0)

                        var dist = sqrt((b_x - m_x)*(b_x - m_x) + (b_y - m_y)*(b_y - m_y))
                        if dist < b_r + m_r + 20.0:
                            var currency = b.get("currency", 0) if typeof(b) == TYPE_DICTIONARY else (b.currency if "currency" in b else 0)
                            var prestige = b.get("prestige_tokens", 0) if typeof(b) == TYPE_DICTIONARY else (b.prestige_tokens if "prestige_tokens" in b else 0)
                            var hired = false

                            if prestige >= 1:
                                if typeof(b) == TYPE_DICTIONARY: b["prestige_tokens"] = prestige - 1
                                else:
                                    if b.has_method("set_meta"): b.set_meta("prestige_tokens", prestige - 1)
                                    else: b.prestige_tokens = prestige - 1
                                hired = true
                            elif currency >= 10:
                                if typeof(b) == TYPE_DICTIONARY: b["currency"] = currency - 10
                                else:
                                    if b.has_method("set_meta"): b.set_meta("currency", currency - 10)
                                    else: b.currency = currency - 10
                                hired = true

                            if hired:
                                var b_id = b.get("id", null) if typeof(b) == TYPE_DICTIONARY else (b.id if "id" in b else null)
                                var b_team = b.get("team", null) if typeof(b) == TYPE_DICTIONARY else (b.team if "team" in b else null)

                                if typeof(m) == TYPE_DICTIONARY:
                                    m["owner_id"] = b_id
                                    m["team"] = b_team
                                    m["hire_timer"] = 30.0
                                else:
                                    if m.has_method("set_meta"):
                                        m.set_meta("owner_id", b_id)
                                        m.set_meta("team", b_team)
                                        m.set_meta("hire_timer", 30.0)
                                    else:
                                        m.owner_id = b_id
                                        m.team = b_team
                                        m.hire_timer = 30.0

                                if typeof(b) == TYPE_DICTIONARY:
                                    b["purchase_cooldown"] = 1.0
                                else:
                                    if b.has_method("set_meta"): b.set_meta("purchase_cooldown", 1.0)
                                    else: b.purchase_cooldown = 1.0
                                break

    var new_mercs = []

    for h in world.arena.hazards:
        var is_outpost = false
        if typeof(h) == TYPE_DICTIONARY and h.get("kind", "") == "mercenary_outpost":
            is_outpost = true
        elif typeof(h) == TYPE_OBJECT and h.get("kind") == "mercenary_outpost":
            is_outpost = true

        if is_outpost:
            var h_x = 0.0
            var h_y = 0.0
            var spawn_timer = 0.0
            var spawn_interval = 5.0

            if typeof(h) == TYPE_DICTIONARY:
                h_x = h.get("x", 0.0)
                h_y = h.get("y", 0.0)
                spawn_timer = h.get("spawn_timer", 0.0)
                spawn_interval = h.get("spawn_interval", 5.0)
            else:
                h_x = h.get("x") if "x" in h else 0.0
                h_y = h.get("y") if "y" in h else 0.0
                spawn_timer = h.get("spawn_timer") if "spawn_timer" in h else 0.0
                spawn_interval = h.get("spawn_interval") if "spawn_interval" in h else 5.0

            spawn_timer += delta
            if spawn_timer >= spawn_interval:
                var unowned = 0
                for m in balls:
                    var m_type = m.get("ball_type", "") if typeof(m) == TYPE_DICTIONARY else (m.ball_type if "ball_type" in m else "")
                    var m_alive = m.get("alive", true) if typeof(m) == TYPE_DICTIONARY else (m.alive if "alive" in m else true)
                    var m_owner = m.get("owner_id", null) if typeof(m) == TYPE_DICTIONARY else (m.owner_id if "owner_id" in m else null)

                    if m_type == "mercenary" and m_owner == null and m_alive:
                        var m_x = m.get("x", 0.0) if typeof(m) == TYPE_DICTIONARY else (m.x if "x" in m else 0.0)
                        var m_y = m.get("y", 0.0) if typeof(m) == TYPE_DICTIONARY else (m.y if "y" in m else 0.0)
                        var dist = sqrt((m_x - h_x)*(m_x - h_x) + (m_y - h_y)*(m_y - h_y))
                        if dist < 200.0:
                            unowned += 1

                if unowned < 3:
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
                        "team": null,
                        "owner_id": null,
                        "speed": 120.0,
                        "base_speed": 120.0,
                        "damage": 15.0,
                        "base_damage": 15.0,
                        "speed_multiplier": 1.0,
                        "damage_multiplier": 1.0,
                        "perception_radius": 400.0,
                        "base_perception_radius": 400.0,
                        "hire_timer": 0.0
                    }
                    new_mercs.append(merc)

            if typeof(h) == TYPE_DICTIONARY:
                h["spawn_timer"] = spawn_timer
            else:
                if h.has_method("set_meta"): h.set_meta("spawn_timer", spawn_timer)
                else: h.spawn_timer = spawn_timer

    if new_mercs.size() > 0:
        for m in new_mercs:
            balls.append(m)

    apply_dynamic_traits(world, balls, delta)
