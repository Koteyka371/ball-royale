class_name ActionLayer
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):
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
    elif strategy == "attack" or strategy == "chase":
        _attack(delta)
    elif strategy == "defend":
        _defend(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        _collect_booster(delta)
    elif strategy == "use skill":
        _use_skill()
    else:
        _idle(delta)

    _clamp_position()
    _update_skill_timer(delta)

func _get_enemies() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("enemies"):
            return entities["enemies"]
        elif typeof(entities) == TYPE_ARRAY:
            var enemies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type != b_type:
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
                    if e_type == b_type and e != self.ball:
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
    var dist = sqrt(dx*dx + dy*dy)

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
        var adist = sqrt(adx*adx + ady*ady)
        if adist > 0.01:
            ally_nx = adx / adist
            ally_ny = ady / adist

    var safe_nx = 0.0
    var safe_ny = 0.0
    if self.world != null and "width" in self.world and "height" in self.world:
        var center_x = self.world.width / 2.0
        var center_y = self.world.height / 2.0
        var cdx = center_x - self.ball.x
        var cdy = center_y - self.ball.y
        var cdist = sqrt(cdx*cdx + cdy*cdy)

        var min_center_dim = center_x
        if center_y < center_x:
            min_center_dim = center_y

        if cdist > min_center_dim * 0.3 and cdist > 0.01:
            safe_nx = cdx / cdist
            safe_ny = cdy / cdist

    var comb_nx = flee_nx * 1.0 + ally_nx * 0.4 + safe_nx * 0.3
    var comb_ny = flee_ny * 1.0 + ally_ny * 0.4 + safe_ny * 0.3

    var comb_dist = sqrt(comb_nx*comb_nx + comb_ny*comb_ny)
    if comb_dist > 0.01:
        comb_nx /= comb_dist
        comb_ny /= comb_dist

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var boosted_speed = speed * 1.5

    self.ball.x += comb_nx * boosted_speed * delta * 60.0
    self.ball.y += comb_ny * boosted_speed * delta * 60.0

func _attack(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = null
        var min_dist_sq = INF
        for e in enemies:
            var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                target = e

        var personality = "idle"
        if "personality" in self.ball:
            personality = self.ball.personality

        if personality == "sniper" and self.ball.has_method("set_meta"):
            var has_msg = false
            if self.ball.has_meta("team_message"):
                has_msg = self.ball.get_meta("team_message") != null
            if not has_msg:
                self.ball.set_meta("team_message", {"type": "target_spotted", "x": target.x, "y": target.y})

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist = sqrt(dx*dx + dy*dy)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        var nx = 0.0
        var ny = 0.0
        if dist > 0.01:
            nx = dx / dist
            ny = dy / dist

        # --- BOIDS LOGIC FOR SWARM ---
        if personality == "swarm":
            var allies = _get_allies()
            var swarm_allies = []
            for a in allies:
                var a_pers = ""
                if "personality" in a:
                    a_pers = a.personality
                if a_pers == "swarm":
                    swarm_allies.append(a)

            if swarm_allies.size() > 0:
                var sep_x = 0.0
                var sep_y = 0.0
                var align_x = 0.0
                var align_y = 0.0
                var coh_x = 0.0
                var coh_y = 0.0

                var ball_radius = 10.0
                if "radius" in self.ball: ball_radius = self.ball.radius
                var perception = 250.0
                if "perception_radius" in self.ball: perception = self.ball.perception_radius

                var sep_count = 0
                var coh_count = 0
                var align_count = 0

                for a in swarm_allies:
                    var adx = self.ball.x - a.x
                    var ady = self.ball.y - a.y
                    var adist = sqrt(adx*adx + ady*ady)

                    # Separation
                    if adist > 0.0001 and adist < ball_radius * 3.0:
                        sep_x += adx / adist
                        sep_y += ady / adist
                        sep_count += 1

                    # Alignment
                    if adist < perception * 0.5:
                        if a.has_method("get_meta") and a.has_meta("vx"):
                            align_x += a.get_meta("vx")
                        elif "vx" in a:
                            align_x += a.vx
                        if a.has_method("get_meta") and a.has_meta("vy"):
                            align_y += a.get_meta("vy")
                        elif "vy" in a:
                            align_y += a.vy
                        align_count += 1

                    # Cohesion
                    if adist < perception * 0.5:
                        coh_x += a.x
                        coh_y += a.y
                        coh_count += 1

                if sep_count > 0:
                    sep_x /= sep_count
                    sep_y /= sep_count

                if align_count > 0:
                    align_x /= align_count
                    align_y /= align_count

                if coh_count > 0:
                    coh_x /= coh_count
                    coh_y /= coh_count
                    # Vector from self to center of mass
                    coh_x = coh_x - self.ball.x
                    coh_y = coh_y - self.ball.y
                    var coh_dist = sqrt(coh_x*coh_x + coh_y*coh_y)
                    if coh_dist > 0.0001:
                        coh_x /= coh_dist
                        coh_y /= coh_dist

                # Combine weights: 1.0 Target, 1.5 Separation, 0.5 Alignment, 0.5 Cohesion
                nx = nx * 1.0 + sep_x * 1.5 + align_x * 0.5 + coh_x * 0.5
                ny = ny * 1.0 + sep_y * 1.5 + align_y * 0.5 + coh_y * 0.5

                # Normalize again
                var comb_dist = sqrt(nx*nx + ny*ny)
                if comb_dist > 0.0001:
                    nx /= comb_dist
                    ny /= comb_dist

        if dist > 0.01:
            var step = speed * delta * 60.0

            # Save velocity for alignment
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("vx", nx)
                self.ball.set_meta("vy", ny)
            else:
                if "vx" in self.ball: self.ball.vx = nx
                if "vy" in self.ball: self.ball.vy = ny

            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

            # Update distance for damage check
            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist = sqrt(dx*dx + dy*dy)

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + target_radius + 5.0 + 0.01:
            if self.world != null and self.world.has_method("_deal_damage"):
                self.world._deal_damage(self.ball, target)
    else:
        _idle(delta)

func _defend(delta: float):
    _idle(delta * 0.5)

func _collect_booster(delta: float):
    var boosters = _get_boosters()
    if boosters.size() > 0:
        var nearest = null
        var min_dist_sq = INF
        for b in boosters:
            var dist_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = b

        var dx = nearest.x - self.ball.x
        var dy = nearest.y - self.ball.y
        var dist = sqrt(dx*dx + dy*dy)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist > 0.01:
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + 10:
            if self.world != null and self.world.has_method("_collect_booster"):
                self.world._collect_booster(self.ball, nearest)
    else:
        _idle(delta)

func _use_skill():
    if self.ball.has_method("use_skill"):
        self.ball.use_skill()

func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    self.ball.x += randf_range(-1.0, 1.0) * speed * 0.3
    self.ball.y += randf_range(-1.0, 1.0) * speed * 0.3

func _clamp_position():
    if self.world != null and "width" in self.world and "height" in self.world:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius

        if is_nan(self.ball.x) or is_inf(self.ball.x):
            self.ball.x = self.world.width / 2.0
        if is_nan(self.ball.y) or is_inf(self.ball.y):
            self.ball.y = self.world.height / 2.0

        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
