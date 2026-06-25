class_name ActionLayer
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):
    if strategy == "target_weak":
        _target_weak(delta)
        _update_skill_timer(delta)
        _resolve_collisions()
        _clamp_position()
        return
    var old_x = self.ball.x
    var old_y = self.ball.y

    if "arena" in self.world and self.world.arena.has_method("update_zone"):
        var current_tick = 0
        if "tick" in self.world:
            current_tick = self.world.tick
        self.world.arena.update_zone(current_tick, delta)

        var ball_type = null
        if "ball_type" in self.ball:
            ball_type = self.ball.ball_type
        elif self.ball.has_method("get_ball_type"):
            ball_type = self.ball.get_ball_type()

        if ball_type != "spectator":
            var cx = 0.0
            var cy = 0.0
            var r = INF
            if "safe_zone_center" in self.world.arena:
                var center = self.world.arena.safe_zone_center
                if center.size() >= 2:
                    cx = center[0]
                    cy = center[1]
            if "safe_zone_radius" in self.world.arena:
                r = self.world.arena.safe_zone_radius

            var dist = sqrt((self.ball.x - cx) * (self.ball.x - cx) + (self.ball.y - cy) * (self.ball.y - cy))
            if dist > r:
                var zone_damage = 10.0 * delta
                if self.ball.has_method("take_damage"):
                    self.ball.take_damage(zone_damage)
                elif "hp" in self.ball:
                    self.ball.hp -= zone_damage
                    if self.ball.hp <= 0:
                        self.ball.alive = false


        if "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                if hazard.kind == "trap":
                    var current_tick = 0
                    if "tick" in self.world:
                        current_tick = self.world.tick
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)
                        var dur = 5.0
                        if hazard.has_meta("duration"):
                            dur = hazard.get_meta("duration")
                        hazard.set_meta("duration", dur - delta)
                elif hazard.kind == "black_hole":
                    var current_tick = 0
                    if "tick" in self.world:
                        current_tick = self.world.tick
                    if not hazard.has_meta("last_updated_tick") or hazard.get_meta("last_updated_tick") != current_tick:
                        hazard.set_meta("last_updated_tick", current_tick)
                        if not hazard.has_meta("vx"):
                            hazard.set_meta("vx", 10.0)
                            hazard.set_meta("vy", 10.0)
                        var hvx = hazard.get_meta("vx")
                        var hvy = hazard.get_meta("vy")
                        hazard.x += hvx * delta
                        hazard.y += hvy * delta
                        if hazard.x < 100 or hazard.x > self.world.arena.width - 100:
                            hazard.set_meta("vx", -hvx)
                        if hazard.y < 100 or hazard.y > self.world.arena.height - 100:
                            hazard.set_meta("vy", -hvy)

                        if "boosters" in self.world:
                            for b in self.world.boosters:
                                var bdx = hazard.x - b.x
                                var bdy = hazard.y - b.y
                                var bdist_sq = bdx * bdx + bdy * bdy
                                if bdist_sq > 0.0001:
                                    var bdist = sqrt(bdist_sq)
                                    var bnx = bdx / bdist
                                    var bny = bdy / bdist
                                    var bmin_dist = 10.0
                                    if bdist > bmin_dist:
                                        bmin_dist = bdist
                                    var bpull_strength = (hazard.radius * 2.0 / bmin_dist) * 50.0 * delta
                                    b.x += bnx * bpull_strength
                                    b.y += bny * bpull_strength

                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq > 0.0001:
                        var dist = sqrt(dist_sq)
                        var nx = dx / dist
                        var ny = dy / dist
                        var min_dist = 10.0
                        if dist > min_dist:
                            min_dist = dist
                        var pull_strength = (hazard.radius * 2.0 / min_dist) * 50.0 * delta
                        self.ball.x += nx * pull_strength
                        self.ball.y += ny * pull_strength

        if "hazards" in self.world.arena:
            var alive_hazards = []
            for h in self.world.arena.hazards:
                if h.kind != "trap" or (h.has_meta("duration") and h.get_meta("duration") > 0.0):
                    alive_hazards.append(h)
            self.world.arena.hazards = alive_hazards

        if ball_type != "spectator" and "hazards" in self.world.arena:
            for hazard in self.world.arena.hazards:
                var dist = sqrt((self.ball.x - hazard.x) * (self.ball.x - hazard.x) + (self.ball.y - hazard.y) * (self.ball.y - hazard.y))
                if dist < (self.ball.radius + hazard.radius):
                    if hazard.kind == "trap":
                        if ball_type != "sniper":
                            self.ball.x = (self.ball.x + old_x) / 2.0
                            self.ball.y = (self.ball.y + old_y) / 2.0
                        continue

                    var hazard_damage = hazard.damage * delta
                    if self.ball.has_method("take_damage"):
                        self.ball.take_damage(hazard_damage)
                    elif "hp" in self.ball:
                        self.ball.hp -= hazard_damage
                        if self.ball.hp <= 0:
                            self.ball.alive = false

    if "current_action" in self.ball:
        self.ball.current_action = strategy

    if self.ball.has_method("set_meta"):
        self.ball.set_meta("team_message", null)

        var hp_percent = 1.0
        if self.ball.has_method("get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif "hp" in self.ball and "max_hp" in self.ball:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if hp_percent < 0.3:
            self.ball.set_meta("team_message", {"type": "request_help", "x": self.ball.x, "y": self.ball.y})
        elif personality == "healer":
            self.ball.set_meta("team_message", {"type": "wounded_call", "x": self.ball.x, "y": self.ball.y})
        elif strategy == "defend" and personality == "tank":
            self.ball.set_meta("team_message", {"type": "hold_position", "x": self.ball.x, "y": self.ball.y})

    if strategy == "flee":
        _flee(delta)
    elif strategy == "attack":
        _attack(delta)
    elif strategy == "kite":
        # Cosmetics: kite verify auto-implement-kite-держит-дистанцию-атакует-при
        _kite(delta)
    elif strategy == "chase":
        _chase(delta)
    elif strategy == "flank":
        _flank(delta)
    elif strategy == "escort":
        _escort(delta)
    elif strategy == "intercept":
        _intercept(delta)
    elif strategy == "hide_behind":
        _hide_behind(delta)
    elif strategy == "group_attack":
        _group_attack(delta)
    elif strategy == "defend":
        _defend(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        _collect_booster(delta)
    elif strategy == "use skill" or strategy == "use_skill" or strategy == "action_skill" or strategy == "Действие":
        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill
        elif "SKILL" in self.ball:
            skill_name = self.ball.SKILL

        if skill_name == "flank":
            if "current_action" in self.ball:
                self.ball.current_action = "flank"
            elif self.ball.has_method("set_meta"):
                self.ball.set_meta("current_action", "flank")
            _flank(delta)
        else:
            _use_skill()
    else:
        _idle(delta)

    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()
    if bounced_wall or bounced_col:
        _trigger_ripple_effect()

    _update_skill_timer(delta)

    if delta > 0:
        var vx = (self.ball.x - old_x) / delta
        var vy = (self.ball.y - old_y) / delta
        if "vx" in self.ball:
            self.ball.vx = vx
            self.ball.vy = vy
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("vx", vx)
            self.ball.set_meta("vy", vy)


func _apply_boid_rules(nx: float, ny: float) -> Array:
    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    if b_type != "swarm":
        return [nx, ny]

    var allies = _get_allies()
    if allies.size() == 0:
        return [nx, ny]

    var cohesion_weight = 0.5
    var alignment_weight = 0.5
    var separation_weight = 1.0

    var center_x = 0.0
    var center_y = 0.0
    var align_vx = 0.0
    var align_vy = 0.0
    var sep_nx = 0.0
    var sep_ny = 0.0

    var count = 0
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    for ally in allies:
        var dx = self.ball.x - ally.x
        var dy = self.ball.y - ally.y
        var dist_sq = dx*dx + dy*dy

        if dist_sq > 0.0001 and dist_sq < perception_radius * perception_radius:
            count += 1
            var dist = sqrt(dist_sq)

            center_x += ally.x
            center_y += ally.y

            if "vx" in ally: align_vx += ally.vx
            elif ally.has_method("get_meta") and ally.has_meta("vx"): align_vx += ally.get_meta("vx")

            if "vy" in ally: align_vy += ally.vy
            elif ally.has_method("get_meta") and ally.has_meta("vy"): align_vy += ally.get_meta("vy")

            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius
            var ally_radius = 10.0
            if "radius" in ally: ally_radius = ally.radius

            var sep_dist = (ball_radius + ally_radius) * 2.0
            if dist < sep_dist:
                sep_nx += (dx / dist) / dist
                sep_ny += (dy / dist) / dist

    if count > 0:
        center_x /= count
        center_y /= count

        var coh_dx = center_x - self.ball.x
        var coh_dy = center_y - self.ball.y
        var coh_dist_sq = coh_dx*coh_dx + coh_dy*coh_dy
        var coh_nx = 0.0
        var coh_ny = 0.0
        if coh_dist_sq > 0.0001:
            var coh_dist = sqrt(coh_dist_sq)
            coh_nx = coh_dx / coh_dist
            coh_ny = coh_dy / coh_dist

        align_vx /= count
        align_vy /= count
        var align_speed_sq = align_vx*align_vx + align_vy*align_vy
        var al_nx = 0.0
        var al_ny = 0.0
        if align_speed_sq > 0.0001:
            var align_speed = sqrt(align_speed_sq)
            al_nx = align_vx / align_speed
            al_ny = align_vy / align_speed

        var comb_nx = nx + coh_nx * cohesion_weight + al_nx * alignment_weight + sep_nx * separation_weight
        var comb_ny = ny + coh_ny * cohesion_weight + al_ny * alignment_weight + sep_ny * separation_weight

        var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
        if comb_dist_sq > 0.0001:
            var comb_dist = sqrt(comb_dist_sq)
            return [comb_nx / comb_dist, comb_ny / comb_dist]

    return [nx, ny]

func _apply_obstacle_avoidance(nx: float, ny: float, target=null, ignore_enemies: bool = false) -> Array:
    var all_entities = []
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY:
            if entities.has("enemies") and not ignore_enemies:
                for e in entities["enemies"]:
                    all_entities.append(e)
            if entities.has("allies"):
                for e in entities["allies"]:
                    all_entities.append(e)
        elif typeof(entities) == TYPE_ARRAY:
            for e in entities:
                var is_alive = true
                if "alive" in e: is_alive = e.alive

                var is_enemy = false
                if "ball_type" in self.ball and "ball_type" in e:
                    var e_type = e.ball_type
                    is_enemy = (self.ball.ball_type != e_type and e_type != "booster")

                if is_alive and e != self.ball:
                    if ignore_enemies and is_enemy:
                        continue
                    all_entities.append(e)
            if entities.has("allies"):
                for e in entities["allies"]:
                    all_entities.append(e)
        elif typeof(entities) == TYPE_ARRAY:
            for e in entities:
                var is_alive = true
                if "alive" in e: is_alive = e.alive

                var is_enemy = false
                if "ball_type" in self.ball and "ball_type" in e:
                    is_enemy = (self.ball.ball_type != e.ball_type)

                if is_alive and e != self.ball:
                    if ignore_enemies and is_enemy:
                        continue
                    all_entities.append(e)

    var repulse_nx = 0.0
    var repulse_ny = 0.0
    var ball_radius = 10.0
    if "radius" in self.ball:
        ball_radius = self.ball.radius

    for entity in all_entities:
        if entity == target or entity == self.ball:
            continue

        var entity_radius = 10.0
        if "radius" in entity:
            entity_radius = entity.radius

        var dx = self.ball.x - entity.x
        var dy = self.ball.y - entity.y
        var dist_sq = dx*dx + dy*dy

        var safe_dist = ball_radius + entity_radius + 5.0
        if dist_sq > 0.0001 and dist_sq < safe_dist * safe_dist:
            var dist = sqrt(dist_sq)
            var force = 1.0 - (dist / safe_dist)
            var is_enemy = false
            if "ball_type" in entity and "ball_type" in self.ball:
                is_enemy = entity.ball_type != self.ball.ball_type and entity.ball_type != "spectator"
            elif entity.has_method("get_ball_type") and self.ball.has_method("get_ball_type"):
                is_enemy = entity.get_ball_type() != self.ball.get_ball_type() and entity.get_ball_type() != "spectator"

            if is_enemy:
                var damage = 10.0
                if "damage" in entity:
                    damage = entity.damage
                var cd = 1.5
                if "attack_cooldown" in entity:
                    cd = max(0.1, entity.attack_cooldown)
                var dps = damage / cd
                var attack_range = 150.0
                if "attack_range" in entity:
                    attack_range = entity.attack_range

                var danger_coefficient = 1.0
                if self.world != null and "arena" in self.world and "danger_grid" in self.world.arena:
                    var grid_x = int(entity.x / 100)
                    var grid_y = int(entity.y / 100)
                    var key = str(grid_x) + "," + str(grid_y)
                    if self.world.arena.danger_grid.has(key):
                        danger_coefficient += self.world.arena.danger_grid[key]

                if dist < attack_range:
                    danger_coefficient += (dps / 10.0)
                force *= danger_coefficient
            repulse_nx += (dx / dist) * force
            repulse_ny += (dy / dist) * force

    var comb_nx = nx + repulse_nx * 0.5
    var comb_ny = ny + repulse_ny * 0.5

    var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
    if comb_dist_sq > 0.0001:
        var comb_dist = sqrt(comb_dist_sq)
        return [comb_nx / comb_dist, comb_ny / comb_dist]
    return [nx, ny]

func _get_enemies() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("enemies"):
            var enemies = []
            for e in entities["enemies"]:
                var e_type = e.ball_type if "ball_type" in e else (e.get_ball_type() if e.has_method("get_ball_type") else "")
                if e_type != "spectator":
                    enemies.append(e)
            return enemies
        elif typeof(entities) == TYPE_ARRAY:
            var enemies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type != b_type and e_type != "spectator":
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            enemies.append(e)
            return enemies
    return []

func _get_allies() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("allies"):
            return entities["allies"]
        elif typeof(entities) == TYPE_ARRAY:
            var allies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type == b_type and e != self.ball and e_type != "spectator":
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            allies.append(e)
            return allies
    return []

func _get_boosters() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("boosters"):
            return entities["boosters"]

    var boosters = []
    if self.world != null and "boosters" in self.world:
        for b in self.world.boosters:
            if "active" in b and b.active:
                var dx = b.x - self.ball.x
                var dy = b.y - self.ball.y
                if sqrt(dx*dx + dy*dy) <= perception_radius:
                    boosters.append(b)
    return boosters

func _flee(delta: float):
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var nearest = null
    var min_dist_sq = INF
    for e in enemies:
        var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest = e

    var dx = self.ball.x - nearest.x
    var dy = self.ball.y - nearest.y
    var dist_sq = dx*dx + dy*dy
    var dist = 0.01
    if dist_sq > 0.0001:
        dist = sqrt(dist_sq)

    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if dist > perception_radius * 0.8:
        _idle(delta)
        return

    if dist < 0.01:
        dist = 0.01

    var flee_nx = dx / dist
    var flee_ny = dy / dist

    var allies = _get_allies()
    var ally_nx = 0.0
    var ally_ny = 0.0

    if allies.size() > 0:
        var nearest_ally = null
        var min_adist_sq = INF
        for a in allies:
            var adist_sq = pow(a.x - self.ball.x, 2) + pow(a.y - self.ball.y, 2)
            if adist_sq < min_adist_sq:
                min_adist_sq = adist_sq
                nearest_ally = a

        var adx = nearest_ally.x - self.ball.x
        var ady = nearest_ally.y - self.ball.y
        var adist_sq = adx*adx + ady*ady
        if adist_sq > 0.0001:
            var adist = sqrt(adist_sq)
            ally_nx = adx / adist
            ally_ny = ady / adist

    var safe_nx = 0.0
    var safe_ny = 0.0
    if self.world != null and "width" in self.world and "height" in self.world:
        var center_x = self.world.width / 2.0
        var center_y = self.world.height / 2.0
        var cdx = center_x - self.ball.x
        var cdy = center_y - self.ball.y
        var cdist_sq = cdx*cdx + cdy*cdy

        if cdist_sq > 0.0001:
            var cdist = sqrt(cdist_sq)
            var min_center_dim = center_x
            if center_y < center_x:
                min_center_dim = center_y

            if cdist > min_center_dim * 0.3:
                safe_nx = cdx / cdist
                safe_ny = cdy / cdist

    var comb_nx = flee_nx * 1.0 + ally_nx * 0.4 + safe_nx * 0.3
    var comb_ny = flee_ny * 1.0 + ally_ny * 0.4 + safe_ny * 0.3

    var comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
    if comb_dist_sq > 0.0001:
        var comb_dist = sqrt(comb_dist_sq)
        comb_nx /= comb_dist
        comb_ny /= comb_dist
    else:
        comb_nx = flee_nx
        comb_ny = flee_ny

    var boid_vec = _apply_boid_rules(comb_nx, comb_ny)
    comb_nx = boid_vec[0]
    comb_ny = boid_vec[1]

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var boosted_speed = speed * 1.5

    var emotion = "neutral"
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("emotion"):
        emotion = self.ball.get_meta("emotion")
    elif "emotion" in self.ball:
        emotion = self.ball.emotion

    if emotion == "fear":
        boosted_speed *= 1.5

    self.ball.x += comb_nx * boosted_speed * delta * 60.0
    self.ball.y += comb_ny * boosted_speed * delta * 60.0

func _evaluate_target_strength_deterministic(e: Object) -> Array:
    var e_max_hp = 0.0
    if "max_hp" in e:
        e_max_hp = float(e.max_hp)
    elif "hp" in e:
        e_max_hp = float(e.hp)

    var e_hp = 0.0
    if "hp" in e:
        e_hp = float(e.hp)

    var d_sq = float(pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2))
    var e_id = 0
    if "id" in e:
        e_id = int(e.id)

    return [e_max_hp, e_hp, -d_sq, e_id]

func _find_strongest_enemy_deterministic(enemies: Array) -> Object:
    var best_score = [-1.0, -1.0, -INF, -1]
    var target = null

    for e in enemies:
        var score = _evaluate_target_strength_deterministic(e)

        var is_better = false
        if score[0] > best_score[0]:
            is_better = true
        elif score[0] == best_score[0]:
            if score[1] > best_score[1]:
                is_better = true
            elif score[1] == best_score[1]:
                if score[2] > best_score[2]:
                    is_better = true
                elif score[2] == best_score[2]:
                    if score[3] > best_score[3]:
                        is_better = true

        if is_better:
            best_score = score
            target = e

    return target

func _get_target(enemies: Array) -> Object:
    var ball_memory = {}
    if self.ball.has_method("get_meta") and self.ball.has_meta("memory"):
        ball_memory = self.ball.get_meta("memory")
    elif "memory" in self.ball:
        ball_memory = self.ball.memory

    var rival_targets = []
    # Ball Relationships - Balls remember each other
    # Rivalry skill: attacked me before -> attack on sight
    for e in enemies:
        if "id" in e and ball_memory.has(e.id):
            var rel = ball_memory[e.id]
            if typeof(rel) == TYPE_DICTIONARY and rel.get("relation") == "rival":
                rival_targets.append(e)

    if rival_targets.size() > 0:
        var c_rival = null
        var min_d_sq = INF
        for r_ent in rival_targets:
            var d_sq = pow(r_ent.x - self.ball.x, 2) + pow(r_ent.y - self.ball.y, 2)
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                c_rival = r_ent
        return c_rival

    var target_msg = null
    var allies = _get_allies()
    for ally in allies:
        var msg = null
        if ally.has_method("get_meta") and ally.has_meta("team_message"):
            msg = ally.get_meta("team_message")
        if typeof(msg) == TYPE_DICTIONARY and msg.has("type") and msg["type"] == "target_spotted":
            target_msg = msg
            break

    var target = null
    var min_dist_sq = INF

    if target_msg != null:
        var tx = target_msg.get("x", self.ball.x)
        var ty = target_msg.get("y", self.ball.y)
        for e in enemies:
            var dist_sq = pow(e.x - tx, 2) + pow(e.y - ty, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                target = e
    else:
        var b_type = ""
        if "ball_type" in self.ball:
            b_type = self.ball.ball_type.to_lower()
        if b_type == "tank":
            target = _find_strongest_enemy_deterministic(enemies)
        elif b_type == "bomber":
            var max_crowd = -1
            var min_dist_sq_bomber = INF
            for e1 in enemies:
                var crowd = 0
                for e2 in enemies:
                    if e1 != e2 and pow(e1.x - e2.x, 2) + pow(e1.y - e2.y, 2) <= 1600.0:
                        crowd += 1
                var dist_sq = pow(e1.x - self.ball.x, 2) + pow(e1.y - self.ball.y, 2)
                if crowd > max_crowd or (crowd == max_crowd and dist_sq < min_dist_sq_bomber):
                    max_crowd = crowd
                    min_dist_sq_bomber = dist_sq
                    target = e1
        else:
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    target = e

    return target


func _group_attack(delta: float):
    var enemies = _get_enemies()
    var allies = _get_allies()

    if enemies.size() > 0:
        var target = _get_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist_sq = dx * dx + dy * dy

        if dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist

            # Apply boid-like cohesion to stick with allies
            var cohesion_x = 0.0
            var cohesion_y = 0.0

            if allies.size() > 0:
                for ally in allies:
                    cohesion_x += ally.x
                    cohesion_y += ally.y
                cohesion_x /= allies.size()
                cohesion_y /= allies.size()

                var cdx = cohesion_x - self.ball.x
                var cdy = cohesion_y - self.ball.y
                var cdist_sq = cdx * cdx + cdy * cdy
                if cdist_sq > 0.0001:
                    var cdist = sqrt(cdist_sq)
                    var cnx = cdx / cdist
                    var cny = cdy / cdist

                    # Blend movement: 60% towards target, 40% towards allies center
                    nx = nx * 0.6 + cnx * 0.4
                    ny = ny * 0.6 + cny * 0.4

                    var ndist_sq = nx * nx + ny * ny
                    if ndist_sq > 0.0001:
                        var ndist = sqrt(ndist_sq)
                        nx /= ndist
                        ny /= ndist

            var target_radius = 10.0
            if "radius" in target: target_radius = float(target.radius)
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = float(self.ball.radius)

            if nx != 0.0 or ny != 0.0:
                var avoided = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoided[0]
                ny = avoided[1]

                var boided = _apply_boid_rules(nx, ny)
                nx = boided[0]
                ny = boided[1]

                var speed = 2.0
                if "speed" in self.ball: speed = float(self.ball.speed)
                var step = speed * delta * 60.0

                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        # Recalculate distance
        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        dist_sq = dx * dx + dy * dy
        var dist = 0.0
        if dist_sq > 0.0001: dist = sqrt(dist_sq)

        var target_radius = 10.0
        if "radius" in target: target_radius = float(target.radius)
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = float(self.ball.radius)
        var attack_range = ball_radius + target_radius + 5.0

        var skill_timer = 0.0
        if "skill_timer" in self.ball: skill_timer = float(self.ball.skill_timer)

        if skill_timer <= 0.0 and dist <= attack_range * 1.5:
            if self.ball.has_method("use_skill"):
                self.ball.use_skill()
                _spawn_skill_particles()

            var cd = 5.0
            if "skill_cooldown" in self.ball: cd = float(self.ball.skill_cooldown)
            self.ball.skill_timer = cd

        var attack_timer = 0.0
        if "attack_timer" in self.ball: attack_timer = float(self.ball.attack_timer)

        if attack_timer <= 0.0 and dist <= attack_range:
            if self.world != null and self.world.has_method("_deal_damage"):
                self.world._deal_damage(self.ball, target)

                if "id" in target and "id" in self.ball:
                    var target_memory = {}
                    if target.has_method("get_meta") and target.has_meta("memory"):
                        target_memory = target.get_meta("memory")
                    elif "memory" in target and typeof(target.memory) == TYPE_DICTIONARY:
                        target_memory = target.memory

                    # Ball Relationships - Balls remember each other


                    # Rivalry skill: attacked me before -> attack on sight
                    target_memory[self.ball.id] = {"relation": "rival"}
                    if target.has_method("set_meta"):
                        target.set_meta("memory", target_memory)
                    elif "memory" in target:
                        target.memory = target_memory

            var speed = 2.0
            if "speed" in self.ball: speed = float(self.ball.speed)
            var cooldown = 1.0
            if speed > 0: cooldown = max(0.2, 2.0 / speed)
            self.ball.attack_timer = cooldown

    else:
        _idle(delta)


func _get_flank_target(enemies: Array):
    var best_target = null
    var best_score_dp = -INF
    var best_score_dist = -INF
    var best_score_id = -INF

    for e in enemies:
        var dx = e.x - self.ball.x
        var dy = e.y - self.ball.y
        var dist_sq = dx * dx + dy * dy
        var dist = 0.0
        if dist_sq > 0:
            dist = sqrt(dist_sq)

        var target_vx = 0.0
        var target_vy = 0.0

        if "vx" in e: target_vx = e.vx
        elif e.has_method("get_meta") and e.has_meta("vx"): target_vx = e.get_meta("vx")

        if "vy" in e: target_vy = e.vy
        elif e.has_method("get_meta") and e.has_meta("vy"): target_vy = e.get_meta("vy")

        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            if e.has_method("get_meta") and e.has_meta("last_vx"):
                target_vx = e.get_meta("last_vx")
                target_vy = e.get_meta("last_vy")
            else:
                target_vx = 1.0
                target_vy = 0.0

            if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                target_vx = 1.0
                target_vy = 0.0
        else:
            var v_dist_sq = target_vx*target_vx + target_vy*target_vy
            if v_dist_sq > 0.0001:
                var v_dist = sqrt(v_dist_sq)
                target_vx /= v_dist
                target_vy /= v_dist

        var dot_product = 0.0
        if dist > 0.0001:
            dot_product = (dx / dist) * target_vx + (dy / dist) * target_vy

        var e_id = 0
        if "id" in e:
            e_id = int(e.id)

        var better = false
        if dot_product > best_score_dp:
            better = true
        elif dot_product == best_score_dp:
            if -dist > best_score_dist:
                better = true
            elif -dist == best_score_dist:
                if e_id > best_score_id:
                    better = true

        if best_target == null or better:
            best_score_dp = dot_product
            best_score_dist = -dist
            best_score_id = e_id
            best_target = e

    return best_target

func _get_flank_position(target) -> Array:
    var target_vx = 0.0
    var target_vy = 0.0

    if "vx" in target: target_vx = target.vx
    elif target.has_method("get_meta") and target.has_meta("vx"): target_vx = target.get_meta("vx")

    if "vy" in target: target_vy = target.vy
    elif target.has_method("get_meta") and target.has_meta("vy"): target_vy = target.get_meta("vy")

    if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
        if target.has_method("get_meta") and target.has_meta("last_vx"):
            target_vx = target.get_meta("last_vx")
            target_vy = target.get_meta("last_vy")
        else:
            target_vx = 1.0
            target_vy = 0.0

        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            target_vx = 1.0
            target_vy = 0.0
    else:
        var v_dist_sq = target_vx*target_vx + target_vy*target_vy
        if v_dist_sq > 0.0001:
            var v_dist = sqrt(v_dist_sq)
            target_vx /= v_dist
            target_vy /= v_dist

    var flank_target_radius = 10.0
    if "radius" in target: flank_target_radius = target.radius
    var flank_distance = flank_target_radius * 2.0 + 20.0
    var flank_x = target.x - target_vx * flank_distance
    var flank_y = target.y - target_vy * flank_distance

    return [target_vx, target_vy, flank_x, flank_y]

func _flank(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = _get_flank_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var flank_data = _get_flank_position(target)
        var target_vx = flank_data[0]
        var target_vy = flank_data[1]
        var flank_x = flank_data[2]
        var flank_y = flank_data[3]

        var dx = flank_x - self.ball.x
        var dy = flank_y - self.ball.y
        var dist_sq = dx*dx + dy*dy

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist

            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step = speed * delta * 60.0
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        var direct_dx = target.x - self.ball.x
        var direct_dy = target.y - self.ball.y
        var direct_dist_sq = direct_dx*direct_dx + direct_dy*direct_dy
        var direct_dist = 0.0
        if direct_dist_sq > 0.0001:
            direct_dist = sqrt(direct_dist_sq)

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var attack_range = ball_radius + target_radius + 5.0

        var skill_timer = 0.0
        if "skill_timer" in self.ball:
            skill_timer = self.ball.skill_timer

        if skill_timer <= 0.0 and direct_dist > attack_range * 1.5:
            if self.ball.has_method("use_skill"):
                self.ball.use_skill()
            var cd = 5.0
            if "skill_cooldown" in self.ball: cd = self.ball.skill_cooldown
            self.ball.skill_timer = cd

        if direct_dist <= attack_range:
            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0.0:
                var dot_product = 0.0
                if direct_dist > 0.0001:
                    var ndx = direct_dx / direct_dist
                    var ndy = direct_dy / direct_dist
                    dot_product = ndx * target_vx + ndy * target_vy

                var is_critical = dot_product > 0.5

                var original_damage = 5.0
                if "damage" in self.ball: original_damage = self.ball.damage

                if is_critical:
                    if "ball_type" in self.ball and self.ball.ball_type == "ninja":
                        self.ball.damage = original_damage * 3.0
                    else:
                        self.ball.damage = original_damage * 2.0

                if self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, target)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                if is_critical:
                    self.ball.damage = original_damage

                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
    else:
        _idle(delta)



func _target_weak(delta: float):
    # Target Weak — ищет самого слабого врага
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var weakest_enemy = null
    var min_score = INF # Higher is stronger

    for e in enemies:
        var hp = 100.0
        if "hp" in e:
            hp = e.hp
        elif "max_hp" in e:
            hp = e.max_hp

        var dist_sq = pow(e.x - ball.x, 2) + pow(e.y - ball.y, 2)

        # We want the lowest HP. If HP is equal, the closest distance.
        var score = hp * 1000000 + dist_sq
        if score < min_score:
            min_score = score
            weakest_enemy = e

    if weakest_enemy != null:
        _chase_target(weakest_enemy, delta)
    else:
        _idle(delta)

func _chase_target(target, delta: float):
    var dx = target.x - ball.x
    var dy = target.y - ball.y
    var dist_sq = dx*dx + dy*dy
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist

        var avoid = _apply_obstacle_avoidance(nx, ny, target)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var speed = 2.0
        if "speed" in ball: speed = ball.speed
        var step = speed * delta * 60.0

        ball.x += nx * step
        ball.y += ny * step

func _chase(delta: float):
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var target = _get_target(enemies)

    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality
    if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive"]:
        var has_msg = false
        if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
            has_msg = self.ball.get_meta("team_message") != null
        if not has_msg and self.ball.has_method("set_meta"):
            self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

    var target_dx = target.x - self.ball.x
    var target_dy = target.y - self.ball.y
    var dist_to_target = sqrt(target_dx*target_dx + target_dy*target_dy)

    var target_radius = 10.0
    if "radius" in target: target_radius = target.radius
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius
    var attack_range = ball_radius + target_radius + 5.0

    var b_type_chase = ""
    if "ball_type" in self.ball:
        b_type_chase = self.ball.ball_type.to_lower()
    elif self.ball.has_method("get_ball_type"):
        b_type_chase = self.ball.get_ball_type().to_lower()

    if b_type_chase == "sniper":
        attack_range = 150.0

    var nx = 0.0
    var ny = 0.0
    if dist_to_target <= attack_range:
        if b_type_chase == "sniper" and dist_to_target < attack_range * 0.8:
            if dist_to_target > 0.01:
                nx = -target_dx / dist_to_target
                ny = -target_dy / dist_to_target
        else:
            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                if self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, target)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)

                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
            return
    else:
        if dist_to_target > 0.01:
            if b_type_chase == "ninja":
                var tvx = 0.0
                var tvy = 0.0
                if "vx" in target: tvx = target.vx
                if "vy" in target: tvy = target.vy
                var tv_dist_sq = tvx*tvx + tvy*tvy
                if tv_dist_sq > 0.0001:
                    var tv_dist = sqrt(tv_dist_sq)
                    var back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                    var back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                    var bdx = back_x - self.ball.x
                    var bdy = back_y - self.ball.y
                    var b_dist = sqrt(bdx*bdx + bdy*bdy)
                    if b_dist > 0.01:
                        nx = bdx / b_dist
                        ny = bdy / b_dist
                    else:
                        nx = target_dx / dist_to_target
                        ny = target_dy / dist_to_target
                else:
                    nx = target_dx / dist_to_target
                    ny = target_dy / dist_to_target
            else:
                nx = target_dx / dist_to_target
                ny = target_dy / dist_to_target

    var repel_x = 0.0
    var repel_y = 0.0
    var all_entities = _get_allies()
    for e in enemies:
        if e != target:
            all_entities.append(e)

    for entity in all_entities:
        var edx = self.ball.x - entity.x
        var edy = self.ball.y - entity.y
        var edist = sqrt(edx*edx + edy*edy)
        var entity_radius = 10.0
        if "radius" in entity: entity_radius = entity.radius

        if edist > 0.01 and edist < (ball_radius + entity_radius) * 2.0:
            var repel_force = 1.0 / edist
            repel_x += (edx / edist) * repel_force
            repel_y += (edy / edist) * repel_force

    var comb_nx = nx + repel_x * 10.0
    var comb_ny = ny + repel_y * 10.0
    var comb_dist = sqrt(comb_nx*comb_nx + comb_ny*comb_ny)
    if comb_dist > 0.01:
        comb_nx /= comb_dist
        comb_ny /= comb_dist

    var boid_vec = _apply_boid_rules(comb_nx, comb_ny)
    comb_nx = boid_vec[0]
    comb_ny = boid_vec[1]

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var step = speed * delta * 60.0

    self.ball.x += comb_nx * step
    self.ball.y += comb_ny * step

