class_name ActionLayer
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):
    var old_x = self.ball.x
    var old_y = self.ball.y

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
        _kite(delta)
    elif strategy == "chase":
        _chase(delta)
    elif strategy == "flank":
        _flank(delta)
    elif strategy == "defend":
        _defend(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        _collect_booster(delta)
    elif strategy == "use skill" or strategy == "use_skill" or strategy == "action_skill" or strategy == "Действие":
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

    self.ball.x += comb_nx * boosted_speed * delta * 60.0
    self.ball.y += comb_ny * boosted_speed * delta * 60.0

func _get_target(enemies: Array) -> Object:
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
            var max_hp = -1.0
            for e in enemies:
                var hp = 0.0
                if "max_hp" in e:
                    hp = e.max_hp
                elif "hp" in e:
                    hp = e.hp
                if hp > max_hp:
                    max_hp = hp
                    target = e
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

func _flank(delta: float):
    var enemies = _get_enemies()
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

        var flank_distance = 40.0
        var flank_x = target.x - target_vx * flank_distance
        var flank_y = target.y - target_vy * flank_distance

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
                    self.ball.damage = original_damage * 2.0

                if self.world != null and self.world.has_method("_deal_damage"):
                    self.world._deal_damage(self.ball, target)

                if is_critical:
                    self.ball.damage = original_damage

                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
    else:
        _idle(delta)


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
                    var max_hp = -1.0
                    var strongest = null
                    for e in enemies:
                        var hp = 0.0
                        if "max_hp" in e: hp = e.max_hp
                        elif "hp" in e: hp = e.hp
                        if hp > max_hp:
                            max_hp = hp
                            strongest = e
                    optimal = (target == strongest)
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

                var max_hp = -1.0
                for e in enemies:
                    var hp = 0.0
                    if "hp" in e:
                        hp = e.hp
                    if hp > max_hp:
                        max_hp = hp
                        target = e
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
        self.ball.use_skill()

        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill

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

        if "skill_cooldown" in self.ball:
            self.ball.skill_timer = self.ball.skill_cooldown

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
    if self.world != null and "width" in self.world and "height" in self.world:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius

        if is_nan(self.ball.x) or is_inf(self.ball.x):
            self.ball.x = self.world.width / 2.0
            bounced = true
        if is_nan(self.ball.y) or is_inf(self.ball.y):
            self.ball.y = self.world.height / 2.0
            bounced = true

        var old_x = self.ball.x
        var old_y = self.ball.y
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
    var enemies = _get_enemies()
    if enemies.size() > 0:
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
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    target = e

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

        var attack_range = 150.0

        if dist_sq > 0.0001:
            var nx = dx / dist
            var ny = dy / dist

            if dist > attack_range:
                pass
            elif dist < attack_range * 0.8:
                nx = -nx
                ny = -ny
            else:
                nx = 0.0
                ny = 0.0

            if nx != 0.0 or ny != 0.0:
                var avoid_vec = _apply_obstacle_avoidance(nx, ny, target)
                nx = avoid_vec[0]
                ny = avoid_vec[1]

                var boid_vec = _apply_boid_rules(nx, ny)
                nx = boid_vec[0]
                ny = boid_vec[1]

                var step = speed * delta * 60.0
                if dist < attack_range * 0.8:
                    self.ball.x += nx * step
                    self.ball.y += ny * step
                else:
                    self.ball.x += nx * min(step, dist)
                    self.ball.y += ny * min(step, dist)

        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        var dist_after = 0.0
        if dist_sq > 0.0001:
            dist_after = sqrt(dist_sq)

        attack_range = 150.0

        if dist_after <= attack_range:
            var skill_timer = 0.0
            if "skill_timer" in self.ball:
                skill_timer = self.ball.skill_timer

            if skill_timer <= 0:
                if dist_after < attack_range * 0.8:
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
                    self.world._deal_damage(self.ball, target)

                var cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                if "attack_timer" in self.ball:
                    self.ball.attack_timer = cooldown
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("attack_timer", cooldown)
    else:
        _idle(delta)
