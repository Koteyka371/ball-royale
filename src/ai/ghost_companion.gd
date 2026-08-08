extends "res://src/ai/game_modes.gd".GameMode

class_name GhostCompanionMode

func _init().():
    name = "Ghost Companion"
    description = "Eliminated players spawn as ghosts that can attach to living players, applying small buffs or debuffs."

func setup(world, balls):
    .setup(world, balls)
    if not world.has("dead_balls"):
        world.dead_balls = []

func tick(world, balls, delta = 0.016):
    .tick(world, balls, delta)

    # Process ghost logic
    for b in balls:
        var b_id = b.id if "id" in b else null
        var b_type = b.ball_type if "ball_type" in b else null

        if b_id == null or b_type == "spectator":
            continue

        var hp = b.hp if "hp" in b else 100.0
        var is_ghost = b.is_ghost if "is_ghost" in b else false

        if hp <= 0 and not is_ghost:
            b.is_ghost = true
            b.ghost_target_id = null
            b.alive = true
            b.max_hp = 50.0
            b.hp = 50.0
            b.speed = 150.0
            b.damage = 0.0
            if "dead_balls" in world and world.dead_balls.has(b_id):
                world.dead_balls.erase(b_id)

    for b in balls:
        if "is_ghost" in b and b.is_ghost:
            var target_id = b.ghost_target_id if "ghost_target_id" in b else null

            # Check if target is alive or triggered hazard
            if target_id != null:
                var target_b = null
                var is_hazard = false
                for ob in balls:
                    if ("id" in ob) and ob.id == target_id:
                        target_b = ob
                        break

                if target_b == null and "arena" in world and world.arena != null and "hazards" in world.arena:
                    for h in world.arena.hazards:
                        if ("id" in h) and h.id == target_id:
                            target_b = h
                            is_hazard = true
                            break

                if is_hazard:
                    var t_triggered = target_b.triggered if "triggered" in target_b else false
                    var t_active = target_b.active if "active" in target_b else false
                    if t_triggered or t_active:
                        b.ghost_target_id = null
                        target_id = null
                else:
                    var t_alive = target_b.alive if target_b and "alive" in target_b else false
                    var t_ghost = target_b.is_ghost if target_b and "is_ghost" in target_b else false
                    if not target_b or not t_alive or t_ghost:
                        b.ghost_target_id = null
                        target_id = null

            if target_id == null:
                var min_dist = 999999.0
                var best_target = null

                for ob in balls:
                    var o_alive = ob.alive if "alive" in ob else false
                    var o_ghost = ob.is_ghost if "is_ghost" in ob else false
                    var o_type = ob.ball_type if "ball_type" in ob else null

                    if o_alive and not o_ghost and o_type != "spectator":
                        var dx = ob.x - b.x
                        var dy = ob.y - b.y
                        var d = dx*dx + dy*dy
                        if d < min_dist:
                            min_dist = d
                            best_target = ob

                if best_target == null and "arena" in world and world.arena != null and "hazards" in world.arena:
                    for h in world.arena.hazards:
                        var h_triggered = h.triggered if "triggered" in h else false
                        var h_active = h.active if "active" in h else false
                        if not h_triggered and not h_active:
                            var h_x = h.x if "x" in h else 0.0
                            var h_y = h.y if "y" in h else 0.0
                            var dx = h_x - b.x
                            var dy = h_y - b.y
                            var d = dx*dx + dy*dy
                            if d < min_dist:
                                min_dist = d
                                best_target = h

                if best_target != null:
                    b.ghost_target_id = best_target.id if "id" in best_target else null
            else:
                var target_b = null
                var is_hazard = false
                for ob in balls:
                    if ("id" in ob) and ob.id == target_id:
                        target_b = ob
                        break

                if target_b == null and "arena" in world and world.arena != null and "hazards" in world.arena:
                    for h in world.arena.hazards:
                        if ("id" in h) and h.id == target_id:
                            target_b = h
                            is_hazard = true
                            break

                if target_b != null:
                    b.x = target_b.x if "x" in target_b else b.x
                    b.y = target_b.y if "y" in target_b else b.y
                    b.vx = 0.0
                    b.vy = 0.0

                    if not is_hazard:
                        var b_team = b.team if "team" in b else null
                        var t_team = target_b.team if "team" in target_b else null
                        var t_base_speed = target_b.base_speed if "base_speed" in target_b else 100.0

                        if b_team == t_team:
                            target_b.speed = t_base_speed * 1.2
                            var max_hp = target_b.max_hp if "max_hp" in target_b else 100.0
                            var cur_hp = target_b.hp if "hp" in target_b else 100.0
                            target_b.hp = min(max_hp, cur_hp + 2.0 * delta)
                        else:
                            target_b.speed = t_base_speed * 0.8
                            if target_b.has_method("take_damage"):
                                target_b.take_damage(5.0 * delta)
                            else:
                                var cur_hp = target_b.hp if "hp" in target_b else 100.0
                                target_b.hp = cur_hp - 5.0 * delta
                                if target_b.hp <= 0:
                                    target_b.hp = 0
                                    target_b.alive = false
                    else:
                        var enemy_near = false
                        var b_team = b.team if "team" in b else null
                        for ob in balls:
                            var o_alive = ob.alive if "alive" in ob else false
                            var o_ghost = ob.is_ghost if "is_ghost" in ob else false
                            var o_type = ob.ball_type if "ball_type" in ob else null
                            var o_team = ob.team if "team" in ob else null

                            if o_alive and not o_ghost and o_type != "spectator":
                                if o_team != b_team:
                                    var dx = ob.x - b.x
                                    var dy = ob.y - b.y
                                    var d = dx*dx + dy*dy
                                    if d < 10000.0:
                                        enemy_near = true
                                        break

                        if enemy_near:
                            if typeof(target_b) == TYPE_OBJECT:
                                if "active" in target_b: target_b.active = true
                                elif target_b.has_method("set_meta"): target_b.set_meta("active", true)
                                if "triggered" in target_b: target_b.triggered = true
                                elif target_b.has_method("set_meta"): target_b.set_meta("triggered", true)
                            elif typeof(target_b) == TYPE_DICTIONARY:
                                target_b["active"] = true
                                target_b["triggered"] = true
                            b.ghost_target_id = null

func check_winner(world, balls):
    var alive_teams = {}
    var alive_count = 0

    for b in balls:
        var is_alive = b.alive if "alive" in b else false
        var b_type = b.ball_type if "ball_type" in b else null
        var is_ghost = b.is_ghost if "is_ghost" in b else false

        if is_alive and b_type != "spectator" and not is_ghost:
            var team = b.team if "team" in b else b_type
            if team != null:
                alive_teams[team] = true
                alive_count += 1

    if alive_count == 0:
        return "Draw"

    if alive_teams.size() == 1:
        return alive_teams.keys()[0]

    return null