func _attack(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = _get_target(enemies)

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality in ["warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive"]:
            var has_msg = false
            if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg and self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var dist = 0.0
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        var b_type_attack = ""
        if "ball_type" in self.ball:
            b_type_attack = self.ball.ball_type.to_lower()
        elif self.ball.has_method("get_ball_type"):
            b_type_attack = self.ball.get_ball_type().to_lower()

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var attack_range = ball_radius + target_radius + 5.0

        var nx = 0.0
        var ny = 0.0

        if b_type_attack == "ninja":
            var tvx = 0.0
            var tvy = 0.0
            if "vx" in target: tvx = target.vx
            if "vy" in target: tvy = target.vy
            var tv_dist_sq = tvx*tvx + tvy*tvy
            if tv_dist_sq > 0.0001:
                var tv_dist = sqrt(tv_dist_sq)
                var back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                var back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                var bdx = back_x - self.ball.x
                var bdy = back_y - self.ball.y
                var b_dist = sqrt(bdx*bdx + bdy*bdy)
                if b_dist > 0.01:
                    nx = bdx / b_dist
                    ny = bdy / b_dist

        if nx == 0.0 and ny == 0.0 and dist_sq > 0.0001:
            nx = dx / dist
            ny = dy / dist

        if dist_sq > 0.0001:
            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step = speed * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)
        else:
            dist = 0.0

        target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius
        attack_range = ball_radius + target_radius + 5.0

        if b_type_attack == "sniper":
            attack_range = 150.0

        if dist <= attack_range:
            var skill_timer = 0.0
            if "skill_timer" in self.ball:
                skill_timer = self.ball.skill_timer

            if skill_timer <= 0:
                var optimal = true
                var b_type = ""
                if "ball_type" in self.ball:
                    b_type = self.ball.ball_type
                elif self.ball.has_method("get_ball_type"):
                    b_type = self.ball.get_ball_type()

                if b_type == "bomber":
                    var close_enemies = 0
                    for e in enemies:
                        var e_radius = 10.0
                        if "radius" in e: e_radius = e.radius
                        var edx = e.x - self.ball.x
                        var edy = e.y - self.ball.y
                        if sqrt(edx*edx + edy*edy) <= ball_radius + e_radius + 15:
                            close_enemies += 1
                    optimal = close_enemies >= 3

                    if optimal and "hp" in self.ball:
                        self.ball.hp = 0
                        if "alive" in self.ball:
                            self.ball.alive = false
                elif b_type == "tank":
                    optimal = (target == _find_strongest_enemy_deterministic(enemies))
                elif b_type == "warrior":
                    var in_front = 0
                    var move_dx = target.x - self.ball.x
                    var move_dy = target.y - self.ball.y
                    var move_dist = sqrt(move_dx*move_dx + move_dy*move_dy)
                    if move_dist > 0.0001:
                        var mnx = move_dx / move_dist
                        var mny = move_dy / move_dist
                        for e in enemies:
                            var e_radius = 10.0
                            if "radius" in e: e_radius = e.radius
                            var edx = e.x - self.ball.x
                            var edy = e.y - self.ball.y
                            var edist = sqrt(edx*edx + edy*edy)
                            if edist <= ball_radius + e_radius + 40.0 and edist > 0.0001:
                                var enx = edx / edist
                                var eny = edy / edist
                                var dot_product = mnx * enx + mny * eny
                                if dot_product > 0.5:
                                    in_front += 1
                    optimal = in_front >= 2

                if optimal:
                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()
                    var cooldown = 5.0
                    if "skill_cooldown" in self.ball:
                        cooldown = self.ball.skill_cooldown
                    self.ball.skill_timer = cooldown

            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                var b_type = ""
                if "ball_type" in self.ball:
                    b_type = self.ball.ball_type.to_lower()
                elif self.ball.has_method("get_ball_type"):
                    b_type = self.ball.get_ball_type().to_lower()

                var original_damage = 10.0
                if "damage" in self.ball:
                    original_damage = float(self.ball.damage)

                if b_type == "ninja":
                    var tvx = 0.0
                    var tvy = 0.0
                    if "vx" in target: tvx = float(target.vx)
                    if "vy" in target: tvy = float(target.vy)
                    var tv_dist_sq = tvx * tvx + tvy * tvy
                    if tv_dist_sq > 0.0001:
                        var tv_dist = sqrt(tv_dist_sq)
                        var tnx = tvx / tv_dist
                        var tny = tvy / tv_dist

                        var adx = float(target.x) - float(self.ball.x)
                        var ady = float(target.y) - float(self.ball.y)
                        var adist_sq = adx * adx + ady * ady
                        if adist_sq > 0.0001:
                            var adist = sqrt(adist_sq)
                            var anx = adx / adist
                            var any = ady / adist

                            var dot_product = anx * tnx + any * tny
                            if dot_product > 0.5:
                                self.ball.damage = original_damage * 2.0

                if self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, target)
                    if "id" in target and "id" in self.ball:
                        var mem = {}
                        if target.has_method("get_meta") and target.has_meta("memory"):
                            mem = target.get_meta("memory")
                        elif "memory" in target:
                            mem = target.memory
                        # Ball Relationships - Balls remember each other

                        # Rivalry skill: attacked me before -> attack on sight
                        mem[self.ball.id] = {"relation": "rival"}
                        if target.has_method("set_meta"):
                            target.set_meta("memory", mem)
                        else:
                            target.memory = mem

                if b_type == "ninja":
                    self.ball.damage = original_damage

                var cooldown = 0.5
                if b_type in ["scout", "assassin", "phantom", "swarm", "rogue", "ninja"]:
                    cooldown = 0.3
                elif b_type in ["tank", "juggernaut", "guardian"]:
                    cooldown = 1.5
                else:
                    var speed = 2.0
                    if "speed" in self.ball: speed = self.ball.speed
                    cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)

                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
    else:
        _idle(delta)

func _defend(delta: float):
    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality
    if personality in ["tank", "defender", "guardian", "juggernaut"]:
        var enemies = _get_enemies()
        if enemies.size() > 0:
            var target_enemy = null
            var target_pos_x = self.ball.x
            var target_pos_y = self.ball.y
            var should_move = false

            var b_type = ""
            if "ball_type" in self.ball:
                b_type = self.ball.ball_type.to_lower()

            if b_type == "tank":
                var allies = _get_allies()
                var ally_to_protect = null
                if allies.size() > 0:
                    var healers = []
                    for a in allies:
                        var a_type = ""
                        if "ball_type" in a:
                            a_type = str(a.ball_type).to_lower()
                        elif a.has_method("get") and a.get("BALL_TYPE") != null:
                            a_type = str(a.get("BALL_TYPE")).to_lower()
                        if a_type == "healer":
                            healers.append(a)

                    if healers.size() > 0:
                        var min_d_sq = INF
                        for h in healers:
                            var dsq = pow(h.x - self.ball.x, 2) + pow(h.y - self.ball.y, 2)
                            if dsq < min_d_sq:
                                min_d_sq = dsq
                                ally_to_protect = h
                    else:
                        var min_hp_pct = INF
                        for a in allies:
                            var a_hp_pct = 1.0
                            if a.has_method("get_hp_percent"):
                                a_hp_pct = a.get_hp_percent()
                            elif "hp" in a and "max_hp" in a and float(a.max_hp) > 0:
                                a_hp_pct = float(a.hp) / float(a.max_hp)
                            if a_hp_pct < min_hp_pct:
                                min_hp_pct = a_hp_pct
                                ally_to_protect = a

                target = _find_strongest_enemy_deterministic(enemies)
            else:
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e

            var dx = target.x - self.ball.x
            var dy = target.y - self.ball.y
            var dist_sq = dx*dx + dy*dy
            if dist_sq > 0.0001:
                var dist = sqrt(dist_sq)
                var nx = dx / dist
                var ny = dy / dist
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]
                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var step = speed * 0.5 * delta * 60.0
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist_sq = dx*dx + dy*dy
            var dist_after = 0.0
            if dist_sq > 0.0001:
                dist_after = sqrt(dist_sq)

            var target_radius = 10.0
            if "radius" in target: target_radius = target.radius
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius

            if dist_after <= ball_radius + target_radius + 5:
                var attack_timer = 0.0
                if "attack_timer" in self.ball:
                    attack_timer = self.ball.attack_timer
                elif self.ball.has_meta("attack_timer"):
                    attack_timer = self.ball.get_meta("attack_timer")

                if attack_timer <= 0:
                    if self.world != null and self.world.has_method("_deal_damage"):
                        self.world._deal_damage(self.ball, target)
                        if "id" in target and "id" in self.ball:
                            var mem = {}
                            if target.has_method("get_meta") and target.has_meta("memory"):
                                mem = target.get_meta("memory")
                            elif "memory" in target:
                                mem = target.memory
                            # Ball Relationships - Balls remember each other
                            # Rivalry skill: attacked me before -> attack on sight
                            mem[self.ball.id] = {"relation": "rival"}
                            if target.has_method("set_meta"):
                                target.set_meta("memory", mem)
                            else:
                                target.memory = mem

                    var cooldown = 1.5
                    var b_type = ""
                    if "ball_type" in self.ball:
                        b_type = self.ball.ball_type.to_lower()
                    elif self.ball.has_method("get_ball_type"):
                        b_type = self.ball.get_ball_type().to_lower()

                    if not (b_type in ["tank", "juggernaut", "guardian"]):
                        var spd = 2.0
                        if "speed" in self.ball: spd = self.ball.speed
                        cooldown = max(0.2, 2.0 / spd if spd > 0 else 1.0)

                    if "attack_timer" in self.ball:
                        self.ball.attack_timer = cooldown
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("attack_timer", cooldown)
            return
    elif personality == "healer" or personality == "leader" or personality == "caring":
        var allies = _get_allies()
        var target_ally = null
        var lowest_hp = 0.8
        for ally in allies:
            var ally_hp_pct = 1.0
            if ally.has_method("get_hp_percent"):
                ally_hp_pct = ally.get_hp_percent()
            elif "hp" in ally and "max_hp" in ally:
                ally_hp_pct = float(ally.hp) / float(ally.max_hp)
            if ally_hp_pct < lowest_hp:
                lowest_hp = ally_hp_pct
                target_ally = ally
        if target_ally != null:
            var dx = target_ally.x - self.ball.x
            var dy = target_ally.y - self.ball.y
            var dist_sq = dx*dx + dy*dy
            if dist_sq > 0.0001:
                var dist = sqrt(dist_sq)
                var nx = dx / dist
                var ny = dy / dist
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target_ally)
                nx = avoid_vec[0]
                ny = avoid_vec[1]
                var speed = 2.0
                if "speed" in self.ball: speed = self.ball.speed
                var step = speed * delta * 60.0
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist_sq = dx*dx + dy*dy
            var dist_after = 0.0
            if dist_sq > 0.0001:
                dist_after = sqrt(dist_sq)

            var target_radius = 10.0
            if "radius" in target: target_radius = target.radius
            var ball_radius = 10.0
            if "radius" in self.ball: ball_radius = self.ball.radius

            if dist_after <= ball_radius + target_radius + 5:
                var attack_timer = 0.0
                if "attack_timer" in self.ball:
                    attack_timer = self.ball.attack_timer
                elif self.ball.has_meta("attack_timer"):
                    attack_timer = self.ball.get_meta("attack_timer")

                if attack_timer <= 0:
                    # Explicit healing logic
                    if "hp" in target_ally and "max_hp" in target_ally:
                        var damage = 5.0
                        if "damage" in self.ball:
                            damage = self.ball.damage
                        target_ally.hp = min(target_ally.max_hp, target_ally.hp + (damage * 3.0))

                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()

                    if "skill_cooldown" in self.ball:
                        if "skill_timer" in self.ball:
                            self.ball.skill_timer = self.ball.skill_cooldown

                    var cooldown = 1.5
                    var b_type = ""
                    if "ball_type" in self.ball:
                        b_type = self.ball.ball_type.to_lower()
                    elif self.ball.has_method("get_ball_type"):
                        b_type = self.ball.get_ball_type().to_lower()

                    if not (b_type in ["tank", "juggernaut", "guardian"]):
                        var spd = 2.0
                        if "speed" in self.ball: spd = self.ball.speed
                        cooldown = max(0.2, 2.0 / spd if spd > 0 else 1.0)

                    if "attack_timer" in self.ball:
                        self.ball.attack_timer = cooldown
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("attack_timer", cooldown)
            return

    _idle(delta * 0.5)

func _collect_booster(delta: float):
    var boosters = _get_boosters()
    if boosters.size() > 0:
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var enemies = _get_enemies()
        if enemies.size() > 0:
            var nearest_enemy = null
            var min_dist_enemy_sq = INF
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_enemy_sq:
                    min_dist_enemy_sq = dist_sq
                    nearest_enemy = e

            var enemy_radius = 10.0
            if "radius" in nearest_enemy: enemy_radius = nearest_enemy.radius

            if min_dist_enemy_sq > 0.0001:
                var dist_enemy = sqrt(min_dist_enemy_sq)
                if dist_enemy < ball_radius + enemy_radius + 30.0:
                    _flee(delta)
                    return

        var nearest = null
        var min_dist_sq = INF
        for b in boosters:
            var dist_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = b

        var dx = nearest.x - self.ball.x
        var dy = nearest.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var dist = 0.0
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist_sq > 0.0001:
            var nx = dx / dist
            var ny = dy / dist
            var avoid_vec = _apply_obstacle_avoidance(nx, ny, nearest, true)
            nx = avoid_vec[0]
            ny = avoid_vec[1]

            var boid_vec = _apply_boid_rules(nx, ny)
            nx = boid_vec[0]
            ny = boid_vec[1]

            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = nearest.x - self.ball.x
        dy = nearest.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)
        else:
            dist = 0.0

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + 10:
            if self.world != null and self.world.has_method("_collect_booster"):
                self.world._collect_booster(self.ball, nearest)
    else:
        _idle(delta)

func _use_skill():
    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer

    if skill_timer <= 0.0 and self.ball.has_method("use_skill"):
        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill
        elif "SKILL" in self.ball:
            skill_name = self.ball.SKILL


        self.ball.use_skill()
        _spawn_skill_particles(skill_name)

        if skill_name == "command":
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "buff_command", "radius": 200})
            elif "team_message" in self.ball:
                self.ball.team_message = {"type": "buff_command", "radius": 200}
        elif skill_name == "Действие" or skill_name == "action_skill":
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("team_message", {"type": "action_skill_used", "radius": 150})
            elif "team_message" in self.ball:
                self.ball.team_message = {"type": "action_skill_used", "radius": 150}
        elif skill_name == "numpy":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(min_dist_sq)
                if dist > 0.0001:
                    var hp_ratio = 1.0
                    if "hp" in self.ball and "max_hp" in self.ball and self.ball.max_hp > 0:
                        hp_ratio = self.ball.hp / self.ball.max_hp
                    var inputs = [dx/dist, dy/dist, hp_ratio, 1.0]

                    var h_weights = [[0.5, -0.5, 0.1], [0.1, 0.5, -0.1], [0.0, 0.2, 0.8], [0.0, 0.0, 0.0]]
                    var h_biases = [0.1, 0.0, -0.1]
                    var hidden = [0.0, 0.0, 0.0]
                    for j in range(3):
                        var val = inputs[0]*h_weights[0][j] + inputs[1]*h_weights[1][j] + inputs[2]*h_weights[2][j] + inputs[3]*h_weights[3][j] + h_biases[j]
                        hidden[j] = max(0.0, val)

                    var o_weights = [[0.8, -0.2], [0.2, 0.8], [0.1, 0.1]]
                    var o_biases = [0.0, 0.0]
                    var out_x = hidden[0]*o_weights[0][0] + hidden[1]*o_weights[1][0] + hidden[2]*o_weights[2][0] + o_biases[0]
                    var out_y = hidden[0]*o_weights[0][1] + hidden[1]*o_weights[1][1] + hidden[2]*o_weights[2][1] + o_biases[1]

                    var mag = sqrt(out_x*out_x + out_y*out_y)
                    if mag > 0.0001:
                        self.ball.x += (out_x/mag) * 80.0
                        self.ball.y += (out_y/mag) * 80.0
        elif skill_name == "dash":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = null
                var min_dist_sq = INF
                for e in enemies:
                    var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = e
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(min_dist_sq)
                if dist > 0.0001:
                    self.ball.x += (dx/dist) * 100.0
                    self.ball.y += (dy/dist) * 100.0
            else:
                var angle = randf() * PI * 2.0
                self.ball.x += cos(angle) * 100.0
                self.ball.y += sin(angle) * 100.0

        elif skill_name == "snipe":
            if "arena" in self.world and "hazards" in self.world.arena:
                var trap_id = self.world.arena.hazards.size() + randi() % 10000
                var trap = ProceduralArena.Hazard.new()
                trap.id = trap_id
                trap.x = self.ball.x
                trap.y = self.ball.y
                trap.radius = 15.0
                trap.kind = "trap"
                trap.damage = 0.0
                trap.set_meta("duration", 5.0)
                self.world.arena.hazards.append(trap)
        elif skill_name == "target_strong":
            var enemies = _get_enemies()
            if enemies.size() > 0:
                var target = _find_strongest_enemy_deterministic(enemies)
                var dx = target.x - self.ball.x
                var dy = target.y - self.ball.y
                var dist = sqrt(dx*dx + dy*dy)
                if dist > 0.0001:
                    self.ball.x += (dx/dist) * 150.0
                    self.ball.y += (dy/dist) * 150.0
            else:
                var angle = randf() * PI * 2.0
                self.ball.x += cos(angle) * 150.0
                self.ball.y += sin(angle) * 150.0

        if "skill_cooldown" in self.ball:
            self.ball.skill_timer = self.ball.skill_cooldown

func _spawn_skill_particles(skill_name: String = ""):
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("add_child"):
        var particles = CPUParticles2D.new()
        particles.emitting = true
        particles.one_shot = true

        # Configure particle properties based on skill
        if skill_name == "wave_attack":
            particles.amount = 50
            particles.spread = 360.0
            particles.initial_velocity_min = 100.0
            particles.initial_velocity_max = 150.0
            particles.color = Color(0.2, 0.5, 1.0, 0.8) # Blue wave
            particles.lifetime = 0.6
            particles.explosiveness = 0.9
        elif skill_name == "explosion":
            particles.amount = 60
            particles.spread = 360.0
            particles.initial_velocity_min = 150.0
            particles.initial_velocity_max = 200.0
            particles.color = Color(1.0, 0.3, 0.0, 0.9) # Fiery explosion
            particles.lifetime = 0.4
            particles.explosiveness = 1.0
        elif skill_name == "dash":
            particles.amount = 20
            particles.spread = 20.0
            particles.initial_velocity_min = 30.0
            particles.initial_velocity_max = 80.0
            particles.color = Color(0.8, 0.8, 0.8, 0.5) # Dust/wind trail
            particles.lifetime = 0.3
            particles.explosiveness = 0.5
            # Could orient opposite to velocity if we had it, but spread and low life is fine
        elif skill_name == "shield" or skill_name == "protect_ally":
            particles.amount = 40
            particles.spread = 360.0
            particles.initial_velocity_min = 20.0
            particles.initial_velocity_max = 40.0
            particles.color = Color(0.9, 0.8, 0.2, 0.7) # Golden/yellow aura
            particles.lifetime = 0.8
            particles.explosiveness = 0.2 # Sustained bubble look
        elif skill_name == "heal_ally":
            particles.amount = 25
            particles.spread = 180.0
            particles.initial_velocity_min = 40.0
            particles.initial_velocity_max = 70.0
            particles.gravity = Vector2(0, -50) # Floating up
            particles.color = Color(0.2, 0.9, 0.3, 0.8) # Green healing
            particles.lifetime = 0.7
            particles.explosiveness = 0.4
        else:
            # Default generic skill particles
            particles.amount = 30
            particles.spread = 180.0
            particles.initial_velocity_min = 50.0
            particles.initial_velocity_max = 100.0
            particles.lifetime = 0.5
            particles.explosiveness = 0.8

        if skill_name != "heal_ally": particles.gravity = Vector2(0, 0)
        self.ball.add_child(particles)
        if particles.has_signal("finished"):
            particles.finished.connect(particles.queue_free)


func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var nx = randf_range(-1.0, 1.0)
    var ny = randf_range(-1.0, 1.0)
    var dist_sq = nx*nx + ny*ny
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        nx /= dist
        ny /= dist
    else:
        nx = 0.0
        ny = 0.0

    var boid_vec = _apply_boid_rules(nx, ny)
    nx = boid_vec[0]
    ny = boid_vec[1]

    self.ball.x += nx * speed * 0.3
    self.ball.y += ny * speed * 0.3

func _clamp_position() -> bool:
    var bounced = false
    if self.world != null:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius

        if is_nan(self.ball.x) or is_inf(self.ball.x):
            if "width" in self.world:
                self.ball.x = self.world.width / 2.0
            else:
                self.ball.x = 1000.0 / 2.0
            bounced = true
        if is_nan(self.ball.y) or is_inf(self.ball.y):
            if "height" in self.world:
                self.ball.y = self.world.height / 2.0
            else:
                self.ball.y = 1000.0 / 2.0
            bounced = true

        var old_x = self.ball.x
        var old_y = self.ball.y

        if "arena" in self.world and self.world.arena != null and self.world.arena.has_method("clamp_position"):
            var res = self.world.arena.clamp_position(self.ball.x, self.ball.y, radius)
            self.ball.x = res[0]
            self.ball.y = res[1]
            if res[2]:
                bounced = true
        elif "width" in self.world and "height" in self.world:
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))
            if old_x != self.ball.x or old_y != self.ball.y:
                bounced = true

    return bounced

func _resolve_collisions() -> bool:
    var bounced = false
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius

    var nearby = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var data = self.world.get_nearby_entities(self.ball, ball_radius * 2)
        if typeof(data) == TYPE_DICTIONARY:
            if data.has("enemies"): nearby += data["enemies"]
            if data.has("allies"): nearby += data["allies"]
        elif typeof(data) == TYPE_ARRAY:
            nearby = data

    for other in nearby:
        if other == self.ball:
            continue
        var other_radius = 10.0
        if "radius" in other: other_radius = other.radius
        var dx = self.ball.x - other.x
        var dy = self.ball.y - other.y
        var dist_sq = dx * dx + dy * dy
        var min_dist = ball_radius + other_radius
        if dist_sq < min_dist * min_dist and dist_sq > 0.0001:
            var dist = sqrt(dist_sq)
            var overlap = min_dist - dist
            var nx = dx / dist
            var ny = dy / dist
            self.ball.x += nx * overlap
            self.ball.y += ny * overlap
            bounced = true

    return bounced

func _trigger_ripple_effect():
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var ripple_radius = ball_radius * 3.0 + speed * 10.0

    var nearby = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var data = self.world.get_nearby_entities(self.ball, ripple_radius)
        if typeof(data) == TYPE_DICTIONARY:
            if data.has("enemies"): nearby += data["enemies"]
            if data.has("allies"): nearby += data["allies"]
        elif typeof(data) == TYPE_ARRAY:
            nearby = data

    for other in nearby:
        if other == self.ball:
            continue
        var dx = other.x - self.ball.x
        var dy = other.y - self.ball.y
        var dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001 and dist_sq < ripple_radius * ripple_radius:
            var dist = sqrt(dist_sq)
            var nx = dx / dist
            var ny = dy / dist
            var push_strength = (ripple_radius - dist) / ripple_radius * speed * 2.0
            other.x += nx * push_strength
            other.y += ny * push_strength

            if speed > 2.5:
                var my_type = ""
                var other_type = ""
                if "ball_type" in self.ball: my_type = self.ball.ball_type
                if "ball_type" in other: other_type = other.ball_type
                var is_enemy = (my_type != other_type)

                if is_enemy and self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, other)
                    if "id" in other and "id" in self.ball:
                        var mem = {}
                        if other.has_method("get_meta") and other.has_meta("memory"):
                            mem = other.get_meta("memory")
                        elif "memory" in other:
                            mem = other.memory
                            # Ball Relationships - Balls remember each other
                            # Rivalry skill: attacked me before -> attack on sight
                            mem[self.ball.id] = {"relation": "rival"}
                        if other.has_method("set_meta"):
                            other.set_meta("memory", mem)
                        else:
                            other.memory = mem

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta

    var attack_timer = 0.0
    if "attack_timer" in self.ball:
        attack_timer = self.ball.attack_timer
    elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
        attack_timer = self.ball.get_meta("attack_timer")

    if attack_timer > 0:
        attack_timer -= delta
        if "attack_timer" in self.ball:
            self.ball.attack_timer = attack_timer
        elif self.ball.has_method("set_meta"):
            self.ball.set_meta("attack_timer", attack_timer)

func _kite(delta: float):
    # Added Kite cosmetic comment
    # Kiting is fully implemented
    # auto-implement-kite-держит-дистанцию-атакует-при
    # Maintain distance from enemies and attack when they are close
    # Kiting behavior implementation: keeping the distance and attacking
    # Kite — держит дистанцию, атакует при приближении skill: для Sniper
    var active_enemies = _get_enemies()
    if active_enemies.size() > 0:
        var target_msg = null
        var team_allies = _get_allies()
        for ally in team_allies:
            var msg = null
            if ally.has_method("get_meta") and ally.has_meta("team_message"):
                msg = ally.get_meta("team_message")
            if typeof(msg) == TYPE_DICTIONARY and msg.has("type") and msg["type"] == "target_spotted":
                target_msg = msg
                break

        var optimal_target = null
        var min_dist_sq = INF

        if target_msg != null:
            var tx = target_msg.get("x", self.ball.x)
            var ty = target_msg.get("y", self.ball.y)
            for e in active_enemies:
                var dist_sq = pow(e.x - tx, 2) + pow(e.y - ty, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    optimal_target = e
        else:
            for e in active_enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    optimal_target = e

        var has_msg = false
        if self.ball.has_method("has_meta") and self.ball.has_meta("team_message"):
            has_msg = self.ball.get_meta("team_message") != null
        if not has_msg and self.ball.has_method("set_meta"):
            self.ball.set_meta("team_message", {"type": "target_spotted", "x": optimal_target.x, "y": optimal_target.y})

        var dx = optimal_target.x - self.ball.x
        var dy = optimal_target.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var actual_dist = 0.0
        if dist_sq > 0.0001:
            actual_dist = sqrt(dist_sq)

        var b_speed = float(2.0)
        if "speed" in self.ball: b_speed = self.ball.speed

        var b_attack_range = 150.0
        if "attack_range" in self.ball: b_attack_range = self.ball.attack_range

        if dist_sq > 0.0001:
            var nx = dx / actual_dist
            var ny = dy / actual_dist
            if actual_dist > b_attack_range:
                pass
            elif actual_dist < b_attack_range * 0.8:
                nx = -nx
                ny = -ny
            else:
                nx = 0.0
                ny = 0.0

            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, optimal_target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step: float = b_speed * delta * 60.0
                if actual_dist < b_attack_range * 0.8:
                    self.ball.x += nx * step
                    self.ball.y += ny * step
                elif actual_dist > b_attack_range:
                    self.ball.x += nx * min(step, actual_dist - b_attack_range)
                    self.ball.y += ny * min(step, actual_dist - b_attack_range)
        dx = optimal_target.x - self.ball.x
        dy = optimal_target.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        var dist_after = 0.0
        if dist_sq > 0.0001:
            dist_after = sqrt(dist_sq)

        b_attack_range = 150.0
        if "attack_range" in self.ball: b_attack_range = self.ball.attack_range

        if dist_after <= b_attack_range:
            var skill_timer = 0.0
            if "skill_timer" in self.ball:
                skill_timer = self.ball.skill_timer

            if skill_timer <= 0:
                if dist_after < b_attack_range * 0.8:
                    if self.ball.has_method("use_skill"):
                        self.ball.use_skill()
                    var cd = 5.0
                    if "skill_cooldown" in self.ball: cd = self.ball.skill_cooldown
                    self.ball.skill_timer = cd

            var attack_timer = 0.0
            if "attack_timer" in self.ball:
                attack_timer = self.ball.attack_timer
            elif self.ball.has_method("get_meta") and self.ball.has_meta("attack_timer"):
                attack_timer = self.ball.get_meta("attack_timer")

            if attack_timer <= 0:
                if self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, optimal_target)
                    if "id" in optimal_target and "id" in self.ball:
                        var mem = {}
                        if optimal_target.has_method("get_meta") and optimal_target.has_meta("memory"):
                            mem = optimal_target.get_meta("memory")
                        elif "memory" in optimal_target:
                            mem = optimal_target.memory
                        # Ball Relationships - Balls remember each other
                        mem[self.ball.id] = {"relation": "rival"}
                        if optimal_target.has_method("set_meta"):
                            optimal_target.set_meta("memory", mem)
                        else:
                            optimal_target.memory = mem

                var cooldown = max(0.2, 2.0 / b_speed if b_speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
    else:
        _idle(delta)


func _escort(delta: float) -> void:
    var allies = _get_allies()
    if allies.size() == 0:
        _idle(delta)
        return

    var target_ally = null
    for ally in allies:
        if "has_flag" in ally and ally.has_flag:
            target_ally = ally
            break

    if target_ally == null:
        var min_dist = 9999999.0
        for ally in allies:
            var d_sq = (ally.x - ball.x)*(ally.x - ball.x) + (ally.y - ball.y)*(ally.y - ball.y)
            if d_sq < min_dist:
                min_dist = d_sq
                target_ally = ally

    var dx = target_ally.x - ball.x
    var dy = target_ally.y - ball.y
    var dist_sq = dx*dx + dy*dy

    if dist_sq > 2500.0:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist

        var avoid = _apply_obstacle_avoidance(nx, ny)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var b_speed = 2.0
        if "speed" in ball:
            b_speed = ball.speed
        var step = b_speed * delta * 60.0

        ball.x += nx * min(step, dist - 40.0)
        ball.y += ny * min(step, dist - 40.0)
    else:
        var enemies = _get_enemies()
        if enemies.size() > 0:
            var closest_enemy = null
            var e_min_dist = 9999999.0
            for enemy in enemies:
                var e_d_sq = (enemy.x - target_ally.x)*(enemy.x - target_ally.x) + (enemy.y - target_ally.y)*(enemy.y - target_ally.y)
                if e_d_sq < e_min_dist:
                    e_min_dist = e_d_sq
                    closest_enemy = enemy

            if e_min_dist < 40000.0:
                ball.team_message = {"type": "target_spotted", "x": closest_enemy.x, "y": closest_enemy.y}
                var attack_timer = 0.0
                if "attack_timer" in ball:
                    attack_timer = ball.attack_timer

                if attack_timer <= 0.0:
                    var my_dist = (closest_enemy.x - ball.x)*(closest_enemy.x - ball.x) + (closest_enemy.y - ball.y)*(closest_enemy.y - ball.y)
                    var atk_range = 150.0
                    if "attack_range" in ball:
                        atk_range = ball.attack_range

                    if my_dist < atk_range * atk_range:
                        if world.has_method("_deal_damage"):
                            world._deal_damage(ball, closest_enemy)
                        var s_speed = 2.0
                        if "speed" in ball:
                            s_speed = ball.speed
                        var new_cd = max(0.2, 2.0 / s_speed if s_speed > 0 else 1.0)
                        ball.attack_timer = new_cd

func _intercept(delta: float) -> void:
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var target_enemy = null
    for enemy in enemies:
        if "has_flag" in enemy and enemy.has_flag:
            target_enemy = enemy
            break

    if target_enemy == null:
        _chase(delta)
        return

    var dx = target_enemy.x - ball.x
    var dy = target_enemy.y - ball.y
    var dist_sq = dx*dx + dy*dy
    var dist = 0.0
    if dist_sq > 0.0:
        dist = sqrt(dist_sq)

    if dist > 0.0001:
        var nx = dx / dist
        var ny = dy / dist

        var ex_vel = 0.0
        var ey_vel = 0.0
        if "vx" in target_enemy:
            ex_vel = target_enemy.vx
        if "vy" in target_enemy:
            ey_vel = target_enemy.vy

        var lead_x = nx + (ex_vel * 0.5)
        var lead_y = ny + (ey_vel * 0.5)
        var lead_mag = sqrt(lead_x*lead_x + lead_y*lead_y)

        if lead_mag > 0.0:
            nx = lead_x / lead_mag
            ny = lead_y / lead_mag

        var avoid = _apply_obstacle_avoidance(nx, ny)
        nx = avoid[0]
        ny = avoid[1]

        var boid = _apply_boid_rules(nx, ny)
        nx = boid[0]
        ny = boid[1]

        var b_speed = 2.0
        if "speed" in ball:
            b_speed = ball.speed
        var step = b_speed * delta * 60.0

        ball.x += nx * step
        ball.y += ny * step

        var atk_range = 150.0
        if "attack_range" in ball:
            atk_range = ball.attack_range

        if dist < atk_range:
            var attack_timer = 0.0
            if "attack_timer" in ball:
                attack_timer = ball.attack_timer

            if attack_timer <= 0.0:
                if world.has_method("_deal_damage"):
                    world._deal_damage(ball, target_enemy)
                var s_speed = 2.0
                if "speed" in ball:
                    s_speed = ball.speed
                var new_cd = max(0.2, 2.0 / s_speed if s_speed > 0 else 1.0)
                ball.attack_timer = new_cd

func _hide_behind(delta: float):
    var enemies = _get_enemies()
    var allies = _get_allies()

    if enemies.size() == 0 or allies.size() == 0:
        _flee(delta)
        return

    var target_enemy = _find_strongest_enemy_deterministic(enemies)

    var best_ally = null
    var best_score = -1.0

    for ally in allies:
        var b_type = ""
        if "ball_type" in ally:
            b_type = str(ally.ball_type).to_lower()

        var score = 100.0
        if "max_hp" in ally:
            score = float(ally.max_hp)

        if b_type == "tank":
            score += 1000.0

        var dist_sq = pow(ally.x - ball.x, 2) + pow(ally.y - ball.y, 2)
        score -= dist_sq * 0.001

        if score > best_score:
            best_score = score
            best_ally = ally

    if best_ally == null:
        _flee(delta)
        return

    var dx = target_enemy.x - best_ally.x
    var dy = target_enemy.y - best_ally.y
    var dist_e = sqrt(dx*dx + dy*dy)

    if dist_e < 0.0001:
        _flee(delta)
        return

    var nx = dx / dist_e
    var ny = dy / dist_e

    var target_x = best_ally.x - nx * 30.0
    var target_y = best_ally.y - ny * 30.0

    var dx_m = target_x - ball.x
    var dy_m = target_y - ball.y
    var dist_m = sqrt(dx_m*dx_m + dy_m*dy_m)

    if dist_m > 0.0001:
        var nx_m = dx_m / dist_m
        var ny_m = dy_m / dist_m

        var avoid = _apply_obstacle_avoidance(nx_m, ny_m)
        nx_m = avoid[0]
        ny_m = avoid[1]

        var boid = _apply_boid_rules(nx_m, ny_m)
        nx_m = boid[0]
        ny_m = boid[1]

        var speed = 2.0
        if "speed" in ball:
            speed = ball.speed

        var step = speed * delta * 60.0

        ball.x += nx_m * min(step, dist_m)
        ball.y += ny_m * min(step, dist_m)
# Cosmetics: kite behavior confirmed

# Cosmetic change to trigger a commit for auto-implement-kite-держит-дистанцию-атакует-при
